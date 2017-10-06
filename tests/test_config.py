from unittest.mock import MagicMock, patch, mock_open

from aturan_calendar_bot.core import get_config, validate_config


@patch('json.loads')
@patch('builtins.open', new_callable=mock_open)
def test_get_config_bad_path(m_open, m_loads):
    m_loads.side_effect = KeyError
    m_open.side_effect = KeyError
    filename = '/my/config/json'

    assert get_config(filename) is None
    m_open.assert_called_with(filename, 'r')
    m_loads.assert_not_called()


@patch('json.loads')
@patch('builtins.open', new_callable=mock_open, read_data='{"a": "b"}')
def test_get_config_bad_json(m_open, m_loads):
    m_loads.side_effect = KeyError

    assert get_config('') is None
    m_open.assert_called_with('', 'r')
    m_loads.assert_called_with('{"a": "b"}')


@patch('builtins.open', new_callable=mock_open, read_data='{"a": "b"}')
def test_get_config_good(m_open):
    assert get_config('') == {'a': 'b'}


def test_validate_config_missing_token():
    rv = validate_config({
        'token_secret': 'one',
        'consumer_key': 'two',
        'consumer_secret': 'three'
    })

    assert "'token'" in rv
    assert "required key not provided" in rv


def test_validate_config_invalid_token():
    rv = validate_config({
        'token': '123',
        'token_secret': 'one',
        'consumer_key': 'two',
        'consumer_secret': 'three'
    })

    assert "'token'" in rv
    assert "does not match" in rv


def test_validate_config_missing_token_secret():
    rv = validate_config({
        'token': '123-456',
        'consumer_key': 'two',
        'consumer_secret': 'three'
    })

    assert "'token_secret'" in rv
    assert "required key not provided" in rv


def test_validate_config_invalid_token_secret():
    rv = validate_config({
        'token': '123-456',
        'token_secret': '',
        'consumer_key': 'two',
        'consumer_secret': 'three'
    })

    assert "'token_secret'" in rv
    assert "length of value must be at least 1" in rv


def test_validate_config_missing_consumer_key():
    rv = validate_config({
        'token': '123-456',
        'token_secret': 'one',
        'consumer_secret': 'three'
    })

    assert "'consumer_key'" in rv
    assert "required key not provided" in rv


def test_validate_config_invalid_consumer_key():
    rv = validate_config({
        'token': '123-456',
        'token_secret': 'one',
        'consumer_key': '',
        'consumer_secret': 'three'
    })

    assert "'consumer_key'" in rv
    assert "length of value must be at least 1" in rv


def test_validate_config_missing_consumer_secret():
    rv = validate_config({
        'token': '123-456',
        'token_secret': 'one',
        'consumer_key': 'two'
    })

    assert "'consumer_secret'" in rv
    assert "required key not provided" in rv


def test_validate_config_invalid_consumer_secret():
    rv = validate_config({
        'token': '123-456',
        'token_secret': 'one',
        'consumer_key': 'two',
        'consumer_secret': ''
    })

    assert "'consumer_secret'" in rv
    assert "length of value must be at least 1" in rv


def test_validate_config_valid():
    rv = validate_config({
        'token': '123-456',
        'token_secret': 'one',
        'consumer_key': 'two',
        'consumer_secret': 'three'
    })

    assert rv is None
