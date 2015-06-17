#!/usr/bin/python
# -*- coding: utf-8 -*-

from dcp.utils import misc

import networkx

from sqlalchemy import MetaData
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

class hashabledict(dict):
    '''
    From https://stackoverflow.com/a/1151705/808806
    '''
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

class hashablelist(list):
    def __hash__(self):
        return hash(tuple(sorted(self)))

def memoize(func):
    '''
    Record which (table, filters) pairs have been queried for already.
    '''
    def memoized(self, table, filters=None):

        if isinstance(filters, dict):
            hashable_filters = hashabledict(filters)
        elif isinstance(filters, list):
            hashable_filters = hashablelist(filters)
        elif filters is None:
            hashable_filters = None
        else:
            pass

        if table not in self._visited or hashable_filters not in self._visited[table]:
            if table in self._visited:
                self._visited[table].add(hashable_filters)
            else:
                self._visited[table] = set((hashable_filters,))
            return func(self, table, filters)

    return memoized

class Schema(object):
    '''
    Encapsulates a database schema, using a digraph for capturing
    relationships between tables.
    '''

    def __init__(self, src):
        '''
        Extracts the configuration-augmented schema from the source database.
        '''

        # Get metadata.
        meta = MetaData()
        meta.reflect(bind=src['engine'])

        self.Session = sessionmaker(bind=src['engine'])
        self.session = self.Session()

        # Create the network.The nodes of this graph will be the SA table
        # objects we just reflected and an edge a -> b will mean that
        # table a has a foreign key depedency on table b.
        schema = networkx.DiGraph()

        self.meta = meta
        self.schema = schema
        self.src = src

        # _visited will contain the pairs (table, filters) for all
        # queries executed against this schema, to avoid visiting the
        # same rows of data more than once. Each self._visited[table]
        # is a set of (hashable) filters.
        self._visited = {}

        # tables is a mapping of table names to SA table objects
        self.tables = {table: meta.tables[table] for table in meta.tables}

        # Add edges for manually configured links
        for child, parent in src['link']:
            # KeyError will be raised if the config is specifying we
            # should have an edge to or from a table that doesn't
            # exist. This isn't recoverable, so reraise it.
            child_table = meta.tables[child[0]]
            parent_table = meta.tables[parent[0]]
            fk_mapping = {child[1]: parent[1]}
            schema.add_edge(child_table, parent_table, fk_mapping)

        # Add edges for foreign keys
        for table in meta.tables:
            child = meta.tables[table]

            # Add the foreign keys.
            for key in child.foreign_keys:

                parent = key.column.table

                # Extract a dictionary of column->column mappings
                # between this table and its referenced table
                fk_mapping = {}
                for src_col, target_col in zip(key.constraint.columns,
                                               key.constraint.elements):
                    fk_mapping[src_col.name] = target_col.column.name

                # We might have already added the edge above in the
                # force linkage, but it's not an issue to try adding
                # it again.
                schema.add_edge(child, parent, fk_mapping)

        # Remove manually configured "unlinks"
        for child, parent in src['unlink']:

            # In this case, a KeyError is OK - if either the child or
            # parent doesn't exist then for sure there will be no edge
            # between them in our graph.
            with misc.suppress(KeyError):
                child_table = meta.tables[child[0]]
                parent_table = meta.tables[parent[0]]

                if schema.has_edge(parent_table, child_table):
                    schema.remove_edge(parent_table, child_table)
                else:
                    # Maybe give a notice here? If the edge is specified
                    # to unlink but doesn't exist, then the state of the
                    # graph is as expected. However, user expectations
                    # about the state of the database aren't entirely
                    # correct.
                    pass

    def parents(self, table):
        '''
        Returns an iterator over the edges to child table(s) of the
        given table. Results are in the format (child, d), where d is
        a dictionary containing the edge data.
        '''
        for u, v, d in self.schema.out_edges_iter(table, data=True):
            yield v, d

    def children(self, table):
        '''
        Returns an iterator over the edges from child table(s) of the
        given table. Results are in the format (parent, d), where d is
        a dictionary containing the edge data.
        '''
        for u, v, d in self.schema.in_edges_iter(table, data=True):
            yield u, d

    @memoize
    def _query(self, table, filters=None):
        '''
        Issue a query against `table` using `filters` to filter rows
        and return an iterator over each row of data, provided as a
        dict.
        '''

        if isinstance(filters, basestring):
            query = self.session.query(table).filter(filters)
        elif isinstance(filters, dict):
            query = self.session.query(table).filter_by(**filters)
        elif isinstance(filters, list):
            filters = [text(filter_) for filter_ in filters]
            query = self.session.query(table).filter(*filters)
        elif filters is None:
            query = self.session.query(table)
        else:
            pass

        pk_columns = table.primary_key.columns

        for row in query:
            data = row._asdict()
            pk = {column.name: data[column.name] for column in pk_columns}
            yield {
                'table': table.name,
                'pk': pk,
                'data': data,
            }

    def _walk_parents(self, table, row, filters=None):
        '''
        Perform a DFS walk up the tree from the given table.
        '''
        for parent, edge_data in self.parents(table):

            parent_filters = {}
            for src_col, target_col in edge_data.iteritems():
                parent_filters[target_col] = row['data'][src_col]

            for this_row in self._query(parent, parent_filters):
                for parent_row in self._walk_parents(parent,
                                                     this_row,
                                                     parent_filters):
                    yield this_row

                yield this_row

    def _walk_children(self, table, row, filters=None):
        '''
        Perform a DFS down the tree from the given table.
        '''
        for child, edge_data in self.children(table):

            # Note: the table/row pair we were given as input are this
            # child table row's parent, so the roles of src_col and
            # target_col here are opposite what they are in
            # _walk_parents.
            child_filters = {}
            for src_col, target_col in edge_data.iteritems():
                child_filters[src_col] = row['data'][target_col]

            for this_row in self._query(child, child_filters):
                for child_row in self._walk_children(child,
                                                     this_row,
                                                     child_filters):
                    yield child_row

                yield this_row

    def data(self, table, filters=None):

        if isinstance(table, basestring):
            table = self.tables[table]

        for row in self._query(table, filters):

            for parent_row in self._walk_parents(table, row):
                yield parent_row

            yield row

            for child_row in self._walk_children(table, row):
                yield child_row
