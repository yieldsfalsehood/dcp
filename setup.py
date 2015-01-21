#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


version = '0.1.0'

description = '''
The data copy tool.
'''
long_description = '''
Intelligently copy data between databases, using the schema.
'''

url = 'https://github.com/RishiRamraj/dcp'
download_url = 'https://github.com/RishiRamraj/dcp/archive/%s.tar.gz'

setup(
    name='dcp',
    version=version,
    description=description,
    long_description=long_description,
    license='MIT',
    author='Rishi Ramraj',
    author_email='thereisnocowlevel@gmail.com',
    url=url,
    download_url=download_url % version,
    packages=find_packages(),
    install_requires=[
        'setuptools',
    ],
    tests_require=[
        'mock',
        'nose',
    ],
    test_suite='nose.collector',
    entry_points={
        'console_scripts': [
            'dcp = dcp.main:main',
        ],
    },
)
