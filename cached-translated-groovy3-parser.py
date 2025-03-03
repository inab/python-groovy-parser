#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: Apache-2.0
# groovy-parser, a proof of concept Groovy parser based on Pygments and Lark
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
    parse_and_digest_groovy_content,
)

from lark import (
    Lark,
    Transformer,
    v_args,
)
from lark.visitors import Discard


# FilteredOutTokens = (
#    Token.Comment,
#    Token.Comments,
#    Token.Generic,
#    Token.Other,
# )


ROOT_RULE = ["compilation_unit", "script_statements"]

INCLUDE_PROCESS_RULE = [
    #    "script_statement",
    "statement",
    "statement_expression",
    "command_expression",
]

IDENTIFIER_RULE = ["primary", "identifier"]

PRE_IDENTIFIER_NAME = [
    "expression",
    "postfix_expression",
    "path_expression",
]


PROCESS_CHILD = {"leaf": "IDENTIFIER", "value": "process"}

INCLUDE_CHILD = {"leaf": "IDENTIFIER", "value": "include"}

WORKFLOW_CHILD = {"leaf": "IDENTIFIER", "value": "workflow"}


CONTAINER_CHILD = {"leaf": "IDENTIFIER", "value": "container"}

CONDA_CHILD = {"leaf": "IDENTIFIER", "value": "conda"}

TEMPLATE_CHILD = {"leaf": "IDENTIFIER", "value": "template"}


P_RULE = [
    "argument_list",
    "first_argument_list_element",
    "expression_list_element",
    "expression",
    "postfix_expression",
    "path_expression",
]

W_RULE = [
    "argument_list",
    "first_argument_list_element",
    "expression_list_element",
    "expression",
    "postfix_expression",
    "path_expression",
]

NAMELESS_W_RULE = [
    "argument_list",
    "first_argument_list_element",
    "expression_list_element",
    "expression",
    "postfix_expression",
    "path_expression",
    "primary",
    "closure_or_lambda_expression",
    "closure",
]


def extract_strings(node: "Union[EmptyNode, LeafNode, RuleNode]") -> "Iterator[str]":
    leaf_type = node.get("leaf")
    if leaf_type is not None:
        lnode = cast("LeafNode", node)
        if leaf_type in ("STRING_LITERAL", "STRING_LITERAL_PART"):
            yield lnode["value"]
    else:
        children = node.get("children")
        if isinstance(children, list):
            for child in children:
                yield from extract_strings(child)


class NfProcess(NamedTuple):
    name: "str"
    containers: "Sequence[str]"
    condas: "Sequence[str]"
    templates: "Sequence[str]"


def extract_nextflow_containers(
    node: "Union[EmptyNode, LeafNode, RuleNode]",
) -> "Iterator[str]":
    # return [ node ]
    yield from filter(
        lambda s: s not in ("singularity", "docker"), extract_strings(node)
    )


def extract_nextflow_condas(
    node: "Union[EmptyNode, LeafNode, RuleNode]",
) -> "Iterator[str]":
    # return [ node ]
    spsplt = re.compile("[\t ]+")
    for conda_str in extract_strings(node):
        yield from spsplt.split(conda_str)


def extract_nextflow_templates(
    node: "Union[EmptyNode, LeafNode, RuleNode]",
) -> "Iterator[str]":
    # return [ node ]
    yield from extract_strings(node)


def extract_process_features(
    t_tree: "RuleNode",
) -> "Tuple[Sequence[str], Sequence[str], Sequence[str]]":
    templates: "MutableSequence[str]" = []
    containers: "MutableSequence[str]" = []
    condas: "MutableSequence[str]" = []

    # First, sanity check
    # root_rule = t_tree.get("rule")
    # if root_rule[-len(ROOT_RULE):] == ROOT_RULE:

    # Now, capture what it is interesting
    for child in t_tree["children"]:
        if "rule" in child:
            r_child = cast("RuleNode", child)
            child_rule = r_child["rule"]
            unprocessed = True
            if child_rule[-len(INCLUDE_PROCESS_RULE) :] == INCLUDE_PROCESS_RULE:
                # Save the process
                c_children = r_child["children"]
                c_children_0 = cast("RuleNode", c_children[0])
                c_children_0_rule = c_children_0.get("rule")
                if (
                    c_children_0_rule is not None
                    and c_children_0_rule[-len(PRE_IDENTIFIER_NAME) :]
                    == PRE_IDENTIFIER_NAME
                ):
                    c_children_0 = cast("RuleNode", c_children_0["children"][0])
                    c_children_0_rule = c_children_0.get("rule")

                # This is needed to re-evaluate
                if (
                    c_children_0_rule is not None
                    and c_children_0_rule[-len(IDENTIFIER_RULE) :] == IDENTIFIER_RULE
                ):
                    c_children_0_children = c_children_0["children"]

                    if c_children_0_children[0] == CONTAINER_CHILD:
                        containers.extend(extract_nextflow_containers(c_children[1]))
                        unprocessed = False
                    elif c_children_0_children[0] == CONDA_CHILD:
                        # both named and nameless workflows
                        condas.extend(extract_nextflow_condas(c_children[1]))
                        unprocessed = False
                    elif c_children_0_children[0] == TEMPLATE_CHILD:
                        templates.extend(extract_nextflow_templates(c_children[-1]))
                        unprocessed = False

            if unprocessed:
                c_containers, c_condas, c_templates = extract_process_features(r_child)
                containers.extend(c_containers)
                condas.extend(c_condas)
                templates.extend(c_templates)

    return containers, condas, templates


def extract_nextflow_process(node: "RuleNode") -> "NfProcess":
    p_rule = node.get("rule")
    process_name = "<error>"
    templates: "Sequence[str]" = []
    containers: "Sequence[str]" = []
    condas: "Sequence[str]" = []
    if p_rule == P_RULE:
        p_c_children = node["children"]
        assert len(p_c_children) > 0
        assert "children" in p_c_children[0]
        pro_node = cast("RuleNode", p_c_children[0])
        assert len(pro_node["children"]) > 0
        assert "value" in pro_node["children"][0]
        process_name = cast("LeafNode", pro_node["children"][0])["value"]
        process_body = cast("RuleNode", p_c_children[1])
        containers, condas, templates = extract_process_features(process_body)
    return NfProcess(
        name=process_name,
        templates=templates,
        containers=containers,
        condas=condas,
    )


class NfInclude(NamedTuple):
    path: "str"


def extract_nextflow_includes(node: "RuleNode") -> "Sequence[NfInclude]":
    # return [ node ]
    return [
        NfInclude(
            path=path,
        )
        for path in extract_strings(node)
    ]


class NfWorkflow(NamedTuple):
    name: "Optional[str]"


def extract_nextflow_workflow(node: "RuleNode") -> "NfWorkflow":
    nodes = None
    name = None
    if node["rule"] == W_RULE:
        assert len(node["children"]) > 1
        name = cast("LeafNode", cast("RuleNode", node["children"][0])["children"][0])[
            "value"
        ]
        nodes = cast("RuleNode", node["children"][1])["children"]
    elif node["rule"] == NAMELESS_W_RULE:
        nodes = node["children"]

    return NfWorkflow(
        name=name,
    )


def extract_nextflow_features(
    t_tree: "RuleNode",
) -> "Tuple[Sequence[NfProcess], Sequence[NfInclude], Sequence[NfWorkflow]]":
    processes: "MutableSequence[NfProcess]" = []
    includes: "MutableSequence[NfInclude]" = []
    workflows: "MutableSequence[NfWorkflow]" = []

    # First, sanity check
    # root_rule = t_tree.get("rule")
    # if root_rule[-len(ROOT_RULE):] == ROOT_RULE:

    # Now, capture what it is interesting
    for a_child in t_tree["children"]:
        if "rule" in a_child:
            child = cast("RuleNode", a_child)
            child_rule = child["rule"]

            unprocessed = True
            if child_rule[-len(INCLUDE_PROCESS_RULE) :] == INCLUDE_PROCESS_RULE:
                # Save the process
                c_children = child["children"]
                c_children_0 = cast("RuleNode", c_children[0])
                c_children_0_rule = c_children_0.get("rule")
                if (
                    c_children_0_rule is not None
                    and c_children_0_rule[-len(PRE_IDENTIFIER_NAME) :]
                    == PRE_IDENTIFIER_NAME
                ):
                    c_children_0 = cast("RuleNode", c_children_0["children"][0])
                    c_children_0_rule = c_children_0.get("rule")

                # This is needed to re-evaluate
                if (
                    c_children_0_rule is not None
                    and c_children_0_rule[-len(IDENTIFIER_RULE) :] == IDENTIFIER_RULE
                ):
                    c_children_0_children = c_children_0["children"]

                    if c_children_0_children[0] == PROCESS_CHILD:
                        processes.append(
                            extract_nextflow_process(cast("RuleNode", c_children[1]))
                        )
                        unprocessed = False
                    elif c_children_0_children[0] == WORKFLOW_CHILD:
                        # both named and nameless workflows
                        workflows.append(
                            extract_nextflow_workflow(cast("RuleNode", c_children[1]))
                        )
                        unprocessed = False
                    elif c_children_0_children[0] == INCLUDE_CHILD:
                        includes.extend(
                            extract_nextflow_includes(cast("RuleNode", c_children[-1]))
                        )
                        unprocessed = False

            if unprocessed:
                c_processes, c_includes, c_workflows = extract_nextflow_features(child)
                processes.extend(c_processes)
                includes.extend(c_includes)
                workflows.extend(c_workflows)

    return processes, includes, workflows


def analyze_nf_source(
    filename: "str",
    jsonfile: "str",
    resultfile: "str",
    cache_directory: "Optional[str]" = None,
    ro_cache_directories: "Sequence[str]" = [],
) -> "Union[RuleNode, LeafNode, EmptyNode]":
    with open(filename, mode="r", encoding="utf-8") as wfH:
        content = wfH.read()

    t_tree = parse_and_digest_groovy_content(
        content,
        cache_directory=cache_directory,
        ro_cache_directories=ro_cache_directories,
    )

    # These are for debugging purposes
    # logging.debug(tree.pretty())
    # with open(jsonfile, mode="w", encoding="utf-8") as jH:
    #    json.dump(tree, jH, indent=4, cls=LarkFilteringTreeEncoder)
    with open(jsonfile, mode="w", encoding="utf-8") as jH:
        json.dump(t_tree, jH, indent=4)

    # res = None
    # res = ParseNextflowTreeToDict().transform(tree)
    # import json
    # json.dump(res, sys.stdout, indent=4, sort_keys=True)
    #
    # logging.debug('-->')
    # logging.debug(res) # prints {'alice': [1, 27, 3], 'bob': [4], 'carrie': [], 'dan': [8, 6]}
    if "rule" in t_tree:
        processes, includes, workflows = extract_nextflow_features(
            cast("RuleNode", t_tree)
        )
    else:
        processes = []
        includes = []
        workflows = []
    with open(resultfile, mode="w", encoding="utf-8") as rW:
        print(f"P {processes}", file=rW)
        print(f"I {includes}", file=rW)
        print(f"W {workflows}", file=rW)

    return t_tree


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
    )
    log = logging.getLogger()  # root logger
    cache_directory = os.environ.get("GROOVY_CACHEDIR")
    if cache_directory is not None:
        print(f"* Using as caching directory {cache_directory}")
        os.makedirs(cache_directory, exist_ok=True)
    else:
        print(
            "[WARNING] No caching is done. If you want to cache parsed content declare variable GROOVY_CACHEDIR"
        )

    ro_cache_directories = []
    cache_directory_ro = os.environ.get("GROOVY_CACHEDIRS_RO")
    if cache_directory_ro is not None:
        print(f"* Using as read-only caching directories {cache_directory_ro}")
        ro_cache_directories = cache_directory_ro.split(":")
    else:
        print(
            "[WARNING] No read-only caching is used. If you want to use cached parsed contents declare variable GROOVY_CACHEDIRS_RO, separating more than one path by colons"
        )
    for filename in sys.argv[1:]:
        print(f"* Parsing {filename}")
        logfile = filename + ".lark"
        jsonfile = logfile + ".json"
        resultfile = logfile + ".result"
        fH = logging.FileHandler(logfile, mode="w", encoding="utf-8")
        for hdlr in log.handlers[:]:  # remove all old handlers
            log.removeHandler(hdlr)
        log.addHandler(fH)  # set the new handler
        try:
            analyze_nf_source(
                filename,
                jsonfile,
                resultfile,
                cache_directory=cache_directory,
                ro_cache_directories=ro_cache_directories,
            )
        except Exception as e:
            print(f"\tParse failed, see {logfile}")
            logging.exception("Parse failed")
        fH.close()
