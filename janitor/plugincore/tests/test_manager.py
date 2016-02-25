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
    'ManagerTests',
]

import os
import sys
import unittest

from janitor.plugincore.manager import PluginManager
from janitor.plugincore.plugin import Plugin
from janitor.plugincore.testing.helpers import setup_plugins, Application


class ManagerTests(unittest.TestCase):
    """Test of the plugin manager."""

    def setUp(self):
        self._app = Application()
        self._sys_path = sys.path[:]

    def tearDown(self):
        # The tests which actually load plugins pollutes sys.path, so save and
        # restore it around tests.
        sys.path = self._sys_path

    def test_missing_plugindir_is_ignored(self):
        plugin_dir, cleanup = setup_plugins()
        self.addCleanup(cleanup)
        missing_dir = os.path.join(plugin_dir, 'does', 'not', 'exist')
        manager = PluginManager(self._app, [missing_dir])
        # Even though the manager is pointing to a missing plugins dir,
        # getting all the plugin files will not crash, it will just return an
        # empty sequence.
        self.assertEqual(list(manager.plugin_files), [])

    def test_finds_no_plugins_in_empty_directory(self):
        plugin_dir, cleanup = setup_plugins()
        self.addCleanup(cleanup)
        manager = PluginManager(self._app, [plugin_dir])
        self.assertEqual(len(manager.get_plugins()), 0)

    def test_finds_one_plugin_file(self):
        plugin_dir, cleanup = setup_plugins('alpha_plugin.py')
        self.addCleanup(cleanup)
        manager = PluginManager(self._app, [plugin_dir])
        self.assertEqual(list(manager.plugin_files),
                         [os.path.join(plugin_dir, 'alpha_plugin.py')])

    def test_finds_one_plugin(self):
        plugin_dir, cleanup = setup_plugins('alpha_plugin.py')
        self.addCleanup(cleanup)
        manager = PluginManager(self._app, [plugin_dir])
        plugins = list(manager.get_plugins())
        self.assertEqual(len(plugins), 1)
        self.assertTrue(isinstance(plugins[0], Plugin))

    def test_plugin_loading_sets_application(self):
        plugin_dir, cleanup = setup_plugins('alpha_plugin.py')
        self.addCleanup(cleanup)
        manager = PluginManager(self._app, [plugin_dir])
        plugins = list(manager.get_plugins())
        self.assertEqual(plugins[0].app, self._app)

    def test_plugin_loading_callback(self):
        callback_calls = []

        def callback(filename, i, total):
            callback_calls.append((os.path.basename(filename), i, total))

        plugin_dir, cleanup = setup_plugins('alpha_plugin.py')
        manager = PluginManager(self._app, [plugin_dir])
        manager.get_plugins(callback=callback)
        self.assertEqual(callback_calls, [('alpha_plugin.py', 0, 1)])

    def test_plugin_loading_callback_with_multiple_plugins(self):
        callback_calls = []

        def callback(filename, i, total):
            callback_calls.append((os.path.basename(filename), i, total))

        plugin_dir, cleanup = setup_plugins(
            'alpha_plugin.py', 'bravo_plugin.py')
        manager = PluginManager(self._app, [plugin_dir])
        manager.get_plugins(callback=callback)
        self.assertEqual(callback_calls, [
            ('alpha_plugin.py', 0, 2),
            ('bravo_plugin.py', 1, 2),
        ])

    def test_condition_equality(self):
        # The first part of the conditions test looks for exactly equality
        # between the condition argument and the plugin's condition
        # attribute.
        plugin_dir, cleanup = setup_plugins(
            'alpha_plugin.py', 'bravo_plugin.py')
        manager = PluginManager(self._app, [plugin_dir])
        # Start by getting all the plugins.
        all_plugins = manager.get_plugins()
        # Set some conditions on the plugins.
        all_plugins[0].condition = 'alpha'
        all_plugins[1].condition = 'bravo'
        self.assertEqual(manager.get_plugins(condition='zero'), [])
        self.assertEqual(manager.get_plugins(condition='alpha'),
                         [all_plugins[0]])
        self.assertEqual(manager.get_plugins(condition='bravo'),
                         [all_plugins[1]])

    def test_condition_in(self):
        # The second part of the conditions test checks for the given
        # condition being in the sequence of conditions in the plugin.  This
        # is kind of crappy because let's say a plugin's condition is
        # 'happy_days' and you pass in condition='happy', you'll get a match.
        # Oh well, it's been this way forever.
        plugin_dir, cleanup = setup_plugins(
            'alpha_plugin.py', 'bravo_plugin.py')
        manager = PluginManager(self._app, [plugin_dir])
        # Start by getting all the plugins.
        all_plugins = manager.get_plugins()
        # Set some conditions on the plugins.
        all_plugins[0].condition = ['alpha', 'happy']
        all_plugins[1].condition = ['bravo', 'happy', 'sad']
        self.assertEqual(manager.get_plugins(condition='zero'), [])
        self.assertEqual(manager.get_plugins(condition='alpha'),
                         [all_plugins[0]])
        self.assertEqual(manager.get_plugins(condition='bravo'),
                         [all_plugins[1]])
        self.assertEqual(manager.get_plugins(condition='happy'), all_plugins)
        self.assertEqual(manager.get_plugins(condition='sad'),
                         [all_plugins[1]])

    def test_condition_wildcard(self):
        # The third conditions test matches everything.
        plugin_dir, cleanup = setup_plugins(
            'alpha_plugin.py', 'bravo_plugin.py', 'charlie_plugin.py')
        manager = PluginManager(self._app, [plugin_dir])
        # Start by getting all the plugins.
        all_plugins = manager.get_plugins()
        self.assertEqual(len(all_plugins), 3)
        # Set some conditions on the plugins.
        all_plugins[0].condition = ['alpha', 'happy']
        all_plugins[1].condition = ['bravo', 'happy', 'sad']
        # Do not give the third plugin an explicit condition.
        self.assertEqual(manager.get_plugins(condition='*'), all_plugins)

    def test_condition_default_matches_conditionless(self):
        # By default, only conditionless plugins match the manager default.
        plugin_dir, cleanup = setup_plugins(
            'alpha_plugin.py', 'bravo_plugin.py', 'charlie_plugin.py')
        manager = PluginManager(self._app, [plugin_dir])
        # Start by getting all the plugins.
        all_plugins = manager.get_plugins()
        self.assertEqual(len(all_plugins), 3)
        # Set some conditions on the plugins.
        all_plugins[0].condition = ['alpha', 'happy']
        all_plugins[1].condition = ['bravo', 'happy', 'sad']
        # Do not give the third plugin an explicit condition.
        self.assertEqual(manager.get_plugins(), [all_plugins[2]])
