#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging
from contextlib import contextmanager


def set_log_level(level):
    '''
    Set the log level using a string.
    '''
    lookup = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
    }
    logging.basicConfig(level=lookup[level])


@contextmanager
def reraise(src, dest, *args, **kwargs):
    '''
    Catches and swaps src with dest. dest is a function of the form:

    exception = dest(exception, *args, **kwargs)

    exception is raised.
    '''
    try:
        yield

    except src as exception:
        raise dest(exception, *args, **kwargs)


@contextmanager
def catch(exceptions):
    '''
    Catches, logs and suppresses the list of exceptions.
    '''
    try:
        yield

    except Exception as exception:
        # Test the exception.
        tests = [isinstance(exception, item) for item in exceptions]

        # Exit early.
        if not any(tests):
            raise

        # Log the exception and exit.
        logging.exception(exception)
        sys.exit(1)
