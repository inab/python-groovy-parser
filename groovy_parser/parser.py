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

import gzip
import importlib.resources
import hashlib
import json
import os
import os.path
from typing import (
    cast,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from typing import (
        Any,
        Mapping,
        MutableSequence,
        Optional,
        Sequence,
        Union,
    )
    from lark.tree import ParseTree

    from typing_extensions import (
        TypedDict,
    )

    class EmptyNode(TypedDict):
        pass

    class LeafNode(TypedDict):
        leaf: "str"
        value: "str"

    class RuleNode(TypedDict):
        rule: "Sequence[str]"
        children: "Sequence[Union[EmptyNode, LeafNode, RuleNode]]"


from pygments import (
    __version__ as pygments_version,
)
from lark import (
    __version__ as lark_version,
    Lark,
    Tree as LarkTree,
)
from lark.lexer import Token as LarkToken
from lark.exceptions import ParseError as LarkParseError

from .tokenizer import (
    __file__ as tokenizer_source_path,
    GroovyRestrictedTokenizer,
)
from .lexer import (
    __file__ as lexer_source_path,
    PygmentsGroovyLexer,
)


class LarkTokenEncoder(json.JSONEncoder):
    def default(
        self,
        obj: "Any",
    ) -> "LeafNode":
        if isinstance(obj, LarkToken):
            return {
                "leaf": obj.type,
                #                "value": json.JSONEncoder.default(self, obj.value[1] if isinstance(obj.value, tuple) else obj.value),
                "value": (obj.value[1] if isinstance(obj.value, tuple) else obj.value),
            }

        # Let the base class default method raise the TypeError
        return cast("LeafNode", json.JSONEncoder.default(self, obj))


class LarkFilteringTreeEncoder(LarkTokenEncoder):
    def default(  # type: ignore[override]
        self,
        obj: "Any",
        rule: "Sequence[str]" = [],
        prune: "Sequence[str]" = ["sep", "nls"],
        noflat: "Sequence[str]" = ["script_statement"],
    ) -> "Union[LeafNode, RuleNode, EmptyNode]":
        if isinstance(obj, LarkTree):
            new_rule = cast("MutableSequence[str]", rule[:])
            # This is needed because the type annotation of the data
            # facet from a lark tree is str instead of Token
            # (which is a subclass of str)
            new_rule.append(cast("LarkToken", obj.data).value)
            children = []
            for child in obj.children:
                if isinstance(child, LarkTree) and child.data in prune:
                    continue
                children.append(child)
            if children:
                if (
                    len(children) == 1
                    and isinstance(children[0], LarkTree)
                    and children[0].data not in noflat
                ):
                    return self.default(children[0], rule=new_rule)
                else:
                    return {
                        "rule": new_rule,
                        "children": [self.default(child) for child in children],
                    }
            else:
                # No children!!!!!!!
                return {}

        # Let the base class default method raise the TypeError (if it is the case)
        return super().default(obj)


GROOVY_3_0_X_GRAMMAR = os.path.join(
    os.path.dirname(__file__), "GROOVY_3_0_X", "master_groovy_parser.g"
)


def create_groovy_parser() -> "Lark":
    with open(GROOVY_3_0_X_GRAMMAR, mode="r", encoding="utf-8") as gH:
        parser = Lark(
            gH,
            lexer=PygmentsGroovyLexer,
            #    parser='lalr',
            #    debug=True,
            start="compilation_unit",
            # lexer_callbacks={
            #    'square_bracket_block': jarlmethod
            # }
        )

    return parser


def parse_groovy_content(content: "str") -> "ParseTree":
    parser = create_groovy_parser()

    try:
        gResLex = GroovyRestrictedTokenizer()
        # import logging
        # tokens = []
        # for tok in gResLex.get_tokens(content):
        #    logging.info(f"TOK {tok}")
        #    tokens.append(tok)
        tokens = list(gResLex.get_tokens(content))
        # The type ignore is needed due the poor type annotation of
        # lark, which assumes the input is always a string
        tree = parser.parse(
            tokens,  # type: ignore[arg-type]
            #    on_error=handle_errors
        )
    except LarkParseError as pe:
        raise pe

    return tree


def digest_lark_tree(tree: "ParseTree") -> "Union[RuleNode, LeafNode, EmptyNode]":
    return LarkFilteringTreeEncoder().default(tree)


SIGNATURE_FILES = [
    GROOVY_3_0_X_GRAMMAR,
    tokenizer_source_path,
    lexer_source_path,
    __file__,
]

SIGNATURE_VERSIONS = [
    pygments_version,
    lark_version,
]

BLOCK_SIZE = 1024 * 1024


def parse_and_digest_groovy_content(
    content: "str", cache_directory: "Optional[str]" = None
) -> "Union[RuleNode, LeafNode, EmptyNode]":
    t_tree: "Optional[Union[RuleNode, LeafNode, EmptyNode]]" = None
    hashfile: "Optional[str]" = None
    if cache_directory is not None and os.path.isdir(cache_directory):
        h = hashlib.sha256()
        buff = bytearray(BLOCK_SIZE)

        # The base signature for the caching directory
        for signature_file in SIGNATURE_FILES:
            with open(signature_file, mode="rb") as sH:
                numbytes = 1
                while numbytes > 0:
                    numbytes = sH.readinto(buff)
                    if numbytes > 0:
                        if numbytes < BLOCK_SIZE:
                            h.update(buff[:numbytes])
                        else:
                            h.update(buff)

        # Without forgetting both pygments and lark versions
        for signature_version in SIGNATURE_VERSIONS:
            h.update(signature_version.encode("utf-8"))

        # Now we can obtain the relative directory, unique to this
        # version of the software and its dependencies
        hreldir = h.copy().hexdigest()
        this_cache_directory = os.path.join(cache_directory, hreldir)
        os.makedirs(this_cache_directory, exist_ok=True)

        # Now, let's go for the content signature
        h.update(content.encode("utf-8"))
        hashfile = os.path.join(this_cache_directory, h.hexdigest() + ".json.gz")

        if os.path.isfile(hashfile):
            try:
                with gzip.open(hashfile, mode="rt", encoding="utf-8") as jH:
                    t_tree = json.load(jH)
            except:
                # If it is unreadable, re-create
                pass

    if t_tree is None:
        tree = parse_groovy_content(content)
        t_tree = LarkFilteringTreeEncoder().default(tree)

        if hashfile is not None:
            with gzip.open(hashfile, mode="wt", encoding="utf-8") as jH:
                json.dump(t_tree, jH, sort_keys=True)

    return t_tree
