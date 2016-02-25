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
    'DpkgStatusCruft',
    'DpkgStatusPlugin',
]


import logging
import subprocess

from apt_pkg import TagFile

from janitor.plugincore.cruft import Cruft
from janitor.plugincore.i18n import setup_gettext
from janitor.plugincore.plugin import Plugin

_ = setup_gettext()


class DpkgStatusCruft(Cruft):
    def __init__(self, n_items):
        self.n_items = n_items

    def get_prefix(self):
        return 'dpkg-status'

    def get_prefix_description(self):
        return _('%i obsolete entries in the status file') % self.n_items

    def get_shortname(self):
        return _('Obsolete entries in dpkg status')

    def get_description(self):  # pragma: no cover
        return _('Obsolete dpkg status entries')

    def cleanup(self):
        logging.debug('calling dpkg --forget-old-unavail')
        res = subprocess.call('dpkg --forget-old-unavail'.split())
        logging.debug('dpkg --forget-old-unavail returned {}'.format(res))


class DpkgStatusPlugin(Plugin):
    def __init__(self, filename=None):
        self.status = ('/var/lib/dpkg/status'
                       if filename is None
                       else filename)
        self.condition = ['PostCleanup']

    def get_cruft(self):
        n_cruft = 0
        with open(self.status) as fp:
            tagf = TagFile(fp)
            while tagf.step():
                statusline = tagf.section.get('Status')
                (want, flag, status) = statusline.split()
                if (want == 'purge' and
                        flag == 'ok' and
                        status == 'not-installed'):
                    # Then...
                    n_cruft += 1
        logging.debug('DpkgStatusPlugin found {} cruft items'.format(n_cruft))
        if n_cruft:
            return [DpkgStatusCruft(n_cruft)]
        return []
