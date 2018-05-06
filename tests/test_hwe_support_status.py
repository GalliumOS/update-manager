#!/usr/bin/python3


import apt
import builtins
import unittest
import os

from unittest import TestCase
from mock import (
    patch,
)

import hwe_support_status

builtins  # pyflakes


def make_mock_pkg(name, ver_str="1.0"):
    arch = apt.apt_pkg.config.find("APT::Architecture")
    return hwe_support_status.Package(name, ver_str, arch)


class HweSupportStatusTestCase(TestCase):

    INSTALLED_UNSUPPORTED_HWE_KERNEL_PKG_NAMES = (
        "linux-generic-lts-utopic",
        "linux-image-3.16.0-20-generic",
    )
    INSTALLED_UNSUPPORTED_HWE_XORG_PKG_NAMES = (
        "xserver-xorg-core-lts-utopic",
    )
    INSTALLED_SUPPORTED_HWE_PKG_NAMES = (
        "xserver-xorg-core-lts-trusty",
    )
    INSTALLED_OTHER_PKG_NAMES = (
        "2vcard",
    )

    INSTALLED_UNSUPPORTED_HWE_PKG_NAMES = (
        INSTALLED_UNSUPPORTED_HWE_KERNEL_PKG_NAMES +
        INSTALLED_UNSUPPORTED_HWE_XORG_PKG_NAMES)

    def setUp(self):
        self.cache = []
        INSTALL = (self.INSTALLED_UNSUPPORTED_HWE_PKG_NAMES +
                   self.INSTALLED_SUPPORTED_HWE_PKG_NAMES +
                   self.INSTALLED_OTHER_PKG_NAMES)
        for name in INSTALL:
            self.cache.append(make_mock_pkg(name))

    def test_find_unsupported_hwe_packages(self):
        unsupported, supported = hwe_support_status.find_hwe_packages(
            self.cache)
        self.assertEqual(
            set([pkg.name for pkg in unsupported]),
            set(self.INSTALLED_UNSUPPORTED_HWE_PKG_NAMES))

    def test_is_unsupported_hwe_kernel_running(self):
        running_kver = os.uname()[2]
        mock_installed_kernel_pkg = make_mock_pkg(
            self.INSTALLED_UNSUPPORTED_HWE_KERNEL_PKG_NAMES[0],
            ver_str=running_kver)
        unsupported = [mock_installed_kernel_pkg]
        self.assertTrue(
            hwe_support_status.is_unsupported_hwe_kernel_running(unsupported))

    def test_is_unsupported_hwe_xorg_running(self):
        mock_installed_xorg_pkg = make_mock_pkg(
            self.INSTALLED_UNSUPPORTED_HWE_XORG_PKG_NAMES[0])
        unsupported = [mock_installed_xorg_pkg]
        self.assertTrue(
            hwe_support_status.is_unsupported_xstack_running(unsupported))

    def test_advice_about_hwe_status_is_running(self):
        with patch("hwe_support_status.is_unsupported_hwe_running") as m:
            with patch("builtins.print") as mock_print:
                m.return_value = True
                mock_unsupported_hwe_pkgs = []
                mock_unsupported_hwe_pkgs.append(make_mock_pkg(
                    self.INSTALLED_UNSUPPORTED_HWE_XORG_PKG_NAMES[0]))
                from HweSupportStatus.consts import HWE_EOL_DATE
                from datetime import timedelta
                today = HWE_EOL_DATE - timedelta(14)
                hwe_support_status.advice_about_hwe_status(
                    mock_unsupported_hwe_pkgs, [], [], False, today,
                    verbose=True)
                text = mock_print.call_args[0][0]
                self.assertIn("Your current Hardware Enablement Stack (HWE) "
                              "is going out of support", text)

    def test_advice_about_hwe_status_installed_only(self):
        with patch("hwe_support_status.is_unsupported_hwe_running") as m:
            with patch("builtins.print") as mock_print:
                m.return_value = False
                mock_unsupported_hwe_pkgs = []
                mock_unsupported_hwe_pkgs.append(make_mock_pkg(
                    self.INSTALLED_UNSUPPORTED_HWE_XORG_PKG_NAMES[0]))
                from HweSupportStatus.consts import HWE_EOL_DATE
                from datetime import timedelta
                today = HWE_EOL_DATE + timedelta(14)
                hwe_support_status.advice_about_hwe_status(
                    mock_unsupported_hwe_pkgs, [], [], False, today,
                    verbose=True)
                text = mock_print.call_args[0][0]
                self.assertIn("You have packages from the Hardware "
                              "Enablement Stack (HWE) installed that",
                              text)

    def test_advice_about_hwe_status_no_hwe_stack(self):
        with patch("hwe_support_status.is_unsupported_hwe_running") as m:
            with patch("builtins.print") as mock_print:
                m.return_value = False
                mock_unsupported_hwe_pkgs = []
                from HweSupportStatus.consts import LTS_EOL_DATE
                from datetime import timedelta
                today = LTS_EOL_DATE - timedelta(14)
                hwe_support_status.advice_about_hwe_status(
                    mock_unsupported_hwe_pkgs, [], [], False, today,
                    verbose=True)
                text = mock_print.call_args[0][0]
                print("43242343243", mock_print.call_count)
                self.assertIn(
                    "Your system is supported until April 2019", text)

    def test_advice_about_hwe_status_supported_hwe_stack(self):
        with patch("hwe_support_status.is_unsupported_hwe_running") as m:
            with patch("builtins.print") as mock_print:
                m.return_value = False
                mock_supported_hwe_pkgs = []
                mock_supported_hwe_pkgs.append(make_mock_pkg(
                    self.INSTALLED_SUPPORTED_HWE_PKG_NAMES[0]))
                from HweSupportStatus.consts import LTS_EOL_DATE
                from datetime import timedelta
                today = LTS_EOL_DATE - timedelta(14)
                hwe_support_status.advice_about_hwe_status(
                    [], mock_supported_hwe_pkgs, [], False, today,
                    verbose=True)
                text = mock_print.call_args[0][0]
                self.assertIn(
                    "Your Hardware Enablement Stack (HWE) is supported "
                    "until April 2019", text)


if __name__ == "__main__":
    unittest.main()
