#!/usr/bin/python
# -*- coding: utf-8 -*-

# Used to get the configuration.
import os
from os.path import expanduser, exists

# Used to parse and validate the configuration.
import configparser
import jsonschema
from jsonschema import ValidationError

# Used to prompt the user.
from logging import warning

# Misc utils.
from dcp.utils import misc
from dcp.utils.exceptions import NoDatabase, BadConfig, InvalidTargets
from dcp.utils.constants import DCP_ENV, PATH, TEMPLATE, CONFIG_SCHEMA


def path():
    '''
    Return the path of the configuration file.
    '''
    return os.environ.get(DCP_ENV, PATH)


def format(value):
    '''
    Formats the link value into the format expected by parse.
    '''
    result = []
    for line in value.strip().splitlines():
        # Test the config.
        if not (line.count('=') == 1 and line.count(':') == 2):
            warning('Ignoring invalid configuration: %s', line.strip())
            continue

        # Split helper.
        def split(item, char):
            return tuple(item.strip().split(char))

        # Append the result.
        left, right = split(line, '=')
        result.append((split(left, ':'), split(right, ':')))

    return tuple(result)


def database(name, config):
    '''
    Extracts and formats the configuration as expected by parse.
    '''
    # Get the target database.
    with misc.reraise(KeyError, NoDatabase, name, PATH):
        database = config[name]

    # Validate the database.
    with misc.reraise(ValidationError, BadConfig):
        jsonschema.validate(dict(database), CONFIG_SCHEMA)

    # The overrides are optional.
    result = {'dsn': database['dsn']}

    # Add the overrides.
    with misc.suppress(KeyError):
        result['link'] = format(database['link'])
    with misc.suppress(KeyError):
        result['unlink'] = format(database['unlink'])

    return result


def template():
    '''
    If the config file doesn't exist, create it.
    '''
    if not exists(path()):
        with misc.open(path(), 'w') as file:
            file.write(TEMPLATE)


def parse(src, dest):
    '''
    Parses the configuration and returns the following structure:

    [
        # source
        {
            'dsn': 'dsn',
            'link': [
                (('table1', 'column1'), ('table2', 'column2')),
                (('table1', 'column1'), ('table3', 'column2')),
            ],
            'unlink': [
                # Same as link.
            ],
        },
        # destination
        {
            # Same as source.
            ...
        },
    ]

    Returns None if the configuration can't be parsed.
    '''
    # Check the source and destinations.
    if src == dest:
        message = 'The source and destination databases are the same.'
        raise InvalidTargets(message)

    # Template the config file.
    template()

    # Create the parser.
    config = configparser.ConfigParser()
    config.read(expanduser(PATH))

    # Parse the targets.
    return database(src, config), database(dest, config)
