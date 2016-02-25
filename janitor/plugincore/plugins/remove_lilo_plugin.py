# Copyright (C) 2009  Canonical, Ltd.
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

"""Remove lilo if grub is also installed."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'RemoveLiloPlugin',
]


import os
import logging

from janitor.plugincore.i18n import setup_gettext
from janitor.plugincore.core.package_cruft import PackageCruft
from janitor.plugincore.plugin import Plugin

_ = setup_gettext()


class RemoveLiloPlugin(Plugin):
    """Plugin to remove lilo if grub is also installed."""

    def __init__(self):
        self.condition = ['jauntyPostDistUpgradeCache']

    def get_description(self):
        return _('Remove lilo since grub is also installed.'
                 '(See bug #314004 for details.)')

    def get_cruft(self):
        if 'lilo' in self.app.apt_cache and 'grub' in self.app.apt_cache:
            lilo = self.app.apt_cache['lilo']
            grub = self.app.apt_cache['grub']
            if lilo.is_installed and grub.is_installed:
                if not os.path.exists('/etc/lilo.conf'):
                    yield PackageCruft(lilo, self.description)
                else:
                    logging.warning('lilo and grub installed, but '
                                    'lilo.conf exists')
