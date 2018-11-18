# coding=utf-8
import re

from .utils import extract_upstream_zone


class UpstreamContext:
    name = None
    servers = []
    zone = None
    state = None
    hash = None
    ip_hash = False
    keepalive = None
    keepalive_requests = 100
    keepalive_timeout = '60s'
    ntlm = False
    least_conn = False
    least_time = None
    queue = None
    random = None
    sticky = None

    def __init__(self, name, content):
        self.name = name

        # zone directive
        self.zone = extract_upstream_zone(content)

        # server directive
        self.servers = []
        servers = re.findall(r'server\s+([^\s]*)\s*([^;]*)', content)
        for server in servers:
            self.servers.append({
                'address': server[0],
                'parameters': {_[0]: _[1] if _[1] != '' else True for _ in re.findall(r'(\w*)=*(\w*)', server[1]) if
                               _[0] != ''}
            })

        # state directive
        state = re.search(r'state\s+([^;]*)', content)
        self.state = state.group(1) if state else self.state

        # hash directive
        hash_ = re.search(r'hash\s+([^\s]*)\s*(consistent)*;', content)
        self.hash = dict(key=hash_.group(1), consistent=True if hash_.group(2) else False) if hash_ else self.hash

        # ip_hash directive
        self.ip_hash = 'ip_hash;' in content

        # keepalive directive
        keepalive = re.search(r'keepalive\s+(\d+);', content)
        self.keepalive = int(keepalive.group(1)) if keepalive else None

        # keekpalive_requests directive
        keepalive_requests = re.search(r'keepalive_requests\s+(\d+);', content)
        self.keepalive_timeout = int(keepalive_requests.group(1)) if keepalive_requests else 100

        # keepalive_timeout directive
        keepalive_timeout = re.search(r'keepalive_timeout\s+(\w);', content)
        self.keepalive_timeout = keepalive_timeout.group(1) if keepalive_timeout else '60s'

        # ntlm directive
        self.ntlm = 'ntlm;' in content

        # least_conn directive
        self.least_conn = 'least_conn;' in content

        # least_time
        self.least_time = None
        least_time = re.search(r'least_time\s+([^;]*)', content)
        self.least_time = dict(header='header' in least_time.group(1), last_byte='last_byte' in least_time.group(1),
                               inflight='inflight' in least_time.group(1)) \
            if least_time else self.least_time

        # queue directive
        queue = re.search(r'queue\s+(\d+)\s*(timeout=(\w+))?;', content)
        self.queue = dict(value=int(queue.group(1)),
                          timeout=queue.group(3) if queue.group(3) else '60s') if queue else None

        # random directive
        random = re.search(r'random\s*(two)?\s*([^;]*)', content)
        self.random = dict(two=True if random.group(1) else False,
                           method=random.group(2) if random.group(2) else None) if random else None

        # sticky directive
        sticky = re.search(r'sticky\s*(cookie|route|learn)\s*([^;]*)', content)
        if sticky:
            # sticky cookie
            if 'cookie' == sticky.group(1):
                self.sticky = dict(
                    type='cookie',
                    name=re.search(r'^([^\s]*)', sticky.group(2)).group(1),
                    expires=re.search(r'expires=([^\s]*)', sticky.group(2)).group(1) if 'expires' in sticky.group(
                        2) else None,
                    domain=re.search(r'domain=([^\s]*)', sticky.group(2)).group(1) if 'domain' in sticky.group(
                        2) else None,
                    httponly='httponly' in sticky.group(2),
                    secure='secure' in sticky.group(2),
                    path=re.search(r'path=([^\s]*)', sticky.group(2)).group(1) if 'path' in sticky.group(2) else None
                )
            elif 'route' == sticky.group(1):
                self.sticky = dict(
                    type='route',
                    variables=re.findall(r'(\$\w+)', sticky.group(2))
                )
            elif 'learn' == sticky.group(1):
                zone = re.search(r'zone=([^\s]*)', sticky.group(2)).group(1)
                self.sticky = dict(
                    type='learn',
                    create=re.search(r'create=([^\s]*)', sticky.group(2)).group(1),
                    zone=dict(name=zone.split(':')[0], size=zone.split(':')[1]),
                    lookup=re.search(r'lookup=([^\s]*)', sticky.group(2)).group(1),
                    timeout=re.search(r'timeout=([^\s]*)', sticky.group(2)).group(1) if 'timeout' in sticky.group(
                        2) else None,
                    header='header' in sticky.group(2),
                    sync='sync' in sticky.group(2)
                )
