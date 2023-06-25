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

import importlib.resources
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import lark

from lark import (
    Lark,
)
import lark.exceptions

from .tokenizer import (
    GroovyRestrictedTokenizer,
)
from .lexer import (
    PygmentsGroovyLexer,
)

def create_groovy_parser() -> "Lark":
    parser = Lark.open(
        "GROOVY_3_0_X/master_groovy_parser.g",
        rel_to=__file__,
        lexer=PygmentsGroovyLexer,
    #    parser='lalr',
    #    debug=True,
        start='compilation_unit',
        #lexer_callbacks={
        #    'square_bracket_block': jarlmethod
        #}
    )
    
    return parser

def parse_groovy_content(content: "str") -> "lark.Tree":
    parser = create_groovy_parser()

    try:
        gResLex = GroovyRestrictedTokenizer()
        tokens = list(gResLex.get_tokens(content))
        tree = parser.parse(
            tokens,
        #    on_error=handle_errors
        )
    except lark.exceptions.ParseError as pe:
        raise pe
        #gLex = GroovyTokenizer()
        #tokens = list(gLex.get_tokens(content))
        #tree = parser.parse(
        #    tokens,
        ##    on_error=handle_errors
        #)

    return tree