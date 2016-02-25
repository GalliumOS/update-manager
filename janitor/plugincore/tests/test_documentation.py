# Copyright (C) 2008-2012  Canonical, Ltd.
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.


"""Test harness for doctests."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'additional_tests',
]

import os
import atexit
import doctest
import unittest

from pkg_resources import (
    resource_filename, resource_exists, resource_listdir, cleanup_resources)

COMMASPACE = ', '
DOT = '.'
DOCTEST_FLAGS = (
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE |
    doctest.REPORT_NDIFF |
    doctest.IGNORE_EXCEPTION_DETAIL)


WHOAMI = 'janitor.plugincore'


def stop():
    """Call into pdb.set_trace()"""
    # Do the import here so that you get the wacky special hacked pdb instead
    # of Python's normal pdb.
    import pdb
    pdb.set_trace()


def setup(testobj):
    """Test setup."""
    # Make sure future statements in our doctests match the Python code.
    try:
        testobj.globs['absolute_import'] = absolute_import
        testobj.globs['print_function'] = print_function
        testobj.globs['unicode_literals'] = unicode_literals
    except NameError:
        pass
    testobj.globs['stop'] = stop
    testobj.globs['cleanups'] = []


def teardown(testobj):
    for cleanup in testobj.globs['cleanups']:
        cleanup()


def additional_tests():
    "Run the doc tests (README.rst and docs/*, if any exist)"
    doctest_files = [
        ## os.path.abspath(resource_filename(WHOAMI, 'README.rst')),
    ]
    if resource_exists(WHOAMI, 'docs'):
        for name in resource_listdir(WHOAMI, 'docs'):
            if name.endswith('.rst'):
                doctest_files.append(
                    os.path.abspath(
                        resource_filename(WHOAMI, 'docs/%s' % name)))
    kwargs = dict(module_relative=False,
                  optionflags=DOCTEST_FLAGS,
                  setUp=setup, tearDown=teardown,
                  )
    atexit.register(cleanup_resources)
    return unittest.TestSuite((
        doctest.DocFileSuite(*doctest_files, **kwargs)))
