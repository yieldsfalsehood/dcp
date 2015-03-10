#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Testing tools.
import unittest
from mock import patch

# To be tested.
from dcp import options, utils


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
            '--log-level',
            'debug',
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
            'log_level': 'debug'
        }

        # Create the parser and parse.
        args = options.parser().parse_args(test)

        # Check the result.
        for key, value in expected.items():
            self.assertEqual(getattr(args, key), value)


class Utils(unittest.TestCase):
    '''
    Tests for functions in the utils module.
    '''
    @patch('dcp.utils.logging')
    def test_set_log_level(self, logging):
        '''
        A silly test for the set_log_level function for completion.
        '''
        # Create fake data.
        tests = {
            'critical': logging.CRITICAL,
            'error': logging.ERROR,
            'warning': logging.WARNING,
            'info': logging.INFO,
            'debug': logging.DEBUG,
        }

        # Check the result.
        for level, expected in tests.items():
            utils.set_log_level(level)
            logging.basicConfig.assert_called_with(level=expected)


# Run the tests if the file is called directly.
if __name__ == '__main__':
    unittest.main()
