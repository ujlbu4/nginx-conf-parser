# coding=utf-8
import unittest
from nginx_conf_parser.http_context import HttpContext


class HttpContextTest(unittest.TestCase):
    def setUp(self):
        self.context_string = """
        http {
            server {
                absolute_redirect on;
                location = /test {
                    absolute_redirect on;
                    proxy_pass http://login.example2.com; 
                } 
            }
            
            server {
                absolute_redirect on;
                location = /test2 {
                    absolute_redirect on;
                    proxy_pass http://login.example3.com; 
                }
            }
            
            server {
                absolute_redirect off;
                location = /test3 {
                    absolute_redirect off;
                    proxy_pass http://login.example2.com;
                }
            }
            
            types {
                application/octet-stream bin exe dll;
                application/octet-stream deb;
                application/octet-stream dmg;
            }
            
            absolute_redirect on;
            aio on;
            aio_write on;
            chunked_transfer_encoding off;
            client_body_buffer_size 82k;
            client_body_in_file_only clean;
            client_body_in_single_buffer on;
            client_body_temp_path /spool/nginx/client_temp 1 2;
            client_body_timeout 1h;
            client_header_buffer_size 10k;
            client_header_timeout 2h;
            client_max_body_size 25m;
            connection_pool_size 12m;
            default_type application/json;
            directio 4m;
            directio_alignment 445m;
            disable_symlinks if_not_owner from=$document_root;
            error_page 500 502 =200 503 504 /50x.html;
            etag off;
            if_modified_since before;
            ignore_invalid_headers off;
            keepalive_disable safari;
            keepalive_requests 200;
            keepalive_timeout 75s 34s;
            large_client_header_buffers 3 9k;
            limit_rate_after 500k;
            limit_rate 4k;
            lingering_close on;
            lingering_time 34s;
            lingering_timeout 8s;
            log_not_found off;
            log_subrequest on;
            max_ranges 32;
            merge_slashes off;
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
            request_pool_size 62k;
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
            server_names_hash_bucket_size 512;
            server_names_hash_max_size 1024;
            server_tokens build;
            subrequest_output_buffer_size 9k;
            tcp_nodelay off;
            tcp_nopush off;
            types_hash_bucket_size 14m;
            types_hash_max_size 512;
            underscores_in_headers off;
            variables_hash_bucket_size 128;
            variables_hash_max_size 2048;
        }
        """
        self.http = HttpContext(self.context_string)

    def _update_directive(self, initial, new):
        self.context_string = self.context_string.replace(initial, new)
        self.http = HttpContext(self.context_string)

    def test_absolute_redirect_extraction(self):
        self.assertIsNotNone(self.http.absolute_redirect)
        self.assertEqual('on', self.http.absolute_redirect)

        self._update_directive('absolute_redirect on;', '')
        self.assertIsNotNone(self.http.absolute_redirect)
        self.assertEqual('off', self.http.absolute_redirect)

    def test_aio_extraction(self):
        self.assertIsNotNone(self.http.aio)
        self.assertEqual('on', self.http.aio)

        self._update_directive('aio on;', 'aio off;')
        self.assertEqual('off', self.http.aio)

        self._update_directive('aio off;', 'aio threads;')
        self.assertIsInstance(self.http.aio, dict)
        self.assertIn('threads', self.http.aio.keys())
        self.assertIn('pool', self.http.aio.keys())
        self.assertTrue(self.http.aio.get('threads'))
        self.assertIsNone(self.http.aio.get('pool'))

        self._update_directive('aio threads;', 'aio threads=pool$disk;')
        self.assertEqual('pool$disk', self.http.aio.get('pool'))

        self._update_directive('aio threads=pool$disk;', '')
        self.assertIsNotNone(self.http.aio)
        self.assertEqual('off', self.http.aio)

    def test_aio_write_extraction(self):
        self.assertIsNotNone(self.http.aio_write)
        self.assertEqual('on', self.http.aio_write)

        self._update_directive('aio_write on;', 'aio_write off;')
        self.assertEqual('off', self.http.aio_write)

        self._update_directive('aio_write off;', '')
        self.assertIsNotNone(self.http.aio_write)
        self.assertEqual('off', self.http.aio_write)

    def test_chunked_transfer_encoding_extraction(self):
        self.assertIsNotNone(self.http.chunked_transfer_encoding)
        self.assertEqual('off', self.http.chunked_transfer_encoding)

        self._update_directive('chunked_transfer_encoding off;', 'chunked_transfer_encoding on;')
        self.assertEqual('on', self.http.chunked_transfer_encoding)

        self._update_directive('chunked_transfer_encoding on;', '')
        self.assertIsNotNone(self.http.chunked_transfer_encoding)
        self.assertEqual('on', self.http.chunked_transfer_encoding)

    def test_client_body_buffer_size_extraction(self):
        self.assertIsNotNone(self.http.client_body_buffer_size)
        self.assertEqual('82k', self.http.client_body_buffer_size)

        self._update_directive('client_body_buffer_size 82k;', '')
        self.assertIsNotNone(self.http.client_body_buffer_size)
        self.assertEqual('8k|16k', self.http.client_body_buffer_size)

    def test_client_body_in_file_only_extraction(self):
        self.assertIsNotNone(self.http.client_body_in_file_only)
        self.assertEqual('clean', self.http.client_body_in_file_only)

        self._update_directive('client_body_in_file_only clean;', 'client_body_in_file_only on;')
        self.assertEqual('on', self.http.client_body_in_file_only)

        self._update_directive('client_body_in_file_only on;', 'client_body_in_file_only off;')
        self.assertEqual('off', self.http.client_body_in_file_only)

        self._update_directive('client_body_in_file_only off;', '')
        self.assertIsNotNone(self.http.client_body_in_file_only)
        self.assertEqual('off', self.http.client_body_in_file_only)

    def test_client_body_in_single_buffer_extraction(self):
        self.assertIsNotNone(self.http.client_body_in_single_buffer)
        self.assertEqual('on', self.http.client_body_in_single_buffer)

        self._update_directive('client_body_in_single_buffer on;', 'client_body_in_single_buffer off;')
        self.assertEqual('off', self.http.client_body_in_single_buffer)

        self._update_directive('client_body_in_single_buffer off;', '')
        self.assertIsNotNone(self.http.client_body_in_single_buffer)
        self.assertEqual('off', self.http.client_body_in_single_buffer)

    def test_client_body_temp_path_extraction(self):
        self.assertIsNotNone(self.http.client_body_temp_path)
        self.assertIsInstance(self.http.client_body_temp_path, dict)
        self.assertIn('path', self.http.client_body_temp_path.keys())
        self.assertIn('level1', self.http.client_body_temp_path.keys())
        self.assertIn('level2', self.http.client_body_temp_path.keys())
        self.assertIn('level3', self.http.client_body_temp_path.keys())

        self.assertEqual('/spool/nginx/client_temp', self.http.client_body_temp_path.get('path'))
        self.assertIsNotNone(self.http.client_body_temp_path.get('level1'))
        self.assertEqual('1', self.http.client_body_temp_path.get('level1'))

        self.assertIsNotNone(self.http.client_body_temp_path.get('level2'))
        self.assertEqual('2', self.http.client_body_temp_path.get('level2'))

        self.assertIsNone(self.http.client_body_temp_path.get('level3'))

        self._update_directive(
            'client_body_temp_path /spool/nginx/client_temp 1 2;',
            'client_body_temp_path /spool/nginx/client_temp 1 2 3;'
        )
        self.assertIsNotNone(self.http.client_body_temp_path.get('level3'))
        self.assertEqual('3', self.http.client_body_temp_path.get('level3'))

        self._update_directive(
            'client_body_temp_path /spool/nginx/client_temp 1 2 3;',
            'client_body_temp_path /spool/nginx/client_temp 1;'
        )
        self.assertIsNone(self.http.client_body_temp_path.get('level2'))
        self.assertIsNone(self.http.client_body_temp_path.get('level3'))

        self._update_directive(
            'client_body_temp_path /spool/nginx/client_temp 1;',
            'client_body_temp_path /spool/nginx/client_temp;'
        )
        self.assertIsNone(self.http.client_body_temp_path.get('level1'))
        self.assertIsNone(self.http.client_body_temp_path.get('level2'))
        self.assertIsNone(self.http.client_body_temp_path.get('level3'))

        self._update_directive(
            'client_body_temp_path /spool/nginx/client_temp;',
            ''
        )
        self.assertIsNotNone(self.http.client_body_temp_path)
        self.assertEqual('client_body_temp', self.http.client_body_temp_path.get('path'))
        self.assertIsNone(self.http.client_body_temp_path.get('level1'))
        self.assertIsNone(self.http.client_body_temp_path.get('level2'))
        self.assertIsNone(self.http.client_body_temp_path.get('level3'))

    def test_client_body_timeout_extraction(self):
        self.assertIsNotNone(self.http.client_body_timeout)
        self.assertEqual('1h', self.http.client_body_timeout)

        self._update_directive('client_body_timeout 1h;', '')
        self.assertIsNotNone(self.http.client_body_timeout)
        self.assertEqual('60s', self.http.client_body_timeout)

    def test_client_header_buffer_size_extraction(self):
        self.assertIsNotNone(self.http.client_header_buffer_size)
        self.assertEqual('10k', self.http.client_header_buffer_size)

        self._update_directive('client_header_buffer_size 10k;', '')
        self.assertIsNotNone(self.http.client_header_buffer_size)
        self.assertEqual('1k', self.http.client_header_buffer_size)

    def test_client_header_timemout(self):
        self.assertIsNotNone(self.http.client_header_timeout)
        self.assertEqual('2h', self.http.client_header_timeout)

        self._update_directive('client_header_timeout 2h;', '')
        self.assertIsNotNone(self.http.client_header_timeout)
        self.assertEqual('60s', self.http.client_header_timeout)

    def test_client_max_body_size_extraction(self):
        self.assertIsNotNone(self.http.client_max_body_size)
        self.assertEqual('25m', self.http.client_max_body_size)

        self._update_directive('client_max_body_size 25m;', '')
        self.assertIsNotNone(self.http.client_max_body_size)
        self.assertEqual('1m', self.http.client_max_body_size)

    def test_connection_pool_size_extraction(self):
        self.assertIsNotNone(self.http.connection_pool_size)
        self.assertEqual('12m', self.http.connection_pool_size)

        self._update_directive('connection_pool_size 12m;', '')
        self.assertIsNotNone(self.http.connection_pool_size)
        self.assertEqual('256|512', self.http.connection_pool_size)

    def test_default_type_extraction(self):
        self.assertIsNotNone(self.http.default_type)
        self.assertEqual('application/json', self.http.default_type)

        self._update_directive('default_type application/json;', '')
        self.assertIsNotNone(self.http.default_type)
        self.assertEqual('text/plain', self.http.default_type)

    def test_directio_extracion(self):
        self.assertIsNotNone(self.http.directio)
        self.assertEqual('4m', self.http.directio)

        self._update_directive('directio 4m;', 'directio off;')
        self.assertEqual('off', self.http.directio)

        self._update_directive('directio off;', '')
        self.assertIsNotNone(self.http.directio)
        self.assertEqual('off', self.http.directio)

    def test_directio_alignment_extraction(self):
        self.assertIsNotNone(self.http.directio_alignment)
        self.assertEqual('445m', self.http.directio_alignment)

        self._update_directive('directio_alignment 445m;', '')
        self.assertEqual('512', self.http.directio_alignment)

    def test_disable_symlinks_extraction(self):
        self.assertIsNotNone(self.http.disable_symlinks)
        self.assertIsInstance(self.http.disable_symlinks, dict)
        self.assertIn('value', self.http.disable_symlinks.keys())
        self.assertIn('_from', self.http.disable_symlinks.keys())
        self.assertEqual('if_not_owner', self.http.disable_symlinks.get('value'))
        self.assertEqual('$document_root', self.http.disable_symlinks.get('_from'))

        self._update_directive('disable_symlinks if_not_owner from=$document_root;', 'disable_symlinks if_not_owner;')
        self.assertIsNone(self.http.disable_symlinks.get('_from'))

        self._update_directive('disable_symlinks if_not_owner;', 'disable_symlinks on;')
        self.assertIsInstance(self.http.disable_symlinks, dict)
        self.assertIn('value', self.http.disable_symlinks.keys())
        self.assertIn('_from', self.http.disable_symlinks.keys())
        self.assertEqual('on', self.http.disable_symlinks.get('value'))
        self.assertIsNone(self.http.disable_symlinks.get('_from'))

        self._update_directive('disable_symlinks on;', 'disable_symlinks on from=$document_root;')
        self.assertIsNotNone(self.http.disable_symlinks.get('_from'))
        self.assertEqual('$document_root', self.http.disable_symlinks.get('_from'))

        self._update_directive('disable_symlinks on from=$document_root', 'disable_symlinks off;')
        self.assertNotIsInstance(self.http.disable_symlinks, dict)
        self.assertEqual('off', self.http.disable_symlinks)

        self._update_directive('disable_symlinks off;', '')
        self.assertIsNotNone(self.http.disable_symlinks)
        self.assertEqual('off', self.http.disable_symlinks)

    def test_error_page_extraction(self):
        self.assertIsNotNone(self.http.error_page)
        self.assertIsInstance(self.http.error_page, dict)
        self.assertEqual('/50x.html', self.http.error_page.get('uri'))
        self.assertEqual('500 502 =200 503 504', self.http.error_page.get('codes'))

        self._update_directive('error_page 500 502 =200 503 504 /50x.html;', '')
        self.assertIsNone(self.http.error_page)

    def test_etag_extraction(self):
        self.assertIsNotNone(self.http.etag)
        self.assertEqual('off', self.http.etag)

        self._update_directive('etag off;', 'etag on;')
        self.assertEqual('on', self.http.etag)

        self._update_directive('etag on;', '')
        self.assertIsNotNone(self.http.etag)
        self.assertEqual('on', self.http.etag)

    def test_if_modified_since_extraction(self):
        self.assertIsNotNone(self.http.if_modified_since)
        self.assertEqual('before', self.http.if_modified_since)

        self._update_directive('if_modified_since before;', 'if_modified_since exact;')
        self.assertEqual('exact', self.http.if_modified_since)

        self._update_directive('if_modified_since exact;', 'if_modified_since off;')
        self.assertEqual('off', self.http.if_modified_since)

        self._update_directive('if_modified_since off;', '')
        self.assertIsNotNone(self.http.if_modified_since)
        self.assertEqual('exact', self.http.if_modified_since)

    def test_ignore_invalid_headers_extraction(self):
        self.assertIsNotNone(self.http.ignore_invalid_headers)
        self.assertEqual('off', self.http.ignore_invalid_headers)

        self._update_directive('ignore_invalid_headers off;', 'ignore_invalid_headers on;')
        self.assertEqual('on', self.http.ignore_invalid_headers)

        self._update_directive('ignore_invalid_headers on;', '')
        self.assertIsNotNone(self.http.ignore_invalid_headers)
        self.assertEqual('on', self.http.ignore_invalid_headers)

    def test_keepalive_disable_extraction(self):
        self.assertIsNotNone(self.http.keepalive_disable)
        self.assertEqual('safari', self.http.keepalive_disable)

        self._update_directive('keepalive_disable safari;', '')
        self.assertIsNotNone(self.http.keepalive_disable)
        self.assertEqual('msie6', self.http.keepalive_disable)

    def test_keepalive_requests_extraction(self):
        self.assertIsNotNone(self.http.keepalive_requests)
        self.assertEqual(200, self.http.keepalive_requests)

        self._update_directive('keepalive_requests 200;', '')
        self.assertIsNotNone(self.http.keepalive_requests)
        self.assertEqual(100, self.http.keepalive_requests)

    def test_keepalive_timeout_extraction(self):
        self.assertIsNotNone(self.http.keepalive_timeout)
        self.assertIsInstance(self.http.keepalive_timeout, dict)
        self.assertIn('timeout', self.http.keepalive_timeout.keys())
        self.assertIn('header_timeout', self.http.keepalive_timeout.keys())
        self.assertEqual('75s', self.http.keepalive_timeout.get('timeout'))
        self.assertEqual('34s', self.http.keepalive_timeout.get('header_timeout'))

        self._update_directive('keepalive_timeout 75s 34s;', 'keepalive_timeout 76s;')
        self.assertIsInstance(self.http.keepalive_timeout, dict)
        self.assertIn('timeout', self.http.keepalive_timeout.keys())
        self.assertIn('header_timeout', self.http.keepalive_timeout.keys())
        self.assertEqual('76s', self.http.keepalive_timeout.get('timeout'))
        self.assertIsNone(self.http.keepalive_timeout.get('header_timeout'))

        self._update_directive('keepalive_timeout 76s;', '')
        self.assertIsNotNone(self.http.keepalive_timeout)
        self.assertIsInstance(self.http.keepalive_timeout, dict)
        self.assertIn('timeout', self.http.keepalive_timeout.keys())
        self.assertIn('header_timeout', self.http.keepalive_timeout.keys())
        self.assertEqual('75s', self.http.keepalive_timeout.get('timeout'))
        self.assertIsNone(self.http.keepalive_timeout.get('header_timeout'))

    def test_large_client_header_buffers_extraction(self):
        self.assertIsNotNone(self.http.large_client_header_buffers)
        self.assertIsInstance(self.http.large_client_header_buffers, dict)
        self.assertIn('number', self.http.large_client_header_buffers.keys())
        self.assertIn('size', self.http.large_client_header_buffers.keys())

        self.assertEqual(3, self.http.large_client_header_buffers.get('number'))
        self.assertEqual('9k', self.http.large_client_header_buffers.get('size'))

        self._update_directive('large_client_header_buffers 3 9k;', '')
        self.assertIsNotNone(self.http.large_client_header_buffers)
        self.assertIsInstance(self.http.large_client_header_buffers, dict)
        self.assertIn('number', self.http.large_client_header_buffers.keys())
        self.assertIn('size', self.http.large_client_header_buffers.keys())
        self.assertEqual(4, self.http.large_client_header_buffers.get('number'))
        self.assertEqual('8k', self.http.large_client_header_buffers.get('size'))

    def test_limit_rate_extraction(self):
        self.assertIsNotNone(self.http.limit_rate)
        self.assertEqual('4k', self.http.limit_rate)

        self._update_directive('limit_rate 4k;', '')
        self.assertIsNotNone(self.http.limit_rate)
        self.assertEqual('0', self.http.limit_rate)

    def test_limit_rate_after_extraction(self):
        self.assertIsNotNone(self.http.limit_rate_after)
        self.assertEqual('500k', self.http.limit_rate_after)

        self._update_directive('limit_rate_after 500k;', '')
        self.assertIsNotNone(self.http.limit_rate_after)
        self.assertEqual('0', self.http.limit_rate_after)

    def test_lingering_close_extraction(self):
        self.assertIsNotNone(self.http.lingering_close)
        self.assertEqual('on', self.http.lingering_close)

        self._update_directive('lingering_close on;', 'lingering_close off;')
        self.assertEqual('off', self.http.lingering_close)

        self._update_directive('lingering_close off;', 'lingering_close always;')
        self.assertEqual('always', self.http.lingering_close)

        self._update_directive('lingering_close always;', '')
        self.assertIsNotNone(self.http.lingering_close)
        self.assertEqual('on', self.http.lingering_close)

    def test_lingering_time_extraction(self):
        self.assertIsNotNone(self.http.lingering_time)
        self.assertEqual('34s', self.http.lingering_time)

        self._update_directive('lingering_time 34s;', '')
        self.assertIsNotNone(self.http.lingering_time)
        self.assertEqual('30s', self.http.lingering_time)

    def test_lingering_timeout_extraction(self):
        self.assertIsNotNone(self.http.lingering_timeout)
        self.assertEqual('8s', self.http.lingering_timeout)

        self._update_directive('lingering_timeout 8s;', '')
        self.assertIsNotNone(self.http.lingering_timeout)
        self.assertEqual('5s', self.http.lingering_timeout)

    def test_log_not_found_extraction(self):
        self.assertIsNotNone(self.http.log_not_found)
        self.assertEqual('off', self.http.log_not_found)

        self._update_directive('log_not_found off;', 'log_not_found on;')
        self.assertEqual('on', self.http.log_not_found)

        self._update_directive('log_not_found on;', '')
        self.assertIsNotNone(self.http.log_not_found)
        self.assertEqual('on', self.http.log_not_found)

    def test_log_subrequest_extraction(self):
        self.assertIsNotNone(self.http.log_subrequest)
        self.assertEqual('on', self.http.log_subrequest)

        self._update_directive('log_subrequest on;', 'log_subrequest off;')
        self.assertEqual('off', self.http.log_subrequest)

        self._update_directive('log_subrequest off;', '')
        self.assertIsNotNone(self.http.log_subrequest)
        self.assertEqual('off', self.http.log_subrequest)

    def test_max_ranges_extraction(self):
        self.assertIsNotNone(self.http.max_ranges)
        self.assertEqual(32, self.http.max_ranges)

        self._update_directive('max_ranges 32;', '')
        self.assertIsNone(self.http.max_ranges)

    def test_merge_slashes_extraction(self):
        self.assertIsNotNone(self.http.merge_slashes)
        self.assertEqual('off', self.http.merge_slashes)

        self._update_directive('merge_slashes off;', 'merge_slashes on;')
        self.assertEqual('on', self.http.merge_slashes)

        self._update_directive('merge_slashes on;', '')
        self.assertIsNotNone(self.http.merge_slashes)
        self.assertEqual('on', self.http.merge_slashes)

    def test_msie_padding_extraction(self):
        self.assertIsNotNone(self.http.msie_padding)
        self.assertEqual('off', self.http.msie_padding)

        self._update_directive('msie_padding off;', 'msie_padding on;')
        self.assertEqual('on', self.http.msie_padding)

        self._update_directive('msie_padding on;', '')
        self.assertIsNotNone(self.http.msie_padding)
        self.assertEqual('on', self.http.msie_padding)

    def test_msie_refresh_extraction(self):
        self.assertIsNotNone(self.http.msie_refresh)
        self.assertEqual('on', self.http.msie_refresh)

        self._update_directive('msie_refresh on;', 'msie_refresh off;')
        self.assertEqual('off', self.http.msie_refresh)

        self._update_directive('msie_refresh off;', '')
        self.assertIsNotNone(self.http.msie_refresh)
        self.assertEqual('off', self.http.msie_refresh)

    def test_open_file_cache_extraction(self):
        self.assertIsNotNone(self.http.open_file_cache)
        self.assertIsInstance(self.http.open_file_cache, dict)
        self.assertIn('max', self.http.open_file_cache.keys())
        self.assertIn('inactive', self.http.open_file_cache.keys())
        self.assertEqual(1000, self.http.open_file_cache.get('max'))
        self.assertEqual('20s', self.http.open_file_cache.get('inactive'))

        self._update_directive('open_file_cache max=1000 inactive=20s;', 'open_file_cache max=1000;')
        self.assertIsInstance(self.http.open_file_cache, dict)
        self.assertEqual(1000, self.http.open_file_cache.get('max'))
        self.assertIsNone(self.http.open_file_cache.get('inactive'))

        self._update_directive('open_file_cache max=1000;', 'open_file_cache off;')
        self.assertNotIsInstance(self.http.open_file_cache, dict)
        self.assertEqual('off', self.http.open_file_cache)

        self._update_directive('open_file_cache off;', '')
        self.assertIsNotNone(self.http.open_file_cache)
        self.assertEqual('off', self.http.open_file_cache)

    def test_open_file_cache_errors_extraction(self):
        self.assertIsNotNone(self.http.open_file_cache_errors)
        self.assertEqual('on', self.http.open_file_cache_errors)

        self._update_directive('open_file_cache_errors on;', 'open_file_cache_errors off;')
        self.assertEqual('off', self.http.open_file_cache_errors)

        self._update_directive('open_file_cache_errors off;', '')
        self.assertIsNotNone(self.http.open_file_cache_errors)
        self.assertEqual('off', self.http.open_file_cache_errors)

    def test_open_file_cache_min_uses_extraction(self):
        self.assertIsNotNone(self.http.open_file_cache_min_uses)
        self.assertEqual(2000, self.http.open_file_cache_min_uses)

        self._update_directive('open_file_cache_min_uses 2000;', '')
        self.assertIsNotNone(self.http.open_file_cache_min_uses)
        self.assertEqual(1, self.http.open_file_cache_min_uses)

    def test_open_file_cache_valid_extraction(self):
        self.assertIsNotNone(self.http.open_file_cache_valid)
        self.assertEqual('32s', self.http.open_file_cache_valid)

        self._update_directive('open_file_cache_valid 32s;', '')
        self.assertIsNotNone(self.http.open_file_cache_valid)
        self.assertEqual('60s', self.http.open_file_cache_valid)

    def test_output_buffers_extraction(self):
        self.assertIsNotNone(self.http.output_buffers)
        self.assertIsInstance(self.http.output_buffers, dict)
        self.assertIn('number', self.http.output_buffers.keys())
        self.assertIn('size', self.http.output_buffers.keys())
        self.assertEqual(4, self.http.output_buffers.get('number'))
        self.assertEqual('22k', self.http.output_buffers.get('size'))

        self._update_directive('output_buffers 4 22k;', '')
        self.assertIsNotNone(self.http.output_buffers)
        self.assertIsInstance(self.http.output_buffers, dict)
        self.assertIn('number', self.http.output_buffers.keys())
        self.assertIn('size', self.http.output_buffers.keys())
        self.assertEqual(2, self.http.output_buffers.get('number'))
        self.assertEqual('32k', self.http.output_buffers.get('size'))

    def test_port_in_redirect_extraction(self):
        self.assertIsNotNone(self.http.port_in_redirect)
        self.assertEqual('off', self.http.port_in_redirect)

        self._update_directive('port_in_redirect off;', 'port_in_redirect on;')
        self.assertEqual('on', self.http.port_in_redirect)

        self._update_directive('port_in_redirect on;', '')
        self.assertIsNotNone(self.http.port_in_redirect)
        self.assertEqual('on', self.http.port_in_redirect)

    def test_postpone_output_extraction(self):
        self.assertIsNotNone(self.http.postpone_output)
        self.assertEqual('1423', self.http.postpone_output)

        self._update_directive('postpone_output 1423;', '')
        self.assertIsNotNone(self.http.postpone_output)
        self.assertEqual('1460', self.http.postpone_output)

    def test_read_ahead_extraction(self):
        self.assertIsNotNone(self.http.read_ahead)
        self.assertEqual('14', self.http.read_ahead)

        self._update_directive('read_ahead 14;', '')
        self.assertIsNotNone(self.http.read_ahead)
        self.assertEqual('0', self.http.read_ahead)

    def test_recursive_error_pages_extraction(self):
        self.assertIsNotNone(self.http.recursive_error_pages)
        self.assertEqual('on', self.http.recursive_error_pages)

        self._update_directive('recursive_error_pages on;', 'recursive_error_pages off;')
        self.assertEqual('off', self.http.recursive_error_pages)

        self._update_directive('recursive_error_pages off;', '')
        self.assertIsNotNone(self.http.recursive_error_pages)
        self.assertEqual('off', self.http.recursive_error_pages)

    def test_request_pool_size_extraction(self):
        self.assertIsNotNone(self.http.request_pool_size)
        self.assertEqual('62k', self.http.request_pool_size)

        self._update_directive('request_pool_size 62k;', '')
        self.assertIsNotNone(self.http.request_pool_size)
        self.assertEqual('4k', self.http.request_pool_size)

    def test_reset_timedout_connection_extraction(self):
        self.assertIsNotNone(self.http.reset_timedout_connection)
        self.assertEqual('on', self.http.reset_timedout_connection)

        self._update_directive('reset_timedout_connection on;', 'reset_timedout_connection off;')
        self.assertEqual('off', self.http.reset_timedout_connection)

        self._update_directive('reset_timedout_connection off;', '')
        self.assertIsNotNone(self.http.reset_timedout_connection)
        self.assertEqual('off', self.http.reset_timedout_connection)

    def test_resolver_extraction(self):
        self.assertIsNotNone(self.http.resolver)
        self.assertIsInstance(self.http.resolver, dict)
        self.assertIn('address', self.http.resolver.keys())
        self.assertIn('valid', self.http.resolver.keys())
        self.assertIn('ipv6', self.http.resolver.keys())

        self.assertIsInstance(self.http.resolver.get('address'), list)
        self.assertIn('localhost:8080', self.http.resolver.get('address'))
        self.assertIn('192.168.1.1', self.http.resolver.get('address'))
        self.assertEqual('12s', self.http.resolver.get('valid'))
        self.assertEqual('on', self.http.resolver.get('ipv6'))

    def test_resolver_timeout_extraction(self):
        self.assertIsNotNone(self.http.resolver_timeout)
        self.assertEqual('54s', self.http.resolver_timeout)

        self._update_directive('resolver_timeout 54s;', '')
        self.assertIsNotNone(self.http.resolver_timeout)
        self.assertEqual('30s', self.http.resolver_timeout)

    def test_root_extraction(self):
        self.assertIsNotNone(self.http.root)
        self.assertEqual('/var/www/html', self.http.root)

        self._update_directive('root /var/www/html;', '')
        self.assertIsNotNone(self.http.root)
        self.assertEqual('html', self.http.root)

    def test_satisfy_extraction(self):
        self.assertIsNotNone(self.http.satisfy)
        self.assertEqual('any', self.http.satisfy)

        self._update_directive('satisfy any;', 'satisfy all;')
        self.assertEqual('all', self.http.satisfy)

        self._update_directive('satisfy all;', '')
        self.assertIsNotNone(self.http.satisfy)
        self.assertEqual('all', self.http.satisfy)

    def test_send_lowat_extraction(self):
        self.assertIsNotNone(self.http.send_lowat)
        self.assertEqual('14m', self.http.send_lowat)

        self._update_directive('send_lowat 14m;', '')
        self.assertIsNotNone(self.http.send_lowat)
        self.assertEqual('0', self.http.send_lowat)

    def test_send_timeout_extraction(self):
        self.assertIsNotNone(self.http.send_timeout)
        self.assertEqual('54s', self.http.send_timeout)

        self._update_directive('send_timeout 54s;', '')
        self.assertIsNotNone(self.http.send_timeout)
        self.assertEqual('60s', self.http.send_timeout)

    def test_sendfile_extraction(self):
        self.assertIsNotNone(self.http.sendfile)
        self.assertEqual('on', self.http.sendfile)

        self._update_directive('sendfile on;', 'sendfile off;')
        self.assertEqual('off', self.http.sendfile)

        self._update_directive('sendfile off;', '')
        self.assertIsNotNone(self.http.sendfile)
        self.assertEqual('off', self.http.sendfile)

    def test_sendfile_max_chunk_extraction(self):
        self.assertIsNotNone(self.http.sendfile_max_chunk)
        self.assertEqual('15m', self.http.sendfile_max_chunk)

        self._update_directive('sendfile_max_chunk 15m;', '')
        self.assertIsNotNone(self.http.sendfile_max_chunk)
        self.assertEqual('0', self.http.sendfile_max_chunk)

    def test_server_name_in_redirect_extraction(self):
        self.assertIsNotNone(self.http.server_name_in_redirect)
        self.assertEqual('on', self.http.server_name_in_redirect)

        self._update_directive('server_name_in_redirect on;', 'server_name_in_redirect off;')
        self.assertEqual('off', self.http.server_name_in_redirect)

        self._update_directive('server_name_in_redirect off;', '')
        self.assertEqual('off', self.http.server_name_in_redirect)

    def test_server_names_hash_bucket_size_extraction(self):
        self.assertIsNotNone(self.http.server_names_hash_bucket_size)
        self.assertEqual('512', self.http.server_names_hash_bucket_size)

    def test_server_names_hash_max_size_extraction(self):
        self.assertIsNotNone(self.http.server_names_hash_max_size)
        self.assertEqual('1024', self.http.server_names_hash_max_size)

    def test_server_tokens_extraction(self):
        self.assertIsNotNone(self.http.server_tokens)
        self.assertEqual('build', self.http.server_tokens)

        self._update_directive('server_tokens build;', 'server_tokens on;')
        self.assertEqual('on', self.http.server_tokens)

        self._update_directive('server_tokens on;', 'server_tokens off;')
        self.assertEqual('off', self.http.server_tokens)

        self._update_directive('server_tokens off;', 'server_tokens $variable;')
        self.assertEqual('$variable', self.http.server_tokens)

        self._update_directive('server_tokens $variable;', '')
        self.assertEqual('on', self.http.server_tokens)

    def test_subrequest_output_buffer_size_extraction(self):
        self.assertIsNotNone(self.http.subrequest_output_buffer_size)
        self.assertEqual('9k', self.http.subrequest_output_buffer_size)

        self._update_directive('subrequest_output_buffer_size 9k;', '')
        self.assertEqual('4k|8k', self.http.subrequest_output_buffer_size)

    def test_tcp_nodelay_extraction(self):
        self.assertIsNotNone(self.http.tcp_nodelay)
        self.assertEqual('off', self.http.tcp_nodelay)

        self._update_directive('tcp_nodelay off;', 'tcp_nodelay on;')
        self.assertEqual('on', self.http.tcp_nodelay)

        self._update_directive('tcp_nodelay on;', '')
        self.assertEqual('on', self.http.tcp_nodelay)

    def test_tcp_nopush_extraction(self):
        self.assertIsNotNone(self.http.tcp_nopush)
        self.assertEqual('off', self.http.tcp_nopush)

        self._update_directive('tcp_nopush off;', 'tcp_nopush on;')
        self.assertEqual('on', self.http.tcp_nopush)

        self._update_directive('tcp_nopush on;', '')
        self.assertIsNotNone(self.http.tcp_nopush)
        self.assertEqual('off', self.http.tcp_nopush)

    def test_types_extraction(self):
        self.assertIsNotNone(self.http.types)
        self.assertIsInstance(self.http.types, dict)
        self.assertEqual(5, len(self.http.types.keys()))
        self.assertEqual({'bin', 'exe', 'dll', 'deb', 'dmg'}, set(self.http.types.keys()))
        for _ in ['bin', 'exe', 'dll', 'deb', 'dmg']:
            self.assertEqual('application/octet-stream', self.http.types[_])

    def test_types_hash_bucket_size_extraction(self):
        self.assertIsNotNone(self.http.types_hash_bucket_size)
        self.assertEqual('14m', self.http.types_hash_bucket_size)

        self._update_directive('types_hash_bucket_size 14m;', '')
        self.assertIsNotNone(self.http.types_hash_bucket_size)
        self.assertEqual('64', self.http.types_hash_bucket_size)

    def test_types_hash_max_size_extraction(self):
        self.assertIsNotNone(self.http.types_hash_max_size)
        self.assertEqual('512', self.http.types_hash_max_size)

        self._update_directive('types_hash_max_size 512;', '')
        self.assertIsNotNone(self.http.types_hash_max_size)
        self.assertEqual('1024', self.http.types_hash_max_size)

    def test_underscores_in_headers_extraction(self):
        self.assertIsNotNone(self.http.underscores_in_headers)
        self.assertEqual('off', self.http.underscores_in_headers)

        self._update_directive('underscores_in_headers off;', 'underscores_in_headers on;')
        self.assertEqual('on', self.http.underscores_in_headers)

        self._update_directive('underscores_in_headers on;', '')
        self.assertIsNotNone(self.http.underscores_in_headers)
        self.assertEqual('off', self.http.underscores_in_headers)

    def test_variables_hash_bucket_size_extraction(self):
        self.assertIsNotNone(self.http.variables_hash_bucket_size)
        self.assertEqual('128', self.http.variables_hash_bucket_size)

        self._update_directive('variables_hash_bucket_size 128;', '')
        self.assertIsNotNone(self.http.variables_hash_bucket_size)
        self.assertEqual('64', self.http.variables_hash_bucket_size)

    def test_variables_hash_max_size_extraction(self):
        self.assertIsNotNone(self.http.variables_hash_max_size)
        self.assertEqual('2048', self.http.variables_hash_max_size)

        self._update_directive('variables_hash_max_size 2048;', '')
        self.assertIsNotNone(self.http.variables_hash_max_size)
        self.assertEqual('1024', self.http.variables_hash_max_size)


if __name__ == '__main__':
    unittest.main()
