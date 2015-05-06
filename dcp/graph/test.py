#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Testing tools.
import sqlite3
import tempfile
import unittest

from dcp.utils import options, config

from sqlalchemy import create_engine

# To be tested.
from dcp.graph import schema

queries = [
'''
PRAGMA foreign_keys = ON;
''',

'''
CREATE TABLE distributors (
  id bigint PRIMARY KEY,
  name text NOT NULL
);
''',

'''
CREATE TABLE movies (
  id bigint PRIMARY KEY,
  distributor bigint REFERENCES distributors (id),
  name text NOT NULL,
  code text
);
''',

'''
CREATE TABLE types (
  id bigint PRIMARY KEY,
  name text NOT NULL
);
''',

'''
/*
 * The distributor here is intentionally a redundant key to
 * distributors, used to verify that a) manual linking will cause the
 * edge to appear in the graph and b) the distributor data is properly
 * memoized and only appears once in the output.
 */
CREATE TABLE movie_reviews (
  id bigint PRIMARY KEY,
  movie bigint REFERENCES movies (id),
  distributor bigint,
  reviewer text NOT NULL,
  review text
);
''',

'''
-- Copy in the data.
insert into distributors (id, name)
values
(1,	'new videos'),
(2,	'old videos'),
(3,	'cat videos')
;
''',

'''
insert into types (id, name)
values
(1,	'social'),
(2,	'movies'),
(3,	'articles')
;
''',

'''
insert into movies (id, distributor, name, code)
values
(1,	1,	'The New Superheroes',	null),
(2,	2,	'A Generic Western',	'12345ABC'),
(3,	1,	'Something Techish',	null),
(4,	1,	'A Dystopian Future',	null),
(5,	2,	'A Black and White Romance',	'5'),
(6,	3,	'A Startled Cat',	null),
(7,	3,	'A Cute Kitten',	null)
;
''',

'''
insert into movie_reviews (id, movie, reviewer, review, distributor)
values
(1,	1,	'hates-action',	'The New Superheroes is super zero', 1),
(2,	6,	'loves-kitties',	'Startled Cat is the best movie ever', 3),
(3,	7,	'loves-kitties',	'Cute Kitten is even better!', 3)
;
'''
]

class Schema(unittest.TestCase):
    '''
    Tests for functions in the options module.
    '''
    def setUp(self):

        self.engine = create_engine('sqlite://')

        conn = self.engine.connect()
        cur = conn.connection.cursor()
        for query in queries:
            cur.execute(query)
        conn.connection.commit()
        conn.close()

    def checkEdgeExists(self, s, u, v):
        '''
        Helper function to check that an edge from table `u` to table
        `v` exists in the schema `s`. `u` and `v` should be table
        names.
        '''
        self.assertTrue(s.schema.has_edge(s.tables[u], s.tables[v]))

    def test_schema(self):
        '''
        Test schema creation
        '''
        src = {
            'engine': self.engine,
            'link': [
                (('movie_reviews', 'distributor'), ('distributors', 'id')),
            ],
            'unlink': [
            ],
        }
        source_schema = schema.Schema(src)

        self.checkEdgeExists(source_schema, 'movies', 'distributors')
        self.checkEdgeExists(source_schema, 'movie_reviews', 'movies')
        self.checkEdgeExists(source_schema, 'movie_reviews', 'distributors')

    def test_data(self):
        '''
        Test schema walking
        '''
        src = {
            'engine': self.engine,
            'link': [
            ],
            'unlink': [
            ],
        }
        source_schema = schema.Schema(src)

        expected = [
            {
                'table': 'distributors',
                'pk': {
                    'id': 3
                },
                'data': {
                    'id': 3,
                    'name': u'cat videos'
                }
            },
            {
                'table': 'movies',
                'pk': {
                    'id': 7
                },
                'data': {
                    'distributor': 3,
                    'code': None,
                    'id': 7,
                    'name': u'A Cute Kitten'
                }
            },
            {
                'table': 'movie_reviews',
                'pk': {
                    'id': 3
                },
                'data': {
                    'movie': 7,
                    'review': u'Cute Kitten is even better!',
                    'id': 3,
                    'reviewer': u'loves-kitties',
                    'distributor': 3
                }
            }
        ]

        filters = {'name': 'A Cute Kitten'}
        actual = [row for row in source_schema.data('movies', filters)]

        self.assertSequenceEqual(actual, expected)

# Run the tests if the file is called directly.
if __name__ == '__main__':
    unittest.main()
