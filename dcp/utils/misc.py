#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import logging
from contextlib import contextmanager
from collections import Iterable


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


class IdentityError(Exception):
    '''
    Used in conjunction with reraise. This exception casts the original
    exception as a string and raises a new exception with that string.
    '''
    def __init__(self, src):
        super(Exception, self).__init__(src.message)


def iter(target):
    '''
    If target is already iterable and not a string, target is returned.
    Otherwise tuple(target) is returned.
    '''
    if isinstance(target, Iterable) and not isinstance(target, str):
        return target

    return (target, )


@contextmanager
def trap(trigger, *exceptions):
    '''
    Runs the trigger when the exception is trapped. trigger is a function
    that accepts the trapped exception instance as a parameter.
    '''
    try:
        yield

    except Exception as exception:
        # Test the exception.
        tests = [isinstance(exception, item) for item in exceptions]

        # Exit early.
        if not any(tests):
            raise

        # Trigger the trap.
        trigger(exception)


@contextmanager
def reraise(src, dest, *args, **kwargs):
    '''
    Catches and swaps srcs with dest. srcs is either an iterable or single
    class of exception.

    exception = dest(exception, *args, **kwargs)

    exception is raised.
    '''
    # Raise the new exception.
    def trigger(exception):
        raise dest(exception, *args, **kwargs)

    # Trap the exception.
    with trap(trigger, *iter(src)):
        yield


@contextmanager
def catch(*exceptions):
    '''
    Catches, logs and suppresses the list of exceptions.
    '''
    # Log the exception and exit.
    def trigger(exception):
        logging.error(exception.message)
        sys.exit(1)

    # Trap the exception.
    with trap(trigger, *exceptions):
        yield


@contextmanager
def suppress(*exceptions):
    '''
    Catches, and suppresses the list of exceptions without logging.
    '''
    # Suppress the exception.
    def trigger(exception):
        pass

    # Trap the exception.
    with trap(trigger, *exceptions):
        yield
