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

from __future__ import absolute_import, print_function, unicode_literals

__metaclass__ = type
__all__ = [
    'MissingPackageCruft',
]


from janitor.plugincore.cruft import Cruft
from janitor.plugincore.i18n import setup_gettext
_ = setup_gettext()


class MissingPackageCruft(Cruft):
    """Install a missing package."""

    def __init__(self, package, description=None):
        self.package = package
        self._description = description

    def get_prefix(self):
        return 'install-deb'

    def get_prefix_description(self):
        return _('Install missing package.')

    def get_shortname(self):
        return self.package.name

    def get_description(self):
        if self._description:
            return self._description
        else:
            # 2012-06-08 BAW: i18n string; don't use {} or PEP 292.
            return _('Package %s should be installed.') % self.package.name

    def cleanup(self):
        self.package.markInstall()
