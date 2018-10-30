# coding=utf-8
from core.context import Context


class HttpContext(Context):
    def _parse(self):
        super(HttpContext, self)._parse()
