# coding=utf-8
import unittest
from core.stream_context import StreamContext
from core.utils import extract_context
from os.path import dirname


class StreamContextTest(unittest.TestCase):
    def test_server_extraction(self):
        f = open('{0}/features/nginx_stream_sample.conf'.format(dirname(__file__)))

        f.close()
