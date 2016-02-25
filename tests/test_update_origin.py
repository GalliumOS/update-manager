#!/usr/bin/python3
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-

import os

import apt
import shutil
import unittest
from UpdateManager.Core.UpdateList import UpdateList
from UpdateManager.Core.MyCache import MyCache

CURDIR = os.path.dirname(os.path.abspath(__file__))


class TestOriginMatcher(unittest.TestCase):

    def setUp(self):
        self.aptroot = os.path.join(CURDIR,
                                    "aptroot-update-origin")
        self.dpkg_status = open("%s/var/lib/dpkg/status" % self.aptroot, "w")
        self.dpkg_status.flush()
        self.cache = MyCache(apt.progress.base.OpProgress(),
                             rootdir=self.aptroot)
        self.cache._listsLock = 0
        self.cache.update()
        self.cache.open()

    def tearDown(self):
        # kill data dirs
        # FIXME: use tmpdir in the long run
        for d in ["var/lib/apt/lists/",
                  "var/cache/apt"]:
            try:
                shutil.rmtree(os.path.join(self.aptroot, d))
            except IOError:
                pass
        # kill off status file
        try:
            os.remove(os.path.join(self.aptroot, "var/lib/dpkg/status"))
        except OSError:
            pass

    def testOriginMatcherSimple(self):
        test_pkgs = set()
        for pkg in self.cache:
            if pkg.candidate and pkg.candidate.origins:
                if [l.archive for l in pkg.candidate.origins
                        if l.archive == "lucid-security"]:
                    test_pkgs.add(pkg.name)
        self.assertTrue(len(test_pkgs) > 0)
        ul = UpdateList(None, dist="lucid")
        for pkgname in test_pkgs:
            pkg = self.cache[pkgname]
            self.assertTrue(ul._is_security_update(pkg),
                            "pkg '%s' is not in lucid-security" % pkg.name)

    def testOriginMatcherWithVersionInUpdatesAndSecurity(self):
        # empty dpkg status
        self.cache.open(apt.progress.base.OpProgress())

        # find test packages set
        test_pkgs = set()
        for pkg in self.cache:
            # only test on native arch
            if ":" in pkg.name:
                continue
            # check if the candidate origin is -updates (but not also
            # -security, often packages are available in both)
            if pkg.candidate is not None:
                # ensure that the origin is not -updates and -security
                is_in_updates = False
                is_in_security = False
                for v in pkg.candidate.origins:
                    # test if the package is not in both updates and security
                    if v.archive == "lucid-updates":
                        is_in_updates = True
                    elif v.archive == "lucid-security":
                        is_in_security = True
                if (is_in_updates and
                        not is_in_security and
                        len(pkg._pkg.version_list) > 2):
                    test_pkgs.add(pkg.name)
        self.assertTrue(len(test_pkgs) > 0,
                        "no suitable test package found that has a version in "
                        "both -security and -updates and where -updates is "
                        "newer")

        # now test if versions in -security are detected
        ul = UpdateList(None, dist="lucid")
        for pkgname in test_pkgs:
            pkg = self.cache[pkgname]
            self.assertTrue(ul._is_security_update(pkg),
                            "package '%s' from lucid-updates contains also a "
                            "(not yet installed) security updates, but it is "
                            "not labeled as such" % pkg.name)

        # now check if it marks the version with -update if the -security
        # version is installed
        for pkgname in test_pkgs:
            pkg = self.cache[pkgname]
            # FIXME: make this more inteligent (picking the versin from
            #        -security
            sec_ver = pkg._pkg.version_list[1]
            self.dpkg_status.write("Package: %s\n"
                                   "Status: install ok installed\n"
                                   "Installed-Size: 1\n"
                                   "Version: %s\n"
                                   "Architecture: all\n"
                                   "Description: foo\n\n"
                                   % (pkg.name, sec_ver.ver_str))
            self.dpkg_status.flush()
        self.cache.open()
        for pkgname in test_pkgs:
            pkg = self.cache[pkgname]
            self.assertIsNotNone(pkg._pkg.current_ver,
                                 "no package '%s' installed" % pkg.name)
            candidate_version = getattr(pkg.candidate, "version", None)
            self.assertFalse(ul._is_security_update(pkg),
                             "package '%s' (%s) from lucid-updates is "
                             "labelled as a security update even though we "
                             "have marked this version as installed already" %
                             (pkg.name, candidate_version))


if __name__ == "__main__":
    unittest.main()
