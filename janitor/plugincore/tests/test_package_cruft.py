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
    'PackageCruftTests',
]

import unittest

from janitor.plugincore.core.package_cruft import PackageCruft
from janitor.plugincore.testing.helpers import MockAptPackage


class PackageCruftTests(unittest.TestCase):
    def setUp(self):
        self.pkg = MockAptPackage()
        self.cruft = PackageCruft(self.pkg, 'description')

    def test_prefix(self):
        self.assertEqual(self.cruft.get_prefix(), 'deb')
        self.assertEqual(self.cruft.prefix, 'deb')

    def test_prefix_description(self):
        self.assertEqual(self.cruft.get_prefix_description(), '.deb package')
        self.assertEqual(self.cruft.prefix_description, '.deb package')

    def test_shortname(self):
        self.assertEqual(self.cruft.get_shortname(), 'name')
        self.assertEqual(self.cruft.shortname, 'name')

    def test_name(self):
        self.assertEqual(self.cruft.get_name(), 'deb:name')
        self.assertEqual(self.cruft.name, 'deb:name')

    def test_description(self):
        self.assertEqual(self.cruft.get_description(),
                         'description\n\nsummary')
        self.assertEqual(self.cruft.description, 'description\n\nsummary')

    def test_disk_usage(self):
        self.assertEqual(self.cruft.get_disk_usage(), 12765)
        self.assertEqual(self.cruft.disk_usage, 12765)

    def test_cleanup(self):
        self.cruft.cleanup()
        self.assertTrue(self.pkg.deleted)
