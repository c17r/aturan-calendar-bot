import argparse
import pytest
import sys
from io import StringIO
from unittest.mock import patch

from aturan_calendar_bot.core import handle_args, CmdLineException


class StdIOBuffer(StringIO):
    pass


class ArgumentParserError(Exception):
    def __init__(self, message, stdout=None, stderr=None, error_code=None):
        Exception.__init__(self, message, stdout, stderr)
        self.message = message
        self.stdout = stdout
        self.stderr = stderr
        self.error_code = error_code


def stderr_to_parser_error(parse_args, *args, **kwargs):
    # if this is being called recursively and stderr or stdout is already being
    # redirected, simply call the function and let the enclosing function
    # catch the exception
    if isinstance(sys.stderr, StdIOBuffer) or isinstance(sys.stdout, StdIOBuffer):
        return parse_args(*args, **kwargs)

    # if this is not being called recursively, redirect stderr and
    # use it as the ArgumentParserError message
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StdIOBuffer()
    sys.stderr = StdIOBuffer()
    try:
        try:
            result = parse_args(*args, **kwargs)
            for key in list(vars(result)):
                if getattr(result, key) is sys.stdout:
                    setattr(result, key, old_stdout)
                if getattr(result, key) is sys.stderr:
                    setattr(result, key, old_stderr)
            return result
        except SystemExit:
            code = sys.exc_info()[1].code
            stdout = sys.stdout.getvalue()
            stderr = sys.stderr.getvalue()
            raise ArgumentParserError("SystemExit", stdout, stderr, code)
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


class ErrorRaisingArgumentParser(argparse.ArgumentParser):

    def parse_args(self, *args, **kwargs):
        parse_args = super(ErrorRaisingArgumentParser, self).parse_args
        return stderr_to_parser_error(parse_args, *args, **kwargs)

    def exit(self, *args, **kwargs):
        exit = super(ErrorRaisingArgumentParser, self).exit
        return stderr_to_parser_error(exit, *args, **kwargs)

    def error(self, *args, **kwargs):
        error = super(ErrorRaisingArgumentParser, self).error
        return stderr_to_parser_error(error, *args, **kwargs)


@patch('aturan_calendar_bot.core.ArgumentParser')
def test_handle_args_missing_config(m_parser):
    log_file = '/a/log.txt'
    m_parser.return_value = ErrorRaisingArgumentParser()

    with pytest.raises(CmdLineException):
        rv = handle_args(['-l', log_file])


def test_handle_args_valid_config():
    config_file = '/a/config.txt'

    rv = handle_args(['-c', config_file])

    assert rv.config_file == config_file


def test_handle_args_missing_log():
    config_file = '/a/config.txt'

    rv = handle_args(['-c', config_file])

    assert rv.log_file is None


def test_handle_args_valid_log():
    config_file = '/a/config.txt'
    log_file = '/a/log.txt'

    rv = handle_args(['-c', config_file, '-l', log_file])

    assert rv.log_file == log_file
