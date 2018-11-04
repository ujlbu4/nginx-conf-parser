# coding=utf-8
from _io import TextIOWrapper
from os.path import isfile
from core.utils import extract_context
from core.events_context import EventContext


class NginxConfParser:
    content = None
    main_context = None
    event_context = None
    http_context = None

    def __init__(self, nginx_conf):
        if isinstance(nginx_conf, str):
            if not isfile(nginx_conf):
                raise Exception('File not found: {0}'.format(nginx_conf))
            self.content = open(nginx_conf, 'r')
        elif isinstance(nginx_conf, TextIOWrapper):
            self.content = nginx_conf
        else:
            raise TypeError('nginx_conf parameter must be a string or a stream')

        self._events_string = extract_context(self.content, 'events')
        self.event_context = EventContext(self._events_string)

        self._http_string = extract_context(self.content, 'http')
        self._stream_string = extract_context(self.content, 'stream')
        self._mail_string = extract_context(self.content, 'mail')
        self.content.close()
