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

__all__ = ['GroovyLexer', 'GroovyRestrictedLexer']

class GroovyLexer(RegexLexer):
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


class GroovyRestrictedLexer(RegexLexer):
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
            (r'"""', String.GString.GStringBegin, 'triple_gstring'),
            (r'"', String.GString.GStringBegin, 'gstring'),
            (r'\$/', String.GString.GStringBegin, 'dolar_slashy_gstring'),
            (r'/', String.GString.GStringBegin, 'slashy_gstring'),
            #(r'""".*?"""', String.Double),
            (r"'''.*?'''", String.Single),
            #(r'"(\\\\|\\[^\\]|[^"\\])*"', String.Double),
            (r"'(\\\\|\\[^\\]|[^'\\])*'", String.Single),
            #(r'\$/((?!/\$).)*/\$', String),
            #(r'/(\\\\|\\[^\\\n]|[^/\\\n])+/', String),
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
        'gstring_closure': [
            (r'\}', String.GString.ClosureEnd, '#pop'),
            include('base'),
        ],
        'gstring_common': [
            (r'\$[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z][a-zA-Z0-9_]*)*', String.GString.GStringPath),
            (r'\$\{', String.GString.ClosureBegin, 'gstring_closure'),
        ],
        'gstring_common_escape': [
            (r'\\u[0-9A-Fa-f]+', String.Escape),
            (r'\\.', String.Escape),    # Escapes $ " and others
            include('gstring_common'),
        ],
        'gstring': [
            (r'"', String.GString.GStringEnd, '#pop'),
            (r'[^$"\\]+', String.Double),
            include('gstring_common_escape')
        ],
        'triple_gstring': [
            (r'"""', String.GString.GStringEnd, '#pop'),
            (r'[^$"\\]+', String.Double),
            (r'"', String.Double),
            (r'""', String.Double),
            include('gstring_common_escape')
        ],
        'slashy_gstring': [
            (r'/', String.GString.GStringEnd, '#pop'),
            (r'[^$\\/]+', String.Double),
            include('gstring_common_escape')
        ],
        'dolar_slashy_gstring': [
            (r'/\$', String.GString.GStringEnd, '#pop'),
            (r'[^$]+', String.Double),
            (r'\$\$', String.Escape),    # Escapes $ " and others
            (r'\$/', String.Escape),    # Escapes $ " and others
            include('gstring_common')
        ],
    }

    def analyse_text(text):
        return shebang_matches(text, r'groovy')