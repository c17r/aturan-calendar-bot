import argparse
import json
import logging
import sys

import arrow
import twitter as twapi
import voluptuous as v
import logbook

import aturan_calendar as calendar

_logger = logging.getLogger(__file__)

def get_config(path):
    try:
        with open(path, "r") as f:
            raw = f.read()
        return json.loads(raw)
    except:
        return None


def validate_config(config):
    schema = v.Schema({
        v.Required('token'): v.All(v.unicode, v.Length(min=1), v.Match(r'\S+-\S+')),
        v.Required('token_secret'): v.All(v.unicode, v.Length(min=1)),
        v.Required('consumer_key'): v.All(v.unicode, v.Length(min=1)),
        v.Required('consumer_secret'): v.All(v.unicode, v.Length(min=1)),
    })
    try:
        schema(config)
    except v.Error as e:
        return str(e)

    return None


def get_twitter(config):
    return twapi.Twitter(auth=twapi.OAuth(**config))


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


def handle_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config-file', '-c',
        required=True,
        type=str
    )
    parser.add_argument(
        '--log-file', '-l',
        type=str
    )
    return parser.parse_args()


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


def main():
    args = handle_args()

    handle_logging(args.log_file)

    config = get_config(args.config_file)
    if config is None:
        log(_logger.error, "Config file can't be loaded")
        return -1

    err = validate_config(config)
    if err is not None:
        log(_logger.error, err)
        return -1

    twitter = get_twitter(config)
    now = arrow.utcnow()
    if check_posted_today(twitter, now):
        log(_logger.info, "Tweet already posted for today, exiting...")
        return 0
    tweet = format_tweet(now)
    post_tweet(twitter, tweet)
    log(_logger.info, "Tweet posted: " + tweet)

    return 0


if __name__ == '__main__':
    sys.exit(main())
