#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2023 Barcelona Supercomputing Center, José M. Fernández
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""
    Derived from
    pygments.lexers.jvm
    ~~~~~~~~~~~~~~~~~~~

    Fixed pygments lexer for Groovy language.

    :copyright: Copyright 2006-2022 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import Lexer, RegexLexer, include, bygroups, using, \
    this, combined, default, words
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Punctuation, Whitespace
from pygments.util import shebang_matches
from pygments import unistring as uni

__all__ = ['GroovyTokenizer', 'GroovyRestrictedTokenizer']

class GroovyTokenizer(RegexLexer):
    """
    For Groovy source code.
    Fixed by jmfernandez

    .. versionadded:: 1.5.1
    """

    name = 'Groovy'
    url = 'https://groovy-lang.org/'
    aliases = ['groovy']
    filenames = ['*.groovy','*.gradle','*.nf']
    mimetypes = ['text/x-groovy']

    flags = re.MULTILINE | re.DOTALL

    tokens = {
        'root': [
            # Groovy allows a file to start with a shebang
            (r'#!(.*?)$', Comment.Preproc, 'base'),
            default('base'),
        ],
        'base': [
            (r'[^\S\n]+', Whitespace),
            #(r'(//.*?)(\n)', bygroups(Comment.Single, Whitespace)),
            (r'(//.*?)$', bygroups(Comment.Single)),
            (r'/\*.*?\*/', Comment.Multiline),
            # keywords: go before method names to avoid lexing "throw new XYZ"
            # as a method signature
            (r'(assert|break|case|catch|continue|default|do|else|finally|for|'
             r'if|goto|instanceof|new|return|switch|this|throw|try|while|in|as)\b',
             Keyword),
            # method names
            (r'^(\s*(?:[a-zA-Z_][\w.\[\]]*\s+)+?)'  # return arguments
             r'('
             r'[a-zA-Z_]\w*'                        # method name
             r'|"(?:\\\\|\\[^\\]|[^"\\])*"'         # or double-quoted method name
             r"|'(?:\\\\|\\[^\\]|[^'\\])*'"         # or single-quoted method name
             r')'
             r'(\s*)(\()',                          # signature start
             bygroups(using(this), Name.Function, Whitespace, Operator)),
            (r'@[a-zA-Z_][\w.]*', Name.Decorator),
            (r'(abstract|const|enum|extends|final|implements|native|private|'
             r'protected|public|static|strictfp|super|synchronized|throws|'
             r'transient|volatile)\b', Keyword.Declaration),
            (r'(def|boolean|byte|char|double|float|int|long|short|void)\b',
             Keyword.Type),
            (r'(package)(\s+)', bygroups(Keyword.Namespace, Whitespace)),
            (r'(true|false|null)\b', Keyword.Constant),
            (r'(class|interface)(\s+)', bygroups(Keyword.Declaration, Whitespace),
             'class'),
            (r'(import)(\s+)', bygroups(Keyword.Namespace, Whitespace), 'import'),
            (r'""".*?"""', String.Double),
            (r"'''.*?'''", String.Single),
            (r'"(\\\\|\\[^\\]|[^"\\])*"', String.Double),
            (r"'(\\\\|\\[^\\]|[^'\\])*'", String.Single),
            (r'\$/((?!/\$).)*/\$', String),
            (r'/(\\\\|\\[^\\]|[^/\\])+/', String),
            (r"'\\.'|'[^\\]'|'\\u[0-9a-fA-F]{4}'", String.Char),
            (r'(\.)([a-zA-Z_]\w*)', bygroups(Operator, Name.Attribute)),
            (r'[a-zA-Z_]\w*:', Name.Label),
            (r'[a-zA-Z_$]\w*', Name),
            (r'[~^*!%&\[\](){}<>|+=:;,./?-]', Operator),
            (r'[0-9][0-9]*\.[0-9]+([eE][0-9]+)?[fd]?', Number.Float),
            (r'0x[0-9a-fA-F]+', Number.Hex),
            (r'[0-9]+L?', Number.Integer),
            (r'\n', Whitespace)
        ],
        'class': [
            (r'[a-zA-Z_]\w*', Name.Class, '#pop')
        ],
        'import': [
            (r'[\w.]+\*?', Name.Namespace, '#pop')
        ],
    }

    def analyse_text(text):
        return shebang_matches(text, r'groovy')


class GroovyRestrictedTokenizer(RegexLexer):
    """
    For Groovy source code.
    Fixed by jmfernandez

    .. versionadded:: 1.5.1
    """

    name = 'Groovy (restricted)'
    url = 'https://groovy-lang.org/'
    aliases = ['groovy']
    filenames = ['*.groovy','*.gradle','*.nf']
    mimetypes = ['text/x-groovy']

    flags = re.MULTILINE | re.DOTALL

    tokens = {
        'root': [
            # Groovy allows a file to start with a shebang
            (r'#!(.*?)$', Comment.Preproc, 'base'),
            default('base'),
        ],
        'base': [
            (r'[^\S\n]+', Whitespace),
            #(r'(//.*?)(\n)', bygroups(Comment.Single, Whitespace)),
            (r'//(.*?)$', bygroups(Comment.Single)),
            (r'(/\*)', bygroups(None), 'multiline_comment'),
            # keywords: go before method names to avoid lexing "throw new XYZ"
            # as a method signature
            (r'(assert|break|case|catch|continue|default|do|else|finally|for|'
             r'if|goto|instanceof|new|return|switch|this|throw|try|while|in|as)\b',
             Keyword),
            # method names
            (r'^(\s*(?:[a-zA-Z_][\w.\[\]]*\s+)+?)'  # return arguments
             r'('
             r'[a-zA-Z_]\w*'                        # method name
             r'|"(?:\\\\|\\[^\\]|[^"\\])*"'         # or double-quoted method name
             r"|'(?:\\\\|\\[^\\]|[^'\\])*'"         # or single-quoted method name
             r')'
             r'(\s*)(\()',                          # signature start
             bygroups(using(this), Name.Function, Whitespace, Operator)),
            (r'@[a-zA-Z_][\w.]*', Name.Decorator),
            (r'(abstract|const|enum|extends|final|implements|native|private|'
             r'protected|public|static|strictfp|super|synchronized|throws|'
             r'transient|volatile)\b', Keyword.Declaration),
            (r'(def|boolean|byte|char|double|float|int|long|short|void)\b',
             Keyword.Type),
            (r'(package)(\s+)', bygroups(Keyword.Namespace, Whitespace)),
            (r'(true|false|null)\b', Keyword.Constant),
            (r'(class|interface)(\s+)', bygroups(Keyword.Declaration, Whitespace),
             'class'),
            (r'(import)(\s+)', bygroups(Keyword.Namespace, Whitespace), 'import'),
            (r'"""', String.GString.GStringBegin, 'triple_gstring'),
            (r'"', String.GString.GStringBegin, 'gstring'),
            (r'\$/', String.GString.GStringBegin, 'dolar_slashy_gstring'),
            # Disambiguation between division and slashy gstrings
            (r'/=', Operator),
            (r'([0-9][0-9]*\.[0-9]+([eE][0-9]+)?[fd]?)([^\S\n]*)/\*', bygroups(Number.Float, Whitespace), 'multiline_comment'),
            (r'([0-9][0-9]*\.[0-9]+([eE][0-9]+)?[fd]?)([^\S\n]*)//(.*?)$', bygroups(Number.Float, Whitespace, Comment.Single)),
            (r'([0-9][0-9]*\.[0-9]+([eE][0-9]+)?[fd]?)([^\S\n]*)(/)', bygroups(Number.Float, Whitespace, Operator)),
            (r'(0x[0-9a-fA-F]+)([^\S\n]*)/\*', bygroups(Number.Hex, Whitespace), 'multiline_comment'),
            (r'(0x[0-9a-fA-F]+)([^\S\n]*)//(.*?)$', bygroups(Number.Hex, Whitespace, Comment.Single)),
            (r'(0x[0-9a-fA-F]+)([^\S\n]*)(/)', bygroups(Number.Hex, Whitespace, Operator)),
            (r'([0-9]+L?)([^\S\n]*)/\*', bygroups(Number.Integer, Whitespace), 'multiline_comment'),
            (r'([0-9]+L?)([^\S\n]*)//(.*?)$', bygroups(Number.Integer, Whitespace, Comment.Single)),
            (r'([0-9]+L?)([^\S\n]*)(/)', bygroups(Number.Integer, Whitespace, Operator)),
            #(r'([\]})])([^\S\n]*)(/)', bygroups(Operator, Whitespace, String.GString.GStringBegin), ('#pop', '#pop', 'slashy_gstring')),
            #(r'([~^*!%&<>|+=:;,.?-])([^\S\n]*)(/)', bygroups(Operator, Whitespace, String.GString.GStringBegin), 'slashy_gstring'),
            #(r'""".*?"""', String.Double),
            (r"'''.*?'''", String.Single),
            #(r'"(\\\\|\\[^\\]|[^"\\])*"', String.Double),
            (r"'(\\\\|\\[^\\]|[^'\\])*'", String.Single),
            #(r'\$/((?!/\$).)*/\$', String),
            #(r'/(\\\\|\\[^\\\n]|[^/\\\n])+/', String),
            (r"'\\.'|'[^\\]'|'\\u[0-9a-fA-F]{4}'", String.Char),
            (r'(\.)([a-zA-Z_]\w*)([^\S\n]*)/\*', bygroups(Operator, Name.Attribute, Whitespace), 'multiline_comment'),
            (r'(\.)([a-zA-Z_]\w*)([^\S\n]*)//(.*?)$', bygroups(Operator, Name.Attribute, Whitespace, Comment.Single)),
            (r'(\.)([a-zA-Z_]\w*)([^\S\n]*)(/)', bygroups(Operator, Name.Attribute, Whitespace, Operator)),
            (r'(\.)([a-zA-Z_]\w*)', bygroups(Operator, Name.Attribute)),
            (r'[a-zA-Z_]\w*:', Name.Label),
            (r'([a-zA-Z_$]\w*)([^\S\n]*)/\*', bygroups(Name, Whitespace), 'multiline_comment'),
            (r'([a-zA-Z_$]\w*)([^\S\n]*)//(.*?)$', bygroups(Name, Whitespace, Comment.Single)),
            (r'([a-zA-Z_$]\w*)([^\S\n]*)(/)', bygroups(Name, Whitespace, Operator)),
            (r'[a-zA-Z_$]\w*', Name),
            (r'\{', Operator, 'braces'),
            (r'\(', Operator, 'parens'),
            (r'\[', Operator, 'brackets'),
            #(r'[~^*!%&<>|+=:;,./?-]', Operator),
            (r'[~^*!%&<>|+=:;,.?-]', Operator),
            (r'[0-9][0-9]*\.[0-9]+([eE][0-9]+)?[fd]?', Number.Float),
            (r'0x[0-9a-fA-F]+', Number.Hex),
            (r'[0-9]+L?', Number.Integer),
            (r'([\]})])([^\S\n]*)/\*', bygroups(Operator, Whitespace), ('#pop', '#pop', 'multiline_comment')),
            (r'([\]})])([^\S\n]*)//(.*?)$', bygroups(Operator, Whitespace, Comment.Single), ('#pop', '#pop')),
            (r'([\]})])([^\S\n]*)(/)', bygroups(Operator, Whitespace, Operator), ('#pop', '#pop')),
            (r'[\]})]', Operator, ('#pop', '#pop')),
            (r'/', String.GString.GStringBegin, 'slashy_gstring'),
            (r'\n', Whitespace),
#            default("#pop"),
        ],
        "multiline_comment": [
            (r'(.*?)\*/', bygroups(Comment.Multiline), '#pop'),
        ],
        "braces": [
            (r"\}", Operator, '#pop'),
            default("base"),
        ],
        "parens": [
            (r"\)", Operator, '#pop'),
            default("base"),
        ],
        "brackets": [
            (r"\]", Operator, '#pop'),
            default("base"),
        ],
        'class': [
            (r'[a-zA-Z_]\w*', Name.Class, '#pop')
        ],
        'import': [
            (r'[\w.]+\*?', Name.Namespace, '#pop')
        ],
        'gstring_closure': [
            (r'\}', String.GString.ClosureEnd, '#pop'),
            default('base'),
        ],
        'gstring_common': [
            (r'\$[a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)*', String.GString.GStringPath),
            (r'\$\{', String.GString.ClosureBegin, 'gstring_closure'),
        ],
        'gstring_common_escape': [
            include('gstring_common'),
            (r'\\u[0-9A-Fa-f]+', String.Escape),
            (r'\\.', String.Escape),    # Escapes $ " and others
        ],
        'gstring': [
            (r'"', String.GString.GStringEnd, '#pop'),
            include('gstring_common_escape'),
            (r'[^$"\\]+', String.Double),
        ],
        'triple_gstring': [
            (r'"""', String.GString.GStringEnd, '#pop'),
            include('gstring_common_escape'),
            (r'[^$"\\]+', String.Double),
            (r'"', String.Double),
            (r'""', String.Double),
        ],
        'slashy_gstring': [
            (r'/', String.GString.GStringEnd, '#pop'),
            include('gstring_common_escape'),
            (r'[^$\\/]+', String.Double),
            # This is needed for regular expressions
            (r'\$', String.Double),
        ],
        'dolar_slashy_gstring': [
            (r'/\$', String.GString.GStringEnd, '#pop'),
            include('gstring_common'),
            (r'[^$]+', String.Double),
            (r'\$\$', String.Escape),    # Escapes $ " and others
            (r'\$/', String.Escape),    # Escapes $ " and others
        ],
    }

    def analyse_text(text):
        return shebang_matches(text, r'groovy')
