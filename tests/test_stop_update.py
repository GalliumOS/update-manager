#!/usr/bin/python3
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-

import logging
import sys
import unittest
from mock import patch
from gettext import gettext as _

from UpdateManager.UpdateManager import UpdateManager
from UpdateManager.UpdatesAvailable import UpdatesAvailable
from UpdateManager import Dialogs

import os
CURDIR = os.path.dirname(os.path.abspath(__file__))


class TestStopUpdate(unittest.TestCase):

    def setUp(self):
        patcher = patch('UpdateManager.UpdateManager.UpdateManager')
        self.addCleanup(patcher.stop)
        self.manager = patcher.start()
        self.manager._check_meta_release.return_value = False
        self.manager.datadir = os.path.join(CURDIR, '..', 'data')

    def test_stop_no_updates(self):
        p = UpdateManager._make_available_pane(self.manager, 0,
                                               cancelled_update=True)
        self.assertIsInstance(p, Dialogs.StoppedUpdatesDialog)

    def test_no_stop_no_updates(self):
        p = UpdateManager._make_available_pane(self.manager, 0,
                                               cancelled_update=False)
        self.assertNotIsInstance(p, Dialogs.StoppedUpdatesDialog)

    def test_stop_updates(self):
        p = UpdateManager._make_available_pane(self.manager, 1,
                                               cancelled_update=True)
        self.assertIsInstance(p, UpdatesAvailable)
        self.assertEqual(p.custom_header,
                         _("You stopped the check for updates."))

    def test_no_stop_updates(self):
        p = UpdateManager._make_available_pane(self.manager, 1,
                                               cancelled_update=False)
        self.assertIsInstance(p, UpdatesAvailable)
        self.assertIsNone(p.custom_header)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()
