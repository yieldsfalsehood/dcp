#!/usr/bin/python
# -*- coding: utf-8 -*-

from dcp.graph import schema
from dcp.utils import options, misc, config
from dcp.utils.exceptions import NoDatabase, BadConfig

from sqlalchemy import create_engine
from sqlalchemy.sql import expression

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

    # Connect to the databases.
    src['engine'] = create_engine(src['dsn'])
    dest['engine'] = create_engine(dest['dsn'])

    # Extract the schemas.
    source_schema = schema.Schema(src)
    dest_schema = schema.Schema(dest)

    for row in source_schema.data(args.table, args.columns):
        table = dest_schema.tables[row['table']]
        statement = expression.insert(table,
                                      values=row['data'],
                                      inline=True)
        dest['engine'].execute(statement)
