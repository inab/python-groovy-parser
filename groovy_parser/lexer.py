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

# https://github.com/daniellansun/groovy-antlr4-grammar-optimized/tree/master/src/main/antlr4/org/codehaus/groovy/parser/antlr4

import inspect
import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import (
        Any,
        Iterator,
        Mapping,
        MutableMapping,
        MutableSequence,
        Sequence,
        Tuple,
        Optional,
    )
    from lark.common import (
        LexerConf,
    )
    from pygments.token import (
        _TokenType,
    )

from pygments.token import Token
from lark.lexer import Lexer, Token as LarkToken

# Mapping between Pygment tokens and TERMINALS
# used in groovy grammar

GMAPPER: "Mapping[_TokenType, Mapping[Optional[str], Optional[str]]]" = {
    Token.Name: {
        None: "IDENTIFIER",
    },
    Token.Name.Attribute: {
        None: "IDENTIFIER",
    },
    Token.Text.Whitespace: {
        "\n": "NL",
        #     None: 'WHITESPACE',
        None: None,
    },
    Token.Comment: {
        None: None,
    },
    Token.Comments: {
        None: None,
    },
    Token.Generic: {
        None: None,
    },
    Token.Other: {
        None: None,
    },
    Token.Keyword: {
        "@": "AT",
        "as": "AS",
        "def": "DEF",
        "in": "IN",
        "trait": "TRAIT",
        "threadsafe": "THREADSAFE",
        "var": "VAR",
        "null": "NULL_LITERAL",
        "true": "BOOLEAN_LITERAL",
        "false": "BOOLEAN_LITERAL",
        "abstract": "ABSTRACT",
        "assert": "ASSERT",
        "boolean": "BOOLEAN",
        "break": "BREAK",
        "yield": "YIELD",
        "byte": "BYTE",
        "case": "CASE",
        "catch": "CATCH",
        "char": "CHAR",
        "class": "CLASS",
        "const": "CONST",
        "continue": "CONTINUE",
        "default": "DEFAULT",
        "do": "DO",
        "double": "DOUBLE",
        "else": "ELSE",
        "enum": "ENUM",
        "extends": "EXTENDS",
        "final": "FINAL",
        "finally": "FINALLY",
        "float": "FLOAT",
        "for": "FOR",
        "if": "IF",
        "goto": "GOTO",
        "implements": "IMPLEMENTS",
        "import": "IMPORT",
        "instanceof": "INSTANCEOF",
        "int": "INT",
        "interface": "INTERFACE",
        "long": "LONG",
        "native": "NATIVE",
        "new": "NEW",
        "non-sealed": "NON_SEALED",
        "package": "PACKAGE",
        "permits": "PERMITS",
        "private": "PRIVATE",
        "protected": "PROTECTED",
        "public": "PUBLIC",
        "record": "RECORD",
        "return": "RETURN",
        "sealed": "SEALED",
        "short": "SHORT",
        "static": "STATIC",
        "strictfp": "STRICTFP",
        "super": "SUPER",
        "switch": "SWITCH",
        "synchronized": "SYNCHRONIZED",
        "this": "THIS",
        "throw": "THROW",
        "throws": "THROWS",
        "trait": "TRAIT",
        "transient": "TRANSIENT",
        "try": "TRY",
        "void": "VOID",
        "volatile": "VOLATILE",
        "while": "WHILE",
        None: "KEYWORD",
    },
    Token.Operator: {
        "{": "LBRACE",
        "}": "RBRACE",
        "[": "LBRACK",
        "]": "RBRACK",
        "(": "LPAREN",
        ")": "RPAREN",
        ",": "COMMA",
        ";": "SEMI",
        ":": "COLON",
        ".": "DOT",
        "=": "ASSIGN",
        "?": "QUESTION",
        "!": "NOT",
        "+": "ADD",
        "-": "SUB",
        "*": "MUL",
        "/": "DIV",
        "%": "MOD",
        "&": "BITAND",
        "|": "BITOR",
        "^": "XOR",
        "~": "BITNOT",
        "<": "LT",
        ">": "GT",
        "<<": "LSHIFT",
        # ">>": "RSHIFT",
        # ">>>": "URSHIFT",
        "..": "RANGE_INCLUSIVE",
        "<..": "RANGE_EXCLUSIVE_LEFT",
        "..<": "RANGE_EXCLUSIVE_RIGHT",
        "<..<": "RANGE_EXCLUSIVE_FULL",
        "*.": "SPREAD_DOT",
        "?.": "SAFE_DOT",
        "?[": "SAFE_INDEX",
        "??.": "SAFE_CHAIN_DOT",
        "?:": "ELVIS",
        ".&": "METHOD_POINTER",
        "::": "METHOD_REFERENCE",
        "=~": "REGEX_FIND",
        "==~": "REGEX_MATCH",
        "**": "POWER",
        "**=": "POWER_ASSIGN",
        "<=>": "SPACESHIP",
        "===": "IDENTICAL",
        "!==": "NOT_IDENTICAL",
        "->": "ARROW",
        "!instanceof": "NOT_INSTANCEOF",
        "!in": "NOT_IN",
        "==": "EQUAL",
        "<=": "LE",
        ">=": "GE",
        "!=": "NOTEQUAL",
        "&&": "AND",
        "||": "OR",
        "++": "INC",
        "--": "DEC",
        "+=": "ADD_ASSIGN",
        "-=": "SUB_ASSIGN",
        "*=": "MUL_ASSIGN",
        "/=": "DIV_ASSIGN",
        "&=": "AND_ASSIGN",
        "|=": "OR_ASSIGN",
        "^=": "XOR_ASSIGN",
        "%=": "MOD_ASSIGN",
        "<<=": "LSHIFT_ASSIGN",
        ">>=": "RSHIFT_ASSIGN",
        ">>>=": "URSHIFT_ASSIGN",
        "?=": "ELVIS_ASSIGN",
        "...": "ELLIPSIS",
        None: "OPERATOR",
    },
    Token.Literal.Number.Integer: {
        None: "INTEGER_LITERAL",
    },
    Token.Literal.Number.Float: {
        None: "FLOATING_POINT_LITERAL",
    },
    Token.Literal.Number: {
        None: "INTEGER_LITERAL",
    },
}

COMBINED_OPERATORS_HASH: "MutableMapping[str, MutableSequence[str]]" = dict()
for c in GMAPPER[Token.Operator].keys():
    if (c is not None) and len(c) > 1:
        COMBINED_OPERATORS_HASH.setdefault(c[0], []).append(c)


class PygmentsGroovyLexer(Lexer):
    def __init__(self, lexer_conf: "LexerConf"):
        self.logger = logging.getLogger(
            dict(inspect.getmembers(self))["__module__"]
            + "::"
            + self.__class__.__name__
        )
        pass

    def _preprocess_tokens(
        self, data: "Sequence[Tuple[_TokenType, str]]"
    ) -> "Iterator[Tuple[_TokenType, str]]":
        # Operators like == are not properly emitted
        # So this pre-processing step helps
        prev_tokens = list()
        prev_start = -1
        combined_operators = None
        numdata = len(data)
        idata = 0
        while idata < numdata:
            token = data[idata]
            idata += 1
            if combined_operators is not None:
                # Possible combined operator
                join_token = "".join(map(lambda t: t[1], prev_tokens)) + token[1]
                could_combine = False
                for combined_operator in combined_operators:
                    if combined_operator.startswith(join_token):
                        # Save it
                        prev_tokens.append(token)
                        could_combine = True
                        break

                if could_combine:
                    # As it was combined, jump
                    continue
                elif len(prev_tokens) == 1:
                    yield prev_tokens[0]
                    combined_operators = None
                else:
                    # Emit previous, and continue the processing
                    for si in range(len(prev_tokens), 1, -1):
                        join_token = "".join(map(lambda t: t[1], prev_tokens[:si]))
                        for combined_operator in combined_operators:
                            if combined_operator == join_token:
                                yield (prev_tokens[0][0], join_token)
                                could_combine = True
                                break

                        if could_combine:
                            prev_start += si - 1
                            break
                    else:
                        yield prev_tokens[0]

                    idata = prev_start
                    combined_operators = None
                    continue

            if token[0] == Token.Operator:
                # Possible combined operator
                combined_operators = COMBINED_OPERATORS_HASH.get(token[1][0])
                if combined_operators is not None:
                    prev_tokens = [token]
                    prev_start = idata
                else:
                    yield token
            else:
                yield token

        if combined_operators is not None:
            while prev_tokens:
                if len(prev_tokens) == 1:
                    yield prev_tokens[0]
                    prev_tokens = []
                else:
                    # Emit previous, and continue the processing
                    for si in range(len(prev_tokens), 1, -1):
                        join_token = "".join(map(lambda t: t[1], prev_tokens[:si]))
                        could_combine = False
                        for combined_operator in combined_operators:
                            if combined_operator == join_token:
                                yield (prev_tokens[0][0], join_token)
                                prev_tokens = prev_tokens[si:]
                                could_combine = True
                                break

                        if could_combine:
                            break
                    else:
                        yield prev_tokens[0]
                        prev_tokens = prev_tokens[1:]

    def lex(self, data: "Sequence[Tuple[_TokenType, str]]") -> "Iterator[LarkToken]":  # type: ignore[override]
        preproc_tokens = self._preprocess_tokens(data)

        # Lex itself
        start_pos = 0
        start_row = 1
        start_column = 0
        for token_type, raw_token in preproc_tokens:
            base_token_type: "Optional[_TokenType]" = token_type
            token_map = None

            the_tokens: "MutableSequence[Tuple[Optional[str], str, str]]" = []

            # Determining the matching type
            while base_token_type is not None:
                # This check is needed because there could
                # be in the future None returns
                if base_token_type in GMAPPER:
                    token_map = GMAPPER[base_token_type]
                    break

                # Try with the parent
                base_token_type = base_token_type.parent

            # Yield or not
            token = raw_token
            ltok: "Optional[str]" = None
            if token_type == Token.Name.Label:
                the_tokens = [
                    ("IDENTIFIER", raw_token[0:-1], raw_token[0:-1]),
                    ("COLON", ":", ":"),
                ]
            elif token_type == Token.Name.Decorator:
                the_tokens = [
                    ("AT", "@", "@"),
                    ("IDENTIFIER", raw_token[1:], raw_token[1:]),
                ]
            elif token_map is not None:
                ltok = token_map.get(token)
                if ltok is None:
                    ltok = token_map.get(None)

                if ltok == "IDENTIFIER":
                    if raw_token[0].isupper():
                        ltok = "CAPITALIZED_IDENTIFIER"
            elif token_type == Token.Literal.String.Single:
                if token.startswith("'''"):
                    token = raw_token[3:-3]
                else:
                    token = raw_token[1:-1]
                ltok = "STRING_LITERAL"
            elif token_type == Token.Literal.String.GString.GStringBegin:
                ltok = "GSTRING_BEGIN"
            elif token_type == Token.Literal.String.GString.GStringPath:
                the_tokens = [
                    ("GSTRING_PART", "$", "$"),
                ]
                for identifier in raw_token[1:].split("."):
                    the_tokens.append(("IDENTIFIER", identifier, identifier))
                    the_tokens.append(("DOT", ".", "."))
                the_tokens.pop()

            elif token_type == Token.Literal.String.Escape:
                if len(raw_token) == 2:
                    token = raw_token[1:]
                else:
                    token = raw_token.encode("ascii").decode("unicode-escape")
                ltok = "STRING_LITERAL_PART"
            elif token_type == Token.Literal.String.GString.ClosureBegin:
                the_tokens = [
                    ("GSTRING_PART", "$", "$"),
                    ("LBRACE", "{", "{"),
                ]
            elif token_type == Token.Literal.String.GString.ClosureEnd:
                ltok = "RBRACE"
            elif token_type == Token.Literal.String.GString.GStringEnd:
                ltok = "GSTRING_END"
            elif token_type == Token.Literal.String.Double:
                # if token.startswith('"""') and token.endswith('"""'):
                #    token = raw_token[3:-3]
                #    ltok = 'STRING_LITERAL'
                # elif token.startswith('"'):
                #    token = raw_token[1:-1]
                #    ltok = 'STRING_LITERAL'
                # else:
                ltok = "STRING_LITERAL_PART"
            elif token_type == Token.Literal.String:
                if token.startswith("/") and token.endswith("/"):
                    token = raw_token[1:-1]
                    ltok = "STRING_LITERAL"
                else:
                    ltok = "SKIPPABLE"
            else:
                ltok = "SKIPPABLE"

            if len(the_tokens) == 0:
                the_tokens.append((ltok, token, raw_token))

            # There could be more than one token to be processed
            for ltok, the_token, the_raw_token in the_tokens:
                next_start_pos = start_pos + len(the_raw_token)
                next_row = start_row + the_raw_token.count("\n")

                lastnl = the_raw_token.rfind("\n")
                if lastnl >= 0:
                    next_column = len(the_raw_token) - lastnl - 1
                else:
                    next_column = start_column + len(the_raw_token)
                if ltok is not None:
                    self.logger.debug(f"=> Yielding {ltok} {the_token} {token_type}")
                    yield LarkToken(
                        ltok,
                        (token_type, the_token, raw_token),
                        start_pos=start_pos,
                        end_pos=next_start_pos,
                        line=start_row,
                        column=start_column,
                    )
                else:
                    self.logger.debug(f"\tFiltered out {token_type} {the_token}")

                start_pos = next_start_pos
                start_row = next_row
                start_column = next_column
