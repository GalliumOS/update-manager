#!/usr/bin/python3
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-

import os

import apt
import unittest

from UpdateManager.Core import UpdateList
from UpdateManager.Core.MyCache import MyCache

from gi.repository import Gio
from mock import patch, PropertyMock, MagicMock

CURDIR = os.path.dirname(os.path.abspath(__file__))


class PhasedTestCase(unittest.TestCase):

    def setUp(self):
        # mangle the arch
        real_arch = apt.apt_pkg.config.find("APT::Architecture")
        apt.apt_pkg.config.set("APT::Architecture", "amd64")
        self.addCleanup(
            lambda: apt.apt_pkg.config.set("APT::Architecture", real_arch))

        self.aptroot = os.path.join(CURDIR,
                                    "aptroot-update-list-test")
        self.cache = MyCache(apt.progress.base.OpProgress(),
                             rootdir=self.aptroot)
        self.cache.open()
        self.updates_list = UpdateList.UpdateList(parent=None)

    def assertUpdatesListLen(self, nr):
        self.assertEqual(self.updates_list.num_updates, nr)

    def test_phased_percentage_not_included(self):
        """ Test that updates above the threshold are not included"""
        with patch.object(self.updates_list.random, "randint") as mock_randint:
            # threshold is 10
            mock_randint.return_value = 11
            self.updates_list.update(self.cache)
            self.assertUpdatesListLen(1)

    def test_phased_percentage_included(self):
        """ Test that updates below the threshold are included"""
        with patch.object(self.updates_list.random, "randint") as mock_randint:
            # threshold is 10
            mock_randint.return_value = 9
            self.updates_list.update(self.cache)
            self.assertUpdatesListLen(3)

    def test_second_phased_binary_not_included(self):
        """ Test that there is no overlap between the source packages of the
            packages being ignored and installed """
        with patch.object(self.updates_list.random, "randint") as mock_randint:
            mock_randint.return_value = 11
            self.updates_list.update(self.cache)
        ignored_srcs = set([pkg.candidate.source_name for pkg in
                            self.updates_list.ignored_phased_updates])
        group = self.updates_list.update_groups[0]
        install_srcs = set([x.pkg.candidate.source_name for x in group.items])
        self.assertEqual(ignored_srcs, set({'zsh'}))
        self.assertEqual(install_srcs, set({'apt'}))
        self.assertTrue(len(ignored_srcs & install_srcs) == 0)

    def test_phased_percentage_included_via_force(self):
        """ Test that the "always" override config works """
        # set config to force override
        apt.apt_pkg.config.set(
            self.updates_list.ALWAYS_INCLUDE_PHASED_UPDATES, "1")
        self.addCleanup(lambda: apt.apt_pkg.config.set(
            self.updates_list.ALWAYS_INCLUDE_PHASED_UPDATES, "0"))
        # ensure it's included even if it's above the threshold
        with patch.object(self.updates_list.random, "randint") as mock_randint:
            mock_randint.return_value = 100
            self.updates_list.update(self.cache)
            self.assertUpdatesListLen(3)

    def test_phased_percentage_excluded_via_force(self):
        """ Test that the "never" override config works """
        # set config to force override
        apt.apt_pkg.config.set(
            self.updates_list.NEVER_INCLUDE_PHASED_UPDATES, "1")
        self.addCleanup(lambda: apt.apt_pkg.config.set(
            self.updates_list.NEVER_INCLUDE_PHASED_UPDATES, "0"))
        # ensure it's excluded even if it's below the threshold
        with patch.object(self.updates_list.random, "randint") as mock_randint:
            mock_randint.return_value = 0
            self.updates_list.update(self.cache)
            self.assertUpdatesListLen(1)

    @patch('UpdateManager.Core.UpdateList.UpdateList._is_security_update')
    def test_phased_percentage_from_security(self, mock_security):
        """ Test that updates from the security node go in"""
        # pretend all updates come from security for the sake of this test
        mock_security.return_value = True
        with patch.object(self.updates_list.random, "randint") as mock_randint:
            mock_randint.return_value = 100
            self.updates_list.update(self.cache)
            self.assertUpdatesListLen(3)


class GroupingTestCase(unittest.TestCase):
    # installed_files does not respect aptroot, so we have to patch it
    @patch('apt.package.Package.installed_files', new_callable=PropertyMock)
    @patch('gi.repository.Gio.DesktopAppInfo.new_from_filename')
    def setUp(self, mock_desktop, mock_installed):
        # mangle the arch
        real_arch = apt.apt_pkg.config.find("APT::Architecture")
        apt.apt_pkg.config.set("APT::Architecture", "amd64")
        self.addCleanup(
            lambda: apt.apt_pkg.config.set("APT::Architecture", real_arch))
        self.aptroot = os.path.join(CURDIR,
                                    "aptroot-grouping-test")
        self.cache = MyCache(apt.progress.base.OpProgress(),
                             rootdir=self.aptroot)
        self.cache.open()
        mock_installed.__get__ = self.fake_installed_files
        mock_desktop.side_effect = self.fake_desktop
        self.updates_list = UpdateList.UpdateList(parent=None, dist='lucid')
        self.updates_list.update(self.cache)

    def fake_installed_files(self, mock_prop, pkg, pkg_class):
        if pkg.name == 'installed-app':
            return ['/usr/share/applications/installed-app.desktop']
        elif pkg.name == 'installed-app-with-subitems':
            return ['/usr/share/applications/installed-app2.desktop']
        else:
            return []

    def fake_desktop(self, path):
        # These can all be the same for our purposes
        app = MagicMock()
        app.get_filename.return_value = path
        app.get_display_name.return_value = 'App ' + os.path.basename(path)
        app.get_icon.return_value = Gio.ThemedIcon.new("package")
        return app

    def test_app(self):
        self.assertGreater(len(self.updates_list.update_groups), 0)
        group = self.updates_list.update_groups[0]
        self.assertIsInstance(group, UpdateList.UpdateApplicationGroup)
        self.assertIsNotNone(group.core_item)
        self.assertEqual(group.core_item.pkg.name, 'installed-app')
        self.assertListEqual([x.pkg.name for x in group.items],
                             ['installed-app'])

    def test_app_with_subitems(self):
        self.assertGreater(len(self.updates_list.update_groups), 1)
        group = self.updates_list.update_groups[1]
        self.assertIsInstance(group, UpdateList.UpdateApplicationGroup)
        self.assertIsNotNone(group.core_item)
        self.assertEqual(group.core_item.pkg.name,
                         'installed-app-with-subitems')
        self.assertListEqual([x.pkg.name for x in group.items],
                             ['installed-app-with-subitems',
                              'installed-pkg-single-dep'])

    def test_pkg(self):
        self.assertGreater(len(self.updates_list.update_groups), 2)
        group = self.updates_list.update_groups[2]
        self.assertIsInstance(group, UpdateList.UpdatePackageGroup)
        self.assertIsNotNone(group.core_item)
        self.assertEqual(group.core_item.pkg.name, 'installed-pkg')
        self.assertListEqual([x.pkg.name for x in group.items],
                             ['installed-pkg'])

    def test_pkg_multiple_deps(self):
        self.assertEqual(len(self.updates_list.update_groups), 4)
        group = self.updates_list.update_groups[3]
        self.assertIsInstance(group, UpdateList.UpdatePackageGroup)
        self.assertIsNotNone(group.core_item)
        self.assertEqual(group.core_item.pkg.name,
                         'installed-pkg-multiple-deps')
        self.assertListEqual([x.pkg.name for x in group.items],
                             ['installed-pkg-multiple-deps'])

    def test_security(self):
        self.assertEqual(len(self.updates_list.security_groups), 1)
        group = self.updates_list.security_groups[0]
        self.assertIsInstance(group, UpdateList.UpdateSystemGroup)
        self.assertIsNone(group.core_item)
        self.assertListEqual([x.pkg.name for x in group.items], ['base-pkg'])

if __name__ == "__main__":
    unittest.main()
