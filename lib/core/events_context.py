# coding=utf-8
import re


class EventContext:
    accept_mutex_delay = None
    accept_mutex = None
    debug_connection = []
    multi_accept = 'off'
    use = None
    worker_aio_requests = 32
    worker_connections = 512
    error_log = dict(file='logs/error.log', level='error')

    def __init__(self, content):
        # accept_mutex_delay
        delay = re.search(r'accept_mutex_delay\s*([^;]*)', content)
        self.accept_mutex_delay = delay.group(1) if delay else '500ms'

        # accept_mutex
        mutex = re.search(r'accept_mutex\s*(on|off);', content)
        self.accept_mutex = mutex.group(1) if mutex else 'off'

        # debug_connection
        debug = re.findall(r'debug_connection\s*([^;]*)', content)
        self.debug_connection = debug

        # multi_accept
        accept = re.search(r'multi_accept\s*(on|off);', content)
        self.multi_accept = accept.group(1) if accept else 'off'

        # use
        use = re.search(r'use\s+(select|poll|kqueue|epoll|/dev/poll|eventport);', content)
        self.use = use.group(1) if use else self.use

        # worker_aio_requests
        aio = re.search(r'worker_aio_requests\s*(\d+);', content)
        self.worker_aio_requests = int(aio.group(1)) if aio else 32

        # worker_connections
        conn = re.search(r'worker_connections\s*(\d+);', content)
        self.worker_connections = int(conn.group(1)) if conn else 512

        # error_log
        error_log = re.search(
            r'error_log\s*([^\s]*)\s*(debug|info|notice|warn|error|crit|alert|emerg)?;', content)
        if error_log:
            self.error_log = dict(
                file=error_log.group(1),
                level=error_log.group(2) if error_log.group(2) else 'error'
            )
        else:
            self.error_log = dict(
                file='logs/error.log',
                level='error'
            )
