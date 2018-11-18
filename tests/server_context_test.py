# coding=utf-8
import unittest

from nginx_conf_parser.server_context import ServerContext


class ServerContextTest(unittest.TestCase):
    def setUp(self):
        self.context_string = """
        server {
            location /test {
                aio on;
                aio_write on; 
            }
            location /test2 {
                aio off;
                aio_write off; 
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
            
            listen 127.0.0.1:8000 ssl http2 backlog=4 reuseport so_keepalive=on;
            listen 127.0.0.1 setfib=34 sndbuf=2k bind;
            listen 8000 default_server spdy accept_filter=dataready so_keepalive=off;
            listen *:8000 fastopen=32 rcvbuf=4k deferred;
            listen localhost:8000 proxy_protocol ipv6only=off so_keepalive=30m::10;
            
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
        }
        """
        self.server = ServerContext(self.context_string.replace('\n', ' '))

    def _update_directive(self, initial, new):
        self.context_string = self.context_string.replace(initial, new)
        self.server = ServerContext(self.context_string)

    def test_absolute_redirect_extraction(self):
        self.assertIsNotNone(self.server.absolute_redirect)
        self.assertEqual('on', self.server.absolute_redirect)

        self._update_directive('absolute_redirect on;', '')
        self.assertIsNotNone(self.server.absolute_redirect)
        self.assertEqual('off', self.server.absolute_redirect)

    def test_aio_extraction(self):
        self.assertIsNotNone(self.server.aio)
        self.assertEqual('on', self.server.aio)

        self._update_directive('aio on;', 'aio off;')
        self.assertEqual('off', self.server.aio)

        self._update_directive('aio off;', 'aio threads;')
        self.assertIsInstance(self.server.aio, dict)
        self.assertIn('threads', self.server.aio.keys())
        self.assertIn('pool', self.server.aio.keys())
        self.assertTrue(self.server.aio.get('threads'))
        self.assertIsNone(self.server.aio.get('pool'))

        self._update_directive('aio threads;', 'aio threads=pool$disk;')
        self.assertEqual('pool$disk', self.server.aio.get('pool'))

        self._update_directive('aio threads=pool$disk;', '')
        self.assertIsNotNone(self.server.aio)
        self.assertEqual('off', self.server.aio)

    def test_aio_write_extraction(self):
        self.assertIsNotNone(self.server.aio_write)
        self.assertEqual('on', self.server.aio_write)

        self._update_directive('aio_write on;', 'aio_write off;')
        self.assertEqual('off', self.server.aio_write)

        self._update_directive('aio_write off;', '')
        self.assertIsNotNone(self.server.aio_write)
        self.assertEqual('off', self.server.aio_write)

    def test_chunked_transfer_encoding_extraction(self):
        self.assertIsNotNone(self.server.chunked_transfer_encoding)
        self.assertEqual('off', self.server.chunked_transfer_encoding)

        self._update_directive('chunked_transfer_encoding off;', 'chunked_transfer_encoding on;')
        self.assertEqual('on', self.server.chunked_transfer_encoding)

        self._update_directive('chunked_transfer_encoding on;', '')
        self.assertIsNotNone(self.server.chunked_transfer_encoding)
        self.assertEqual('on', self.server.chunked_transfer_encoding)

    def test_client_body_buffer_size_extraction(self):
        self.assertIsNotNone(self.server.client_body_buffer_size)
        self.assertEqual('82k', self.server.client_body_buffer_size)

        self._update_directive('client_body_buffer_size 82k;', '')
        self.assertIsNotNone(self.server.client_body_buffer_size)
        self.assertEqual('8k|16k', self.server.client_body_buffer_size)

    def test_client_body_in_file_only_extraction(self):
        self.assertIsNotNone(self.server.client_body_in_file_only)
        self.assertEqual('clean', self.server.client_body_in_file_only)

        self._update_directive('client_body_in_file_only clean;', 'client_body_in_file_only on;')
        self.assertEqual('on', self.server.client_body_in_file_only)

        self._update_directive('client_body_in_file_only on;', 'client_body_in_file_only off;')
        self.assertEqual('off', self.server.client_body_in_file_only)

        self._update_directive('client_body_in_file_only off;', '')
        self.assertIsNotNone(self.server.client_body_in_file_only)
        self.assertEqual('off', self.server.client_body_in_file_only)

    def test_client_body_in_single_buffer_extraction(self):
        self.assertIsNotNone(self.server.client_body_in_single_buffer)
        self.assertEqual('on', self.server.client_body_in_single_buffer)

        self._update_directive('client_body_in_single_buffer on;', 'client_body_in_single_buffer off;')
        self.assertEqual('off', self.server.client_body_in_single_buffer)

        self._update_directive('client_body_in_single_buffer off;', '')
        self.assertIsNotNone(self.server.client_body_in_single_buffer)
        self.assertEqual('off', self.server.client_body_in_single_buffer)

    def test_client_body_temp_path_extraction(self):
        self.assertIsNotNone(self.server.client_body_temp_path)
        self.assertIsInstance(self.server.client_body_temp_path, dict)
        self.assertIn('path', self.server.client_body_temp_path.keys())
        self.assertIn('level1', self.server.client_body_temp_path.keys())
        self.assertIn('level2', self.server.client_body_temp_path.keys())
        self.assertIn('level3', self.server.client_body_temp_path.keys())

        self.assertEqual('/spool/nginx/client_temp', self.server.client_body_temp_path.get('path'))
        self.assertIsNotNone(self.server.client_body_temp_path.get('level1'))
        self.assertEqual('1', self.server.client_body_temp_path.get('level1'))

        self.assertIsNotNone(self.server.client_body_temp_path.get('level2'))
        self.assertEqual('2', self.server.client_body_temp_path.get('level2'))

        self.assertIsNone(self.server.client_body_temp_path.get('level3'))

        self._update_directive(
            'client_body_temp_path /spool/nginx/client_temp 1 2;',
            'client_body_temp_path /spool/nginx/client_temp 1 2 3;'
        )
        self.assertIsNotNone(self.server.client_body_temp_path.get('level3'))
        self.assertEqual('3', self.server.client_body_temp_path.get('level3'))

        self._update_directive(
            'client_body_temp_path /spool/nginx/client_temp 1 2 3;',
            'client_body_temp_path /spool/nginx/client_temp 1;'
        )
        self.assertIsNone(self.server.client_body_temp_path.get('level2'))
        self.assertIsNone(self.server.client_body_temp_path.get('level3'))

        self._update_directive(
            'client_body_temp_path /spool/nginx/client_temp 1;',
            'client_body_temp_path /spool/nginx/client_temp;'
        )
        self.assertIsNone(self.server.client_body_temp_path.get('level1'))
        self.assertIsNone(self.server.client_body_temp_path.get('level2'))
        self.assertIsNone(self.server.client_body_temp_path.get('level3'))

        self._update_directive(
            'client_body_temp_path /spool/nginx/client_temp;',
            ''
        )
        self.assertIsNotNone(self.server.client_body_temp_path)
        self.assertEqual('client_body_temp', self.server.client_body_temp_path.get('path'))
        self.assertIsNone(self.server.client_body_temp_path.get('level1'))
        self.assertIsNone(self.server.client_body_temp_path.get('level2'))
        self.assertIsNone(self.server.client_body_temp_path.get('level3'))

    def test_client_body_timeout_extraction(self):
        self.assertIsNotNone(self.server.client_body_timeout)
        self.assertEqual('1h', self.server.client_body_timeout)

        self._update_directive('client_body_timeout 1h;', '')
        self.assertIsNotNone(self.server.client_body_timeout)
        self.assertEqual('60s', self.server.client_body_timeout)

    def test_client_header_buffer_size_extraction(self):
        self.assertIsNotNone(self.server.client_header_buffer_size)
        self.assertEqual('10k', self.server.client_header_buffer_size)

        self._update_directive('client_header_buffer_size 10k;', '')
        self.assertIsNotNone(self.server.client_header_buffer_size)
        self.assertEqual('1k', self.server.client_header_buffer_size)

    def test_client_header_timemout(self):
        self.assertIsNotNone(self.server.client_header_timeout)
        self.assertEqual('2h', self.server.client_header_timeout)

        self._update_directive('client_header_timeout 2h;', '')
        self.assertIsNotNone(self.server.client_header_timeout)
        self.assertEqual('60s', self.server.client_header_timeout)

    def test_client_max_body_size_extraction(self):
        self.assertIsNotNone(self.server.client_max_body_size)
        self.assertEqual('25m', self.server.client_max_body_size)

        self._update_directive('client_max_body_size 25m;', '')
        self.assertIsNotNone(self.server.client_max_body_size)
        self.assertEqual('1m', self.server.client_max_body_size)

    def test_connection_pool_size_extraction(self):
        self.assertIsNotNone(self.server.connection_pool_size)
        self.assertEqual('12m', self.server.connection_pool_size)

        self._update_directive('connection_pool_size 12m;', '')
        self.assertIsNotNone(self.server.connection_pool_size)
        self.assertEqual('256|512', self.server.connection_pool_size)

    def test_default_type_extraction(self):
        self.assertIsNotNone(self.server.default_type)
        self.assertEqual('application/json', self.server.default_type)

        self._update_directive('default_type application/json;', '')
        self.assertIsNotNone(self.server.default_type)
        self.assertEqual('text/plain', self.server.default_type)

    def test_directio_extracion(self):
        self.assertIsNotNone(self.server.directio)
        self.assertEqual('4m', self.server.directio)

        self._update_directive('directio 4m;', 'directio off;')
        self.assertEqual('off', self.server.directio)

        self._update_directive('directio off;', '')
        self.assertIsNotNone(self.server.directio)
        self.assertEqual('off', self.server.directio)

    def test_directio_alignment_extraction(self):
        self.assertIsNotNone(self.server.directio_alignment)
        self.assertEqual('445m', self.server.directio_alignment)

        self._update_directive('directio_alignment 445m;', '')
        self.assertEqual('512', self.server.directio_alignment)

    def test_disable_symlinks_extraction(self):
        self.assertIsNotNone(self.server.disable_symlinks)
        self.assertIsInstance(self.server.disable_symlinks, dict)
        self.assertIn('value', self.server.disable_symlinks.keys())
        self.assertIn('_from', self.server.disable_symlinks.keys())
        self.assertEqual('if_not_owner', self.server.disable_symlinks.get('value'))
        self.assertEqual('$document_root', self.server.disable_symlinks.get('_from'))

        self._update_directive('disable_symlinks if_not_owner from=$document_root;', 'disable_symlinks if_not_owner;')
        self.assertIsNone(self.server.disable_symlinks.get('_from'))

        self._update_directive('disable_symlinks if_not_owner;', 'disable_symlinks on;')
        self.assertIsInstance(self.server.disable_symlinks, dict)
        self.assertIn('value', self.server.disable_symlinks.keys())
        self.assertIn('_from', self.server.disable_symlinks.keys())
        self.assertEqual('on', self.server.disable_symlinks.get('value'))
        self.assertIsNone(self.server.disable_symlinks.get('_from'))

        self._update_directive('disable_symlinks on;', 'disable_symlinks on from=$document_root;')
        self.assertIsNotNone(self.server.disable_symlinks.get('_from'))
        self.assertEqual('$document_root', self.server.disable_symlinks.get('_from'))

        self._update_directive('disable_symlinks on from=$document_root', 'disable_symlinks off;')
        self.assertNotIsInstance(self.server.disable_symlinks, dict)
        self.assertEqual('off', self.server.disable_symlinks)

        self._update_directive('disable_symlinks off;', '')
        self.assertIsNotNone(self.server.disable_symlinks)
        self.assertEqual('off', self.server.disable_symlinks)

    def test_error_page_extraction(self):
        self.assertIsNotNone(self.server.error_page)
        self.assertIsInstance(self.server.error_page, dict)
        self.assertEqual('/50x.html', self.server.error_page.get('uri'))
        self.assertEqual('500 502 =200 503 504', self.server.error_page.get('codes'))

        self._update_directive('error_page 500 502 =200 503 504 /50x.html;', '')
        self.assertIsNone(self.server.error_page)

    def test_etag_extraction(self):
        self.assertIsNotNone(self.server.etag)
        self.assertEqual('off', self.server.etag)

        self._update_directive('etag off;', 'etag on;')
        self.assertEqual('on', self.server.etag)

        self._update_directive('etag on;', '')
        self.assertIsNotNone(self.server.etag)
        self.assertEqual('on', self.server.etag)

    def test_if_modified_since_extraction(self):
        self.assertIsNotNone(self.server.if_modified_since)
        self.assertEqual('before', self.server.if_modified_since)

        self._update_directive('if_modified_since before;', 'if_modified_since exact;')
        self.assertEqual('exact', self.server.if_modified_since)

        self._update_directive('if_modified_since exact;', 'if_modified_since off;')
        self.assertEqual('off', self.server.if_modified_since)

        self._update_directive('if_modified_since off;', '')
        self.assertIsNotNone(self.server.if_modified_since)
        self.assertEqual('exact', self.server.if_modified_since)

    def test_ignore_invalid_headers_extraction(self):
        self.assertIsNotNone(self.server.ignore_invalid_headers)
        self.assertEqual('off', self.server.ignore_invalid_headers)

        self._update_directive('ignore_invalid_headers off;', 'ignore_invalid_headers on;')
        self.assertEqual('on', self.server.ignore_invalid_headers)

        self._update_directive('ignore_invalid_headers on;', '')
        self.assertIsNotNone(self.server.ignore_invalid_headers)
        self.assertEqual('on', self.server.ignore_invalid_headers)

    def test_keepalive_disable_extraction(self):
        self.assertIsNotNone(self.server.keepalive_disable)
        self.assertEqual('safari', self.server.keepalive_disable)

        self._update_directive('keepalive_disable safari;', '')
        self.assertIsNotNone(self.server.keepalive_disable)
        self.assertEqual('msie6', self.server.keepalive_disable)

    def test_keepalive_requests_extraction(self):
        self.assertIsNotNone(self.server.keepalive_requests)
        self.assertEqual(200, self.server.keepalive_requests)

        self._update_directive('keepalive_requests 200;', '')
        self.assertIsNotNone(self.server.keepalive_requests)
        self.assertEqual(100, self.server.keepalive_requests)

    def test_keepalive_timeout_extraction(self):
        self.assertIsNotNone(self.server.keepalive_timeout)
        self.assertIsInstance(self.server.keepalive_timeout, dict)
        self.assertIn('timeout', self.server.keepalive_timeout.keys())
        self.assertIn('header_timeout', self.server.keepalive_timeout.keys())
        self.assertEqual('75s', self.server.keepalive_timeout.get('timeout'))
        self.assertEqual('34s', self.server.keepalive_timeout.get('header_timeout'))

        self._update_directive('keepalive_timeout 75s 34s;', 'keepalive_timeout 76s;')
        self.assertIsInstance(self.server.keepalive_timeout, dict)
        self.assertIn('timeout', self.server.keepalive_timeout.keys())
        self.assertIn('header_timeout', self.server.keepalive_timeout.keys())
        self.assertEqual('76s', self.server.keepalive_timeout.get('timeout'))
        self.assertIsNone(self.server.keepalive_timeout.get('header_timeout'))

        self._update_directive('keepalive_timeout 76s;', '')
        self.assertIsNotNone(self.server.keepalive_timeout)
        self.assertIsInstance(self.server.keepalive_timeout, dict)
        self.assertIn('timeout', self.server.keepalive_timeout.keys())
        self.assertIn('header_timeout', self.server.keepalive_timeout.keys())
        self.assertEqual('75s', self.server.keepalive_timeout.get('timeout'))
        self.assertIsNone(self.server.keepalive_timeout.get('header_timeout'))

    def test_large_client_header_buffers_extraction(self):
        self.assertIsNotNone(self.server.large_client_header_buffers)
        self.assertIsInstance(self.server.large_client_header_buffers, dict)
        self.assertIn('number', self.server.large_client_header_buffers.keys())
        self.assertIn('size', self.server.large_client_header_buffers.keys())

        self.assertEqual(3, self.server.large_client_header_buffers.get('number'))
        self.assertEqual('9k', self.server.large_client_header_buffers.get('size'))

        self._update_directive('large_client_header_buffers 3 9k;', '')
        self.assertIsNotNone(self.server.large_client_header_buffers)
        self.assertIsInstance(self.server.large_client_header_buffers, dict)
        self.assertIn('number', self.server.large_client_header_buffers.keys())
        self.assertIn('size', self.server.large_client_header_buffers.keys())
        self.assertEqual(4, self.server.large_client_header_buffers.get('number'))
        self.assertEqual('8k', self.server.large_client_header_buffers.get('size'))

    def test_limit_rate_extraction(self):
        self.assertIsNotNone(self.server.limit_rate)
        self.assertEqual('4k', self.server.limit_rate)

        self._update_directive('limit_rate 4k;', '')
        self.assertIsNotNone(self.server.limit_rate)
        self.assertEqual('0', self.server.limit_rate)

    def test_limit_rate_after_extraction(self):
        self.assertIsNotNone(self.server.limit_rate_after)
        self.assertEqual('500k', self.server.limit_rate_after)

        self._update_directive('limit_rate_after 500k;', '')
        self.assertIsNotNone(self.server.limit_rate_after)
        self.assertEqual('0', self.server.limit_rate_after)

    def test_lingering_close_extraction(self):
        self.assertIsNotNone(self.server.lingering_close)
        self.assertEqual('on', self.server.lingering_close)

        self._update_directive('lingering_close on;', 'lingering_close off;')
        self.assertEqual('off', self.server.lingering_close)

        self._update_directive('lingering_close off;', 'lingering_close always;')
        self.assertEqual('always', self.server.lingering_close)

        self._update_directive('lingering_close always;', '')
        self.assertIsNotNone(self.server.lingering_close)
        self.assertEqual('on', self.server.lingering_close)

    def test_lingering_time_extraction(self):
        self.assertIsNotNone(self.server.lingering_time)
        self.assertEqual('34s', self.server.lingering_time)

        self._update_directive('lingering_time 34s;', '')
        self.assertIsNotNone(self.server.lingering_time)
        self.assertEqual('30s', self.server.lingering_time)

    def test_lingering_timeout_extraction(self):
        self.assertIsNotNone(self.server.lingering_timeout)
        self.assertEqual('8s', self.server.lingering_timeout)

        self._update_directive('lingering_timeout 8s;', '')
        self.assertIsNotNone(self.server.lingering_timeout)
        self.assertEqual('5s', self.server.lingering_timeout)

    def test_listen_extraction(self):
        self.assertIsInstance(self.server.listen, list)
        self.assertEqual(5, len(self.server.listen))

        self.assertEqual('127.0.0.1:8000', self.server.listen[0].get('value'))
        self.assertFalse(self.server.listen[0].get('default_server'))
        self.assertTrue(self.server.listen[0].get('ssl'))
        self.assertTrue(self.server.listen[0].get('http2'))
        self.assertFalse(self.server.listen[0].get('spdy'))
        self.assertFalse(self.server.listen[0].get('proxy_protocol'))
        self.assertIsNone(self.server.listen[0].get('setfib'))
        self.assertIsNone(self.server.listen[0].get('fastopen'))
        self.assertEqual(4, self.server.listen[0].get('backlog'))
        self.assertIsNone(self.server.listen[0].get('rcvbuf'))
        self.assertIsNone(self.server.listen[0].get('sndbuf'))
        self.assertIsNone(self.server.listen[0].get('accept_filter'))
        self.assertFalse(self.server.listen[0].get('deferred'))
        self.assertFalse(self.server.listen[0].get('bind'))
        self.assertEqual('on', self.server.listen[0].get('ipv6only'))
        self.assertTrue(self.server.listen[0].get('reuseport'))
        self.assertEqual('on', self.server.listen[0].get('so_keepalive'))

        self.assertEqual('127.0.0.1', self.server.listen[1].get('value'))
        self.assertFalse(self.server.listen[1].get('default_server'))
        self.assertFalse(self.server.listen[1].get('ssl'))
        self.assertFalse(self.server.listen[1].get('http2'))
        self.assertFalse(self.server.listen[1].get('spdy'))
        self.assertFalse(self.server.listen[1].get('proxy_protocol'))
        self.assertEqual(34, self.server.listen[1].get('setfib'))
        self.assertIsNone(self.server.listen[1].get('fastopen'))
        self.assertIsNone(self.server.listen[1].get('backlog'))
        self.assertIsNone(self.server.listen[1].get('rcvbuf'))
        self.assertEqual('2k', self.server.listen[1].get('sndbuf'))
        self.assertIsNone(self.server.listen[1].get('accept_filter'))
        self.assertFalse(self.server.listen[1].get('deferred'))
        self.assertTrue(self.server.listen[1].get('bind'))
        self.assertEqual('on', self.server.listen[1].get('ipv6only'))
        self.assertFalse(self.server.listen[1].get('reuseport'))
        self.assertIsNone(self.server.listen[1].get('so_keepalive'))

        self.assertEqual('8000', self.server.listen[2].get('value'))
        self.assertTrue(self.server.listen[2].get('default_server'))
        self.assertFalse(self.server.listen[2].get('ssl'))
        self.assertFalse(self.server.listen[2].get('http2'))
        self.assertTrue(self.server.listen[2].get('spdy'))
        self.assertFalse(self.server.listen[2].get('proxy_protocol'))
        self.assertIsNone(self.server.listen[2].get('setfib'))
        self.assertIsNone(self.server.listen[2].get('fastopen'))
        self.assertIsNone(self.server.listen[2].get('backlog'))
        self.assertIsNone(self.server.listen[2].get('rcvbuf'))
        self.assertIsNone(self.server.listen[2].get('sndbuf'))
        self.assertEqual('dataready', self.server.listen[2].get('accept_filter'))
        self.assertFalse(self.server.listen[2].get('deferred'))
        self.assertFalse(self.server.listen[2].get('bind'))
        self.assertEqual('on', self.server.listen[2].get('ipv6only'))
        self.assertFalse(self.server.listen[2].get('reuseport'))
        self.assertEqual('off', self.server.listen[2].get('so_keepalive'))

        self.assertEqual('*:8000', self.server.listen[3].get('value'))
        self.assertFalse(self.server.listen[3].get('default_server'))
        self.assertFalse(self.server.listen[3].get('ssl'))
        self.assertFalse(self.server.listen[3].get('http2'))
        self.assertFalse(self.server.listen[3].get('spdy'))
        self.assertFalse(self.server.listen[3].get('proxy_protocol'))
        self.assertIsNone(self.server.listen[3].get('setfib'))
        self.assertEqual(32, self.server.listen[3].get('fastopen'))
        self.assertIsNone(self.server.listen[3].get('backlog'))
        self.assertEqual('4k', self.server.listen[3].get('rcvbuf'))
        self.assertIsNone(self.server.listen[3].get('sndbuf'))
        self.assertIsNone(self.server.listen[3].get('accept_filter'))
        self.assertTrue(self.server.listen[3].get('deferred'))
        self.assertFalse(self.server.listen[3].get('bind'))
        self.assertEqual('on', self.server.listen[3].get('ipv6only'))
        self.assertFalse(self.server.listen[3].get('reuseport'))
        self.assertIsNone(self.server.listen[3].get('so_keepalive'))

        self.assertEqual('localhost:8000', self.server.listen[4].get('value'))
        self.assertFalse(self.server.listen[4].get('default_server'))
        self.assertFalse(self.server.listen[4].get('ssl'))
        self.assertFalse(self.server.listen[4].get('http2'))
        self.assertFalse(self.server.listen[4].get('spdy'))
        self.assertIsNone(self.server.listen[4].get('fastopen'))
        self.assertIsNone(self.server.listen[4].get('backlog'))
        self.assertTrue(self.server.listen[4].get('proxy_protocol'))
        self.assertIsNone(self.server.listen[4].get('setfib'))
        self.assertIsNone(self.server.listen[4].get('rcvbuf'))
        self.assertIsNone(self.server.listen[4].get('sndbuf'))
        self.assertIsNone(self.server.listen[4].get('accept_filter'))
        self.assertFalse(self.server.listen[4].get('deferred'))
        self.assertFalse(self.server.listen[4].get('bind'))
        self.assertEqual('off', self.server.listen[4].get('ipv6only'))
        self.assertFalse(self.server.listen[4].get('reuseport'))
        self.assertEqual('30m::10', self.server.listen[4].get('so_keepalive'))

    def test_log_not_found_extraction(self):
        self.assertIsNotNone(self.server.log_not_found)
        self.assertEqual('off', self.server.log_not_found)

        self._update_directive('log_not_found off;', 'log_not_found on;')
        self.assertEqual('on', self.server.log_not_found)

        self._update_directive('log_not_found on;', '')
        self.assertIsNotNone(self.server.log_not_found)
        self.assertEqual('on', self.server.log_not_found)

    def test_log_subrequest_extraction(self):
        self.assertIsNotNone(self.server.log_subrequest)
        self.assertEqual('on', self.server.log_subrequest)

        self._update_directive('log_subrequest on;', 'log_subrequest off;')
        self.assertEqual('off', self.server.log_subrequest)

        self._update_directive('log_subrequest off;', '')
        self.assertIsNotNone(self.server.log_subrequest)
        self.assertEqual('off', self.server.log_subrequest)

    def test_max_ranges_extraction(self):
        self.assertIsNotNone(self.server.max_ranges)
        self.assertEqual(32, self.server.max_ranges)

        self._update_directive('max_ranges 32;', '')
        self.assertIsNone(self.server.max_ranges)

    def test_merge_slashes_extraction(self):
        self.assertIsNotNone(self.server.merge_slashes)
        self.assertEqual('off', self.server.merge_slashes)

        self._update_directive('merge_slashes off;', 'merge_slashes on;')
        self.assertEqual('on', self.server.merge_slashes)

        self._update_directive('merge_slashes on;', '')
        self.assertIsNotNone(self.server.merge_slashes)
        self.assertEqual('on', self.server.merge_slashes)

    def test_msie_padding_extraction(self):
        self.assertIsNotNone(self.server.msie_padding)
        self.assertEqual('off', self.server.msie_padding)

        self._update_directive('msie_padding off;', 'msie_padding on;')
        self.assertEqual('on', self.server.msie_padding)

        self._update_directive('msie_padding on;', '')
        self.assertIsNotNone(self.server.msie_padding)
        self.assertEqual('on', self.server.msie_padding)

    def test_msie_refresh_extraction(self):
        self.assertIsNotNone(self.server.msie_refresh)
        self.assertEqual('on', self.server.msie_refresh)

        self._update_directive('msie_refresh on;', 'msie_refresh off;')
        self.assertEqual('off', self.server.msie_refresh)

        self._update_directive('msie_refresh off;', '')
        self.assertIsNotNone(self.server.msie_refresh)
        self.assertEqual('off', self.server.msie_refresh)

    def test_open_file_cache_extraction(self):
        self.assertIsNotNone(self.server.open_file_cache)
        self.assertIsInstance(self.server.open_file_cache, dict)
        self.assertIn('max', self.server.open_file_cache.keys())
        self.assertIn('inactive', self.server.open_file_cache.keys())
        self.assertEqual(1000, self.server.open_file_cache.get('max'))
        self.assertEqual('20s', self.server.open_file_cache.get('inactive'))

        self._update_directive('open_file_cache max=1000 inactive=20s;', 'open_file_cache max=1000;')
        self.assertIsInstance(self.server.open_file_cache, dict)
        self.assertEqual(1000, self.server.open_file_cache.get('max'))
        self.assertIsNone(self.server.open_file_cache.get('inactive'))

        self._update_directive('open_file_cache max=1000;', 'open_file_cache off;')
        self.assertNotIsInstance(self.server.open_file_cache, dict)
        self.assertEqual('off', self.server.open_file_cache)

        self._update_directive('open_file_cache off;', '')
        self.assertIsNotNone(self.server.open_file_cache)
        self.assertEqual('off', self.server.open_file_cache)

    def test_open_file_cache_errors_extraction(self):
        self.assertIsNotNone(self.server.open_file_cache_errors)
        self.assertEqual('on', self.server.open_file_cache_errors)

        self._update_directive('open_file_cache_errors on;', 'open_file_cache_errors off;')
        self.assertEqual('off', self.server.open_file_cache_errors)

        self._update_directive('open_file_cache_errors off;', '')
        self.assertIsNotNone(self.server.open_file_cache_errors)
        self.assertEqual('off', self.server.open_file_cache_errors)

    def test_open_file_cache_min_uses_extraction(self):
        self.assertIsNotNone(self.server.open_file_cache_min_uses)
        self.assertEqual(2000, self.server.open_file_cache_min_uses)

        self._update_directive('open_file_cache_min_uses 2000;', '')
        self.assertIsNotNone(self.server.open_file_cache_min_uses)
        self.assertEqual(1, self.server.open_file_cache_min_uses)

    def test_open_file_cache_valid_extraction(self):
        self.assertIsNotNone(self.server.open_file_cache_valid)
        self.assertEqual('32s', self.server.open_file_cache_valid)

        self._update_directive('open_file_cache_valid 32s;', '')
        self.assertIsNotNone(self.server.open_file_cache_valid)
        self.assertEqual('60s', self.server.open_file_cache_valid)

    def test_output_buffers_extraction(self):
        self.assertIsNotNone(self.server.output_buffers)
        self.assertIsInstance(self.server.output_buffers, dict)
        self.assertIn('number', self.server.output_buffers.keys())
        self.assertIn('size', self.server.output_buffers.keys())
        self.assertEqual(4, self.server.output_buffers.get('number'))
        self.assertEqual('22k', self.server.output_buffers.get('size'))

        self._update_directive('output_buffers 4 22k;', '')
        self.assertIsNotNone(self.server.output_buffers)
        self.assertIsInstance(self.server.output_buffers, dict)
        self.assertIn('number', self.server.output_buffers.keys())
        self.assertIn('size', self.server.output_buffers.keys())
        self.assertEqual(2, self.server.output_buffers.get('number'))
        self.assertEqual('32k', self.server.output_buffers.get('size'))

    def test_port_in_redirect_extraction(self):
        self.assertIsNotNone(self.server.port_in_redirect)
        self.assertEqual('off', self.server.port_in_redirect)

        self._update_directive('port_in_redirect off;', 'port_in_redirect on;')
        self.assertEqual('on', self.server.port_in_redirect)

        self._update_directive('port_in_redirect on;', '')
        self.assertIsNotNone(self.server.port_in_redirect)
        self.assertEqual('on', self.server.port_in_redirect)

    def test_postpone_output_extraction(self):
        self.assertIsNotNone(self.server.postpone_output)
        self.assertEqual('1423', self.server.postpone_output)

        self._update_directive('postpone_output 1423;', '')
        self.assertIsNotNone(self.server.postpone_output)
        self.assertEqual('1460', self.server.postpone_output)

    def test_read_ahead_extraction(self):
        self.assertIsNotNone(self.server.read_ahead)
        self.assertEqual('14', self.server.read_ahead)

        self._update_directive('read_ahead 14;', '')
        self.assertIsNotNone(self.server.read_ahead)
        self.assertEqual('0', self.server.read_ahead)

    def test_recursive_error_pages_extraction(self):
        self.assertIsNotNone(self.server.recursive_error_pages)
        self.assertEqual('on', self.server.recursive_error_pages)

        self._update_directive('recursive_error_pages on;', 'recursive_error_pages off;')
        self.assertEqual('off', self.server.recursive_error_pages)

        self._update_directive('recursive_error_pages off;', '')
        self.assertIsNotNone(self.server.recursive_error_pages)
        self.assertEqual('off', self.server.recursive_error_pages)

    def test_request_pool_size_extraction(self):
        self.assertIsNotNone(self.server.request_pool_size)
        self.assertEqual('62k', self.server.request_pool_size)

        self._update_directive('request_pool_size 62k;', '')
        self.assertIsNotNone(self.server.request_pool_size)
        self.assertEqual('4k', self.server.request_pool_size)


if __name__ == '__main__':
    unittest.main()