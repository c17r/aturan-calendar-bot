from unittest.mock import patch, MagicMock

from aturan_calendar_bot.core import sentry_exception


@patch('aturan_calendar_bot.core.get_sentry_client')
def test_no_config(m_client):
    rv = sentry_exception(None, None)

    m_client.assert_not_called()


@patch('aturan_calendar_bot.core.get_sentry_client')
def test_no_url(m_client):
    rv = sentry_exception(None, {'sentry': {'url': ''}})

    m_client.assert_not_called()


@patch('aturan_calendar_bot.core.get_sentry_client')
def test_good(m_client):
    config = {'sentry': {'url': 'hi'}}
    rv = sentry_exception(KeyError(), config)

    m_client.assert_called_with(config)
