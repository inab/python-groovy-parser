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
import json
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import (
        Any,
        Mapping,
        Sequence,
        Union,
    )
    import lark
    
    from typing_extensions import (
        TypedDict,
    )
    
    class LeafNode(TypedDict):
        leaf: "str"
        value: "Any"
    
    class RuleNode(TypedDict):
        rule: "Sequence[str]"
        children: "Sequence[Union[LeafNode, RuleNode]]"

from lark import (
    Lark,
)
from lark import Tree as LarkTree
from lark.lexer import Token as LarkToken
import lark.exceptions

from .tokenizer import (
    GroovyRestrictedTokenizer,
)
from .lexer import (
    PygmentsGroovyLexer,
)

class LarkTokenEncoder(json.JSONEncoder):
    def default(self, obj: "Any") -> "LeafNode":
        if isinstance(obj, LarkToken):

            return {
                "leaf": obj.type,
#                "value": json.JSONEncoder.default(self, obj.value[1] if isinstance(obj.value, tuple) else obj.value),
                "value": (obj.value[1] if isinstance(obj.value, tuple) else obj.value),
            }

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

class LarkFilteringTreeEncoder(LarkTokenEncoder):
    def default(self, obj: "Any", rule = [], prune=["sep", "nls"], noflat=["script_statement"]) -> "Union[LeafNode, RuleNode]":
        if isinstance(obj, LarkTree):
            new_rule = rule[:]
            new_rule.append(obj.data.value)
            children = []
            for child in obj.children:
                if isinstance(child, LarkTree) and child.data in prune:
                    continue
                children.append(child)
            if children:
                if len(children) == 1 and isinstance(children[0], LarkTree) and children[0].data not in noflat:
                    return self.default(children[0], rule=new_rule)
                else:
                    return {
                        "rule": new_rule,
                        "children": [
                            self.default(child)
                            for child in children
                        ]
                    }
            else:
                # No children!!!!!!!
                return {}

        # Let the base class default method raise the TypeError (if it is the case)
        return super().default(obj)


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

def parse_groovy_content(content: "str") -> "LarkTree":
    parser = create_groovy_parser()

    try:
        gResLex = GroovyRestrictedTokenizer()
        #import logging
        #tokens = []
        #for tok in gResLex.get_tokens(content):
        #    logging.info(f"TOK {tok}")
        #    tokens.append(tok)
        tokens = list(gResLex.get_tokens(content))
        tree = parser.parse(
            tokens,
        #    on_error=handle_errors
        )
    except lark.exceptions.ParseError as pe:
        raise pe

    return tree

def digest_lark_tree(tree: "LarkTree") -> "Union[RuleNode, LeafNode]":
    return LarkFilteringTreeEncoder().default(tree)