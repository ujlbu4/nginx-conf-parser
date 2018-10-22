# coding=utf-8

class HttpContext:
    content = None

    def __init__(self, content):
        self.content = content
        self._parse()

    def _parse(self):
        if self.content is None:
            raise ValueError('Content not initialized')
