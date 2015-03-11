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
        Parse known command line parameters.
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
        Set the log level and ensure the right log level was set.
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

    def test_reraise(self):
        '''
        Raise an exception, make sure it is suppressed and an alternative
        exception is raised.
        '''
        # Create a test class.
        class Test(utils.Identity):
            pass

        # Perform the test.
        with self.assertRaisesRegexp(Test, 'test'):
            with utils.reraise(ValueError, Test):
                raise ValueError('test')

    def test_reraise_miss(self):
        '''
        Raise an exception not related to the reraise trap.
        '''
        # Create a test class.
        class Test(utils.Identity):
            pass

        # Perform the test.
        with self.assertRaisesRegexp(KeyError, 'test'):
            with utils.reraise(ValueError, Test):
                raise KeyError('test')

    @patch('dcp.utils.logging')
    @patch('dcp.utils.sys')
    def test_catch(self, sys, logging):
        '''
        Catch an exception and log it.
        '''
        # Create test data.
        exception = ValueError('test')

        # Perform the test.
        with utils.catch((ValueError, )):
            raise exception

        # Check the result.
        logging.exception.assert_called_once_with(exception)
        sys.exit.assert_called_once_with(1)

    @patch('dcp.utils.logging')
    @patch('dcp.utils.sys')
    def test_catch_miss(self, sys, logging):
        '''
        Pass an exception that isn't in the catch trap.
        '''
        # Perform the test.
        with self.assertRaisesRegexp(KeyError, 'test'):
            with utils.catch((ValueError, )):
                raise KeyError('test')

        # Check the result.
        self.assertFalse(logging.exception.called)
        self.assertFalse(sys.exit.called)


# Run the tests if the file is called directly.
if __name__ == '__main__':
    unittest.main()
