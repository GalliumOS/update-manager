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
    'Application',
    'MockAptPackage',
    'setup_plugins',
]


import os
import shutil
import tempfile
import pkg_resources


def setup_plugins(*plugin_filenames):
    plugin_dir = tempfile.mkdtemp()
    for filename in plugin_filenames:
        src = pkg_resources.resource_filename(
            'janitor.plugincore.tests.data', filename)
        dst = os.path.join(plugin_dir, filename)
        shutil.copyfile(src, dst)
    return (plugin_dir, lambda: shutil.rmtree(plugin_dir))


class Application:
    def __init__(self):
        self.notifications = []
        self.commit_called = False
        self.refresh_called = False
        self.apt_cache = self

    def commit(self, foo, bar):
        self.commit_called = True

    def refresh_apt_cache(self):
        self.refresh_called = True


class MockAptPackage:
    def __init__(self):
        self.name = 'name'
        self.summary = 'summary'
        self.installedSize = 12765
        self.installed = False
        self.deleted = False

    def markInstall(self):
        self.installed = True

    def markDelete(self):
        self.deleted = True
