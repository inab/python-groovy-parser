#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: Apache-2.0
# groovy-parser, a proof of concept Groovy parser based on Pygments and Lark
# Copyright (C) 2024 Barcelona Supercomputing Center, José M. Fernández
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

import json
import logging
import os
import re
import sys

from typing import (
    cast,
    NamedTuple,
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from typing import (
        IO,
        Iterator,
        MutableSequence,
        Optional,
        Sequence,
        Tuple,
        Union,
    )

    from groovy_parser.parser import (
        EmptyNode,
        LeafNode,
        RuleNode,
    )

from pygments.token import Token

from groovy_parser.parser import (
    parse_groovy_content,
    digest_lark_tree,
)

from lark import (
    Lark,
    Transformer,
    v_args,
)
from lark.visitors import Discard

prev_wants_space = False


def write_groovy(
    t_tree: "Union[RuleNode, LeafNode, EmptyNode]",
    mH: "IO[str]",
    reset_prev_wants_space: "bool" = False,
) -> None:
    global prev_wants_space
    if reset_prev_wants_space:
        prev_wants_space = False
    children = cast("RuleNode", t_tree).get("children")
    if children is not None:
        for child in children:
            write_groovy(child, mH=mH)
    else:
        leaf = cast("LeafNode", t_tree).get("leaf")
        value = cast("LeafNode", t_tree).get("value")
        if value is not None and leaf is not None:
            wants_space = False
            print(f"Leaf {leaf} value {value}")
            if prev_wants_space and leaf in (
                "STRING_LITERAL",
                "IDENTIFIER",
                "CAPITALIZED_IDENTIFIER",
                "LBRACE",
                "GSTRING_BEGIN",
            ):
                # These whitespace separators were silenced
                mH.write(" ")

            if leaf == "STRING_LITERAL":
                mH.write("'")

            mH.write(value)
            if leaf in ("IDENTIFIER", "CAPITALIZED_IDENTIFIER", "RBRACE", "COMMA"):
                wants_space = True
            elif leaf == "STRING_LITERAL":
                mH.write("'")

            prev_wants_space = wants_space


def mirror_groovy_source(
    filename: "str", jsonfile: "str", mirror_filename: "str"
) -> "Union[RuleNode, LeafNode, EmptyNode]":
    with open(filename, mode="r", encoding="utf-8") as wfH:
        content = wfH.read()

    tree = parse_groovy_content(content)

    t_tree = digest_lark_tree(tree, prune=[])

    # These are for debugging purposes
    # logging.debug(tree.pretty())
    # with open(jsonfile, mode="w", encoding="utf-8") as jH:
    #    json.dump(tree, jH, indent=4, cls=LarkFilteringTreeEncoder)
    with open(jsonfile, mode="w", encoding="utf-8") as jH:
        json.dump(t_tree, jH, indent=4)

    with open(mirror_filename, mode="w", encoding="utf-8") as mH:
        write_groovy(t_tree, mH, reset_prev_wants_space=True)

    return t_tree


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
    )
    log = logging.getLogger()  # root logger
    for filename in sys.argv[1:]:
        print(f"* Parsing {filename}")
        logfile = filename + ".lark"
        jsonfile = logfile + ".json"
        mirrored_filename = filename + ".mirrored"
        fH = logging.FileHandler(logfile, mode="w", encoding="utf-8")
        for hdlr in log.handlers[:]:  # remove all old handlers
            log.removeHandler(hdlr)
        log.addHandler(fH)  # set the new handler
        try:
            mirror_groovy_source(filename, jsonfile, mirrored_filename)
        except Exception as e:
            print(f"\tParse failed, see {logfile}")
            logging.exception("Parse failed")
        fH.close()
