# coding=utf-8
import unittest
from core.EventContext import EventContext


class EventContextTest(unittest.TestCase):
    def test_default_directive_values_extraction(self):
        event_context = EventContext("events { }")
        self.assertEqual(event_context.accept_mutex, 'off')
        self.assertEqual(event_context.accept_mutex_delay, '500ms')
        self.assertEqual(event_context.multi_accept, 'off')
        self.assertEqual(event_context.debug_connection, [])
        self.assertIsNone(event_context.use)
        self.assertEqual(event_context.worker_aio_requests, '32')
        self.assertEqual(event_context.worker_connections, '512')

    def test_simple_directive_extraction(self):
        # accept_mutex
        event_context = EventContext("events { accept_mutex on; }")
        self.assertEqual(event_context.accept_mutex, 'on')

        # accept mutex_delay
        event_context = EventContext("events { accept_mutex_delay 300ms; }")
        self.assertEqual(event_context.accept_mutex_delay, '300ms')
        event_context = EventContext("events { accept_mutex on; accept_mutex_delay 300ms; }")
        self.assertEqual(event_context.accept_mutex_delay, '300ms')

        # debug connection
        event_context = EventContext("events { debug_connection localhost; }")
        self.assertEqual(event_context.debug_connection, 'localhost')
        event_context = EventContext("events { debug_connection localhost; debug_connection 192.168.1.1; }")
        self.assertEqual(event_context.debug_connection, ['localhost', '192.168.1.1'])

        # multi accept
        event_context = EventContext("events { multi_accept on; }")
        self.assertEqual(event_context.multi_accept, 'on')

        # use
        event_context = EventContext("events { use standard; }")
        self.assertEqual(event_context.use, 'standard')

        # worker_aio_requests
        event_context = EventContext("events { worker_aio_requests 45; }")
        self.assertEqual(event_context.worker_aio_requests, '45')

        # worker_connections
        event_context = EventContext("events { worker_connections 1024; }")
        self.assertEqual(event_context.worker_connections, '1024')


if __name__ == '__main__':
    unittest.main()
