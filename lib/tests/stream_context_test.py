# coding=utf-8
import unittest
from core.stream_context import StreamContext
from core.utils import extract_context


class StreamContextTest(unittest.TestCase):
    def test_server_extraction(self):
        extract_context(open('{0}/features/nginx_stream_sample.conf'))
