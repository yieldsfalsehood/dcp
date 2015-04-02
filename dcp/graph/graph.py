#!/usr/bin/python
# -*- coding: utf-8 -*-

def add_table_links(G, tables, links):
    '''
    Given a graph and a set of links, add edges to the graph for each
    link.
    '''
    for child, parent in links:
        try:
            child_table = tables[child[0]]
            parent_table = tables[parent[0]]
        except IndexError, KeyError:
            # In this case, the config is specifying we should
            # have an edge to or from a table that doesn't even
            # exist. This isn't recoverable, so stop here.
            raise
        G.add_edge(parent_table, child_table)

def add_table_fks(G, tables):
    '''
    Given a graph and a set of tables, add the table fk's as edges to
    the graphs.
    '''
    for table in tables:
        child_table = table
        for fk in table.foreign_keys:
            parent_table = fk.column.table
            # We might have already added the edge above in the
            # force linkage, but it's not an issue to try adding
            # it again.
            G.add_edge(parent_table, child_table)

def remove_table_unlinks(G, unlinks):
    '''
    Given a graph and a set of links, remove edges from the graph for
    each unlink.
    '''
    for child, parent in unlinks:
        try:
            child_table = source_metadata.tables[child[0]]
            parent_table = source_metadata.tables[parent[0]]
        except IndexError, KeyError:
            # Either the config is broken (not so likely, since
            # both child and parent should have two elements
            # each), or one of them is referencing a table that
            # doesn't even exist.
            continue
        if G.has_edge(parent_table, child_table):
            G.remove_edge(parent_table, child_table)
        else:
            # Maybe give a notice here? If the edge is specified
            # to unlink but doesn't exist, then the state of the
            # graph is as expected. However, user expectations
            # about the state of the database aren't entirely
            # correct.
            pass
