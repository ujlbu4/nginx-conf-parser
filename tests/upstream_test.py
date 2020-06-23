# coding=utf-8
import re
import unittest

from parser.nginx_conf_parser.upstream_context import UpstreamContext


class UpstreamTest(unittest.TestCase):
    def setUp(self):
        self.upstream_string = """
        upstream dynamic {
            zone upstream_dynamic 64k;
            state /var/lib/nginx/state/servers.conf; # path for Linux
            hash $remote_addr consistent;
            
            keepalive 32;
            keepalive_requests 100;
            keepalive_timeout 60s;
            least_conn;
            least_time header inflight;
            
            queue 54 timeout=56s;
            random two least_conn;
            
            ip_hash;
            ntlm;

            server backend1.example.com      weight=5;
            server backend2.example.com:8080 fail_timeout=5s slow_start=30s;
            server 192.0.2.1                 max_fails=3;
            server backend3.example.com      resolve;
            server backend4.example.com      service=http resolve;

            server backup1.example.com:8080  backup;
            server backup2.example.com:8080  backup;
            
            sticky cookie srv_id expires=1h domain=.example.com path=/;
        }
        """.replace('\n', '')

        self.parsed = re.findall(r'upstream\s+([a-zA-Z]+)\s+{([^}]*)', self.upstream_string)[0]
        self.upstream = UpstreamContext(self.parsed[0], self.parsed[1])

    def _update_directive(self, initial, new):
        self.upstream_string = self.upstream_string.replace(initial, new)
        self.parsed = re.findall(r'upstream\s+([a-zA-Z]+)\s+{([^}]*)', self.upstream_string)[0]
        self.upstream = UpstreamContext(self.parsed[0], self.parsed[1])

    def test_name_extraction(self):
        self.assertEqual('dynamic', self.upstream.name)

    def test_zone_extraction(self):
        self.assertIsInstance(self.upstream.zone, dict)
        self.assertIn('name', self.upstream.zone.keys())
        self.assertIn('size', self.upstream.zone.keys())
        self.assertEqual('upstream_dynamic', self.upstream.zone.get('name'))
        self.assertEqual('64k', self.upstream.zone.get('size'))

    def test_server_extraction(self):
        self.assertEqual(7, len(self.upstream.servers), [_.get('address') for _ in self.upstream.servers])

        self.assertEqual('backend1.example.com', self.upstream.servers[0].get('address'))
        self.assertEqual(1, len(self.upstream.servers[0].get('parameters')), self.upstream.servers[0].get('parameters'))
        self.assertIn('weight', self.upstream.servers[0].get('parameters').keys())
        self.assertEqual('5', self.upstream.servers[0].get('parameters').get('weight'))

        self.assertEqual('backend2.example.com:8080', self.upstream.servers[1].get('address'))

        self.assertEqual('backend3.example.com', self.upstream.servers[3].get('address'))
        self.assertIn('resolve', self.upstream.servers[3].get('parameters'))
        self.assertTrue(self.upstream.servers[3].get('parameters').get('resolve'),
                        self.upstream.servers[3].get('parameters'))

        self.assertEqual('backend4.example.com', self.upstream.servers[4].get('address'))

        self.assertEqual('backup1.example.com:8080', self.upstream.servers[5].get('address'))
        self.assertIn('backup', self.upstream.servers[5].get('parameters'))
        self.assertTrue(self.upstream.servers[5].get('parameters').get('backup'))

        self.assertEqual('backup2.example.com:8080', self.upstream.servers[6].get('address'))

    def test_state_extraction(self):
        self.assertEqual('/var/lib/nginx/state/servers.conf', self.upstream.state)

    def test_hash_extraction(self):
        self.assertIsNotNone(self.upstream.hash)
        self.assertIsInstance(self.upstream.hash, dict)
        self.assertEqual('$remote_addr', self.upstream.hash.get('key'))
        self.assertTrue(self.upstream.hash.get('consistent'))

    def test_ip_hash_extraction(self):
        self.assertTrue(self.upstream.ip_hash)

    def test_keepalive_extraction(self):
        self.assertEqual(32, self.upstream.keepalive)

    def test_keepalive_requests_extraction(self):
        self.assertEqual(100, self.upstream.keepalive_requests)

    def test_keepalive_timeout_extraction(self):
        self.assertEqual('60s', self.upstream.keepalive_timeout)

    def test_ntlm_extraction(self):
        self.assertTrue(self.upstream.ntlm)

    def test_least_conn_extraction(self):
        self.assertTrue(self.upstream.least_conn)

    def test_least_time_extraction(self):
        self.assertIsNotNone(self.upstream.least_time)
        self.assertIsInstance(self.upstream.least_time, dict)
        self.assertTrue(self.upstream.least_time.get('header'))
        self.assertFalse(self.upstream.least_time.get('last_byte'))
        self.assertTrue(self.upstream.least_time.get('inflight'))

        self._update_directive('least_time header inflight;', 'least_time header;')
        self.assertTrue(self.upstream.least_time.get('header'))
        self.assertFalse(self.upstream.least_time.get('inflight'))
        self.assertFalse(self.upstream.least_time.get('last_byte'))

        self._update_directive('least_time header;', 'least_time last_byte;')
        self.assertTrue(self.upstream.least_time.get('last_byte'))
        self.assertFalse(self.upstream.least_time.get('header'))
        self.assertFalse(self.upstream.least_time.get('inflight'))

        self._update_directive('least_time last_byte;', 'least_time last_byte inflight;')
        self.assertTrue(self.upstream.least_time.get('last_byte'))
        self.assertTrue(self.upstream.least_time.get('inflight'))
        self.assertFalse(self.upstream.least_time.get('header'))

    def test_queue_extraction(self):
        self.assertIsNotNone(self.upstream.queue)
        self.assertIsInstance(self.upstream.queue, dict)
        self.assertEqual(54, self.upstream.queue.get('value'))
        self.assertEqual('56s', self.upstream.queue.get('timeout'))

        self._update_directive('queue 54 timeout=56s;', 'queue 46;')
        self.assertEqual(46, self.upstream.queue.get('value'))
        self.assertEqual('60s', self.upstream.queue.get('timeout'))

    def test_random_extraction(self):
        self.assertIsNotNone(self.upstream.random)
        self.assertIsInstance(self.upstream.random, dict)
        self.assertTrue(self.upstream.random.get('two'))
        self.assertEqual('least_conn', self.upstream.random.get('method'))

        self._update_directive('random two least_conn;', 'random two;')
        self.assertIsNotNone(self.upstream.random)
        self.assertIsInstance(self.upstream.random, dict)
        self.assertTrue(self.upstream.random.get('two'))
        self.assertIsNone(self.upstream.random.get('method'))

        self._update_directive('random two;', 'random;')
        self.assertIsNotNone(self.upstream.random)
        self.assertIsInstance(self.upstream.random, dict)
        self.assertFalse(self.upstream.random.get('two'))
        self.assertIsNone(self.upstream.random.get('method'))

    def test_sticky_cookie_extraction(self):
        self.assertIsNotNone(self.upstream.sticky)
        self.assertIsInstance(self.upstream.sticky, dict)

        self.assertIn('name', self.upstream.sticky.keys())
        self.assertIn('expires', self.upstream.sticky.keys())
        self.assertIn('domain', self.upstream.sticky.keys())
        self.assertIn('httponly', self.upstream.sticky.keys())
        self.assertIn('secure', self.upstream.sticky.keys())
        self.assertIn('path', self.upstream.sticky.keys())

        self.assertEqual('cookie', self.upstream.sticky.get('type'))
        self.assertEqual('srv_id', self.upstream.sticky.get('name'))

        self.assertIsNotNone(self.upstream.sticky.get('expires'))
        self.assertEqual('1h', self.upstream.sticky.get('expires'))

        self.assertIsNotNone(self.upstream.sticky.get('domain'))
        self.assertEqual('.example.com', self.upstream.sticky.get('domain'))

        self.assertIsNotNone(self.upstream.sticky.get('path'))
        self.assertEqual('/', self.upstream.sticky.get('path'))

        self.assertFalse(self.upstream.sticky.get('httponly'))
        self.assertFalse(self.upstream.sticky.get('secure'))

        self._update_directive(
            'sticky cookie srv_id expires=1h domain=.example.com path=/;',
            'sticky cookie srv_id domain=.example.com path=/test httponly secure;'
        )
        self.assertEqual('srv_id', self.upstream.sticky.get('name'))
        self.assertIsNone(self.upstream.sticky.get('expires'))
        self.assertEqual('.example.com', self.upstream.sticky.get('domain'))
        self.assertEqual('/test', self.upstream.sticky.get('path'))
        self.assertTrue(self.upstream.sticky.get('httponly'))
        self.assertTrue(self.upstream.sticky.get('secure'))

    def test_sticky_route_extraction(self):
        self._update_directive(
            'sticky cookie srv_id expires=1h domain=.example.com path=/;',
            'sticky route $route_cookie $route_uri;'
        )
        self.assertIsNotNone(self.upstream.sticky)
        self.assertIsInstance(self.upstream.sticky, dict)
        self.assertIn('variables', self.upstream.sticky.keys())

        self.assertEqual('route', self.upstream.sticky.get('type'))
        self.assertIsInstance(self.upstream.sticky.get('variables'), list)

        self.assertEqual(2, len(self.upstream.sticky.get('variables')), self.upstream.sticky.get('variables'))
        self.assertIn('$route_cookie', self.upstream.sticky.get('variables'))
        self.assertIn('$route_uri', self.upstream.sticky.get('variables'))

        self._update_directive(
            'sticky route $route_cookie $route_uri;',
            'sticky route $route_cookie $route_uri $route_test;'
        )

        self.assertEqual(3, len(self.upstream.sticky.get('variables')))
        self.assertIn('$route_test', self.upstream.sticky.get('variables'))

    def test_sticky_learn_extraction(self):
        self._update_directive(
            'sticky cookie srv_id expires=1h domain=.example.com path=/;',
            'sticky learn create=$upstream_cookie_examplecookie lookup=$cookie_examplecookie zone=client_sessions:1m;'
        )
        self.assertIsNotNone(self.upstream.sticky)
        self.assertIsInstance(self.upstream.sticky, dict)
        self.assertIn('create', self.upstream.sticky.keys())
        self.assertIn('zone', self.upstream.sticky.keys())
        self.assertIn('lookup', self.upstream.sticky.keys())
        self.assertIn('timeout', self.upstream.sticky.keys())
        self.assertIn('header', self.upstream.sticky.keys())
        self.assertIn('sync', self.upstream.sticky.keys())

        self.assertEqual('learn', self.upstream.sticky.get('type'))
        self.assertEqual('$upstream_cookie_examplecookie', self.upstream.sticky.get('create'))
        self.assertEqual('$cookie_examplecookie', self.upstream.sticky.get('lookup'))
        self.assertIsInstance(self.upstream.sticky.get('zone'), dict)
        self.assertEqual('client_sessions', self.upstream.sticky.get('zone').get('name'))
        self.assertEqual('1m', self.upstream.sticky.get('zone').get('size'))
        self.assertFalse(self.upstream.sticky.get('header'))
        self.assertFalse(self.upstream.sticky.get('sync'))
        self.assertIsNone(self.upstream.sticky.get('timeout'))

        self._update_directive(
            'sticky learn create=$upstream_cookie_examplecookie lookup=$cookie_examplecookie zone=client_sessions:1m;',
            'sticky learn header sync create=$upstream_cookie_examplecookie lookup=$cookie_examplecookie '
            'zone=client_sessions:1m;'
        )
        self.assertTrue(self.upstream.sticky.get('header'))
        self.assertTrue(self.upstream.sticky.get('sync'))

        self._update_directive(
            'sticky learn header sync create=$upstream_cookie_examplecookie lookup=$cookie_examplecookie '
            'zone=client_sessions:1m;',
            'sticky learn header sync create=$upstream_cookie_examplecookie lookup=$cookie_examplecookie '
            'zone=client_sessions:1m timeout=3s;',
        )
        self.assertEqual('3s', self.upstream.sticky.get('timeout'))


if __name__ == '__main__':
    unittest.main()
