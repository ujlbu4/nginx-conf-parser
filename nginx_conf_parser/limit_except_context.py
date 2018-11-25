# coding=utf-8
import re


class LimitExceptContext:
    allow = None
    deny = None

    def __init__(self, content):
        self._content = content

        # allow directive
        self.allow = re.findall(r'allow\s+([^;]*)', self._content)
        self.allow = None if len(self.allow) == 0 else self.allow

        # deny directive
        self.deny = re.findall(r'deny\s+([^;]*)', self._content)
        self.deny = None if len(self.deny) == 0 else self.deny
