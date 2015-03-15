#!/usr/bin/python
# -*- coding: utf-8 -*-

from dcp.utils import IdentityError


class NoDatabase(Exception):
    '''
    Raised when a database isn't configured.
    '''
    def __init__(self, src, name, path):
        message = 'Database %s not found in %s.'
        super(Exception, self).__init__(message % (name, path))


class BadConfig(IdentityError):
    '''
    Raised when a database configuration is bad.
    '''
    pass


class InvalidTargets(Exception):
    '''
    Raised when the source and destination databases are the same.
    '''
    pass
