# Copyright (C) 2009-2012  Canonical, Ltd.
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
    'AutoRemovalPluginTests',
]


import os
import tempfile
import unittest

from janitor.plugincore.plugins.dpkg_status_plugin import DpkgStatusPlugin


class AutoRemovalPluginTests(unittest.TestCase):
    def setUp(self):
        fd, self.filename = tempfile.mkstemp()
        self.addCleanup(lambda: os.remove(self.filename))
        try:
            os.write(fd, b'Status: purge ok not-installed\n')
        finally:
            os.close(fd)
        self.plugin = DpkgStatusPlugin(self.filename)

    def test_dpkg_status(self):
        names = [cruft.get_name() for cruft in self.plugin.get_cruft()]
        self.assertEqual(
            sorted(names),
            ['dpkg-status:Obsolete entries in dpkg status']
        )
