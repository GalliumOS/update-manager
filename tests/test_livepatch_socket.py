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
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
#  USA

import datetime
from gi.repository import GLib
import http.client
from mock import Mock
import logging
import sys
import unittest
import yaml

from UpdateManager.Core.LivePatchSocket import LivePatchSocket, LivePatchFix


status0 = {'architecture': 'x86_64',
           'boot-time': datetime.datetime(2017, 6, 27, 11, 16),
           'client-version': '7.21',
           'cpu-model': 'Intel(R) Core(TM) i7-6700HQ CPU @ 2.60GHz',
           'last-check': datetime.datetime(2017, 6, 28, 14, 23, 29, 683361),
           'machine-id': 123456789,
           'machine-token': 987654321,
           'uptime': '27h12m12s'}

status1 = {'architecture': 'x86_64',
           'boot-time': datetime.datetime(2017, 6, 27, 11, 16),
           'client-version': '7.21',
           'cpu-model': 'Intel(R) Core(TM) i7-6700HQ CPU @ 2.60GHz',
           'last-check': datetime.datetime(2017, 6, 28, 14, 23, 29, 683361),
           'machine-id': 123456789,
           'machine-token': 987654321,
           'status': [{'kernel': '4.4.0-78.99-generic',
                       'livepatch': {'checkState': 'needs-check',
                                     'fixes': '',
                                     'patchState': 'nothing-to-apply',
                                     'version': '24.2'},
                       'running': True}],
           'uptime': '27h12m12s'}

status2 = {'architecture': 'x86_64',
           'boot-time': datetime.datetime(2017, 6, 27, 11, 16),
           'client-version': '7.21',
           'cpu-model': 'Intel(R) Core(TM) i7-6700HQ CPU @ 2.60GHz',
           'last-check': datetime.datetime(2017, 6, 28, 14, 23, 29, 683361),
           'machine-id': 123456789,
           'machine-token': 987654321,
           'status': [{'kernel': '4.4.0-78.99-generic',
                       'livepatch': {'checkState': 'checked',
                                     'fixes': '* CVE-2016-0001\n'
                                     '* CVE-2016-0002\n'
                                     '* CVE-2017-0001 (unpatched)\n'
                                     '* CVE-2017-0001',
                                     'patchState': 'applied',
                                     'version': '24.2'},
                       'running': True}],
           'uptime': '27h12m12s'}


class TestUtils(object):

    @staticmethod
    def __TimeoutCallback(user_data=None):
        user_data[0] = True
        return False

    @staticmethod
    def __ScheduleTimeout(timeout_reached, timeout_duration=10):
        return GLib.timeout_add(timeout_duration,
                                TestUtils.__TimeoutCallback,
                                timeout_reached)

    @staticmethod
    def WaitUntilMSec(instance, check_function, expected_result=True,
                      max_wait=500, error_msg=''):
        instance.assertIsNotNone(check_function)

        timeout_reached = [False]
        timeout_id = TestUtils.__ScheduleTimeout(timeout_reached, max_wait)

        result = None
        while not timeout_reached[0]:
            result = check_function()
            if result == expected_result:
                break
            GLib.MainContext.default().iteration(True)

        if result == expected_result:
            GLib.Source.remove(timeout_id)

        instance.assertEqual(expected_result, result, error_msg)


class MockResponse():

    def __init__(self, status, data):
        self.status = status
        self.data = data

    def read(self):
        return yaml.dump(self.data)


class TestLivePatchSocket(unittest.TestCase):

    def test_get_check_state(self):
        check_state = LivePatchSocket.get_check_state(status0)
        self.assertEqual(check_state, 'check-failed')
        check_state = LivePatchSocket.get_check_state(status1)
        self.assertEqual(check_state, 'needs-check')
        check_state = LivePatchSocket.get_check_state(status2)
        self.assertEqual(check_state, 'checked')

    def test_get_patch_state(self):
        patch_state = LivePatchSocket.get_patch_state(status0)
        self.assertEqual(patch_state, 'unknown')
        patch_state = LivePatchSocket.get_patch_state(status1)
        self.assertEqual(patch_state, 'nothing-to-apply')
        patch_state = LivePatchSocket.get_patch_state(status2)
        self.assertEqual(patch_state, 'applied')

    def test_get_fixes(self):
        fixes = LivePatchSocket.get_fixes(status0)
        self.assertEqual(fixes, [])
        fixes = LivePatchSocket.get_fixes(status1)
        self.assertEqual(fixes, [])
        fixes = LivePatchSocket.get_fixes(status2)
        self.assertEqual(fixes, [LivePatchFix('CVE-2016-0001'),
                                 LivePatchFix('CVE-2016-0002'),
                                 LivePatchFix('CVE-2017-0001 (unpatched)'),
                                 LivePatchFix('CVE-2017-0001')])

    def test_livepatch_fix(self):
        fix = LivePatchFix('CVE-2016-0001')
        self.assertEqual(fix.name, 'CVE-2016-0001')
        self.assertTrue(fix.patched)

        fix = LivePatchFix('CVE-2016-0001 (unpatched)')
        self.assertEqual(fix.name, 'CVE-2016-0001')
        self.assertFalse(fix.patched)

    def test_callback_not_active(self):
        mock_http_conn = Mock(spec=http.client.HTTPConnection)
        attrs = {'getresponse.return_value': MockResponse(400, None)}
        mock_http_conn.configure_mock(**attrs)

        cb_called = [False]

        def on_done(active, check_state, patch_state, fixes):
            cb_called[0] = True
            self.assertFalse(active)

        lp = LivePatchSocket(mock_http_conn)
        lp.get_status(on_done)

        mock_http_conn.request.assert_called_with(
            'GET', '/status?verbose=True')
        TestUtils.WaitUntilMSec(self, lambda: cb_called[0] is True)

    def test_callback_active(self):
        mock_http_conn = Mock(spec=http.client.HTTPConnection)
        attrs = {'getresponse.return_value': MockResponse(200, status2)}
        mock_http_conn.configure_mock(**attrs)

        cb_called = [False]

        def on_done(active, check_state, patch_state, fixes):
            cb_called[0] = True
            self.assertTrue(active)
            self.assertEqual(check_state, 'checked')
            self.assertEqual(patch_state, 'applied')
            self.assertEqual(fixes, [LivePatchFix('CVE-2016-0001'),
                                     LivePatchFix('CVE-2016-0002'),
                                     LivePatchFix('CVE-2017-0001 (unpatched)'),
                                     LivePatchFix('CVE-2017-0001')])

        lp = LivePatchSocket(mock_http_conn)
        lp.get_status(on_done)

        mock_http_conn.request.assert_called_with(
            'GET', '/status?verbose=True')
        TestUtils.WaitUntilMSec(self, lambda: cb_called[0] is True)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        logging.basicConfig(level=logging.DEBUG)
    unittest.main()
