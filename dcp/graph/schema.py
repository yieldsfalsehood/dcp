#!/usr/bin/python
# -*- coding: utf-8 -*-

import networkx
from sqlalchemy import MetaData


def foreign_keys(meta, schema):
    '''
    Adds foreign key data to the schema.
    '''
    for table in meta.tables:
        child = table

        # Add the foreign keys.
        for key in table.foreign_keys:
            parent = key.column.table

            # We might have already added the edge above in the  force linkage,
            # but it's not an issue to try adding it again.
            schema.add_edge(child, parent)


def get(src, dest):
    '''
    Extracts the configuration augmented schema from the source. Returns a
    graph representing the schema.
    '''
    # Get metadata.
    meta = MetaData()
    meta.reflect(bind=src['engine'])

    # Create the network.
    schema = networkx.DiGraph()

    # Add data.
    foreign_keys(meta, schema)
