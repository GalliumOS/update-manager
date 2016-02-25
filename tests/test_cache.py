#!/usr/bin/python3
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-

import apt
import logging
import os
import sys
import unittest

import mock

from UpdateManager.Core.MyCache import MyCache

CURDIR = os.path.dirname(os.path.abspath(__file__))


class TestCache(unittest.TestCase):

    def setUp(self):
        # Whenever a test will initialize apt_pkg, we must set the architecture
        # to amd64, because our various test files assume that.  Even if this
        # test doesn't use those files, apt_pkg is only initialized once across
        # tests, so we must be consistent.
        real_arch = apt.apt_pkg.config.find("APT::Architecture")
        apt.apt_pkg.config.set("APT::Architecture", "amd64")
        self.addCleanup(
            lambda: apt.apt_pkg.config.set("APT::Architecture", real_arch))

        # We don't need anything special, but since we modify architecture
        # above, we ought to point to an aptroot that matches the arch
        self.aptroot = os.path.join(CURDIR, "aptroot-cache-test")

        self.cache = MyCache(None, rootdir=self.aptroot)
        self.cache.open()

    def test_https_and_creds_in_changelog_uri(self):
        # credentials in https locations are not supported as they can
        # be man-in-the-middled because of the lack of cert checking in
        # urllib2
        pkgname = "package-one"
        uri = "https://user:pass$word@ubuntu.com/foo/bar"
        mock_binary = mock.Mock()
        mock_binary.return_value = uri
        self.cache._guess_third_party_changelogs_uri_by_binary = mock_binary
        mock_source = mock.Mock()
        mock_source.return_value = uri
        self.cache._guess_third_party_changelogs_uri_by_source = mock_source
        self.cache.all_changes[pkgname] = "header\n"
        self.cache._fetch_changelog_for_third_party_package(pkgname)
        self.assertEqual(
            self.cache.all_changes[pkgname],
            "header\n"
            "This update does not come from a source that supports "
            "changelogs.")

    def test_conflicts_replaces_removal(self):
        # An incomplete set of Conflicts/Replaces does not allow removal.
        with mock.patch("logging.info") as mock_info:
            self.assertEqual(1, self.cache.saveDistUpgrade())
            mock_info.assert_called_once_with(
                "package-two Conflicts/Replaces package-one; allowing removal")
        self.assertEqual([], [pkg for pkg in self.cache if pkg.marked_delete])

        # Specifying Conflicts/Replaces allows packages to be removed.
        apt.apt_pkg.config.set(
            "Dir::State::Status",
            self.aptroot + "/var/lib/dpkg/status-minus-three")
        apt.apt_pkg.init_system()
        self.cache.open()
        self.cache._initDepCache()
        with mock.patch("logging.info") as mock_info:
            self.assertEqual(0, self.cache.saveDistUpgrade())
            mock_info.assert_called_once_with(
                "package-two Conflicts/Replaces package-one; allowing removal")
        self.assertEqual(
            [self.cache["package-one"]],
            [pkg for pkg in self.cache if pkg.marked_delete])

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()
