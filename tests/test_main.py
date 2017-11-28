from unittest.mock import patch, MagicMock
import logging
import sys

from aturan_calendar_bot.core import main, _logger, CmdLineException


@patch('aturan_calendar_bot.core.sentry_exception')
@patch('aturan_calendar_bot.core.handle_args')
@patch('aturan_calendar_bot.core.handle_logging')
@patch('aturan_calendar_bot.core.get_config')
@patch('aturan_calendar_bot.core.validate_config')
@patch('aturan_calendar_bot.core.get_twitter')
@patch('aturan_calendar_bot.core.check_posted_today')
@patch('aturan_calendar_bot.core.format_tweet')
@patch('aturan_calendar_bot.core.post_tweet')
@patch('aturan_calendar_bot.core.log')
def test_main_no_config(m_log, m_post, m_format, m_check, m_twitter, m_validate, m_config, m_logging, m_args, m_sentry):
    m_config.side_effect = CmdLineException("Config file can't be loaded")

    rv = main(['one', 'two'])

    assert rv == -1
    m_log.assert_called_with(_logger.error, "Config file can't be loaded")
    m_validate.assert_not_called()
    m_sentry.assert_not_called()


@patch('aturan_calendar_bot.core.sentry_exception')
@patch('aturan_calendar_bot.core.handle_args')
@patch('aturan_calendar_bot.core.handle_logging')
@patch('aturan_calendar_bot.core.get_config')
@patch('aturan_calendar_bot.core.validate_config')
@patch('aturan_calendar_bot.core.get_twitter')
@patch('aturan_calendar_bot.core.check_posted_today')
@patch('aturan_calendar_bot.core.format_tweet')
@patch('aturan_calendar_bot.core.post_tweet')
@patch('aturan_calendar_bot.core.log')
def test_main_invalid_config(m_log, m_post, m_format, m_check, m_twitter, m_validate, m_config, m_logging, m_args, m_sentry):
    m_validate.side_effect = CmdLineException('test error')

    rv = main(['one', 'two'])

    assert rv == -1
    m_log.assert_called_with(_logger.error, 'test error')
    m_twitter.assert_not_called()
    m_sentry.assert_not_called()


@patch('aturan_calendar_bot.core.sentry_exception')
@patch('aturan_calendar_bot.core.handle_args')
@patch('aturan_calendar_bot.core.handle_logging')
@patch('aturan_calendar_bot.core.get_config')
@patch('aturan_calendar_bot.core.validate_config')
@patch('aturan_calendar_bot.core.get_twitter')
@patch('aturan_calendar_bot.core.check_posted_today')
@patch('aturan_calendar_bot.core.format_tweet')
@patch('aturan_calendar_bot.core.post_tweet')
@patch('aturan_calendar_bot.core.log')
def test_unexpected(m_log, m_post, m_format, m_check, m_twitter, m_validate, m_config, m_logging, m_args, m_sentry):
    exc = Exception('Unexpected')
    m_twitter.side_effect = exc
    m_config.return_value = {}

    rv = main(['one', 'two'])

    assert rv == -2
    m_log.assert_called_with(_logger.error, 'Unexpected')
    m_sentry.assert_called_with(exc, {})


@patch('aturan_calendar_bot.core.sentry_exception')
@patch('aturan_calendar_bot.core.handle_args')
@patch('aturan_calendar_bot.core.handle_logging')
@patch('aturan_calendar_bot.core.get_config')
@patch('aturan_calendar_bot.core.validate_config')
@patch('aturan_calendar_bot.core.get_twitter')
@patch('aturan_calendar_bot.core.check_posted_today')
@patch('aturan_calendar_bot.core.format_tweet')
@patch('aturan_calendar_bot.core.post_tweet')
@patch('aturan_calendar_bot.core.log')
def test_main_already_tweeted(m_log, m_post, m_format, m_check, m_twitter, m_validate, m_config, m_logging, m_args, m_sentry):
    m_validate.return_value = None
    m_check.return_value = True

    rv = main(['one', 'two'])

    assert rv == 0
    m_log.assert_called_with(_logger.info, 'Tweet already posted for today, exiting...')
    m_format.assert_not_called()


@patch('aturan_calendar_bot.core.sentry_exception')
@patch('aturan_calendar_bot.core.handle_args')
@patch('aturan_calendar_bot.core.handle_logging')
@patch('aturan_calendar_bot.core.get_config')
@patch('aturan_calendar_bot.core.validate_config')
@patch('aturan_calendar_bot.core.get_twitter')
@patch('aturan_calendar_bot.core.check_posted_today')
@patch('aturan_calendar_bot.core.format_tweet')
@patch('aturan_calendar_bot.core.post_tweet')
@patch('aturan_calendar_bot.core.log')
def test_main_post_tweet(m_log, m_post, m_format, m_check, m_twitter, m_validate, m_config, m_logging, m_args, m_sentry):
    m_validate.return_value = None
    m_check.return_value = False
    tweet = "hello"
    m_format.return_value = tweet
    m_twitter_object = MagicMock()
    m_twitter.return_value = m_twitter_object

    rv = main(['one', 'two'])

    assert rv == 0
    m_post.assert_called_with(m_twitter_object, tweet)
    m_log.assert_called_with(_logger.info, 'Tweet posted: ' + tweet)
