# coding=utf-8
import re
from _io import TextIOWrapper


def extract_context(conffile, context_name):
    if not isinstance(conffile, TextIOWrapper):
        raise TypeError('Invalid configuration file given, must be a file stream')

    content = conffile.read().replace('\n', ' ')
    try:
        context_begin_index = re.search(context_name + '\s+{', content).start()
        context_string = ''

        depth = 0

        for c in content[context_begin_index:]:
            if c == '{':
                depth += 1
                context_string += c
                continue

            if c == '}':
                depth -= 1
                context_string += c
                if depth == 0:
                    break
                else:
                    continue

            context_string += c

        return context_string
    except AttributeError:
        return ''
