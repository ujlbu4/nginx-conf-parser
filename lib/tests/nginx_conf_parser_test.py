# coding=utf-8
import unittest

from lib.nginx_conf_parser import NginxConfParser


class NginxConfParserTest(unittest.TestCase):
    def test_initialization_with_file_path(self):
        with self.assertRaises(Exception):
            NginxConfParser('/test/for/no/file')

    def test_initialization_with_iowrapper(self):
        pass

    def test_parsing_nginx_configuration_file_with_only_events(self):
        pass
