#!/usr/bin/python3
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-

import logging
import mock
import sys
import unittest
from gettext import gettext as _
from mock import patch

from UpdateManager.Dialogs import NoUpdatesDialog
from UpdateManager.UpdateManager import UpdateManager
from UpdateManager.backend import (InstallBackend, get_backend)
from UpdateManager.UpdatesAvailable import UpdatesAvailable

import os
CURDIR = os.path.dirname(os.path.abspath(__file__))


class TestUpdateManagerError(unittest.TestCase):

    def setUp(self):
        patcher = patch('UpdateManager.UpdateManager.UpdateManager')
        self.addCleanup(patcher.stop)
        self.manager = patcher.start()
        self.manager._check_meta_release.return_value = False
        self.manager.datadir = os.path.join(CURDIR, '..', 'data')

    def test_error_no_updates(self):
        p = UpdateManager._make_available_pane(self.manager, 0,
                                               error_occurred=True)
        self.assertIsInstance(p, NoUpdatesDialog)
        header_markup = "<span size='larger' weight='bold'>%s</span>"
        self.assertEqual(
            p.label_header.get_label(),
            header_markup % _("No software updates are available."))

    def test_error_with_updates(self):
        p = UpdateManager._make_available_pane(self.manager, 1,
                                               error_occurred=True)
        self.assertIsInstance(p, UpdatesAvailable)
        self.assertEqual(p.custom_desc,
                         _("Some software couldn’t be checked for updates."))


class TestBackendError(unittest.TestCase):

    def setUp(self):
        os.environ['UPDATE_MANAGER_FORCE_BACKEND_APTDAEMON'] = '1'

        def clear_environ():
            del os.environ['UPDATE_MANAGER_FORCE_BACKEND_APTDAEMON']

        self.addCleanup(clear_environ)

    @patch('UpdateManager.backend.InstallBackendAptdaemon.'
           'InstallBackendAptdaemon.update')
    def test_backend_error(self, update):
        main = mock.MagicMock()
        main.datadir = os.path.join(CURDIR, '..', 'data')

        update_backend = get_backend(main, InstallBackend.ACTION_UPDATE)
        update.side_effect = lambda: update_backend._action_done(
            InstallBackend.ACTION_UPDATE, True, False, "string", "desc")
        update_backend.start()
        main.start_error.assert_called_once_with(True, "string", "desc")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()
