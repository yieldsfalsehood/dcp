#!/usr/bin/python
# -*- coding: utf-8 -*-

from dcp.graph import schema
from dcp.utils import options, misc, config
from dcp.utils.exceptions import NoDatabase, BadConfig

from sqlalchemy import create_engine, table
from sqlalchemy.sql import expression

import fileinput
import json
import sys

def main():
    '''
    Application entry point.
    '''
    # Parse command line arguments.
    args = options.parser().parse_args()

    # Set the log level.
    misc.set_log_level(args.log_level)

    # Parse the configuration.
    with misc.catch(NoDatabase, BadConfig):
        src, dest = config.parse(args.source, args.destination)

    # Connect to the database.
    dest['engine'] = create_engine(dest['dsn'])

    dest_schema = schema.Schema(dest)

    for line in sys.stdin:
        row = json.loads(line)
        table = dest_schema.tables[row['table']]
        statement = expression.insert(table,
                                      values=row['data'],
                                      inline=True)
        dest['engine'].execute(statement)
