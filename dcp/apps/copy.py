#!/usr/bin/python
# -*- coding: utf-8 -*-

from dcp.graph import schema
from dcp.utils import options, misc, config
from dcp.utils.exceptions import NoDatabase, BadConfig

from sqlalchemy import create_engine


def main():
    '''
    Application entry point.
    '''
    # Parse command line arguments.
    args = options.parser().parse_args()

    # Set the log level.
    misc.set_log_level(args.log_level)

    # Parse the configuration.
    with misc.catch(NoDatabase, BadConfig, InvalidTargets):
        src, dest = config.parse(args.source, args.destination)

    # Connect to the database.
    src['engine'] = create_engine(src['dsn'])

    # Extract the source schema.
    schema.get(src, dest)
