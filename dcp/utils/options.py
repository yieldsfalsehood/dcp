#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
from dcp.utils.constants import DESCRIPTION


def parser():
    '''
    Returns a command line parser.
    '''
    # Create the parser.
    formatter = argparse.RawTextHelpFormatter
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                                     formatter_class=formatter)

    # Add source and destination databases.
    help = 'The source database.'
    parser.add_argument('source', type=str, help=help)
    help = 'The destination database.'
    parser.add_argument('destination', type=str, help=help)

    # Add query specific parameters.
    help = 'The target table.'
    parser.add_argument('table', type=str, help=help)
    help = ('The query in the format of column=value. Multiple\ncolumn value '
            'pairs can be specified.')
    parser.add_argument('columns', type=str, help=help, nargs='+')

    # Add the log level.
    name = '--log-level'
    help = 'The log level.'
    choices = ('debug', 'info', 'warning', 'error', 'critical')
    parser.add_argument(name, choices=choices, default='warning', help=help)

    # Parse arguments and return.
    return parser
