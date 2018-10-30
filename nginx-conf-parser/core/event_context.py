# coding=utf-8
from core.context import Context


class EventContext(Context):
    def _parse(self):
        super(EventContext, self)._parse()

        super(EventContext, self)._extract_values('accept_mutex_delay', '500ms')
        super(EventContext, self)._extract_values('accept_mutex', 'off')
        super(EventContext, self)._extract_values('debug_connection', [])
        super(EventContext, self)._extract_values('multi_accept', 'off')
        super(EventContext, self)._extract_values('use', None)
        super(EventContext, self)._extract_values('worker_aio_requests', '32')
        super(EventContext, self)._extract_values('worker_connections', '512')
        super(EventContext, self)._extract_values('error_log', 'logs/error.log error')


if __name__ == '__main__':
    test = 'events { accept_mutex off; debug_connection localhost; debug_connection 192.168.1.1; }'
    print(test)
    evc = EventContext(test)
    print(evc.debug_connection)
