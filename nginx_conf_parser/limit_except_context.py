# coding=utf-8
import re


class LimitExceptContext:
    allow = None
    deny = None
    auth_jwt = None

    def __init__(self, content):
        self._content = content

        # allow directive
        self.allow = re.findall(r'allow\s+([^;]*)', self._content)
        self.allow = None if len(self.allow) == 0 else self.allow

        # deny directive
        self.deny = re.findall(r'deny\s+([^;]*)', self._content)
        self.deny = None if len(self.deny) == 0 else self.deny

        # auth_jwt directive
        auth_jwt = re.search(r'auth_jwt\s+([^;]*)', self._content)
        if not auth_jwt or auth_jwt.group(1) == 'off':
            self.auth_jwt = 'off'
        else:
            _ = re.search(r'"(.*)"\s*(token=(.*))?', auth_jwt.group(1))
            self.auth_jwt = dict(
                realm='"{0}"'.format(_.group(1)),
                token=_.group(3) if _.group(3) else None
            )
