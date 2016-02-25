#  Copyright (c) 2008 Canonical Ltd
#
#  Author: Jonathan Riddell <jriddell@ubuntu.com>
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation; either version 2 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

#  Checks for new releases, run by Adept

from __future__ import absolute_import, print_function

from .Core.MetaRelease import MetaReleaseCore
import time

metaRelease = MetaReleaseCore(False, False)
while metaRelease.downloading:
    time.sleep(1)
print("no_longer_supported:" + str(metaRelease.no_longer_supported))
if metaRelease.new_dist is None:
    print("new_dist_available:None")
else:
    print("new_dist_available:" + str(metaRelease.new_dist.version))
