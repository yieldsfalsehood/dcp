#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Used to locate the dcp configuration file.
PATH = '~/.dcp'
DCP_ENV = 'DCP'

# Used to validate configurations in .dcp.
CONFIG_SCHEMA = {
    'type': 'object',
    'properties': {
        'dsn': {'type': 'string'},
        'link': {'type': 'string'},
        'unlink': {'type': 'string'},
    },
    'required': ['dsn'],
    'additionalProperties': False,
}

# Template for a configuration file.
TEMPLATE = '''
# Name of the databases used as source and destination parameters below.
#[database]
# The connection string. See the engine configuration section of the sqlalchemy
# library for details.
#dsn = mysql://user:password@localhost:port/database

# Creates foreign key connections that don't exist in the schema. The key on
# the left is the reference (from) and the key on the right is the primary
# (to).
#link =
#    table1:column1 = table2:column1
#    table1:column2 = table3:column1

# Breaks foreign key connections that exist in the schema. The key on the left
# is the reference (from) and the key on the right is the primary (to).
#unlink =
#    table1:column1 = table2:column1
'''

# Description for the dcp command line tool.
DESCRIPTION = '''
Copies data between databases that share similar schemas. Note that database
parameters need to be configured in ~.dcp first. The ~/.dcp path can be changed
by setting the DCP environment variable. It takes the following format:

%s''' % TEMPLATE
