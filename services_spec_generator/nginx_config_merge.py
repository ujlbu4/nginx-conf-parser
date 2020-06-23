#!/usr/bin/env python
import sys
import glob
import string

from pyparsing import (
    Literal, White, Word, alphanums, CharsNotIn, Forward, Group, SkipTo,
    LineEnd, Optional, OneOrMore, ZeroOrMore, pythonStyleComment, printables
)


class NginxParser:
    """
    A class that parses nginx configuration with pyparsing
    """

    # constants
    left_bracket = Literal("{").suppress()
    right_bracket = Literal("}").suppress()
    semicolon = Literal(";").suppress()
    space = White().suppress()
    comment_char = Literal("#")
    # special characters (/-+.) for mime-types
    key = Word(alphanums + "_/-+.")
    value = CharsNotIn("{};,")
    value2 = CharsNotIn(";")
    location = CharsNotIn("{};," + string.whitespace)
    ifword = Literal("if")
    setword = Literal("set")
    # modifier for location uri [ = | ~ | ~* | ^~ ]
    modifier = Literal("=") | Literal("~*") | Literal("~") | Literal("^~")
    # text = Word(printables, excludeChars='\t\n\r\v\f')
    text = Word(printables + ' ')

    # rules
    comment = (comment_char + text)
    assignment = (key + Optional(space + value) + semicolon)
    setblock = (setword + OneOrMore(space + value2) + semicolon)
    block = Forward()
    ifblock = Forward()
    subblock = ZeroOrMore(Group(assignment) | block | ifblock | setblock | Group(comment))
    ifblock = (
        ifword
        + SkipTo('{')
        + left_bracket
        + subblock
        + right_bracket)

    block << Group(
        Group(key + Optional(space + modifier) + Optional(space + location))
        + left_bracket
        + Group(ZeroOrMore(Group(assignment) | block | ifblock | setblock | Group(comment)))
        + right_bracket)

    # script = OneOrMore(Group(assignment) | block).ignore(pythonStyleComment)
    script = OneOrMore(Group(assignment) | block | Group(comment))

    def __init__(self, source):
        self.source = source

    def parse(self):
        """
        Returns the parsed tree.
        """
        return self.script.parseString(self.source)

    def as_list(self):
        """
        Returns the list of tree.
        """
        return self.parse().asList()


def parse_file(path):
    _file = open(path)
    return NginxParser(_file.read()).as_list()


class NginxMergedDumper:
    """
    A class that (recursively) merge nginx configuration files into one string
    """
    def __init__(self, path, indentation=4, spacer=' '):
        self.lines = []
        self.indentation = indentation
        self.spacer = spacer
        self.inline_file(path)

    def add_line(self, line):
        self.lines.append(line)

    def dump(self, blocks, current_indent):
        for key, values in blocks:
            if current_indent:
                self.add_line(self.spacer)
            indentation = self.spacer * current_indent
            if isinstance(key, list):
                self.add_line(indentation + self.spacer.join(key) + ' {')
                for parameter in values:
                    if isinstance(parameter[0], list):
                        self.dump([parameter], current_indent + self.indentation)
                    else:
                        if parameter[0] == 'include':
                            self.inline_by_masks(parameter[1:],
                                current_indent + self.indentation)
                        else:
                            dumped = self.spacer.join(parameter) + ';'
                            self.add_line(self.spacer * (current_indent + self.indentation) + dumped)

                self.add_line(indentation + '}')
            else:
                self.add_line(self.spacer * current_indent + key + self.spacer + values + ';')

    def inline_by_masks(self, masks, current_indent):
        paths = []
        for m in masks:
            paths += glob.glob(m)

        for f in paths:
            self.inline_file(f, current_indent)
            x = 5

    def inline_file(self, path, current_indent=0):
        parsed = parse_file(path)
        self.dump(parsed, current_indent)

    def as_string(self):
        return '\n'.join(self.lines)

