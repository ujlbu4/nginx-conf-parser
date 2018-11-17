# coding=utf-8
import re

from core.utils import extract_upstream_zone, extract_upstream_server_parameters, extract_context
from core.upstream import Upstream


class StreamContext:
    upstreams = []
    servers = []

    def load(self, content):
        # extracting upstreams
        upstreams = re.findall(r'upstream\s+([a-zA-Z]+)\s+{([^}]*)', content)
        for upstream in upstreams:
            self.upstreams.append(Upstream(name=upstream[0], content=upstream[1]))
            to_append = dict(name=upstream[0], servers=[], zone=extract_upstream_zone(upstream[1]))
            # server directives
            servers = re.findall(r'server\s+([^;]*)', upstream[1])
            for server in servers:
                to_append.get('servers').append(
                    dict(address=re.search(r'^([0-9a-zA-Z.:/]+)', server).group(1),
                         parameters=extract_upstream_server_parameters(server)))

            # state directive
            state = re.search(r'state\s+([^;]*)', upstream[1])
            to_append['state'] = state.group(1) if state else None

            # hash directive
            hash = re.search(r'hash\s+([^;]*)', upstream[1])
            if hash:
                consistent = 'consistent' in hash.group(1)
                to_append['hash'] = dict(consistent=consistent, key=hash.group(1).split('consistent')[0].strip())

            # ip_hash
            to_append['ip_hash'] = 'ip_hash' in upstream[1]

            # keep_alive connections;
            keep_alive = re.search(r'keep_alive\s+([^;]*)', upstreams[1])
            to_append['keep_alive'] = keep_alive.group(1) if keep_alive else None

            self.upstreams.append(to_append)

        # extracting servers
        servers = re.findall(r'server\s+{([^}]*)', content)


if __name__ == '__main__':
    from os.path import dirname
    from core.utils import extract_context

    with open('{0}/../tests/features/nginx_stream_sample.conf'.format(dirname(__file__))) as f:
        stream_string = extract_context(f, 'stream')

    stream_context = StreamContext()
    stream_context.load(stream_string)
