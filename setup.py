#!/usr/bin/env python3
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-

import os
import glob

from distutils.core import setup
from subprocess import check_output

from DistUtilsExtra.command import (
    build_extra, build_i18n, build_help)


disabled = []


def plugins():
    return []
    return [os.path.join('janitor/plugincore/plugins', name)
            for name in os.listdir('janitor/plugincore/plugins')
            if name.endswith('_plugin.py') and name not in disabled]


for line in check_output('dpkg-parsechangelog --format rfc822'.split(),
                         universal_newlines=True).splitlines():
    header, colon, value = line.lower().partition(':')
    if header == 'version':
        version = value.strip()
        break
else:
    raise RuntimeError('No version found in debian/changelog')


class CustomBuild(build_extra.build_extra):
    def run(self):
        with open("UpdateManager/UpdateManagerVersion.py", "w") as f:
            f.write("VERSION = '%s'" % version)
        build_extra.build_extra.run(self)


setup(name='update-manager',
      version=version,
      packages=['UpdateManager',
                'UpdateManager.backend',
                'UpdateManager.Core',
                'UpdateManagerText',
                'janitor',
                'janitor.plugincore',
                ],
      scripts=['update-manager',
               'ubuntu-support-status',
               'update-manager-text',
               ],
      data_files=[('share/update-manager/gtkbuilder',
                   glob.glob("data/gtkbuilder/*.ui")
                   ),
                  ('share/man/man8',
                   glob.glob('data/*.8')
                   ),
                  ('share/GConf/gsettings/',
                   ['data/update-manager.convert']),
                  ],
      cmdclass={"build": CustomBuild,
                "build_i18n": build_i18n.build_i18n,
                "build_help": build_help.build_help}
      )
