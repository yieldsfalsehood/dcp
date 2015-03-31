#!/usr/bin/python
# -*- coding: utf-8 -*-

from dcp.utils import options, misc, config
from dcp.utils.exceptions import NoDatabase, BadConfig, InvalidTargets


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
        config.parse(args.source, args.destination)
