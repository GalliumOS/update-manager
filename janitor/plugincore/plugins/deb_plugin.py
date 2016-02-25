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
    'DebPlugin',
]


import apt

from janitor.plugincore.plugin import Plugin


class DebPlugin(Plugin):
    """Plugin for post-cleanup processing with apt.

    This plugin does not find any cruft of its own.  Instead it centralizes
    the post-cleanup handling for all packages that remove .deb packages.
    """
    def get_cruft(self):
        return []

    def post_cleanup(self):
        try:
            self.app.apt_cache.commit(apt.progress.text.AcquireProgress(),
                                      apt.progress.base.InstallProgress())
        finally:
            self.app.refresh_apt_cache()
