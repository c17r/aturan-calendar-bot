from unittest.mock import patch, MagicMock

from aturan_calendar_bot.core import handle_logging


@patch('aturan_calendar_bot.core.logbook')
def test_handle_logging_no_path(m_logbook):
    handle_logging(None)

    m_logbook.set_datetime_format.assert_not_called()


@patch('aturan_calendar_bot.core.logbook')
def test_handle_logging_path(m_logbook):
    handle_logging('/one/two/')

    m_logbook.set_datetime_format.assert_called_with("local")
