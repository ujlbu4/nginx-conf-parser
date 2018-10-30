# coding=utf-8
from abc import ABC, abstractmethod


class Context(ABC):
    content = ''

    def __init__(self, content):
        self.content = content
        self._parse()

    @abstractmethod
    def _parse(self):
        if self.content is None:
            raise ValueError('Content not initialized')

    def _extract_values(self, directive_name, default):
        more = True
        while more:
            try:
                directive_begin_index = self.content.index(directive_name)
                directive_end_index = self.content.index(';', directive_begin_index)
                directive_name_value = self.content[directive_begin_index:directive_end_index + 1]
                directive_value = directive_name_value[len(directive_name):-1].strip()

                if not hasattr(self, directive_name):
                    self.__setattr__(directive_name, directive_value)
                else:
                    self.__setattr__(directive_name, [self.__getattribute__(directive_name)])
                    self.__getattribute__(directive_name).append(directive_value)

                self.content = self.content[:directive_begin_index] + self.content[directive_end_index + 1:]
            except ValueError:
                more = False
                if not hasattr(self, directive_name):
                    self.__setattr__(directive_name, default)
