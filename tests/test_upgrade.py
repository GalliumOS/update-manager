#!/usr/bin/python3
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-

import logging
import mock
import os
import sys
import unittest

from UpdateManager.Dialogs import DistUpgradeDialog

CURDIR = os.path.dirname(os.path.abspath(__file__))


class TestUpgrade(unittest.TestCase):
    """
    Tests that release upgrading works as expected.
    """

    def make_dialog_args(self):
        window_main = mock.MagicMock()
        window_main.datadir = os.path.join(CURDIR, '..', 'data')
        meta_release = mock.MagicMock()
        meta_release.flavor_name = "Ubuntu"
        meta_release.current_dist_version = "1"
        meta_release.upgradable_to.version = "2"
        return (window_main, meta_release)

    def test_pass_args(self):
        """
        Confirms that we pass update-manager args down to do-release-upgrade.
        """
        window_main, meta_release = self.make_dialog_args()
        window_main.options.devel_release = True
        window_main.options.use_proposed = True
        window_main.options.sandbox = True
        dlg = DistUpgradeDialog(window_main, meta_release)
        with mock.patch("os.execl") as execl:
            dlg.upgrade()
            execl.assert_called_once_with(
                "/bin/sh", "/bin/sh", "-c",
                "/usr/bin/pkexec /usr/bin/do-release-upgrade "
                "--frontend=DistUpgradeViewGtk3 -d -p -s")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()
