# Copyright (C) 2008-2012  Canonical, Ltd.
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'FileCruftTests',
]

import os
import errno
import tempfile
import unittest
import subprocess

from janitor.plugincore.core.file_cruft import FileCruft


class FileCruftTests(unittest.TestCase):
    def setUp(self):
        fd, self.pathname = tempfile.mkstemp()

        def cleanup():
            try:
                os.remove(self.pathname)
            except OSError as error:
                if error.errno != errno.ENOENT:
                    raise

        self.addCleanup(cleanup)
        try:
            os.write(fd, b'x' * 1024)
        finally:
            os.close(fd)
        self.cruft = FileCruft(self.pathname, 'description')

    def test_refix(self):
        self.assertEqual(self.cruft.get_prefix(), 'file')
        self.assertEqual(self.cruft.prefix, 'file')

    def test_prefix_description(self):
        self.assertEqual(self.cruft.get_prefix_description(), 'A file on disk')
        self.assertEqual(self.cruft.prefix_description, 'A file on disk')

    def test_shortname(self):
        self.assertEqual(self.cruft.get_shortname(), self.pathname)
        self.assertEqual(self.cruft.shortname, self.pathname)

    def test_name(self):
        expected = 'file:{}'.format(self.pathname)
        self.assertEqual(self.cruft.get_name(), expected)
        self.assertEqual(self.cruft.name, expected)

    def test_description(self):
        self.assertEqual(self.cruft.get_description(), 'description\n')
        self.assertEqual(self.cruft.description, 'description\n')

    def test_disk_usage(self):
        stdout = subprocess.check_output(
            ('du -s -B 1 {}'.format(self.pathname)).split(),
            # Decode output as UTF-8 and convert line endings to \n
            universal_newlines=True)
        du = int(stdout.splitlines()[0].split('\t')[0])
        self.assertEqual(self.cruft.get_disk_usage(), du)
        self.assertEqual(self.cruft.disk_usage, du)

    def test_cleanup(self):
        self.assertTrue(os.path.exists(self.pathname))
        self.cruft.cleanup()
        self.assertFalse(os.path.exists(self.pathname))
