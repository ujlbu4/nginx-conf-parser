# coding=utf-8
from core.context import Context


class StreamContext(Context):
    stream_string = None
    servers = None
    upstreams = None

    def _parse(self):
        self._extract_stream_from_content()

    def _extract_stream_from_content(self):
        stream_begin_index = self.content.index('stream {')
        print(self.content[stream_begin_index:])
