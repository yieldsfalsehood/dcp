#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse


DESCRIPTION = '''
Copies data between databases that share similar schemas. Note that database
parameters need to be configured in ~.dcp first. It takes the following format:

# Name of the databases used as source and destination parameters below.
[database]
# The connection string. See the engine configuration section of the sqlalchemy
# library for details.
dsn = mysql://user:password@localhost:port/database

# Creates foreign key connections that don't exist in the schema. The key on
# the left is the reference (from) and the key on the right is the primary
# (to).
link =
    table1:column1 = table2:column1
    table1:column2 = table3:column1

# Breaks foreign key connections that exist in the schema. The key on the left
# is the reference (from) and the key on the right is the primary (to).
unlink =
    table1:column1 = table2:column1
'''


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
