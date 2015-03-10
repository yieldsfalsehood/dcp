#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Testing tools.
import unittest

# To be tested.
from dcp import options


class Options(unittest.TestCase):
    '''
    Tests for functions in the options module.
    '''
    def test_parse(self):
        '''
        A test for the parse function.
        '''
        # Create fake data.
        test = [
            'source',
            'destination',
            'table',
            'column1=value1',
            'column2=value2',
            'column3=value3',
        ]
        expected = {
            'source': 'source',
            'destination': 'destination',
            'table': 'table',
            'columns': [
                'column1=value1',
                'column2=value2',
                'column3=value3',
            ],
        }

        # Create the parser and parse.
        args = options.parser().parse_args(test)

        # Check the result.
        for key, value in expected.items():
            self.assertEqual(getattr(args, key), value)


# Run the tests if the file is called directly.
if __name__ == '__main__':
    unittest.main()
