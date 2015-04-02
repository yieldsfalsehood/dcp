#!/usr/bin/python
# -*- coding: utf-8 -*-

from dcp.graph import graph
from dcp.utils import options, misc, config
from dcp.utils.exceptions import NoDatabase, BadConfig, InvalidTargets

import networkx as nx
from sqlalchemy import create_engine, MetaData

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
        source, destination = config.parse(args.source, args.destination)

        # Get a connection to the source database and reflect all the
        # metadata.
        source_engine = create_engine(source["dsn"])
        source_metadata = MetaData()
        source_metadata.reflect(bind=source_engine)

        # The nodes of this graph will be the SA Table objects we just
        # reflected and an edge a -> b will mean that table b has a
        # foreign key depedency on table a - that's a little backwards
        # from expectations, but if a topological sorting is used
        # later this is what is needed.
        G = nx.DiGraph()

        graph.add_linked_tables(G, source_metadata.tables, source["link"])
        graph.add_table_fks(G, source_metadata.tables)
        graph.remove_table_unlinks(G, source_metadata.tables, source["unlink"])
