# coding=utf-8
import unittest
from nginx_conf_parser.location_context import LocationContext
from nginx_conf_parser.limit_except_context import LimitExceptContext


class LocationContextTest(unittest.TestCase):
    def setUp(self):
        self.context_string = """
        location {
            limit_except GET {
                allow 192.168.1.0/32;
                deny  all; 
            }
            limit_except POST {
                allow 192.168.1.25/24;
                deny  all; 
            }
            types {
                application/octet-stream bin exe dll;
                application/octet-stream deb;
                application/octet-stream dmg;
            }
            absolute_redirect on;
            
            accept 192.168.1.1;
            accept 10.1.1.0/32;
            
            deny 192.168.1.2;
            deny all;
            
            aio on;
            aio_write on;
            alias /data/w3/images/;
            auth_jwt "closed site" token=$cookie_auth_token;
            auth_jwt_key_file conf/keys.json;
            auth_jwt_leeway 50s;
            chunked_transfer_encoding off;
            client_body_buffer_size 82k;
            client_body_in_file_only clean;
            client_body_in_single_buffer on;
            client_body_temp_path /spool/nginx/client_temp 1 2;
            client_body_timeout 1h;
            client_max_body_size 25m;
            default_type application/json;
            directio 4m;
            directio_alignment 445m;
            disable_symlinks if_not_owner from=$document_root;
            error_page 500 502 =200 503 504 /50x.html;
            etag off;
            if_modified_since before;
            internal;
            keepalive_disable safari;
            keepalive_requests 200;
            keepalive_timeout 75s 34s;
            limit_rate_after 500k;
            limit_rate 4k;
            lingering_close on;
            lingering_time 34s;
            lingering_timeout 8s;
            log_not_found off;
            log_subrequest on;
            max_ranges 32;
            msie_padding off;
            msie_refresh on;
            open_file_cache max=1000 inactive=20s;
            open_file_cache_errors on;
            open_file_cache_min_uses 2000;
            open_file_cache_valid 32s;
            output_buffers 4 22k;
            port_in_redirect off;
            postpone_output 1423;
            read_ahead 14;
            recursive_error_pages on;
            reset_timedout_connection on;
            resolver localhost:8080 192.168.1.1 valid=12s ipv6=on;
            resolver_timeout 54s;
            root /var/www/html;
            satisfy any;
            send_lowat 14m;
            send_timeout 54s;
            sendfile on;
            sendfile_max_chunk 15m;
            server_name_in_redirect on;
            server_tokens build;
            subrequest_output_buffer_size 9k;
            tcp_nodelay off;
            tcp_nopush off;
            try_files $uri $uri/index.html $uri.html =404;
            types_hash_bucket_size 14m;
            types_hash_max_size 512;
        }
        """
        self.location = LocationContext(self.context_string.replace('\n', ' '))

    def _update_directive(self, initial, new):
        self.context_string = self.context_string.replace(initial, new)
        self.location = LocationContext(self.context_string)

    def test_absolute_redirect_extraction(self):
        self.assertIsNotNone(self.location.absolute_redirect)
        self.assertEqual('on', self.location.absolute_redirect)

        self._update_directive('absolute_redirect on;', '')
        self.assertIsNotNone(self.location.absolute_redirect)
        self.assertEqual('off', self.location.absolute_redirect)

    def test_accept_extraction(self):
        self.assertIsNotNone(self.location.accept)
        self.assertIsInstance(self.location.accept, list)
        self.assertEqual(2, len(self.location.accept))
        self.assertEqual({'192.168.1.1', '10.1.1.0/32'}, set(self.location.accept))

        self._update_directive('accept 192.168.1.1;', '')
        self._update_directive('accept 10.1.1.0/32;', '')
        self.assertIsNone(self.location.accept)

    def test_aio_extraction(self):
        self.assertIsNotNone(self.location.aio)
        self.assertEqual('on', self.location.aio)

        self._update_directive('aio on;', 'aio off;')
        self.assertEqual('off', self.location.aio)

        self._update_directive('aio off;', 'aio threads;')
        self.assertIsInstance(self.location.aio, dict)
        self.assertIn('threads', self.location.aio.keys())
        self.assertIn('pool', self.location.aio.keys())
        self.assertTrue(self.location.aio.get('threads'))
        self.assertIsNone(self.location.aio.get('pool'))

        self._update_directive('aio threads;', 'aio threads=pool$disk;')
        self.assertEqual('pool$disk', self.location.aio.get('pool'))

        self._update_directive('aio threads=pool$disk;', '')
        self.assertIsNotNone(self.location.aio)
        self.assertEqual('off', self.location.aio)

    def test_aio_write_extraction(self):
        self.assertIsNotNone(self.location.aio_write)
        self.assertEqual('on', self.location.aio_write)

        self._update_directive('aio_write on;', 'aio_write off;')
        self.assertEqual('off', self.location.aio_write)

        self._update_directive('aio_write off;', '')
        self.assertIsNotNone(self.location.aio_write)
        self.assertEqual('off', self.location.aio_write)

    def test_alias_extraction(self):
        self.assertIsNotNone(self.location.alias)
        self.assertEqual('/data/w3/images/', self.location.alias)

        self._update_directive('alias /data/w3/images/;', '')
        self.assertIsNone(self.location.alias)

    def test_auth_jwt_extraction(self):
        self.assertIsNotNone(self.location.auth_jwt)
        self.assertIsInstance(self.location.auth_jwt, dict)
        self.assertEqual({'realm', 'token'}, set(self.location.auth_jwt.keys()))
        self.assertEqual('"closed site"', self.location.auth_jwt.get('realm'))

        self._update_directive('auth_jwt "closed site" token=$cookie_auth_token;', 'auth_jwt "closed site";')
        self.assertIsInstance(self.location.auth_jwt, dict)
        self.assertEqual('"closed site"', self.location.auth_jwt.get('realm'))
        self.assertIsNone(self.location.auth_jwt.get('token'))

        self._update_directive('auth_jwt "closed site";', 'auth_jwt off;')
        self.assertIsInstance(self.location.auth_jwt, str)
        self.assertEqual('off', self.location.auth_jwt)

        self._update_directive('auth_jwt off;', '')
        self.assertIsInstance(self.location.auth_jwt, str)
        self.assertEqual('off', self.location.auth_jwt)

    def test_auth_jwt_key_file_extraction(self):
        self.assertIsNotNone(self.location.auth_jwt_key_file)
        self.assertEqual('conf/keys.json', self.location.auth_jwt_key_file)

        self._update_directive('auth_jwt_key_file conf/keys.json;', '')
        self.assertIsNone(self.location.auth_jwt_key_file)

    def test_auth_jwt_leeway_extraction(self):
        self.assertIsNotNone(self.location.auth_jwt_leeway)
        self.assertEqual('50s', self.location.auth_jwt_leeway)

        self._update_directive('auth_jwt_leeway 50s;', '')
        self.assertIsNotNone(self.location.auth_jwt_leeway)
        self.assertEqual('0s', self.location.auth_jwt_leeway)

    def test_chunked_transfer_encoding_extraction(self):
        self.assertIsNotNone(self.location.chunked_transfer_encoding)
        self.assertEqual('off', self.location.chunked_transfer_encoding)

        self._update_directive('chunked_transfer_encoding off;', 'chunked_transfer_encoding on;')
        self.assertEqual('on', self.location.chunked_transfer_encoding)

        self._update_directive('chunked_transfer_encoding on;', '')
        self.assertIsNotNone(self.location.chunked_transfer_encoding)
        self.assertEqual('on', self.location.chunked_transfer_encoding)

    def test_client_body_buffer_size_extraction(self):
        self.assertIsNotNone(self.location.client_body_buffer_size)
        self.assertEqual('82k', self.location.client_body_buffer_size)

        self._update_directive('client_body_buffer_size 82k;', '')
        self.assertIsNotNone(self.location.client_body_buffer_size)
        self.assertEqual('8k|16k', self.location.client_body_buffer_size)

    def test_client_body_in_file_only_extraction(self):
        self.assertIsNotNone(self.location.client_body_in_file_only)
        self.assertEqual('clean', self.location.client_body_in_file_only)

        self._update_directive('client_body_in_file_only clean;', 'client_body_in_file_only on;')
        self.assertEqual('on', self.location.client_body_in_file_only)

        self._update_directive('client_body_in_file_only on;', 'client_body_in_file_only off;')
        self.assertEqual('off', self.location.client_body_in_file_only)

        self._update_directive('client_body_in_file_only off;', '')
        self.assertIsNotNone(self.location.client_body_in_file_only)
        self.assertEqual('off', self.location.client_body_in_file_only)

    def test_client_body_in_single_buffer_extraction(self):
        self.assertIsNotNone(self.location.client_body_in_single_buffer)
        self.assertEqual('on', self.location.client_body_in_single_buffer)

        self._update_directive('client_body_in_single_buffer on;', 'client_body_in_single_buffer off;')
        self.assertEqual('off', self.location.client_body_in_single_buffer)

        self._update_directive('client_body_in_single_buffer off;', '')
        self.assertIsNotNone(self.location.client_body_in_single_buffer)
        self.assertEqual('off', self.location.client_body_in_single_buffer)

    def test_client_body_temp_path_extraction(self):
        self.assertIsNotNone(self.location.client_body_temp_path)
        self.assertIsInstance(self.location.client_body_temp_path, dict)
        self.assertIn('path', self.location.client_body_temp_path.keys())
        self.assertIn('level1', self.location.client_body_temp_path.keys())
        self.assertIn('level2', self.location.client_body_temp_path.keys())
        self.assertIn('level3', self.location.client_body_temp_path.keys())

        self.assertEqual('/spool/nginx/client_temp', self.location.client_body_temp_path.get('path'))
        self.assertIsNotNone(self.location.client_body_temp_path.get('level1'))
        self.assertEqual('1', self.location.client_body_temp_path.get('level1'))

        self.assertIsNotNone(self.location.client_body_temp_path.get('level2'))
        self.assertEqual('2', self.location.client_body_temp_path.get('level2'))

        self.assertIsNone(self.location.client_body_temp_path.get('level3'))

        self._update_directive(
            'client_body_temp_path /spool/nginx/client_temp 1 2;',
            'client_body_temp_path /spool/nginx/client_temp 1 2 3;'
        )
        self.assertIsNotNone(self.location.client_body_temp_path.get('level3'))
        self.assertEqual('3', self.location.client_body_temp_path.get('level3'))

        self._update_directive(
            'client_body_temp_path /spool/nginx/client_temp 1 2 3;',
            'client_body_temp_path /spool/nginx/client_temp 1;'
        )
        self.assertIsNone(self.location.client_body_temp_path.get('level2'))
        self.assertIsNone(self.location.client_body_temp_path.get('level3'))

        self._update_directive(
            'client_body_temp_path /spool/nginx/client_temp 1;',
            'client_body_temp_path /spool/nginx/client_temp;'
        )
        self.assertIsNone(self.location.client_body_temp_path.get('level1'))
        self.assertIsNone(self.location.client_body_temp_path.get('level2'))
        self.assertIsNone(self.location.client_body_temp_path.get('level3'))

        self._update_directive(
            'client_body_temp_path /spool/nginx/client_temp;',
            ''
        )
        self.assertIsNotNone(self.location.client_body_temp_path)
        self.assertEqual('client_body_temp', self.location.client_body_temp_path.get('path'))
        self.assertIsNone(self.location.client_body_temp_path.get('level1'))
        self.assertIsNone(self.location.client_body_temp_path.get('level2'))
        self.assertIsNone(self.location.client_body_temp_path.get('level3'))

    def test_client_body_timeout_extraction(self):
        self.assertIsNotNone(self.location.client_body_timeout)
        self.assertEqual('1h', self.location.client_body_timeout)

        self._update_directive('client_body_timeout 1h;', '')
        self.assertIsNotNone(self.location.client_body_timeout)
        self.assertEqual('60s', self.location.client_body_timeout)

    def test_client_max_body_size_extraction(self):
        self.assertIsNotNone(self.location.client_max_body_size)
        self.assertEqual('25m', self.location.client_max_body_size)

        self._update_directive('client_max_body_size 25m;', '')
        self.assertIsNotNone(self.location.client_max_body_size)
        self.assertEqual('1m', self.location.client_max_body_size)

    def test_default_type_extraction(self):
        self.assertIsNotNone(self.location.default_type)
        self.assertEqual('application/json', self.location.default_type)

        self._update_directive('default_type application/json;', '')
        self.assertIsNotNone(self.location.default_type)
        self.assertEqual('text/plain', self.location.default_type)

    def test_deny_extraction(self):
        self.assertIsNotNone(self.location.deny)
        self.assertIsInstance(self.location.deny, list)
        self.assertEqual(2, len(self.location.deny))
        self.assertEqual({'192.168.1.2', 'all'}, set(self.location.deny))

        self._update_directive('deny 192.168.1.2;', '')
        self._update_directive('deny all;', '')
        self.assertIsNone(self.location.deny)

    def test_directio_extracion(self):
        self.assertIsNotNone(self.location.directio)
        self.assertEqual('4m', self.location.directio)

        self._update_directive('directio 4m;', 'directio off;')
        self.assertEqual('off', self.location.directio)

        self._update_directive('directio off;', '')
        self.assertIsNotNone(self.location.directio)
        self.assertEqual('off', self.location.directio)

    def test_directio_alignment_extraction(self):
        self.assertIsNotNone(self.location.directio_alignment)
        self.assertEqual('445m', self.location.directio_alignment)

        self._update_directive('directio_alignment 445m;', '')
        self.assertEqual('512', self.location.directio_alignment)

    def test_disable_symlinks_extraction(self):
        self.assertIsNotNone(self.location.disable_symlinks)
        self.assertIsInstance(self.location.disable_symlinks, dict)
        self.assertIn('value', self.location.disable_symlinks.keys())
        self.assertIn('_from', self.location.disable_symlinks.keys())
        self.assertEqual('if_not_owner', self.location.disable_symlinks.get('value'))
        self.assertEqual('$document_root', self.location.disable_symlinks.get('_from'))

        self._update_directive('disable_symlinks if_not_owner from=$document_root;', 'disable_symlinks if_not_owner;')
        self.assertIsNone(self.location.disable_symlinks.get('_from'))

        self._update_directive('disable_symlinks if_not_owner;', 'disable_symlinks on;')
        self.assertIsInstance(self.location.disable_symlinks, dict)
        self.assertIn('value', self.location.disable_symlinks.keys())
        self.assertIn('_from', self.location.disable_symlinks.keys())
        self.assertEqual('on', self.location.disable_symlinks.get('value'))
        self.assertIsNone(self.location.disable_symlinks.get('_from'))

        self._update_directive('disable_symlinks on;', 'disable_symlinks on from=$document_root;')
        self.assertIsNotNone(self.location.disable_symlinks.get('_from'))
        self.assertEqual('$document_root', self.location.disable_symlinks.get('_from'))

        self._update_directive('disable_symlinks on from=$document_root', 'disable_symlinks off;')
        self.assertNotIsInstance(self.location.disable_symlinks, dict)
        self.assertEqual('off', self.location.disable_symlinks)

        self._update_directive('disable_symlinks off;', '')
        self.assertIsNotNone(self.location.disable_symlinks)
        self.assertEqual('off', self.location.disable_symlinks)

    def test_error_page_extraction(self):
        self.assertIsNotNone(self.location.error_page)
        self.assertIsInstance(self.location.error_page, dict)
        self.assertEqual('/50x.html', self.location.error_page.get('uri'))
        self.assertEqual('500 502 =200 503 504', self.location.error_page.get('codes'))

        self._update_directive('error_page 500 502 =200 503 504 /50x.html;', '')
        self.assertIsNone(self.location.error_page)

    def test_etag_extraction(self):
        self.assertIsNotNone(self.location.etag)
        self.assertEqual('off', self.location.etag)

        self._update_directive('etag off;', 'etag on;')
        self.assertEqual('on', self.location.etag)

        self._update_directive('etag on;', '')
        self.assertIsNotNone(self.location.etag)
        self.assertEqual('on', self.location.etag)

    def test_if_modified_since_extraction(self):
        self.assertIsNotNone(self.location.if_modified_since)
        self.assertEqual('before', self.location.if_modified_since)

        self._update_directive('if_modified_since before;', 'if_modified_since exact;')
        self.assertEqual('exact', self.location.if_modified_since)

        self._update_directive('if_modified_since exact;', 'if_modified_since off;')
        self.assertEqual('off', self.location.if_modified_since)

        self._update_directive('if_modified_since off;', '')
        self.assertIsNotNone(self.location.if_modified_since)
        self.assertEqual('exact', self.location.if_modified_since)

    def test_internal_extraction(self):
        self.assertTrue(self.location.internal)

        self._update_directive('internal;', '')
        self.assertFalse(self.location.internal)

    def test_keepalive_disable_extraction(self):
        self.assertIsNotNone(self.location.keepalive_disable)
        self.assertEqual('safari', self.location.keepalive_disable)

        self._update_directive('keepalive_disable safari;', '')
        self.assertIsNotNone(self.location.keepalive_disable)
        self.assertEqual('msie6', self.location.keepalive_disable)

    def test_keepalive_requests_extraction(self):
        self.assertIsNotNone(self.location.keepalive_requests)
        self.assertEqual(200, self.location.keepalive_requests)

        self._update_directive('keepalive_requests 200;', '')
        self.assertIsNotNone(self.location.keepalive_requests)
        self.assertEqual(100, self.location.keepalive_requests)

    def test_keepalive_timeout_extraction(self):
        self.assertIsNotNone(self.location.keepalive_timeout)
        self.assertIsInstance(self.location.keepalive_timeout, dict)
        self.assertIn('timeout', self.location.keepalive_timeout.keys())
        self.assertIn('header_timeout', self.location.keepalive_timeout.keys())
        self.assertEqual('75s', self.location.keepalive_timeout.get('timeout'))
        self.assertEqual('34s', self.location.keepalive_timeout.get('header_timeout'))

        self._update_directive('keepalive_timeout 75s 34s;', 'keepalive_timeout 76s;')
        self.assertIsInstance(self.location.keepalive_timeout, dict)
        self.assertIn('timeout', self.location.keepalive_timeout.keys())
        self.assertIn('header_timeout', self.location.keepalive_timeout.keys())
        self.assertEqual('76s', self.location.keepalive_timeout.get('timeout'))
        self.assertIsNone(self.location.keepalive_timeout.get('header_timeout'))

        self._update_directive('keepalive_timeout 76s;', '')
        self.assertIsNotNone(self.location.keepalive_timeout)
        self.assertIsInstance(self.location.keepalive_timeout, dict)
        self.assertIn('timeout', self.location.keepalive_timeout.keys())
        self.assertIn('header_timeout', self.location.keepalive_timeout.keys())
        self.assertEqual('75s', self.location.keepalive_timeout.get('timeout'))
        self.assertIsNone(self.location.keepalive_timeout.get('header_timeout'))

    def test_limit_except_extraction(self):
        self.assertIsInstance(self.location.limit_except, dict)
        self.assertEqual(2, len(self.location.limit_except.keys()))
        self.assertEqual({'GET', 'POST'}, set(self.location.limit_except.keys()))

        self.assertIsInstance(self.location.limit_except.get('GET'), LimitExceptContext)
        self.assertIsInstance(self.location.limit_except.get('POST'), LimitExceptContext)

    def test_limit_rate_extraction(self):
        self.assertIsNotNone(self.location.limit_rate)
        self.assertEqual('4k', self.location.limit_rate)

        self._update_directive('limit_rate 4k;', '')
        self.assertIsNotNone(self.location.limit_rate)
        self.assertEqual('0', self.location.limit_rate)

    def test_limit_rate_after_extraction(self):
        self.assertIsNotNone(self.location.limit_rate_after)
        self.assertEqual('500k', self.location.limit_rate_after)

        self._update_directive('limit_rate_after 500k;', '')
        self.assertIsNotNone(self.location.limit_rate_after)
        self.assertEqual('0', self.location.limit_rate_after)

    def test_lingering_close_extraction(self):
        self.assertIsNotNone(self.location.lingering_close)
        self.assertEqual('on', self.location.lingering_close)

        self._update_directive('lingering_close on;', 'lingering_close off;')
        self.assertEqual('off', self.location.lingering_close)

        self._update_directive('lingering_close off;', 'lingering_close always;')
        self.assertEqual('always', self.location.lingering_close)

        self._update_directive('lingering_close always;', '')
        self.assertIsNotNone(self.location.lingering_close)
        self.assertEqual('on', self.location.lingering_close)

    def test_lingering_time_extraction(self):
        self.assertIsNotNone(self.location.lingering_time)
        self.assertEqual('34s', self.location.lingering_time)

        self._update_directive('lingering_time 34s;', '')
        self.assertIsNotNone(self.location.lingering_time)
        self.assertEqual('30s', self.location.lingering_time)

    def test_lingering_timeout_extraction(self):
        self.assertIsNotNone(self.location.lingering_timeout)
        self.assertEqual('8s', self.location.lingering_timeout)

        self._update_directive('lingering_timeout 8s;', '')
        self.assertIsNotNone(self.location.lingering_timeout)
        self.assertEqual('5s', self.location.lingering_timeout)

    def test_log_not_found_extraction(self):
        self.assertIsNotNone(self.location.log_not_found)
        self.assertEqual('off', self.location.log_not_found)

        self._update_directive('log_not_found off;', 'log_not_found on;')
        self.assertEqual('on', self.location.log_not_found)

        self._update_directive('log_not_found on;', '')
        self.assertIsNotNone(self.location.log_not_found)
        self.assertEqual('on', self.location.log_not_found)

    def test_log_subrequest_extraction(self):
        self.assertIsNotNone(self.location.log_subrequest)
        self.assertEqual('on', self.location.log_subrequest)

        self._update_directive('log_subrequest on;', 'log_subrequest off;')
        self.assertEqual('off', self.location.log_subrequest)

        self._update_directive('log_subrequest off;', '')
        self.assertIsNotNone(self.location.log_subrequest)
        self.assertEqual('off', self.location.log_subrequest)

    def test_max_ranges_extraction(self):
        self.assertIsNotNone(self.location.max_ranges)
        self.assertEqual(32, self.location.max_ranges)

        self._update_directive('max_ranges 32;', '')
        self.assertIsNone(self.location.max_ranges)

    def test_msie_padding_extraction(self):
        self.assertIsNotNone(self.location.msie_padding)
        self.assertEqual('off', self.location.msie_padding)

        self._update_directive('msie_padding off;', 'msie_padding on;')
        self.assertEqual('on', self.location.msie_padding)

        self._update_directive('msie_padding on;', '')
        self.assertIsNotNone(self.location.msie_padding)
        self.assertEqual('on', self.location.msie_padding)

    def test_msie_refresh_extraction(self):
        self.assertIsNotNone(self.location.msie_refresh)
        self.assertEqual('on', self.location.msie_refresh)

        self._update_directive('msie_refresh on;', 'msie_refresh off;')
        self.assertEqual('off', self.location.msie_refresh)

        self._update_directive('msie_refresh off;', '')
        self.assertIsNotNone(self.location.msie_refresh)
        self.assertEqual('off', self.location.msie_refresh)

    def test_open_file_cache_extraction(self):
        self.assertIsNotNone(self.location.open_file_cache)
        self.assertIsInstance(self.location.open_file_cache, dict)
        self.assertIn('max', self.location.open_file_cache.keys())
        self.assertIn('inactive', self.location.open_file_cache.keys())
        self.assertEqual(1000, self.location.open_file_cache.get('max'))
        self.assertEqual('20s', self.location.open_file_cache.get('inactive'))

        self._update_directive('open_file_cache max=1000 inactive=20s;', 'open_file_cache max=1000;')
        self.assertIsInstance(self.location.open_file_cache, dict)
        self.assertEqual(1000, self.location.open_file_cache.get('max'))
        self.assertIsNone(self.location.open_file_cache.get('inactive'))

        self._update_directive('open_file_cache max=1000;', 'open_file_cache off;')
        self.assertNotIsInstance(self.location.open_file_cache, dict)
        self.assertEqual('off', self.location.open_file_cache)

        self._update_directive('open_file_cache off;', '')
        self.assertIsNotNone(self.location.open_file_cache)
        self.assertEqual('off', self.location.open_file_cache)

    def test_open_file_cache_errors_extraction(self):
        self.assertIsNotNone(self.location.open_file_cache_errors)
        self.assertEqual('on', self.location.open_file_cache_errors)

        self._update_directive('open_file_cache_errors on;', 'open_file_cache_errors off;')
        self.assertEqual('off', self.location.open_file_cache_errors)

        self._update_directive('open_file_cache_errors off;', '')
        self.assertIsNotNone(self.location.open_file_cache_errors)
        self.assertEqual('off', self.location.open_file_cache_errors)

    def test_open_file_cache_min_uses_extraction(self):
        self.assertIsNotNone(self.location.open_file_cache_min_uses)
        self.assertEqual(2000, self.location.open_file_cache_min_uses)

        self._update_directive('open_file_cache_min_uses 2000;', '')
        self.assertIsNotNone(self.location.open_file_cache_min_uses)
        self.assertEqual(1, self.location.open_file_cache_min_uses)

    def test_open_file_cache_valid_extraction(self):
        self.assertIsNotNone(self.location.open_file_cache_valid)
        self.assertEqual('32s', self.location.open_file_cache_valid)

        self._update_directive('open_file_cache_valid 32s;', '')
        self.assertIsNotNone(self.location.open_file_cache_valid)
        self.assertEqual('60s', self.location.open_file_cache_valid)

    def test_output_buffers_extraction(self):
        self.assertIsNotNone(self.location.output_buffers)
        self.assertIsInstance(self.location.output_buffers, dict)
        self.assertIn('number', self.location.output_buffers.keys())
        self.assertIn('size', self.location.output_buffers.keys())
        self.assertEqual(4, self.location.output_buffers.get('number'))
        self.assertEqual('22k', self.location.output_buffers.get('size'))

        self._update_directive('output_buffers 4 22k;', '')
        self.assertIsNotNone(self.location.output_buffers)
        self.assertIsInstance(self.location.output_buffers, dict)
        self.assertIn('number', self.location.output_buffers.keys())
        self.assertIn('size', self.location.output_buffers.keys())
        self.assertEqual(2, self.location.output_buffers.get('number'))
        self.assertEqual('32k', self.location.output_buffers.get('size'))

    def test_port_in_redirect_extraction(self):
        self.assertIsNotNone(self.location.port_in_redirect)
        self.assertEqual('off', self.location.port_in_redirect)

        self._update_directive('port_in_redirect off;', 'port_in_redirect on;')
        self.assertEqual('on', self.location.port_in_redirect)

        self._update_directive('port_in_redirect on;', '')
        self.assertIsNotNone(self.location.port_in_redirect)
        self.assertEqual('on', self.location.port_in_redirect)

    def test_postpone_output_extraction(self):
        self.assertIsNotNone(self.location.postpone_output)
        self.assertEqual('1423', self.location.postpone_output)

        self._update_directive('postpone_output 1423;', '')
        self.assertIsNotNone(self.location.postpone_output)
        self.assertEqual('1460', self.location.postpone_output)

    def test_read_ahead_extraction(self):
        self.assertIsNotNone(self.location.read_ahead)
        self.assertEqual('14', self.location.read_ahead)

        self._update_directive('read_ahead 14;', '')
        self.assertIsNotNone(self.location.read_ahead)
        self.assertEqual('0', self.location.read_ahead)

    def test_recursive_error_pages_extraction(self):
        self.assertIsNotNone(self.location.recursive_error_pages)
        self.assertEqual('on', self.location.recursive_error_pages)

        self._update_directive('recursive_error_pages on;', 'recursive_error_pages off;')
        self.assertEqual('off', self.location.recursive_error_pages)

        self._update_directive('recursive_error_pages off;', '')
        self.assertIsNotNone(self.location.recursive_error_pages)
        self.assertEqual('off', self.location.recursive_error_pages)

    def test_reset_timedout_connection_extraction(self):
        self.assertIsNotNone(self.location.reset_timedout_connection)
        self.assertEqual('on', self.location.reset_timedout_connection)

        self._update_directive('reset_timedout_connection on;', 'reset_timedout_connection off;')
        self.assertEqual('off', self.location.reset_timedout_connection)

        self._update_directive('reset_timedout_connection off;', '')
        self.assertIsNotNone(self.location.reset_timedout_connection)
        self.assertEqual('off', self.location.reset_timedout_connection)

    def test_resolver_extraction(self):
        self.assertIsNotNone(self.location.resolver)
        self.assertIsInstance(self.location.resolver, dict)
        self.assertIn('address', self.location.resolver.keys())
        self.assertIn('valid', self.location.resolver.keys())
        self.assertIn('ipv6', self.location.resolver.keys())

        self.assertIsInstance(self.location.resolver.get('address'), list)
        self.assertIn('localhost:8080', self.location.resolver.get('address'))
        self.assertIn('192.168.1.1', self.location.resolver.get('address'))
        self.assertEqual('12s', self.location.resolver.get('valid'))
        self.assertEqual('on', self.location.resolver.get('ipv6'))

    def test_resolver_timeout_extraction(self):
        self.assertIsNotNone(self.location.resolver_timeout)
        self.assertEqual('54s', self.location.resolver_timeout)

        self._update_directive('resolver_timeout 54s;', '')
        self.assertIsNotNone(self.location.resolver_timeout)
        self.assertEqual('30s', self.location.resolver_timeout)

    def test_root_extraction(self):
        self.assertIsNotNone(self.location.root)
        self.assertEqual('/var/www/html', self.location.root)

        self._update_directive('root /var/www/html;', '')
        self.assertIsNotNone(self.location.root)
        self.assertEqual('html', self.location.root)

    def test_satisfy_extraction(self):
        self.assertIsNotNone(self.location.satisfy)
        self.assertEqual('any', self.location.satisfy)

        self._update_directive('satisfy any;', 'satisfy all;')
        self.assertEqual('all', self.location.satisfy)

        self._update_directive('satisfy all;', '')
        self.assertIsNotNone(self.location.satisfy)
        self.assertEqual('all', self.location.satisfy)

    def test_send_lowat_extraction(self):
        self.assertIsNotNone(self.location.send_lowat)
        self.assertEqual('14m', self.location.send_lowat)

        self._update_directive('send_lowat 14m;', '')
        self.assertIsNotNone(self.location.send_lowat)
        self.assertEqual('0', self.location.send_lowat)

    def test_send_timeout_extraction(self):
        self.assertIsNotNone(self.location.send_timeout)
        self.assertEqual('54s', self.location.send_timeout)

        self._update_directive('send_timeout 54s;', '')
        self.assertIsNotNone(self.location.send_timeout)
        self.assertEqual('60s', self.location.send_timeout)

    def test_sendfile_extraction(self):
        self.assertIsNotNone(self.location.sendfile)
        self.assertEqual('on', self.location.sendfile)

        self._update_directive('sendfile on;', 'sendfile off;')
        self.assertEqual('off', self.location.sendfile)

        self._update_directive('sendfile off;', '')
        self.assertIsNotNone(self.location.sendfile)
        self.assertEqual('off', self.location.sendfile)

    def test_sendfile_max_chunk_extraction(self):
        self.assertIsNotNone(self.location.sendfile_max_chunk)
        self.assertEqual('15m', self.location.sendfile_max_chunk)

        self._update_directive('sendfile_max_chunk 15m;', '')
        self.assertIsNotNone(self.location.sendfile_max_chunk)
        self.assertEqual('0', self.location.sendfile_max_chunk)

    def test_server_name_in_redirect_extraction(self):
        self.assertIsNotNone(self.location.server_name_in_redirect)
        self.assertEqual('on', self.location.server_name_in_redirect)

        self._update_directive('server_name_in_redirect on;', 'server_name_in_redirect off;')
        self.assertEqual('off', self.location.server_name_in_redirect)

        self._update_directive('server_name_in_redirect off;', '')
        self.assertEqual('off', self.location.server_name_in_redirect)

    def test_server_tokens_extraction(self):
        self.assertIsNotNone(self.location.server_tokens)
        self.assertEqual('build', self.location.server_tokens)

        self._update_directive('server_tokens build;', 'server_tokens on;')
        self.assertEqual('on', self.location.server_tokens)

        self._update_directive('server_tokens on;', 'server_tokens off;')
        self.assertEqual('off', self.location.server_tokens)

        self._update_directive('server_tokens off;', 'server_tokens $variable;')
        self.assertEqual('$variable', self.location.server_tokens)

        self._update_directive('server_tokens $variable;', '')
        self.assertEqual('on', self.location.server_tokens)

    def test_subrequest_output_buffer_size_extraction(self):
        self.assertIsNotNone(self.location.subrequest_output_buffer_size)
        self.assertEqual('9k', self.location.subrequest_output_buffer_size)

        self._update_directive('subrequest_output_buffer_size 9k;', '')
        self.assertEqual('4k|8k', self.location.subrequest_output_buffer_size)

    def test_tcp_nodelay_extraction(self):
        self.assertIsNotNone(self.location.tcp_nodelay)
        self.assertEqual('off', self.location.tcp_nodelay)

        self._update_directive('tcp_nodelay off;', 'tcp_nodelay on;')
        self.assertEqual('on', self.location.tcp_nodelay)

        self._update_directive('tcp_nodelay on;', '')
        self.assertEqual('on', self.location.tcp_nodelay)

    def test_tcp_nopush_extraction(self):
        self.assertIsNotNone(self.location.tcp_nopush)
        self.assertEqual('off', self.location.tcp_nopush)

        self._update_directive('tcp_nopush off;', 'tcp_nopush on;')
        self.assertEqual('on', self.location.tcp_nopush)

        self._update_directive('tcp_nopush on;', '')
        self.assertIsNotNone(self.location.tcp_nopush)
        self.assertEqual('off', self.location.tcp_nopush)

    def test_try_files_extraction(self):
        self.assertIsNotNone(self.location.try_files)
        self.assertIsInstance(self.location.try_files, list)
        self.assertEqual(4, len(self.location.try_files), self.location.try_files)
        self.assertEqual('$uri $uri/index.html $uri.html =404'.split(' '), self.location.try_files)

        self._update_directive('try_files $uri $uri/index.html $uri.html =404;', 'try_files /home/user/index.html;')
        self.assertIsInstance(self.location.try_files, str)
        self.assertEqual('/home/user/index.html', self.location.try_files)

        self._update_directive('try_files /home/user/index.html;', '')
        self.assertIsNone(self.location.try_files)

    def test_types_extraction(self):
        self.assertIsNotNone(self.location.types)
        self.assertIsInstance(self.location.types, dict)
        self.assertEqual(5, len(self.location.types.keys()))
        self.assertEqual({'bin', 'exe', 'dll', 'deb', 'dmg'}, set(self.location.types.keys()))
        for _ in ['bin', 'exe', 'dll', 'deb', 'dmg']:
            self.assertEqual('application/octet-stream', self.location.types[_])

    def test_types_hash_bucket_size_extraction(self):
        self.assertIsNotNone(self.location.types_hash_bucket_size)
        self.assertEqual('14m', self.location.types_hash_bucket_size)

        self._update_directive('types_hash_bucket_size 14m;', '')
        self.assertIsNotNone(self.location.types_hash_bucket_size)
        self.assertEqual('64', self.location.types_hash_bucket_size)

    def test_types_hash_max_size_extraction(self):
        self.assertIsNotNone(self.location.types_hash_max_size)
        self.assertEqual('512', self.location.types_hash_max_size)

        self._update_directive('types_hash_max_size 512;', '')
        self.assertIsNotNone(self.location.types_hash_max_size)
        self.assertEqual('1024', self.location.types_hash_max_size)


if __name__ == '__main__':
    unittest.main()
