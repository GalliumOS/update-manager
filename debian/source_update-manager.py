# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-

'''apport package hook for update-manager

(c) 2011 Canonical Ltd.
Author: Brian Murray <brian@ubuntu.com>
'''

import os
import re
from apport.hookutils import (
    attach_gsettings_package, attach_root_command_outputs,
    attach_file_if_exists, recent_syslog)


def add_info(report, ui):

    problem_type = report.get("ProblemType", None)
    if problem_type == "Bug":
        response = ui.yesno("Is the issue you are reporting one you \
encountered when upgrading Ubuntu from one release to another?")
    else:
        response = None
    if response:
        os.execlp('apport-bug', 'apport-bug', 'ubuntu-release-upgrader')
    else:
        attach_gsettings_package(report, 'update-manager')
        attach_file_if_exists(report, '/var/log/apt/history.log',
                              'DpkgHistoryLog.txt')
        attach_file_if_exists(report, '/var/log/apt/term.log',
                              'DpkgTerminalLog.txt')
        attach_root_command_outputs(
            report,
            {'CurrentDmesg.txt':
                'dmesg | comm -13 --nocheck-order /var/log/dmesg -'})
        report["Aptdaemon"] = recent_syslog(re.compile("AptDaemon"))
