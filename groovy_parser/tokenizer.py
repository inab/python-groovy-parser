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
from typing import cast

from pygments.lexer import (
    Lexer,
    RegexLexer,
    include,
    bygroups,
    using,
    this,
    combined,
    default,
    words,
)
from pygments.token import (
    Text,
    Comment,
    Operator,
    Keyword,
    Name,
    String,
    Number,
    Punctuation,
    Whitespace,
)
from pygments.util import shebang_matches

__all__ = ["GroovyRestrictedTokenizer"]


class GroovyRestrictedTokenizer(RegexLexer):
    """
    For Groovy source code.
    Fixed by jmfernandez

    .. versionadded:: 1.5.1
    """

    name = "Groovy (restricted)"
    url = "https://groovy-lang.org/"
    aliases = ["groovy"]
    filenames = ["*.groovy", "*.gradle", "*.nf"]
    mimetypes = ["text/x-groovy"]

    flags = re.MULTILINE | re.DOTALL

    tokens = {
        "root": [
            # Groovy allows a file to start with a shebang
            (r"#!(.*?)$", Comment.Preproc, "base"),
            default("base"),
        ],
        "base_common": [
            (r"[^\S\n]+", Whitespace),
            # (r'(//.*?)(\n)', bygroups(Comment.Single, Whitespace)),
            (r"//(.*?)$", bygroups(Comment.Single)),  # type: ignore[no-untyped-call]
            (r"(/\*)", bygroups(None), "multiline_comment"),  # type: ignore[no-untyped-call]
            # keywords: go before method names to avoid lexing "throw new XYZ"
            # as a method signature
            (
                r"(assert|break|case|catch|continue|default|do|else|finally|for|"
                r"if|goto|instanceof|new|return|switch|this|throw|try|while|in|as)\b",
                Keyword,
            ),
            # method names
            # (r'^(\s*(?:[a-zA-Z_][\w.\[\]]*\s+)+?)'  # return arguments
            # r'('
            # r'[a-zA-Z_]\w*'                        # method name
            # r'|"(?:\\\\|\\[^\\]|[^"\\])*"'         # or double-quoted method name
            # r"|'(?:\\\\|\\[^\\]|[^'\\])*'"         # or single-quoted method name
            # r')'
            # r'(\s*)(\()',                          # signature start
            # bygroups(using(this), Name.Function, Whitespace, Operator)),
            (
                r"(@)(interface)(\s+)",
                bygroups(Keyword, Keyword.Declaration, Whitespace),  # type: ignore[no-untyped-call]
                "class",
            ),
            (r"@[a-zA-Z_][\w.]*", Name.Decorator),
            (
                r"(abstract|const|extends|final|implements|native|private|"
                r"protected|public|static|strictfp|super|synchronized|throws|"
                r"transient|volatile)\b",
                Keyword.Declaration,
            ),
            (
                r"(def|boolean|byte|char|double|float|int|long|short|void)\b",
                Keyword.Type,
            ),
            (r"(package)(\s+)", bygroups(Keyword.Namespace, Whitespace)),  # type: ignore[no-untyped-call]
            (r"(true|false|null)\b", Keyword.Constant),
            (
                r"(class|interface|enum|trait)(\s+)",
                bygroups(Keyword.Declaration, Whitespace),  # type: ignore[no-untyped-call]
                "class",
            ),
            (r"(import)(\s+)(static)(\s+)", bygroups(Keyword.Namespace, Whitespace, Keyword, Whitespace), "import"),  # type: ignore[no-untyped-call]
            (r"(import)(\s+)", bygroups(Keyword.Namespace, Whitespace), "import"),  # type: ignore[no-untyped-call]
            (r'"""', String.GString.GStringBegin, "triple_gstring"),
            (r'"', String.GString.GStringBegin, "gstring"),
            (r"\$/", String.GString.GStringBegin, "dolar_slashy_gstring"),
            # Disambiguation between division and slashy gstrings
            (r"/=", Operator),
            # See https://docs.groovy-lang.org/docs/latest/html/documentation/#_numbers
            (r"0b[01](?:_?[01]+)*[LlGg]?", Number.Binary, "after_number"),
            (r"0x[0-9a-fA-F](?:_?[0-9a-fA-F]+)*[LlGg]?", Number.Hex, "after_number"),
            (
                r"[0-9](?:_?[0-9]+)*(?:\.[0-9](?:_?[0-9]+)*)?(?:[+-]?[eE][0-9]+)?[FfDdLlGg]?",
                Number.Float,
                "after_number",
            ),
            # Both decimal and octal
            (r"0?[0-9](?:_?[0-9]+)*[LlGg]?", Number.Integer, "after_number"),
            # (r'([\]})])([^\S\n]*)(/)', bygroups(Operator, Whitespace, String.GString.GStringBegin), ('#pop', '#pop', 'slashy_gstring')),
            # (r'([~^*!%&<>|+=:;,.?-])([^\S\n]*)(/)', bygroups(Operator, Whitespace, String.GString.GStringBegin), 'slashy_gstring'),
            # (r'""".*?"""', String.Double),
            (r"'''.*?'''", String.Single),
            # (r'"(\\\\|\\[^\\]|[^"\\])*"', String.Double),
            (r"'(\\\\|\\[^\\]|[^'\\])*'", String.Single),
            # (r'\$/((?!/\$).)*/\$', String),
            # (r'/(\\\\|\\[^\\\n]|[^/\\\n])+/', String),
            (r"'\\.'|'[^\\]'|'\\u[0-9a-fA-F]{4}'", String.Char),
            (r"(\.)([a-zA-Z_]\w*)", bygroups(Operator, Name.Attribute), "after_number"),  # type: ignore[no-untyped-call]
            (r"[a-zA-Z_]\w*:", Name.Label),
            (r"[a-zA-Z_$]\w*", Name, "after_number"),
            (r"\{", Operator, "braces"),
            (r"\(", Operator, "parens"),
            (r"\[", Operator, "brackets"),
            # (r'[~^*!%&<>|+=:;,./?-]', Operator),
            (r"[~^*!%&<>|+=:;,.?-]", Operator),
            (r"/", String.GString.GStringBegin, "slashy_gstring"),
            # Silencing the escaped newline
            (r"(\\$\n)", bygroups(None)),  # type: ignore[no-untyped-call]
            (r"\n", Whitespace),
        ],
        "after_number": [
            (r"([^\S\n]*)/\*", bygroups(Whitespace), ("#pop", "multiline_comment")),  # type: ignore[no-untyped-call]
            (r"([^\S\n]*)//(.*?)$", bygroups(Whitespace, Comment.Single), "#pop"),  # type: ignore[no-untyped-call]
            (r"([^\S\n]*)(/)", bygroups(Whitespace, Operator), "#pop"),  # type: ignore[no-untyped-call]
            default("#pop"),
        ],
        "base": [
            include("base_common"),
            (r"[\]})]", Operator, ("#pop", "#pop", "after_number")),
        ],
        "base_gstring_closure": [
            include("base_common"),
            (r"[\])]", Operator, ("#pop", "#pop", "after_number")),
            default("#pop"),
        ],
        "multiline_comment": [
            (r"(.*?)\*/", bygroups(Comment.Multiline), "#pop"),  # type: ignore[no-untyped-call]
        ],
        "braces": [
            (r"\}", Operator, ("#pop", "after_number")),
            default("base"),
        ],
        "parens": [
            (r"\)", Operator, ("#pop", "after_number")),
            default("base"),
        ],
        "brackets": [
            (r"\]", Operator, ("#pop", "after_number")),
            default("base"),
        ],
        "class": [(r"[a-zA-Z_]\w*", Name.Class, "#pop")],
        "import": [(r"[\w.]+\*?", Name.Namespace, "#pop")],
        "gstring_closure": [
            (r"\}", String.GString.ClosureEnd, "#pop"),
            default("base_gstring_closure"),
        ],
        "gstring_common": [
            (
                r"\$[a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)*",
                String.GString.GStringPath,
            ),
            (r"\$\{", String.GString.ClosureBegin, "gstring_closure"),
        ],
        "gstring_common_escape": [
            include("gstring_common"),
            (r"\\u[0-9A-Fa-f]+", String.Escape),
            (r"\\.", String.Escape),  # Escapes $ " and others
        ],
        "gstring": [
            (r'"', String.GString.GStringEnd, "#pop"),
            include("gstring_common_escape"),
            (r'[^$"\\]+', String.Double),
        ],
        "triple_gstring": [
            (r'("+)(""")', bygroups(String.Double, String.GString.GStringEnd), "#pop"),  # type: ignore[no-untyped-call]
            (r'"""', String.GString.GStringEnd, "#pop"),
            include("gstring_common_escape"),
            (r'[^$"\\]+', String.Double),
            (r'""', String.Double),
            (r'"', String.Double),
        ],
        "slashy_gstring": [
            (r"\\\\/", String.Escape),  # Escapes /
            include("gstring_common_escape"),
            (r"[^$\\/]+", String.Double),
            # This is needed for regular expressions
            (r"\$", String.Double),
            (r"/", String.GString.GStringEnd, "#pop"),
        ],
        "dolar_slashy_gstring": [
            (r"/\$", String.GString.GStringEnd, "#pop"),
            include("gstring_common"),
            (r"[^/$]+(?:/+[^/$]+)*", String.Double),
            (r"\$\$", String.Escape),  # Escapes $ " and others
            (r"\$/", String.Escape),  # Escapes $ " and others
        ],
    }

    @staticmethod
    def analyse_text(text: "str") -> "bool":
        return cast("bool", shebang_matches(text, r"groovy"))  # type: ignore[no-untyped-call]
