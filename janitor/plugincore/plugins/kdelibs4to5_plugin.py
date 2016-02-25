# Copyright (C) 2009-2012  Canonical, Ltd.
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

"""Install kdelibs5-dev if kdeblibs4-dev is installed."""

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'Kdelibs4devToKdelibs5devPlugin',
]


from janitor.plugincore.core.missing_package_cruft import MissingPackageCruft
from janitor.plugincore.i18n import setup_gettext
from janitor.plugincore.plugin import Plugin

_ = setup_gettext()


class Kdelibs4devToKdelibs5devPlugin(Plugin):
    """Plugin to install kdelibs5-dev if kdelibs4-dev is installed.

    See also LP: #279621.
    """

    def __init__(self):
        self.condition = ['from_hardyPostDistUpgradeCache']

    def get_cruft(self):
        fromp = 'kdelibs4-dev'
        top = 'kdelibs5-dev'
        cache = self.app.apt_cache
        if (fromp in cache and cache[fromp].is_installed and
                top in cache and not cache[top].is_installed):
            yield MissingPackageCruft(
                cache[top],
                _('When upgrading, if kdelibs4-dev is installed, '
                  'kdelibs5-dev needs to be installed. See '
                  'bugs.launchpad.net, bug #279621 for details.'))
