#!/usr/bin/python3
# -*- Mode: Python; indent-tabs-mode: nil; tab-width: 4; coding: utf-8 -*-

# Partly based on a script from Review Board, MIT license; but modified to
# act as a unit test.

from __future__ import print_function

import os
import re
import subprocess
import unittest

CURDIR = os.path.dirname(os.path.abspath(__file__))


class TestPyflakesClean(unittest.TestCase):
    """ ensure that the tree is pyflakes clean """

    def read_exclusions(self):
        exclusions = {}
        try:
            excpath = os.path.join(CURDIR, "pyflakes.exclude")
            with open(excpath, "r") as fp:
                for line in fp:
                    if not line.startswith("#"):
                        exclusions[line.rstrip()] = 1
        except IOError:
            pass
        return exclusions

    def filter_exclusions(self, contents):
        exclusions = self.read_exclusions()
        for line in contents:
            if line.startswith("#"):
                continue

            line = line.rstrip().split(CURDIR + '/', 1)[1]
            test_line = re.sub(r":[0-9]+:", r":*:", line, 1)
            test_line = re.sub(r"line [0-9]+", r"line *", test_line)

            if test_line not in exclusions:
                yield line

    def test_pyflakes_clean(self):
        # mvo: type -f here to avoid running pyflakes on imported files
        #      that are symlinks to other packages
        cmd = 'find %s/.. -type f -name "*.py" | xargs pyflakes3' % CURDIR
        p = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            close_fds=True, shell=True, universal_newlines=True)
        contents = p.communicate()[0].splitlines()
        filtered_contents = list(self.filter_exclusions(contents))
        for line in filtered_contents:
            print(line)
        self.assertEqual(0, len(filtered_contents))


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
