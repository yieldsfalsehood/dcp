#!/usr/bin/python
# -*- coding: utf-8 -*-

import configparser
from os.path import expanduser
import jsonschema
from jsonschema import ValidationError

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
    # Functional helper functions.
    def strip(item):
        return item.strip()

    def split(char, item):
        return tuple(strip(part) for part in item.split(char, 1))

    # Split lines in = first and then by :.
    return tuple(
        tuple(split(':', part) for part in split('=', line))
        for line in value.strip().split()
    )


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

    try:
        # Add the overrides.
        result['link'] = format(database['link'])
        result['unlink'] = format(database['unlink'])

    except KeyError:
        pass

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
