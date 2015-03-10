#!/usr/bin/python
# -*- coding: utf-8 -*-

from dcp import options, utils


def main():
    '''
    Application entry point.
    '''
    # Parse command line arguments.
    args = options.parser().parse_args()

    # Set the log level.
    utils.set_log_level(args.log_level)
