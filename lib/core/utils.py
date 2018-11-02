# coding=utf-8
import re
from _io import TextIOWrapper


def extract_context(conffile, context_name):
    if not isinstance(conffile, TextIOWrapper):
        raise TypeError('Invalid configuration file given, must be a file stream')

    content = conffile.read().replace('\n', ' ')
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


if __name__ == '__main__':
    from os.path import dirname

    with open('{0}/../tests/features/nginx_stream_sample.conf'.format(dirname(__file__))) as conf:
        context = extract_context(conf, 'stream')
        print(context)
