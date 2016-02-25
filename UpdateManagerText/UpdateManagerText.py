#!/usr/bin/python3
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-

from __future__ import print_function

import apt
import apt_pkg
import operator
import sys
import threading
import time
from gettext import gettext as _

from UpdateManager.Core.UpdateList import UpdateList
from UpdateManager.Core.MyCache import MyCache

from snack import (SnackScreen,
                   ButtonBar,
                   Textbox,
                   CheckboxTree,
                   GridForm,
                   snackArgs,
                   )


class UpdateManagerText(object):
    DEBUG = False

    def __init__(self, datadir):
        self.screen = SnackScreen()
        # FIXME: self.screen.finish() clears the screen (and all messages)
        #        there too
        #atexit.register(self.restoreScreen)
        self.button_bar = ButtonBar(self.screen,
                                    ((_("Cancel"), "cancel"),
                                     (_("Install"), "ok")),
                                    compact=True)
        self.textview_changes = Textbox(72, 8, _("Changelog"), True, True)
        self.checkbox_tree_updates = CheckboxTree(height=8, width=72, scroll=1)
        self.checkbox_tree_updates.setCallback(self.checkbox_changed)
        self.layout = GridForm(self.screen, _("Updates"), 1, 5)
        self.layout.add(self.checkbox_tree_updates, 0, 0)
        # empty line to make it look less crowded
        self.layout.add(Textbox(60, 1, " ", False, False), 0, 1)
        self.layout.add(self.textview_changes, 0, 2)
        # empty line to make it look less crowded
        self.layout.add(Textbox(60, 1, " ", False, False), 0, 3)
        self.layout.add(self.button_bar, 0, 4)
        # FIXME: better progress than the current suspend/resume screen thing
        self.screen.suspend()
        if not self.DEBUG:
            apt_pkg.pkgsystem_lock()
        self.openCache()
        print(_("Building Updates List"))
        self.fillstore()
        if self.list.distUpgradeWouldDelete > 0:
            print(_("""
A normal upgrade can not be calculated, please run:
  sudo apt-get dist-upgrade


This can be caused by:
 * A previous upgrade which didn't complete
 * Problems with some of the installed software
 * Unofficial software packages not provided by Ubuntu
 * Normal changes of a pre-release version of Ubuntu"""))
            sys.exit(1)
        self.screen.resume()

#    def restoreScreen(self):
#        self.screen.finish()

    def openCache(self):
        # open cache
        progress = apt.progress.text.OpProgress()
        if hasattr(self, "cache"):
            self.cache.open(progress)
            self.cache._initDepCache()
        else:
            self.cache = MyCache(progress)
            self.actiongroup = apt_pkg.ActionGroup(self.cache._depcache)
        # lock the cache
        self.cache.lock = True

    def fillstore(self):
        # populate the list
        self.list = UpdateList(self)
        self.list.update(self.cache)
        origin_list = sorted(
            self.list.pkgs, key=operator.attrgetter("importance"),
            reverse=True)
        for (i, origin) in enumerate(origin_list):
            self.checkbox_tree_updates.append(origin.description,
                                              selected=True)
            for pkg in self.list.pkgs[origin]:
                self.checkbox_tree_updates.addItem(pkg.name,
                                                   (i, snackArgs['append']),
                                                   pkg,
                                                   selected=True)

    def updateSelectionStates(self):
        """
        helper that goes over the cache and updates the selection
        states in the UI based on the cache
        """
        for pkg in self.cache:
            if pkg not in self.checkbox_tree_updates.item2key:
                continue
            # update based on the status
            if pkg.marked_upgrade or pkg.marked_install:
                self.checkbox_tree_updates.setEntryValue(pkg, True)
            else:
                self.checkbox_tree_updates.setEntryValue(pkg, False)
        self.updateUI()

    def updateUI(self):
        self.layout.draw()
        self.screen.refresh()

    def get_news_and_changelog(self, pkg):
        changes = ""
        name = pkg.name

        # if we don't have it, get it
        if (name not in self.cache.all_changes and
                name not in self.cache.all_news):
            self.textview_changes.setText(_("Downloading changelog"))
            lock = threading.Lock()
            lock.acquire()
            changelog_thread = threading.Thread(
                target=self.cache.get_news_and_changelog, args=(name, lock))
            changelog_thread.start()
            # this lock should never take more than 2s even with network down
            while lock.locked():
                time.sleep(0.03)

        # build changes from NEWS and changelog
        if name in self.cache.all_news:
            changes += self.cache.all_news[name]
        if name in self.cache.all_changes:
            changes += self.cache.all_changes[name]

        return changes

    def checkbox_changed(self):
        # item is either a apt.package.Package or a str (for the headers)
        pkg = self.checkbox_tree_updates.getCurrent()
        descr = ""
        if hasattr(pkg, "name"):
            need_refresh = False
            name = pkg.name
            if self.options.show_description:
                descr = getattr(pkg.candidate, "description", None)
            else:
                descr = self.get_news_and_changelog(pkg)
            # check if it is a wanted package
            selected = self.checkbox_tree_updates.getEntryValue(pkg)[1]
            marked_install_upgrade = pkg.marked_install or pkg.marked_upgrade
            if not selected and marked_install_upgrade:
                need_refresh = True
                pkg.mark_keep()
            if selected and not marked_install_upgrade:
                if not (name in self.list.held_back):
                    # FIXME: properly deal with "fromUser" here
                    need_refresh = True
                    pkg.mark_install()
            # fixup any problems
            if self.cache._depcache.broken_count:
                need_refresh = True
                Fix = apt_pkg.ProblemResolver(self.cache._depcache)
                Fix.resolve_by_keep()
            # update the list UI to reflect the cache state
            if need_refresh:
                self.updateSelectionStates()
        self.textview_changes.setText(descr)
        self.updateUI()

    def main(self, options):
        self.options = options
        res = self.layout.runOnce()
        self.screen.finish()
        button = self.button_bar.buttonPressed(res)
        if button == "ok":
            self.screen.suspend()
            res = self.cache.commit(apt.progress.text.AcquireProgress(),
                                    apt.progress.base.InstallProgress())

if __name__ == "__main__":

    umt = UpdateManagerText()
    umt.main()
