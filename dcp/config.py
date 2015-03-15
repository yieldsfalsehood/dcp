#!/usr/bin/python
# -*- coding: utf-8 -*-

import configparser
from os.path import expanduser
import jsonschema
from jsonschema import ValidationError
from logging import warning

from dcp import utils
from dcp.exceptions import NoDatabase, BadConfig


PATH = '~/.dcp'
SCHEMA = {
    'type': 'object',
    'properties': {
        'dsn': {'type': 'string'},
        'link': {'type': 'string'},
        'unlink': {'type': 'string'},
    },
    'required': ['dsn'],
    'additionalProperties': False,
}


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
    with utils.reraise(KeyError, NoDatabase, name, PATH):
        database = config[name]

    # Validate the database.
    with utils.reraise(ValidationError, BadConfig):
        jsonschema.validate(dict(database), SCHEMA)

    # The overrides are optional.
    result = {'dsn': database['dsn']}

    # Add the overrides.
    with utils.suppress(KeyError):
        result['link'] = format(database['link'])
    with utils.suppress(KeyError):
        result['unlink'] = format(database['unlink'])

    return result


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
    # Create the parser.
    config = configparser.ConfigParser()
    config.read(expanduser(PATH))

    # Parse the targets.
    return database(src, config), database(dest, config)
