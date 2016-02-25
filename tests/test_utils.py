#!/usr/bin/python3
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-

import logging
import glob
import mock
import sys
import unittest

from UpdateManager.Core import utils


class TestUtils(unittest.TestCase):

    def test_humanize_size(self):
        # humanize size is a bit funny, it rounds up to kB as the meaningful
        # unit for users
        self.assertEqual(utils.humanize_size(1000), "1 kB")
        self.assertEqual(utils.humanize_size(10), "1 kB")
        self.assertEqual(utils.humanize_size(1200), "2 kB")
        # but not for MB as well
        self.assertEqual(utils.humanize_size(1200 * 1000), "1.2 MB")
        self.assertEqual(utils.humanize_size(1478 * 1000), "1.5 MB")
        # and we don't go to Gb  just yet (as its not really needed
        # in a upgrade context most of the time
        self.assertEqual(utils.humanize_size(1000 * 1000 * 1000), "1000.0 MB")

    @unittest.skipIf(not glob.glob("/boot/*"), "inside chroot")
    def test_estimate_kernel_size(self):
        estimate = utils.estimate_kernel_size_in_boot()
        self.assertTrue(estimate > 0)

    def test_is_child_of_process_name(self):
        self.assertTrue(utils.is_child_of_process_name("init") or
                        utils.is_child_of_process_name("systemd"))
        self.assertFalse(utils.is_child_of_process_name("mvo"))
        for e in glob.glob("/proc/[0-9]*"):
            pid = int(e[6:])
            utils.is_child_of_process_name("gdm", pid)

    def test_is_port_listening(self):
        from UpdateManager.Core.utils import is_port_already_listening
        self.assertTrue(is_port_already_listening(22))

    def test_strip_auth_from_source_entry(self):
        from aptsources.sourceslist import SourceEntry
        # entry with PW
        s = SourceEntry("deb http://user:pass@some-ppa/ ubuntu main")
        self.assertTrue(
            "user" not in utils.get_string_with_no_auth_from_source_entry(s))
        self.assertTrue(
            "pass" not in utils.get_string_with_no_auth_from_source_entry(s))
        self.assertEqual(utils.get_string_with_no_auth_from_source_entry(s),
                         "deb http://hidden-u:hidden-p@some-ppa/ ubuntu main")
        # no pw
        s = SourceEntry("deb http://some-ppa/ ubuntu main")
        self.assertEqual(utils.get_string_with_no_auth_from_source_entry(s),
                         "deb http://some-ppa/ ubuntu main")

    @mock.patch('UpdateManager.Core.utils._load_meta_pkg_list')
    def test_flavor_package_ubuntu_first(self, mock_load):
        cache = {'ubuntu-desktop': mock.MagicMock(),
                 'other-desktop': mock.MagicMock()}
        cache['ubuntu-desktop'].is_installed = True
        cache['other-desktop'].is_installed = True
        mock_load.return_value = ['other-desktop']
        self.assertEqual(utils.get_ubuntu_flavor_package(cache=cache),
                         'ubuntu-desktop')

    @mock.patch('UpdateManager.Core.utils._load_meta_pkg_list')
    def test_flavor_package_match(self, mock_load):
        cache = {'a': mock.MagicMock(),
                 'b': mock.MagicMock(),
                 'c': mock.MagicMock()}
        cache['a'].is_installed = True
        cache['b'].is_installed = True
        cache['c'].is_installed = True
        mock_load.return_value = ['c', 'a', 'b']
        # Must pick alphabetically first
        self.assertEqual(utils.get_ubuntu_flavor_package(cache=cache), 'a')

    def test_flavor_package_default(self):
        self.assertEqual(utils.get_ubuntu_flavor_package(cache={}),
                         'ubuntu-desktop')

    def test_flavor_default(self):
        self.assertEqual(utils.get_ubuntu_flavor(cache={}), 'ubuntu')

    @mock.patch('UpdateManager.Core.utils.get_ubuntu_flavor_package')
    def test_flavor_simple(self, mock_package):
        mock_package.return_value = 'd'
        self.assertEqual(utils.get_ubuntu_flavor(), 'd')

    @mock.patch('UpdateManager.Core.utils.get_ubuntu_flavor_package')
    def test_flavor_chop(self, mock_package):
        mock_package.return_value = 'd-pkg'
        self.assertEqual(utils.get_ubuntu_flavor(), 'd')

    @mock.patch('UpdateManager.Core.utils.get_ubuntu_flavor_package')
    def test_flavor_name_desktop(self, mock_package):
        mock_package.return_value = 'something-desktop'
        self.assertEqual(utils.get_ubuntu_flavor_name(), 'Something')

    @mock.patch('UpdateManager.Core.utils.get_ubuntu_flavor_package')
    def test_flavor_name_netbook(self, mock_package):
        mock_package.return_value = 'something-netbook'
        self.assertEqual(utils.get_ubuntu_flavor_name(), 'Something')

    @mock.patch('UpdateManager.Core.utils.get_ubuntu_flavor_package')
    def test_flavor_name_studio(self, mock_package):
        mock_package.return_value = 'ubuntustudio-desktop'
        self.assertEqual(utils.get_ubuntu_flavor_name(), 'Ubuntu Studio')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()
