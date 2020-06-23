# coding=utf-8
import re
from typing import List

from .server_context import ServerContext
from .upstream_context import UpstreamContext
from .utils import extract_context


class HttpContext:
    """Extract http context from the given string"""
    servers: List[ServerContext] = []
    upstreams: List[UpstreamContext] = None
    absolute_redirect = None
    accept = None
    aio = None
    aio_write = None
    auth_jwt = None
    auth_jwt_claim_set = None
    auth_jwt_header_set = None
    auth_jwt_key_file = None
    auth_jwt_leeway = None
    chunked_transfer_encoding = None
    client_body_buffer_size = None
    client_body_in_file_only = None
    client_body_in_single_buffer = None
    client_body_temp_path = None
    client_body_timeout = None
    client_header_buffer_size = None
    client_header_timeout = None
    client_max_body_size = None
    connection_pool_size = None
    default_type = None
    deny = None
    directio = None
    directio_alignment = None
    disable_symlinks = None
    error_page = None
    etag = None
    if_modified_since = None
    ignore_invalid_headers = None
    keepalive_disable = None
    keepalive_requests = None
    keepalive_timeout = None
    large_client_header_buffers = None
    limit_rate = None
    limit_rate_after = None
    lingering_close = None
    lingering_time = None
    lingering_timeout = None
    log_not_found = None
    log_subrequest = None
    max_ranges = None
    merge_slashes = None
    msie_padding = None
    msie_refresh = None
    open_file_cache = None
    open_file_cache_errors = None
    open_file_cache_min_uses = None
    open_file_cache_valid = None
    output_buffers = None
    port_in_redirect = None
    postpone_output = None
    read_ahead = None
    recursive_error_pages = None
    request_pool_size = None
    reset_timedout_connection = None
    resolver = None
    resolver_timeout = None
    root = None
    satisfy = None
    send_lowat = None
    send_timeout = None
    sendfile = None
    sendfile_max_chunk = None
    server_name_in_redirect = None
    server_names_hash_bucket_size = None
    server_names_hash_max_size = None
    server_tokens = None
    subrequest_output_buffer_size = None
    tcp_nodelay = None
    tcp_nopush = None
    types = None
    types_hash_bucket_size = None
    types_hash_max_size = None
    underscores_in_headers = None
    variables_hash_bucket_size = None
    variables_hash_max_size = None

    def __init__(self, content):
        self._content = content.replace('\n', ' ')

        # extracting upstream
        upstreams = re.findall(r'\bupstream\s+([^{]*){([^}]*)', self._content)
        self.upstreams = []
        for upstream in upstreams:
            self.upstreams.append(UpstreamContext(upstream[0].strip(), upstream[1]))
        self._content = re.sub('\bupstream\s+[^{]*{[^}]*}', '', self._content)

        # extracting servers
        while extract_context(self._content, 'server') != '':
            server = extract_context(self._content, 'server')
            self.servers.append(ServerContext(server))
            self._content = self._content.replace(server, '')

        # accept directive
        self.accept = re.findall(r'accept\s+([^;]*)', self._content)
        self.accept = None if len(self.accept) == 0 else self.accept

        # absolute_redirect directive
        abs_redirect = re.search(r'absolute_redirect\s+(on|off);', self._content)
        self.absolute_redirect = abs_redirect.group(1) if abs_redirect else 'off'

        # aio directive
        aio = re.search(r'aio\s+(on|off|threads=?([^;]*)?)', self._content)
        self.aio = 'off'
        if aio:
            if aio.group(1) == 'on' or aio.group(1) == 'off':
                self.aio = aio.group(1)
            else:
                self.aio = dict(threads=True, pool=aio.group(2) if aio.group(2) else None)

        # aio_write directive
        awrite = re.search(r'aio_write\s+(on|off);', self._content)
        self.aio_write = awrite.group(1) if awrite else 'off'

        # auth_jwt directive
        auth_jwt = re.search(r'auth_jwt\s+([^;]*)', self._content)
        if not auth_jwt or auth_jwt.group(1) == 'off':
            self.auth_jwt = 'off'
        else:
            _ = re.search(r'"(.*)"\s*(token=(.*))?', auth_jwt.group(1))
            self.auth_jwt = dict(
                realm='"{0}"'.format(_.group(1)),
                token=_.group(3) if _.group(3) else None
            )

        # auth_jwt_claim_set directive
        auth_jwt_claim_set = re.findall(r'auth_jwt_claim_set\s+([^;]*)', self._content)
        if auth_jwt_claim_set:
            self.auth_jwt_claim_set = []
            for claim_set in auth_jwt_claim_set:
                reg = re.findall(r'([\w$\-_]+)|("[^"]*")', claim_set)
                self.auth_jwt_claim_set.append(dict(
                    variable=reg[0][0],
                    names=[_[0] if len(_[0]) != 0 else _[1] for _ in reg[1:]]
                ))

        # auth_jwt_header_set directive
        auth_jwt_header_set = re.findall(r'auth_jwt_header_set\s+([^;]*)', self._content)
        if auth_jwt_header_set:
            self.auth_jwt_header_set = []
            for claim_set in auth_jwt_header_set:
                reg = re.findall(r'([\w$\-_]+)|("[^"]*")', claim_set)
                self.auth_jwt_header_set.append(dict(
                    variable=reg[0][0],
                    names=[_[0] if len(_[0]) != 0 else _[1] for _ in reg[1:]]
                ))

        # auth_jwt_key_file directive
        auth_jwt_key_file = re.search(r'auth_jwt_key_file\s+([^;]*)', self._content)
        self.auth_jwt_key_file = auth_jwt_key_file.group(1) if auth_jwt_key_file else None

        # auth_jwt_leeway directive
        auth_jwt_leeway = re.search(r'auth_jwt_leeway\s+([^;]*)', self._content)
        self.auth_jwt_leeway = auth_jwt_leeway.group(1) if auth_jwt_leeway else '0s'

        # chunked_transfer_encoding directive
        cte = re.search(r'chunked_transfer_encoding\s+(on|off);', self._content)
        self.chunked_transfer_encoding = cte.group(1) if cte else 'on'

        # client_body_buffer_size directive
        cbbs = re.search(r'client_body_buffer_size\s+([^;]*)', self._content)
        self.client_body_buffer_size = cbbs.group(1) if cbbs else '8k|16k'

        # client_body_in_file_only directive
        cbif = re.search(r'client_body_in_file_only\s+(on|off|clean);', self._content)
        self.client_body_in_file_only = cbif.group(1) if cbif else 'off'

        # client_body_in_single_buffer directive
        cbisb = re.search(r'client_body_in_single_buffer\s+(on|off);', self._content)
        self.client_body_in_single_buffer = cbisb.group(1) if cbisb else 'off'

        # client_body_temp_path directive
        cbtp = re.search(r'client_body_temp_path\s*([\w/_]*)\s*([^;]*)', self._content)
        if cbtp:
            self.client_body_temp_path = dict(
                path=cbtp.group(1),
                level1=None,
                level2=None,
                level3=None
            )
            levels = re.findall(r'(\w*\s*)', cbtp.group(2)) if cbtp.group(2) else None
            if levels:
                for i in range(0, len(levels)):
                    if levels[i]:
                        self.client_body_temp_path.__setitem__('level{0}'.format(str(i + 1)), levels[i].strip())
        else:
            self.client_body_temp_path = dict(
                path='client_body_temp',
                level1=None,
                level2=None,
                level3=None
            )

        # client_body_timeout directive
        timeout = re.search(r'client_body_timeout\s+([^;]*)', self._content)
        self.client_body_timeout = timeout.group(1) if timeout else '60s'

        # client_header_buffer_size directive
        chbs = re.search(r'client_header_buffer_size\s+([^;]*)', self._content)
        self.client_header_buffer_size = chbs.group(1) if chbs else '1k'

        # client_header_timeout directive
        cht = re.search(r'client_header_timeout\s+([^;]*)', self._content)
        self.client_header_timeout = cht.group(1) if cht else '60s'

        # client_max_body_size directive
        cmbs = re.search(r'client_max_body_size\s+([^;]*)', self._content)
        self.client_max_body_size = cmbs.group(1) if cmbs else '1m'

        # connection_pool_size directive
        cps = re.search(r'connection_pool_size\s+([^;]*)', self._content)
        self.connection_pool_size = cps.group(1) if cps else '256|512'

        # default_type directive
        default_type = re.search(r'default_type\s+([^;]*)', self._content)
        self.default_type = default_type.group(1) if default_type else 'text/plain'

        # deny directive
        self.deny = re.findall(r'deny\s+([^;]*)', self._content)
        self.deny = None if len(self.deny) == 0 else self.deny

        # directio directive
        directio = re.search(r'directio\s+([^;]*)', self._content)
        self.directio = directio.group(1) if directio else 'off'

        # directio_alignment directive
        directio_alignment = re.search(r'directio_alignment\s+([^;]*)', self._content)
        self.directio_alignment = directio_alignment.group(1) if directio_alignment else '512'

        # disable_symlinks directive
        disable_symlinks = re.search(r'disable_symlinks\s+(off|on|if_not_owner)\s*([^;]*)', self._content)
        if disable_symlinks:
            self.disable_symlinks = dict(
                value=disable_symlinks.group(1),
                _from=disable_symlinks.group(2).split('from=')[1] if disable_symlinks.group(2) else None,
            ) if disable_symlinks.group(1) != 'off' else 'off'
        else:
            self.disable_symlinks = 'off'

        # error_page directive
        error_page = re.search(r'error_page\s+([^;]*)', self._content)
        if error_page:
            self.error_page = dict(codes='', uri=re.search(r'([^\s]*)$', error_page.group(1)).group(1))
            self.error_page.__setitem__('codes', error_page.group(1).replace(self.error_page.get('uri'), '').strip())
        else:
            self.error_page = None

        # etag directive
        etag = re.search(r'etag\s+(on|off);', self._content)
        self.etag = etag.group(1) if etag else 'on'

        # if_modified_since directive
        if_modified_since = re.search(r'if_modified_since\s+(off|exact|before);', self._content)
        self.if_modified_since = if_modified_since.group(1) if if_modified_since else 'exact'

        # ignore_invalid_headers directive
        ignore_invalid_headers = re.search(r'ignore_invalid_headers\s+(on|off)', self._content)
        self.ignore_invalid_headers = ignore_invalid_headers.group(1) if ignore_invalid_headers else 'on'

        # keepalive_disable directive
        keepalive_disable = re.search(r'keepalive_disable\s+([^;]*)', self._content)
        self.keepalive_disable = keepalive_disable.group(1) if keepalive_disable else 'msie6'

        # keepalive_requests directive
        keepalive_requests = re.search(r'keepalive_requests\s+(\d+);', self._content)
        self.keepalive_requests = int(keepalive_requests.group(1)) if keepalive_requests else 100

        # keepalive_timeout directive
        keepalive_timeout = re.search(r'keepalive_timeout\s+([^;]*)', self._content)
        if keepalive_timeout:
            timeouts = re.findall(r'(\w+)', keepalive_timeout.group(1))
            self.keepalive_timeout = dict(
                timeout=timeouts[0],
                header_timeout=timeouts[1] if len(timeouts) != 1 else None
            )
        else:
            self.keepalive_timeout = dict(
                timeout='75s',
                header_timeout=None
            )

        # large_client_header_buffers directive
        large_client_header_buffers = re.search(r'large_client_header_buffers\s+(\d+)\s+([^;]*)', self._content)
        self.large_client_header_buffers = dict(
            number=int(large_client_header_buffers.group(1)),
            size=large_client_header_buffers.group(2)
        ) if large_client_header_buffers else dict(
            number=4,
            size='8k'
        )

        # limit_rate directive
        limit_rate = re.search(r'limit_rate\s+([^;]*)', self._content)
        self.limit_rate = limit_rate.group(1) if limit_rate else '0'

        # limit_rate_after directive
        limit_rate_after = re.search(r'limit_rate_after\s+([^;]*)', self._content)
        self.limit_rate_after = limit_rate_after.group(1) if limit_rate_after else '0'

        # lingering_close directive
        lingering_close = re.search(r'lingering_close\s+(on|off|always);', self._content)
        self.lingering_close = lingering_close.group(1) if lingering_close else 'on'

        # lingering_time directive
        lingering_time = re.search(r'lingering_time\s+([^;]*)', self._content)
        self.lingering_time = lingering_time.group(1) if lingering_time else '30s'

        # lingering_timeout directive
        lingering_timeout = re.search(r'lingering_timeout\s+([^;]*)', self._content)
        self.lingering_timeout = lingering_timeout.group(1) if lingering_timeout else '5s'

        # log_not_found directive
        log_not_found = re.search(r'log_not_found\s+(on|off);', self._content)
        self.log_not_found = log_not_found.group(1) if log_not_found else 'on'

        # log_subrequest directive
        log_subrequest = re.search(r'log_subrequest\s+(on|off);', self._content)
        self.log_subrequest = log_subrequest.group(1) if log_subrequest else 'off'

        # max_ranges directive
        max_ranges = re.search(r'max_ranges\s+(\d+);', self._content)
        self.max_ranges = int(max_ranges.group(1)) if max_ranges else None

        # merge_slashes directive
        merge_slashes = re.search(r'merge_slashes\s+(on|off);', self._content)
        self.merge_slashes = merge_slashes.group(1) if merge_slashes else 'on'

        # msie_padding directive
        msie_padding = re.search(r'msie_padding\s+(on|off);', self._content)
        self.msie_padding = msie_padding.group(1) if msie_padding else 'on'

        # msie_refresh directive
        msie_refresh = re.search(r'msie_refresh\s+(on|off);', self._content)
        self.msie_refresh = msie_refresh.group(1) if msie_refresh else 'off'

        # open_file_cache directive
        open_file_cache = re.search(r'open_file_cache\s+(off|max=(\d+)\s*(inactive=(\w+))?)', self._content)
        if open_file_cache:
            if open_file_cache.group(2):
                self.open_file_cache = dict(
                    max=int(open_file_cache.group(2)),
                    inactive=open_file_cache.group(4) if open_file_cache.group(4) else None
                )
            else:
                self.open_file_cache = 'off'
        else:
            self.open_file_cache = 'off'

        # open_file_cache_errors directive
        open_file_cache_errors = re.search(r'open_file_cache_errors\s+(on|off);', self._content)
        self.open_file_cache_errors = open_file_cache_errors.group(1) if open_file_cache_errors else 'off'

        # open_file_cache_min_uses directive
        open_file_cache_min_uses = re.search(r'open_file_cache_min_uses\s+(\d+);', self._content)
        self.open_file_cache_min_uses = int(
            open_file_cache_min_uses.group(1)) if open_file_cache_min_uses else 1

        # open_file_cache_valid directive
        open_file_cache_valid = re.search(r'open_file_cache_valid\s+([^;]*)', self._content)
        self.open_file_cache_valid = open_file_cache_valid.group(1) if open_file_cache_valid else '60s'

        # output_buffers directive
        output_buffers = re.search(r'output_buffers\s+(\d+)\s+([^;]*)', self._content)
        self.output_buffers = dict(
            number=int(output_buffers.group(1)),
            size=output_buffers.group(2)
        ) if output_buffers else dict(
            number=2,
            size='32k'
        )

        # port_in_redirect directive
        port_in_redirect = re.search(r'port_in_redirect\s+(on|off);', self._content)
        self.port_in_redirect = port_in_redirect.group(1) if port_in_redirect else 'on'

        # postpone_output directive
        postpone_output = re.search(r'postpone_output\s+([^;]*)', self._content)
        self.postpone_output = postpone_output.group(1) if postpone_output else '1460'

        # read_ahead directive
        read_ahead = re.search(r'read_ahead\s+([^;]*)', self._content)
        self.read_ahead = read_ahead.group(1) if read_ahead else '0'

        # recursive_error_pages directive
        recursive_error_pages = re.search(r'recursive_error_pages\s+(on|off);', self._content)
        self.recursive_error_pages = recursive_error_pages.group(1) if recursive_error_pages else 'off'

        # request_pool_size directive
        request_pool_size = re.search(r'request_pool_size\s+([^;]*)', self._content)
        self.request_pool_size = request_pool_size.group(1) if request_pool_size else '4k'

        # reset_timedout_connection directive
        reset_timedout_connection = re.search(r'reset_timedout_connection\s+(on|off);', self._content)
        self.reset_timedout_connection = reset_timedout_connection.group(
            1) if reset_timedout_connection else 'off'

        # resolver directive
        resolver = re.search(r'resolver\s+([^;]*)', self._content)
        if resolver:
            valid = re.search(r'valid=(\w+)', resolver.group(1))
            ipv6 = re.search(r'ipv6=(on|off)', resolver.group(1))
            new_resolver = re.sub(r'valid=(\w+)', '', resolver.group(1))
            new_resolver = re.sub(r'ipv6=(on|off)', '', new_resolver)

            self.resolver = dict(
                address=re.findall(r'([^\s]*)', new_resolver),
                valid=valid.group(1) if valid else None,
                ipv6=ipv6.group(1) if ipv6 else None
            )
        else:
            self.resolver = None

        # resolver_timeout directive
        resolver_timeout = re.search(r'resolver_timeout\s+([^;]*)', self._content)
        self.resolver_timeout = resolver_timeout.group(1) if resolver_timeout else '30s'

        # root directive
        root = re.search(r'root\s+([^;]*)', self._content)
        self.root = root.group(1) if root else 'html'

        # satisfy directive
        satisfy = re.search(r'satisfy\s+(all|any);', self._content)
        self.satisfy = satisfy.group(1) if satisfy else 'all'

        # send_lowat directive
        send_lowat = re.search(r'send_lowat\s+([^;]*)', self._content)
        self.send_lowat = send_lowat.group(1) if send_lowat else '0'

        # send_timeout directive
        send_timeout = re.search(r'send_timeout\s+([^;]*)', self._content)
        self.send_timeout = send_timeout.group(1) if send_timeout else '60s'

        # sendfile directive
        sendfile = re.search(r'sendfile\s+(on|off);', self._content)
        self.sendfile = sendfile.group(1) if sendfile else 'off'

        # sendfile_max_chunk directive
        sendfile_max_chunk = re.search(r'sendfile_max_chunk\s+([^;]*)', self._content)
        self.sendfile_max_chunk = sendfile_max_chunk.group(1) if sendfile_max_chunk else '0'

        # server_name_in_redirect directive
        server_name_in_redirect = re.search(r'server_name_in_redirect\s+(on|off);', self._content)
        self.server_name_in_redirect = server_name_in_redirect.group(1) if server_name_in_redirect else 'off'

        # server_names_hash_bucket_size directive
        server_names_hash_bucket_size = re.search(r'server_names_hash_bucket_size\s+([^;]*)', self._content)
        self.server_names_hash_bucket_size = server_names_hash_bucket_size.group(
            1) if server_names_hash_bucket_size else '32|64|128'

        # server_names_hash_max_size directive
        server_names_hash_max_size = re.search(r'server_names_hash_max_size\s+([^;]*)', self._content)
        self.server_names_hash_max_size = server_names_hash_max_size.group(1) if server_names_hash_max_size else '512'

        # server_tokens directive
        server_tokens = re.search(r'server_tokens\s+(on|off|build|[^;]*)', self._content)
        self.server_tokens = server_tokens.group(1) if server_tokens else 'on'

        # subrequest_output_buffer_size directive
        subrequest_output_buffer_size = re.search(r'subrequest_output_buffer_size\s+([^;]*)', self._content)
        self.subrequest_output_buffer_size = subrequest_output_buffer_size.group(
            1) if subrequest_output_buffer_size else '4k|8k'

        # tcp_nodelay directive
        tcp_nodelay = re.search(r'tcp_nodelay\s+(on|off);', self._content)
        self.tcp_nodelay = tcp_nodelay.group(1) if tcp_nodelay else 'on'

        # tcp_nopush directive
        tcp_nopush = re.search(r'tcp_nopush\s+(on|off);', self._content)
        self.tcp_nopush = tcp_nopush.group(1) if tcp_nopush else 'off'

        # types directive
        types = re.search(r'types\s+{([^}]*)', self._content)
        if types:
            self.types = dict()
            subdirectives = [_.strip() for _ in re.findall(r'([^;]+)', types.group(1)) if _.strip()]
            for subdirective in subdirectives:
                _ = re.findall(r'([^\s]+)', subdirective)
                for extension in _[1:]:
                    self.types[extension] = _[0]

        # types_hash_bucket_size directive
        types_hash_bucket_size = re.search(r'types_hash_bucket_size\s+([^;]*)', self._content)
        self.types_hash_bucket_size = types_hash_bucket_size.group(1) if types_hash_bucket_size else '64'

        # types_hash_max_size directive
        types_hash_max_size = re.search(r'types_hash_max_size\s+([^;]*)', self._content)
        self.types_hash_max_size = types_hash_max_size.group(1) if types_hash_max_size else '1024'

        # underscores_in_headers directive
        underscores_in_headers = re.search(r'underscores_in_headers\s+(on|off);', self._content)
        self.underscores_in_headers = underscores_in_headers.group(1) if underscores_in_headers else 'off'

        # variables_hash_bucket_size directive
        variables_hash_bucket_size = re.search(r'variables_hash_bucket_size\s+([^;]*)', self._content)
        self.variables_hash_bucket_size = variables_hash_bucket_size.group(
            1) if variables_hash_bucket_size else '64'

        # variables_hash_max_size directive
        variables_hash_max_size = re.search(r'variables_hash_max_size\s+([^;]*)', self._content)
        self.variables_hash_max_size = variables_hash_max_size.group(1) if variables_hash_max_size else '1024'
