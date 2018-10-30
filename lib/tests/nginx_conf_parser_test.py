# coding=utf-8
import unittest
from os.path import dirname

from lib.nginx_conf_parser import NginxConfParser


class NginxConfParserTest(unittest.TestCase):
    def test_initialization_with_file_path(self):
        # should raise an exception since the path leads to no file
        with self.assertRaises(Exception):
            NginxConfParser('/test/for/no/file')

        # should not raise any exception
        NginxConfParser('{0}/features/nginx_full.conf'.format(dirname(__file__)))

    def test_initialization_with_iowrapper(self):
        with open('{0}/features/nginx_full.conf'.format(dirname(__file__)), 'r') as conf:
            NginxConfParser(conf)

    def test_exception_for_non_recognized_input(self):
        with self.assertRaises(TypeError):
            NginxConfParser(1234)

        with self.assertRaises(TypeError):
            NginxConfParser([])

        with self.assertRaises(TypeError):
            NginxConfParser(dict())

    def test_event_parsing(self):
        parser = NginxConfParser('{0}/features/nginx_with_events.conf'.format(dirname(__file__)))

        # checking variables initialization
        self.assertIsNotNone(parser.event_context)
        self.assertIsNotNone(parser.main_context)
        self.assertIsNone(parser.http_context)

        # checking event values
        self.assertEqual(parser.event_context.worker_connections, '4096')

        # checking main values
        self.assertEqual(parser.main_context.user, 'www www')
        self.assertEqual(parser.main_context.worker_processes, '5')
        self.assertEqual(parser.main_context.error_log, 'logs/error.log')
        self.assertEqual(parser.main_context.pid, 'logs/nginx.pid')
        self.assertEqual(parser.main_context.worker_rlimit_nofile, '8192')

        self.assertIsInstance(parser.main_context.env, list)
        self.assertIn('NODE_PROD', parser.main_context.env)
        self.assertIn('NODE_ENV=production', parser.main_context.env)


if __name__ == '__main__':
    unittest.main()
