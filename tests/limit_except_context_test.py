# coding=utf-8
import unittest

from parser.nginx_conf_parser import LimitExceptContext


class LimitExceptContextTest(unittest.TestCase):
    def setUp(self):
        self.context_string = """
        limit_except GET {
            deny  192.168.1.1;
            allow 192.168.1.0/24;
            allow 10.1.1.0/16;
            allow 2001:0db8::/32;
            deny  all;
            
            auth_jwt "closed site" token=$cookie_auth_token;
            auth_jwt_key_file conf/keys.json;
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

    def test_auth_jwt_extraction(self):
        self.assertIsNotNone(self.limit_except.auth_jwt)
        self.assertIsInstance(self.limit_except.auth_jwt, dict)
        self.assertEqual({'realm', 'token'}, set(self.limit_except.auth_jwt.keys()))
        self.assertEqual('"closed site"', self.limit_except.auth_jwt.get('realm'))

        self._update_directive('auth_jwt "closed site" token=$cookie_auth_token;', 'auth_jwt "closed site";')
        self.assertIsInstance(self.limit_except.auth_jwt, dict)
        self.assertEqual('"closed site"', self.limit_except.auth_jwt.get('realm'))
        self.assertIsNone(self.limit_except.auth_jwt.get('token'))

        self._update_directive('auth_jwt "closed site";', 'auth_jwt off;')
        self.assertIsInstance(self.limit_except.auth_jwt, str)
        self.assertEqual('off',self.limit_except.auth_jwt)

        self._update_directive('auth_jwt off;', '')
        self.assertIsInstance(self.limit_except.auth_jwt, str)
        self.assertEqual('off', self.limit_except.auth_jwt)

    def test_auth_jwt_key_file_extraction(self):
        self.assertIsNotNone(self.limit_except.auth_jwt_key_file)
        self.assertEqual('conf/keys.json', self.limit_except.auth_jwt_key_file)

        self._update_directive('auth_jwt_key_file conf/keys.json;', '')
        self.assertIsNone(self.limit_except.auth_jwt_key_file)


if __name__ == '__main__':
    unittest.main()
