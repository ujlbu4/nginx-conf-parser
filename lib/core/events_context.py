# coding=utf-8
import re


class EventContext:
    accept_mutex_delay = '500ms'
    accept_mutex = 'off'
    debug_connection = []
    multi_accept = 'off'
    use = None
    worker_aio_requests = 32
    worker_connections = 512
    error_log = dict(file='logs/error.log', level='error')

    def load(self, content):
        # accept_mutex_delay
        delay = re.search(r'accept_mutex_delay\s+([a-zA-Z0-9]+);', content)
        self.accept_mutex_delay = delay.group(1) if delay else self.accept_mutex_delay

        # accept_mutex
        mutex = re.search(r'accept_mutex\s+(on|off);', content)
        self.accept_mutex = mutex.group(1) if mutex else self.accept_mutex

        # debug_connection
        debug = re.findall(r'debug_connection\s+([0-9a-zA-Z.-/:]+)', content)
        self.debug_connection = debug

        # multi_accept
        accept = re.search(r'multi_accept\s+(on|off);', content)
        self.multi_accept = accept.group(1) if accept else self.multi_accept

        # use
        use = re.search(r'use\s+(select|poll|kqueue|epoll|/dev/poll|eventport);', content)
        self.use = use.group(1) if use else self.use

        # worker_aio_requests
        aio = re.search(r'worker_aio_requests\s+([0-9]+);', content)
        self.worker_aio_requests = int(aio.group(1)) if aio else self.worker_aio_requests

        # worker_connections
        conn = re.search(r'worker_connections\s+([0-9]+);', content)
        self.worker_connections = int(conn.group(1)) if conn else self.worker_connections

        # error_log
        error_log = re.search(
            r'error_log\s+(([a-zA-Z0-9./\\\-]+)(\s+)?(debug|info|notice|warn|error|crit|alert|emerg)?);', content)
        if error_log:
            self.error_log['file'] = error_log.group(2)
            self.error_log['level'] = error_log.group(4) if error_log.group(4) else 'error'
