import json
import logging
import sys

import arrow
import twitter as twapi
import voluptuous as v
import logbook

from argparse import ArgumentParser
from raven import Client
from .__version__ import __version__

import aturan_calendar as calendar

_logger = logging.getLogger(__file__)


class CmdLineException(Exception):
    pass


def get_config(path):
    try:
        with open(path, "r") as f:
            raw = f.read()
        return json.loads(raw)
    except Exception as e:
        raise CmdLineException("Config file can't be loaded: " + str(e))


def validate_config(config):
    schema = v.Schema({
        v.Required('twitter'): {
            v.Required('token'): v.All(v.unicode, v.Length(min=1), v.Match(r'\S+-\S+')),
            v.Required('token_secret'): v.All(v.unicode, v.Length(min=1)),
            v.Required('consumer_key'): v.All(v.unicode, v.Length(min=1)),
            v.Required('consumer_secret'): v.All(v.unicode, v.Length(min=1))
        },
        v.Required('sentry'): {
            v.Required('url'): v.unicode
        }
    })
    try:
        schema(config)
    except v.Error as e:
        raise CmdLineException("Config file invalid: " + str(e))

    return None


def get_twitter(config):
    return twapi.Twitter(auth=twapi.OAuth(**config['twitter']))


def check_posted_today(twitter, today):
    tweets = twitter.statuses.user_timeline()
    if len(tweets) == 0:
        return False

    last_str = tweets[0]['created_at']
    stripped = ' '.join(last_str.split(' ')[1:])  # arrow doesn't like day-of-week on parsing
    last = arrow.get(stripped, 'MMM DD HH:mm:ss Z YYYY').to('US/Eastern').floor('day')

    check = arrow.get(today).to('US/Eastern').floor('day')

    return last == check


def format_tweet(today):
    today = arrow.get(today).floor('day')
    cal = calendar.western_to_aturan(today)

    fmt = 'Day #{day_of_year} of {year}\n'

    if cal['month_of_year'] is None:
        fmt += '{day_of_span}'  # special High Holy days; no span, no day of span, no month even
    else:
        cal['day_of_month'] = ordinal(cal['day_of_month'])
        cal['span_of_month'] = ordinal(cal['span_of_month'])
        fmt += '{day_of_span}, the {day_of_month} of {month_of_year} ({span_of_month} Span)'

    return fmt.format(**cal)


def ordinal(num):
    SUFFIXES = {
        1: 'st',
        2: 'nd',
        3: 'rd',
    }
    if 10 <= num % 100 <= 20:
        suffix = 'th'
    else:
        suffix = SUFFIXES.get(num % 10, 'th')
    return "{}{}".format(num, suffix)


def post_tweet(twitter, tweet):
    twitter.statuses.update(status=tweet)


def handle_args(sys_args):
    parser = ArgumentParser()
    parser.add_argument('--config-file', '-c', required=True, type=str)
    parser.add_argument('--log-file', '-l', type=str)
    try:
        return parser.parse_args(sys_args)
    except Exception as e:
        raise CmdLineException(str(e))


def handle_logging(path):
    if not path:
        return

    logbook.set_datetime_format("local")
    logbook.compat.redirect_logging()
    logbook.RotatingFileHandler(
        path,
        level='INFO',
        format_string="{record.time:%Y-%m-%d %H:%M:%S.%f} : {record.level_name} : {record.channel} : {record.message}"
    ).push_application()


def log(log_func, msg):
    if log_func:
        log_func(msg)
    print(msg)


def get_sentry_client(config):
    return Client(dsn=config['sentry']['url'], release=__version__)


def sentry_exception(exc, config):
    if config is None:
        return
    if len(config['sentry']['url']) == 0:
        return
    client = get_sentry_client(config)
    client.captureException(exc)


def main(argv):
    config = None

    try:
        args = handle_args(argv)

        handle_logging(args.log_file)

        config = get_config(args.config_file)
        validate_config(config)

        twitter = get_twitter(config)
        now = arrow.utcnow()

        if check_posted_today(twitter, now):
            log(_logger.info, "Tweet already posted for today, exiting...")
            return 0

        tweet = format_tweet(now)
        post_tweet(twitter, tweet)
        log(_logger.info, "Tweet posted: " + tweet)
        return 0

    except CmdLineException as e:
        log(_logger.error, str(e))
        return -1

    except Exception as e:
        log(_logger.error, str(e))
        sentry_exception(e, config)
        return -2


def cli():
    argv = sys.argv[1:]
    return main(argv)


if __name__ == '__main__':
    sys.exit(cli())
