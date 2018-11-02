# coding=utf-8
import unittest

from core.events_context import EventContext


class EventContextTest(unittest.TestCase):
    def setUp(self):
        self.context = EventContext()

    def test_accept_mutex_delay_extraction(self):
        self.assertEqual('500ms', self.context.accept_mutex_delay)

        self.context.load('events { accept_mutex_delay 531ms; }')
        self.assertEqual('531ms', self.context.accept_mutex_delay)

    def test_accept_mutex_extraction(self):
        self.assertEqual('off', self.context.accept_mutex)

        self.context.load('events { accept_mutex on; }')
        self.assertEqual('on', self.context.accept_mutex)

    def test_debug_connection_extraction(self):
        self.assertEqual([], self.context.debug_connection)

        self.context.load(
            'events { debug_connection localhost; debug_connection 192.168.1.1; debug_connection unix:; '
            'debug_connection 2001:0db8::/32; debug_connection ::1; }')
        self.assertEqual(5, len(self.context.debug_connection))
        self.assertIn('localhost', self.context.debug_connection)
        self.assertIn('192.168.1.1', self.context.debug_connection)
        self.assertIn('unix:', self.context.debug_connection)
        self.assertIn('2001:0db8::/32', self.context.debug_connection)
        self.assertIn('::1', self.context.debug_connection)

    def test_multi_accept_extraction(self):
        self.assertEqual('off', self.context.multi_accept)

        self.context.load('events { multi_accept on; }')
        self.assertEqual('on', self.context.multi_accept)

    def test_use_extraction(self):
        self.assertIsNone(self.context.use)

        self.context.load('events { use select; }')
        self.assertEqual('select', self.context.use)

    def test_worker_aio_requests_extraction(self):
        self.assertEqual(32, self.context.worker_aio_requests)

        self.context.load('events { worker_aio_requests 14; }')
        self.assertEqual(14, self.context.worker_aio_requests)

    def test_worker_connections_extraction(self):
        self.assertEqual(512, self.context.worker_connections)

        self.context.load('events { worker_connections 12; }')
        self.assertEqual(12, self.context.worker_connections)

    def test_error_log_extraction(self):
        self.assertEqual(dict(file='logs/error.log', level='error'), self.context.error_log)

        self.context.load("events { error_log logs/error.log; }")
        self.assertEqual(dict(file='logs/error.log', level='error'), self.context.error_log)

        self.context.load("events { error_log logs/errors.log warn; }")
        self.assertEqual(dict(file='logs/errors.log', level='warn'), self.context.error_log)


if __name__ == '__main__':
    unittest.main()
