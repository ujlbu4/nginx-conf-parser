# coding=utf-8
import unittest

from nginx_conf_parser.limit_except_context import LimitExceptContext


class LimitExceptContextTest(unittest.TestCase):
    def setUp(self):
        self.context_string = """
        limit_except GET {
            deny  192.168.1.1;
            allow 192.168.1.0/24;
            allow 10.1.1.0/16;
            allow 2001:0db8::/32;
            deny  all;
        }
        """
        self.limit_except = LimitExceptContext(self.context_string.replace('\n', ' '))

    def _update_directive(self, initial, new):
        self.context_string = self.context_string.replace(initial, new)
        self.limit_except = LimitExceptContext(self.context_string)

    def test_allow_extraction(self):
        self.assertIsNotNone(self.limit_except.allow)
        self.assertIsInstance(self.limit_except.allow, list)
        self.assertEqual(3, len(self.limit_except.allow))

        self.assertEqual({'192.168.1.0/24', '10.1.1.0/16', '2001:0db8::/32'}, set(self.limit_except.allow))

    def test_deny_extraction(self):
        self.assertIsNotNone(self.limit_except.deny)
        self.assertIsInstance(self.limit_except.deny, list)
        self.assertEqual(2, len(self.limit_except.deny))
        self.assertEqual({'192.168.1.1', 'all'}, set(self.limit_except.deny))


if __name__ == '__main__':
    unittest.main()
