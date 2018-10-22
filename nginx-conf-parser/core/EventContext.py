# coding=utf-8


class EventContext:
    content = None

    def __init__(self, content):
        self.content = content
        self._parse()

    def _parse(self):
        if self.content is None:
            raise ValueError('Content not initialized')

        self._extract_value('accept_mutex_delay', '500ms')
        self._extract_value('accept_mutex', 'off')
        self._extract_value('debug_connection', [])
        self._extract_value('multi_accept', 'off')
        self._extract_value('use', None)
        self._extract_value('worker_aio_requests', '32')
        self._extract_value('worker_connections', '512')

    def _extract_value(self, directive_name, default):
        more = True
        while more:
            try:
                directive_begin_index = self.content.index(directive_name)
                directive_end_index = self.content.index(';', directive_begin_index)
                directive_name_value = self.content[directive_begin_index:directive_end_index + 1]
                directive_value = directive_name_value.split(directive_name)[1].strip().replace(';', '')

                if not hasattr(self, directive_name):
                    self.__setattr__(directive_name, directive_value)
                else:
                    self.__setattr__(directive_name, [self.__getattribute__(directive_name)])
                    self.__getattribute__(directive_name).append(directive_value)

                self.content = self.content[:directive_begin_index] + self.content[directive_end_index+1:]
            except ValueError:
                more = False
                if not hasattr(self, directive_name):
                    self.__setattr__(directive_name, default)


if __name__ == '__main__':
    test = 'events { accept_mutex off; debug_connection localhost; debug_connection 192.168.1.1; }'
    print(test)
    evc = EventContext(test)
    print(evc.debug_connection)
