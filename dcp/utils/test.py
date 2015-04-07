#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Testing tools.
import unittest
from mock import patch, call, MagicMock
from dcp.utils.exceptions import NoDatabase, BadConfig, InvalidTargets

# To be tested.
from dcp.utils import options, misc, exceptions, config


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


class Misc(unittest.TestCase):
    '''
    Tests for functions in the misc module.
    '''
    @patch('dcp.utils.misc.logging')
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
            misc.set_log_level(level)
            logging.basicConfig.assert_called_with(level=expected)

    def test_iter(self):
        '''
        Converts a number of values to iterables.
        '''
        # Create tests.
        tests = (
            ('test', ('test', )),
            ([1, 2, 3], [1, 2, 3]),
            (1, (1, )),
        )

        # Check the result.
        for test, expected in tests:
            self.assertEqual(misc.iter(test), expected)

    def test_trap(self):
        '''
        Trap an exception.
        '''
        # Create fake data.
        trigger = MagicMock()

        # Perform the test.
        with misc.trap(trigger, ValueError, KeyError):
            raise ValueError('test')

        # Check the result.
        self.assertTrue(trigger.called)

    def test_trap_miss(self):
        '''
        Trap an exception.
        '''
        # Create fake data.
        trigger = MagicMock()

        # Perform the test.
        with self.assertRaisesRegexp(KeyError, 'test'):
            with misc.trap(trigger, ValueError):
                raise KeyError('test')

        # Check the result.
        self.assertFalse(trigger.called)

    def test_reraise(self):
        '''
        Raise an exception, make sure it is suppressed and an alternative
        exception is raised.
        '''
        # Create a test class.
        class Test(misc.IdentityError):
            pass

        # Perform the test.
        with self.assertRaisesRegexp(Test, 'test'):
            with misc.reraise(ValueError, Test):
                raise ValueError('test')

    @patch('dcp.utils.misc.logging')
    @patch('dcp.utils.misc.sys')
    def test_catch(self, sys, logging):
        '''
        Catch an exception and log it.
        '''
        # Create test data.
        exception = ValueError('test')

        # Perform the test.
        with misc.catch(ValueError):
            raise exception

        # Check the result.
        logging.error.assert_called_once_with('test')
        sys.exit.assert_called_once_with(1)

    def test_suppress(self):
        '''
        Suppress an exception.
        '''
        # Perform the test.
        with misc.suppress(ValueError, KeyError):
            raise ValueError('test')


class Exceptions(unittest.TestCase):
    '''
    Tests for functions in the exceptions module. These tests are mostly
    for exception constructors used with the reraise utility.
    '''
    def test_no_database(self):
        '''
        Convert a ValueError into a NoDatabase exception.
        '''
        # Create test data.
        target = exceptions.NoDatabase
        name = 'name'
        path = 'path'

        # Perform the test.
        with self.assertRaisesRegexp(target, 'not found'):
            with misc.reraise(ValueError, target, name, path):
                raise ValueError('test')

    def test_bad_config(self):
        '''
        Test a bad configuration.
        '''
        # Create test data.
        target = exceptions.BadConfig

        # Perform the test.
        with self.assertRaisesRegexp(target, 'test'):
            with misc.reraise(ValueError, target):
                raise ValueError('test')


class Config(unittest.TestCase):
    '''
    Tests for functions in the config module.
    '''
    def test_format(self):
        '''
        Format a well formed configuration.
        '''
        # Create test data.
        value = '''
            table1:column1 = table2:column2
            table1:column1 = table3:column2
        '''

        # Perform the test.
        result = config.format(value)

        # Check the result.
        expected = (
            (('table1', 'column1'), ('table2', 'column2')),
            (('table1', 'column1'), ('table3', 'column2')),
        )
        self.assertEqual(result, expected)

    @patch('dcp.utils.config.warning')
    def test_bad_format(self, warning):
        '''
        Format a misformed configuration.
        '''
        # Create test data.
        value = '''
            table1:column1 table2:column2
            table1:column1 = table3column2
            table1:column1 = table3:column2
        '''

        # Perform the test.
        result = config.format(value)

        # Make sure the warnings were logged.
        message = 'Ignoring invalid configuration: %s'
        expected = [
            call(message, 'table1:column1 table2:column2'),
            call(message, 'table1:column1 = table3column2')
        ]
        warning.assert_has_calls(expected)

        # Check the result.
        expected = ((('table1', 'column1'), ('table3', 'column2')),)
        self.assertEqual(result, expected)

    def test_database(self):
        '''
        Parses a well formed database configuration.
        '''
        # Create test data.
        name = 'test'
        _config = {
            'test': {
                'dsn': 'dsn',
                'link': 'table1:column1 = table2:column2',
                'unlink': 'table1:column1 = table3:column2',
            },
        }

        # Perform the test.
        result = config.database(name, _config)

        # Check the result.
        expected = {
            'dsn': 'dsn',
            'link': ((('table1', 'column1'), ('table2', 'column2')),),
            'unlink': ((('table1', 'column1'), ('table3', 'column2')),),
        }
        self.assertEqual(result, expected)

    def test_no_database(self):
        '''
        The config lacks the target database.
        '''
        # Create test data.
        name = 'test'
        _config = {}

        # Perform the test.
        with self.assertRaises(NoDatabase):
            config.database(name, _config)

    def test_bad_config(self):
        '''
        The database configuration is invalid.
        '''
        # Create test data.
        name = 'test'
        _config = {'test': {}, }

        # Perform the test.
        with self.assertRaises(BadConfig):
            config.database(name, _config)

    def test_optional_config(self):
        '''
        The link and unlink properties are optional.
        '''
        # Create test data.
        _config = {
            'link': {
                'dsn': 'dsn',
                'link': 'table1:column1 = table2:column2',
            },
            'unlink': {
                'dsn': 'dsn',
                'unlink': 'table1:column1 = table2:column2',
            },
        }

        # Perform the test. No exceptions should be raised.
        for name in ('link', 'unlink'):
            config.database(name, _config)

    @patch('dcp.utils.config.database')
    @patch('dcp.utils.config.configparser')
    def test_parse(self, configparser, database):
        '''
        A mocky test for parse for completion.
        '''
        # Create test data.
        src = 'src'
        dest = 'dest'
        _config = MagicMock()
        configparser.ConfigParser.return_value = _config
        database.return_value = 'test'

        # Perform the test.
        left, right = config.parse(src, dest)

        # Check the result.
        self.assertEqual(left, 'test')
        self.assertEqual(right, 'test')

        # Check the database calls.
        expected = [
            call('src', _config),
            call('dest', _config),
        ]
        database.assert_has_calls(expected)

    def test_parse_same_targets(self):
        '''
        The source and destination targets are the same.
        '''
        # Create test data.
        src = 'test'
        dest = 'test'

        # Perform the test.
        expected = 'are the same'
        with self.assertRaisesRegexp(InvalidTargets, expected):
            config.parse(src, dest)


# Run the tests if the file is called directly.
if __name__ == '__main__':
    unittest.main()
