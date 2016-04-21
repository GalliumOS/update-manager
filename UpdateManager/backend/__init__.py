#!/usr/bin/env python
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-

"""Integration of package managers into UpdateManager"""
# (c) 2005-2009 Canonical, GPL

from __future__ import absolute_import

from gi.repository import GLib

import os

from UpdateManager.Core.utils import inhibit_sleep
from UpdateManager.Dialogs import Dialog


class InstallBackend(Dialog):
    ACTION_UPDATE = 0
    ACTION_INSTALL = 1

    def __init__(self, window_main, action):
        Dialog.__init__(self, window_main)
        self.action = action
        self.sleep_cookie = None

    def start(self):
        os.environ["APT_LISTCHANGES_FRONTEND"] = "none"

        # Do not suspend during the update process
        self.sleep_cookie = inhibit_sleep()

        if self.action == self.ACTION_INSTALL:
            # Get the packages which should be installed and update
            pkgs_install = []
            pkgs_upgrade = []
            for pkg in self.window_main.cache:
                if pkg.marked_install:
                    pkgname = pkg.name
                    if pkg.is_auto_installed:
                        pkgname += "#auto"
                    pkgs_install.append(pkgname)
                elif pkg.marked_upgrade:
                    pkgs_upgrade.append(pkg.name)
            self.commit(pkgs_install, pkgs_upgrade)
        else:
            self.update()

    def update(self):
        """Run a update to refresh the package list"""
        raise NotImplemented

    def commit(self, pkgs_install, pkgs_upgrade):
        """Commit the cache changes """
        raise NotImplemented

    def _action_done(self, action, authorized, success, error_string,
                     error_desc):

        # If the progress dialog should be closed automatically afterwards
        #settings = Gio.Settings.new("com.ubuntu.update-manager")
        #close_after_install = settings.get_boolean(
        #    "autoclose-install-window")
        # FIXME: confirm with mpt whether this should still be a setting
        #close_after_install = False

        if action == self.ACTION_INSTALL:
            if success:
                self.window_main.start_available()
            elif error_string:
                self.window_main.start_error(False, error_string, error_desc)
            else:
                # exit gracefuly, we can't just exit as this will trigger
                # a crash if system.exit() is called in a exception handler
                GLib.timeout_add(1, self.window_main.exit)
        else:
            if error_string:
                self.window_main.start_error(True, error_string, error_desc)
            else:
                is_cancelled_update = not success
                self.window_main.start_available(is_cancelled_update)


def get_backend(*args, **kwargs):
    """Select and return a package manager backend."""
    # try aptdaemon
    if (os.path.exists("/usr/sbin/aptd") and
            "UPDATE_MANAGER_FORCE_BACKEND_SYNAPTIC" not in os.environ):
        # check if the gtkwidgets are installed as well
        try:
            from .InstallBackendAptdaemon import InstallBackendAptdaemon
            return InstallBackendAptdaemon(*args, **kwargs)
        except ImportError:
            import logging
            logging.exception("importing aptdaemon")
    # try synaptic
    if (os.path.exists("/usr/sbin/synaptic") and
            "UPDATE_MANAGER_FORCE_BACKEND_APTDAEMON" not in os.environ):
        from .InstallBackendSynaptic import InstallBackendSynaptic
        return InstallBackendSynaptic(*args, **kwargs)
    # nothing found, raise
    raise Exception("No working backend found, please try installing "
                    "synaptic or aptdaemon")
