#!/usr/bin/python
# -*- coding: utf-8 -*-

from dcp import options, utils, config
from dcp.exceptions import NoDatabase, BadConfig


def main():
    '''
    Application entry point.
    '''
    # Parse command line arguments.
    args = options.parser().parse_args()

    # Set the log level.
    utils.set_log_level(args.log_level)

    # Parse the configuration.
    with utils.catch((NoDatabase, BadConfig)):
        config.parse(args.source, args.destination)
