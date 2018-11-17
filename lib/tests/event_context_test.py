# coding=utf-8
import unittest
from core.events_context import EventContext
from core.utils import extract_context


class EventContextTest(unittest.TestCase):
    def setUp(self):
        self.event_string = """
        events {
            accept_mutex_delay 531ms;
            accept_mutex on;
            
            debug_connection 127.0.0.1;
            debug_connection localhost;
            debug_connection 192.0.2.0/24;
            debug_connection ::1;
            debug_connection 2001:0db8::/32;
            debug_connection unix:;
            
            multi_accept on;
            use select;
            
            worker_aio_requests 34;
            worker_connections 1024;
            
            error_log /mnt/error.log warn;
        }
        """
        self.parsed = extract_context(self.event_string, 'events')
        self.events = EventContext(self.parsed)

    def _update_directive(self, initial, new):
        self.event_string = self.event_string.replace(initial, new)
        self.parsed = extract_context(self.event_string, 'events')
        self.events = EventContext(self.parsed)

    def test_accept_mutex_delay_extraction(self):
        self.assertIsNotNone(self.events.accept_mutex_delay)
        self.assertEqual('531ms', self.events.accept_mutex_delay)

        self._update_directive('accept_mutex_delay 531ms;', '')
        self.assertIsNotNone(self.events.accept_mutex_delay)
        self.assertEqual('500ms', self.events.accept_mutex_delay)

    def test_accept_mutex_extraction(self):
        self.assertIsNotNone(self.events.accept_mutex)
        self.assertEqual('on', self.events.accept_mutex)

        self._update_directive('accept_mutex on;', '')
        self.assertIsNotNone(self.events.accept_mutex)
        self.assertEqual('off', self.events.accept_mutex)

    def test_debug_connection_extraction(self):
        self.assertIsInstance(self.events.debug_connection, list)
        self.assertEqual(6, len(self.events.debug_connection))

        self.assertIn('127.0.0.1', self.events.debug_connection)
        self.assertIn('localhost', self.events.debug_connection)
        self.assertIn('192.0.2.0/24', self.events.debug_connection)
        self.assertIn('::1', self.events.debug_connection)
        self.assertIn('2001:0db8::/32', self.events.debug_connection)
        self.assertIn('unix:', self.events.debug_connection)

    def test_multi_accept_extraction(self):
        self.assertIsNotNone(self.events.multi_accept)
        self.assertEqual('on', self.events.multi_accept)

        self._update_directive('multi_accept on;', '')
        self.assertIsNotNone(self.events.multi_accept)
        self.assertEqual('off', self.events.multi_accept)

    def test_use_extraction(self):
        self.assertIsNotNone(self.events.use)
        self.assertEqual('select', self.events.use)

        self._update_directive('use select;', 'use poll;')
        self.assertEqual('poll', self.events.use)

        self._update_directive('use poll;', 'use kqueue;')
        self.assertEqual('kqueue', self.events.use)

        self._update_directive('use kqueue;', 'use epoll;')
        self.assertEqual('epoll', self.events.use)

        self._update_directive('use epoll;', 'use /dev/poll;')
        self.assertEqual('/dev/poll', self.events.use)

        self._update_directive('use /dev/poll;', 'use eventport;')
        self.assertEqual('eventport', self.events.use)

        self._update_directive('use eventport;', '')
        self.assertIsNone(self.events.use)

    def test_worker_aio_requests_extraction(self):
        self.assertEqual(34, self.events.worker_aio_requests)

        self._update_directive('worker_aio_requests 34;', '')
        self.assertEqual(32, self.events.worker_aio_requests)

    def test_worker_connections_extraction(self):
        self.assertEqual(1024, self.events.worker_connections)

        self._update_directive('worker_connections 1024;', '')
        self.assertIsNotNone(self.events.worker_connections)
        self.assertEqual(512, self.events.worker_connections)

    def test_error_log_extraction(self):
        self.assertIsNotNone(self.events.error_log)
        self.assertIsInstance(self.events.error_log, dict)
        self.assertIn('file', self.events.error_log.keys())
        self.assertIn('level', self.events.error_log.keys())

        self.assertEqual('/mnt/error.log', self.events.error_log.get('file'))
        self.assertEqual('warn', self.events.error_log.get('level'))

        self._update_directive('error_log /mnt/error.log warn;', 'error_log /mnt/error.log;')
        self.assertEqual('error', self.events.error_log.get('level'))


if __name__ == '__main__':
    unittest.main()
