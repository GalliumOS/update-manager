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
    'PackageCruft',
]


from janitor.plugincore.cruft import Cruft
from janitor.plugincore.i18n import setup_gettext
_ = setup_gettext()


class PackageCruft(Cruft):
    """Cruft that is .deb packages.

    This type of cruft consists of .deb packages installed onto the system
    which can be removed.  Various plugins may decide that various packages
    are cruft; they can all use objects of PackageCruft type to mark such
    packages, regardless of the reason the packages are considered cruft.

    When PackageCruft instantiated, the package is identified by an
    apt.Package object.  That object is used for all the real operations, so
    this class is merely a thin wrapper around it.
    """

    def __init__(self, pkg, description):
        self._pkg = pkg
        self._description = description

    def get_prefix(self):
        return 'deb'

    def get_prefix_description(self):
        return _('.deb package')

    def get_shortname(self):
        return self._pkg.name

    def get_description(self):
        return '{}\n\n{}'.format(self._description, self._pkg.summary)

    def get_disk_usage(self):
        return self._pkg.installedSize

    def cleanup(self):
        self._pkg.markDelete()
