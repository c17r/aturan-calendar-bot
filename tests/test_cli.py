import sys

from unittest.mock import patch, MagicMock

from aturan_calendar_bot.core import cli


@patch('aturan_calendar_bot.core.main')
def test_empty(m_main):

    with patch('sys.argv', ['app']):
        cli()

    m_main.assert_called_with([])


@patch('aturan_calendar_bot.core.main')
def test_good(m_main):

    with patch('sys.argv', ['app', 'one', 'two']):
        cli()

    m_main.assert_called_with(['one', 'two'])
