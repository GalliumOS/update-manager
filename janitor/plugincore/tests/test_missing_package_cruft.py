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


from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'MissingPackageCruftTests',
]


import unittest

from janitor.plugincore.core.missing_package_cruft import MissingPackageCruft
from janitor.plugincore.testing.helpers import MockAptPackage


class MissingPackageCruftTests(unittest.TestCase):
    def setUp(self):
        self.pkg = MockAptPackage()
        self.cruft = MissingPackageCruft(self.pkg)

    def test_prefix(self):
        self.assertEqual(self.cruft.get_prefix(), 'install-deb')
        self.assertEqual(self.cruft.prefix, 'install-deb')

    def test_prefix_description(self):
        self.assertTrue('Install' in self.cruft.get_prefix_description())
        self.assertTrue('Install' in self.cruft.prefix_description)

    def test_shortname(self):
        self.assertEqual(self.cruft.get_shortname(), 'name')
        self.assertEqual(self.cruft.shortname, 'name')

    def test_name(self):
        self.assertEqual(self.cruft.get_name(), 'install-deb:name')
        self.assertEqual(self.cruft.name, 'install-deb:name')

    def test_description(self):
        self.assertTrue('name' in self.cruft.get_description())
        self.assertTrue('name' in self.cruft.description)

    def test_explicit_description(self):
        pkg = MissingPackageCruft(self.pkg, 'foo')
        self.assertEqual(pkg.get_description(), 'foo')
        self.assertEqual(pkg.description, 'foo')

    def test_cleanup(self):
        self.cruft.cleanup()
        self.assertTrue(self.pkg.installed)
