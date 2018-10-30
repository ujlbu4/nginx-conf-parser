# coding=utf-8
import unittest
from os.path import dirname

from nginx_conf_parser import NginxConfParser


class NginxConfParserTest(unittest.TestCase):
    def test_constructor(self):
        with self.assertRaises(TypeError):
            NginxConfParser(1234)

        with self.assertRaises(Exception) as context:
            NginxConfParser('/file/that/does/not/exist')
        self.assertTrue('File not found' in str(context.exception))

        parser = NginxConfParser('{0}/features/nginx_full.conf'.format(dirname(__file__)))
        self.assertIsInstance(parser.content, str)

    def test_extract_http_context(self):
        pass

    def test_extract_event_context(self):
        parser = NginxConfParser('{0}/features/nginx_with_events.conf'.format(dirname(__file__)))
        self.assertIsNotNone(parser.event_context)


if __name__ == '__main__':
    unittest.main()
