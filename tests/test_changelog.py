#!/usr/bin/python3
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-

import apt
import logging
import os
import sys
import unittest
try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError

from UpdateManager.Core.MyCache import MyCache

CURDIR = os.path.dirname(os.path.abspath(__file__))


class TestChangelogs(unittest.TestCase):

    def setUp(self):
        # Whenever a test will initialize apt_pkg, we must set the architecture
        # to amd64, because our various test files assume that.  Even if this
        # test doesn't use those files, apt_pkg is only initialized once across
        # tests, so we must be consistent.
        real_arch = apt.apt_pkg.config.find("APT::Architecture")
        apt.apt_pkg.config.set("APT::Architecture", "amd64")
        self.addCleanup(
            lambda: apt.apt_pkg.config.set("APT::Architecture", real_arch))

        aptroot = os.path.join(CURDIR, "aptroot-changelog")

        self.cache = MyCache(apt.progress.base.OpProgress(), rootdir=aptroot)
        self.cache.open()

    def test_get_changelogs_uri(self):
        pkgname = "gcc"
        # test binary changelogs
        uri = self.cache._guess_third_party_changelogs_uri_by_binary(pkgname)
        pkg = self.cache[pkgname]
        self.assertEqual(uri,
                         pkg.candidate.uri.replace(".deb", ".changelog"))
        # test source changelogs
        uri = self.cache._guess_third_party_changelogs_uri_by_source(pkgname)
        self.assertTrue("gcc-defaults_" in uri)
        self.assertTrue(uri.endswith(".changelog"))
        # and one without a "Source" entry, we don't find something here
        uri = self.cache._guess_third_party_changelogs_uri_by_source("apt")
        self.assertEqual(uri, None)
        # one with srcver == binver
        pkgname = "libgtk2.0-dev"
        uri = self.cache._guess_third_party_changelogs_uri_by_source(pkgname)
        pkg = self.cache[pkgname]
        self.assertTrue(pkg.candidate.version in uri)
        self.assertTrue("gtk+2.0" in uri)

    def test_changelog_not_supported(self):
        def monkey_patched_get_changelogs(name, what, ver, uri):
            with open("/dev/zero") as zero:
                raise HTTPError(
                    "url", "code", "msg", "hdrs", zero)
        pkgname = "gcc"
        # patch origin
        real_origin = self.cache.CHANGELOG_ORIGIN
        self.cache.CHANGELOG_ORIGIN = "xxx"
        # monkey patch to raise the right error
        self.cache._get_changelog_or_news = monkey_patched_get_changelogs
        # get changelog
        self.cache.get_changelog(pkgname)
        error = "This update does not come from a source that "
        error += "supports changelogs."
        # verify that we don't have the lines twice
        self.assertEqual(self.cache.all_changes[pkgname].split("\n")[-1],
                         error)
        self.assertEqual(len(self.cache.all_changes[pkgname].split("\n")), 5)
        self.assertEqual(self.cache.all_changes[pkgname].count(error), 1)
        self.cache.CHANGELOG_ORIGIN = real_origin

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()
