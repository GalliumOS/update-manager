#!/usr/bin/python3
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-

import unittest

import apt_pkg
import logging
import os
import sys

from UpdateManager.Core.utils import init_proxy


class TestInitProxy(unittest.TestCase):
    proxy = "http://10.0.2.2:3128"

    def setUp(self):
        try:
            del os.environ["http_proxy"]
        except KeyError:
            pass
        apt_pkg.config.set("Acquire::http::proxy", self.proxy)

    def tearDown(self):
        try:
            del os.environ["http_proxy"]
        except KeyError:
            pass
        apt_pkg.config.clear("Acquire::http::proxy")

    def testinitproxy(self):
        from gi.repository import Gio
        settings = Gio.Settings.new("com.ubuntu.update-manager")
        detected_proxy = init_proxy(settings)
        self.assertEqual(detected_proxy, self.proxy)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()
