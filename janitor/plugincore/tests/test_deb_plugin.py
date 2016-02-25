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
    'DebPluginTests',
]


import unittest

from janitor.plugincore.plugins.deb_plugin import DebPlugin
from janitor.plugincore.testing.helpers import Application


class DebPluginTests(unittest.TestCase):
    def setUp(self):
        self.plugin = DebPlugin()
        self.app = Application()
        self.plugin.set_application(self.app)

    def test_no_cruft(self):
        self.assertEqual(self.plugin.get_cruft(), [])

    def test_post_cleanup_calls_commit(self):
        self.plugin.post_cleanup()
        self.assertTrue(self.app.commit_called)

    def test_post_cleanup_calls_refresh(self):
        self.plugin.post_cleanup()
        self.assertTrue(self.app.refresh_called)
