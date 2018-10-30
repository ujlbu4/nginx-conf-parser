# coding=utf-8
import re
from _io import TextIOWrapper
from os.path import isfile
from core.event_context import EventContext

RE_USER = r'user\s+(.*);'
RE_WORKER_PROCESSES = r'worker_process'


class NginxConfParser:
    content = None
    main_context = None
    event_context = None
    http_context = None

    def __init__(self, nginx_conf):
        if isinstance(nginx_conf, str):
            if not isfile(nginx_conf):
                raise Exception('File not found: {0}'.format(nginx_conf))
            with open(nginx_conf, 'r') as conffile:
                self.content = ''.join(conffile.read()).replace('\n', ' ')
        elif isinstance(nginx_conf, TextIOWrapper):
            self.content = ''.join(nginx_conf.read()).replace('\n', ' ')
        else:
            raise TypeError('nginx_conf parameter must be a string or a stream')

        self._extract_events_context()
        self.event_context = EventContext(self.event_context_string)
        self._extract_http_context()

    def _extract_events_context(self):
        try:
            events_begin_index = self.content.index('events')
            events_end_index = self.content.index('}', events_begin_index)
            self.event_context_string = self.content[events_begin_index:events_end_index + 1]

            splitted = self.content.split(self.event_context_string)
            self.content = splitted[0] + splitted[1]
        except ValueError:
            pass

    def _extract_http_context(self):
        try:
            http_begin_index = self.content.index('http')
            http_end_index = self.content.index('}', http_begin_index)
            self.http_context = self.content[http_begin_index:http_end_index + 1]

            splitted = self.content.split(self.http_context)
            self.content = splitted[0] + splitted[1]
        except ValueError:
            pass

    def _parse_main_context(self):
        match = re.match(r'user\s+([a-zA-Z\s_]+);', self.content)
        self.user = match.group(1) if match else 'nobody nobody'

        match = re.match(r'daemon\s+(on|off);', self.content)
        self.daemon = match.group(1) if match else 'on'

        match = re.match(r'debug_point\s+(abort|stop);', self.content)
        self.debug_point = match.group(1) if match else None

        match = re.findall(r'env\s+([a-zA-Z_=]+);', self.content)
        self.env = match

        # TODO: error_log (context: main, html, events)

        match = re.match(r'load_module\s+([a-zA-Z_=]+);', self.content)
        self.load_module = match.group(1) if match else None

        match = re.match(r'lock_file\s+([a-zA-Z_=]+);', self.content)
        self.load_module = match.group(1) if match else 'logs/nginx.lock'


if __name__ == '__main__':
    http_context = None
    test = "env     NODE_ENV=production; events { worker_connections  4096;  ## Default: 1024 } lock_file logs/nginx.lock;"
    try:
        test.index('http')
    except ValueError:
        pass
