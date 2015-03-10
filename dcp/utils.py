#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging


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
