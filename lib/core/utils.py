# coding=utf-8
import re
from _io import TextIOWrapper


def extract_context(conffile, context_name):
    if not isinstance(conffile, TextIOWrapper) and not isinstance(conffile, str):
        raise TypeError('Invalid configuration file given, must be a file stream or a string')

    if isinstance(conffile, TextIOWrapper):
        content = conffile.read().replace('\n', ' ')
    else:
        content = conffile.replace('\n', ' ')

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


def extract_upstream_server_parameters(to_parse):
    parameters = {}

    # weight=number
    weight = re.search(r'weight=([0-9]+)', to_parse)
    parameters['weight'] = int(weight.group(1)) if weight else None

    # max_conns=number
    max_conns = re.search(r'max_conns=([0-9]+)', to_parse)
    parameters['max_conns'] = int(max_conns.group(1)) if max_conns else None

    # max_fails=number
    max_fails = re.search(r'max_fails=([0-9]+)', to_parse)
    parameters['max_fails'] = int(max_fails.group(1)) if max_conns else None

    # fail_timeout=time
    fail_timeout = re.search(r'fail_timeout=([0-9a-zA-Z]+)', to_parse)
    parameters['fail_timeout'] = fail_timeout.group(1) if fail_timeout else None

    # backup, down, resolve, drain
    parameters['backup'] = 'backup' in to_parse
    parameters['down'] = 'down' in to_parse
    parameters['resolve'] = 'resolve' in to_parse
    parameters['drain'] = 'drain' in to_parse

    # route=string
    route = re.search(r'route=([a-zA-Z0-9.-_\\/]+)', to_parse)
    parameters['route'] = route.group(1) if route else None

    # service=string
    service = re.search(r'service=([a-zA-Z0-9.-_\\/]+)', to_parse)
    parameters['service'] = service.group(1) if service else None

    # slow_start=time
    slow_start = re.search(r'slow_start=([a-zA-Z0-9]+)', to_parse)
    parameters['slow_start'] = slow_start.group(1) if slow_start else None

    return parameters


def extract_upstream_zone(to_parse):
    zone = re.search(r'zone\s+([a-zA-Z0-9_\-.]+)\s*?([a-z0-9]+)?;', to_parse)
    return dict(name=zone.group(1), size=zone.group(2)) if zone and zone.group(2) else \
        dict(name=zone.group(1), size=None) if zone else None
