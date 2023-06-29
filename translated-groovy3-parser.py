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
import sys

from typing import NamedTuple

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


def handle_errors(err):
    logging.error(f"JARL {err}",file=sys.stderr)
    sys.stderr.flush()
    
    #if err.token.type == 'LABEL':
    #    return True
    
    #return False
    return True

class ParseNextflowTreeToDict(Transformer):
    @v_args(inline=True)
    def include_sentence(self, kw_include, block, kw_from, include_path):
        return {
            kw_include.value[1]: include_path.value[1]
        }
    
    def ignorable_sentence(self, *params):
        return Discard
    
    def workflow_decl(self, *params):
        return Discard
    
    def default_workflow_decl(self, *params):
        return Discard
    
    def input_block(self, *params):
        return Discard
    
    def output_block(self, *params):
        return Discard
    
    def template_block(self, *params):
        return Discard
    
    def when_block(self, *params):
        return Discard
    
    def script_block(self, *params):
        return Discard
    
    def container_decl(self, params):
        kw_container, tag = params
        return {
            kw_container.value[1]: tag.value[1]
        }
    
    def conda_decl(self, params):
        kw_conda, tag = params
        return {
            kw_conda.value[1]: tag.value[1]
        }
    
    def process_decl(self, params):
        kw_process , name, block = params
        return {
            kw_process.value[1]: name.value[1],
            "payload": block
        }
    
    def template_decl(self, kw_template, template_path):
        return {
            kw_template.value[1]: template_path.value[1]
        }

    def process_block(self, params):
        return list(filter(lambda t: isinstance(t, dict) ,params))

    start = list


FilteredOutTokens = (
    Token.Comment,
    Token.Comments,
    Token.Generic,
    Token.Other,
)


ROOT_RULE = [
    "compilation_unit",
    "script_statements"
]

INCLUDE_PROCESS_RULE = [
#    "script_statement",
    "statement",
    "statement_expression",
    "command_expression"
]

IDENTIFIER_RULE = [
    "primary",
    "identifier"
]

PRE_IDENTIFIER_NAME = [
    "expression",
    "postfix_expression",
    "path_expression",
]


PROCESS_CHILD = {
    "leaf": "IDENTIFIER",
    "value": "process"
}

INCLUDE_CHILD = {
    "leaf": "IDENTIFIER",
    "value": "include"
}

WORKFLOW_CHILD = {
    "leaf": "IDENTIFIER",
    "value": "workflow"
}


CONTAINER_CHILD = {
    "leaf": "IDENTIFIER",
    "value": "container"
}

CONDA_CHILD = {
    "leaf": "IDENTIFIER",
    "value": "conda"
}

TEMPLATE_CHILD = {
    "leaf": "IDENTIFIER",
    "value": "template"
}


P_RULE = [
    "argument_list",
    "first_argument_list_element",
    "expression_list_element",
    "expression",
    "postfix_expression",
    "path_expression"
]

W_RULE = [
    "argument_list",
    "first_argument_list_element",
    "expression_list_element",
    "expression",
    "postfix_expression",
    "path_expression"
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
    "closure"
]


def extract_strings(node: "Union[LeaftNode, RuleNode]"):
    strings = []
    leaf_type = node.get("leaf")
    if leaf_type is not None:
        if leaf_type in ('STRING_LITERAL', 'STRING_LITERAL_PART'):
            strings.append(node["value"])
    else:
        for child in node["children"]:
            strings.extend(extract_strings(child))
            
    return strings


class NfProcess(NamedTuple):
    name: "str"
    containers: "Sequence[str]"
    condas: "Sequence[str]"
    templates: "Sequence[str]"


def extract_nextflow_containers(node) -> "Sequence[str]":
    #return [ node ]
    return list(filter(lambda s: s not in ("singularity", "docker"), extract_strings(node)))

def extract_nextflow_condas(node) -> "Sequence[str]":
    #return [ node ]
    return extract_strings(node)

def extract_nextflow_templates(node) -> "Sequence[str]":
    #return [ node ]
    return extract_strings(node)


def extract_process_features(t_tree) -> "Tuple[Sequence[str], Sequence[str], Sequence[str]]":
    
    templates = []
    containers = []
    condas = []
    
    # First, sanity check
    #root_rule = t_tree.get("rule")
    #if root_rule[-len(ROOT_RULE):] == ROOT_RULE:
    
    # Now, capture what it is interesting
    for child in t_tree["children"]:
        child_rule = child.get("rule")
        if child_rule is not None:
            unprocessed = True
            if child_rule[-len(INCLUDE_PROCESS_RULE):] == INCLUDE_PROCESS_RULE:
                # Save the process
                c_children = child["children"]
                c_children_0 = c_children[0]
                c_children_0_rule = c_children_0.get("rule")
                if c_children_0_rule is not None and c_children_0_rule[-len(PRE_IDENTIFIER_NAME):] == PRE_IDENTIFIER_NAME:
                    c_children_0 = c_children_0["children"][0]
                    c_children_0_rule = c_children_0.get("rule")
                
                # This is needed to re-evaluate
                if c_children_0_rule is not None and c_children_0_rule[-len(IDENTIFIER_RULE):] == IDENTIFIER_RULE:
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
                c_containers, c_condas, c_templates = extract_process_features(child)
                containers.extend(c_containers)
                condas.extend(c_condas)
                templates.extend(c_templates)
    
    return containers, condas, templates

def extract_nextflow_process(node):
    p_rule = node.get("rule")
    process_name="<error>"
    templates = []
    containers = []
    condas = []
    if p_rule == P_RULE:
        p_c_children = node["children"]
        process_name = p_c_children[0]["children"][0]["value"]
        process_body = p_c_children[1]
        containers, condas, templates = extract_process_features(process_body)
    return NfProcess(
        name=process_name,
        templates=templates,
        containers=containers,
        condas=condas,
    )


class NfInclude(NamedTuple):
    path: "str"

def extract_nextflow_includes(node) -> "Sequence[NfInclude]":
    #return [ node ]
    return [
        NfInclude(
            path=path,
        )
        for path in extract_strings(node) 
    ]


class NfWorkflow(NamedTuple):
    name: "Optional[str]"

def extract_nextflow_workflow(node):
    nodes = None
    name = None
    if node["rule"] == W_RULE:
        name = node["children"][0]["children"][0]["value"]
        nodes = node["children"][1]["children"]
    elif node["rule"] == NAMELESS_W_RULE:
        nodes = node["children"]
    
    return NfWorkflow(
        name=name,
    )


def extract_nextflow_features(t_tree):
    
    processes = []
    includes = []
    workflows = []
    
    # First, sanity check
    #root_rule = t_tree.get("rule")
    #if root_rule[-len(ROOT_RULE):] == ROOT_RULE:
    
    # Now, capture what it is interesting
    for child in t_tree["children"]:
        child_rule = child.get("rule")
        if child_rule is not None:
            unprocessed = True
            if child_rule[-len(INCLUDE_PROCESS_RULE):] == INCLUDE_PROCESS_RULE:
                # Save the process
                c_children = child["children"]
                c_children_0 = c_children[0]
                c_children_0_rule = c_children_0.get("rule")
                if c_children_0_rule is not None and c_children_0_rule[-len(PRE_IDENTIFIER_NAME):] == PRE_IDENTIFIER_NAME:
                    c_children_0 = c_children_0["children"][0]
                    c_children_0_rule = c_children_0.get("rule")
                
                # This is needed to re-evaluate
                if c_children_0_rule is not None and c_children_0_rule[-len(IDENTIFIER_RULE):] == IDENTIFIER_RULE:
                    c_children_0_children = c_children_0["children"]
                    
                    if c_children_0_children[0] == PROCESS_CHILD:
                        processes.append(extract_nextflow_process(c_children[1]))
                        unprocessed = False
                    elif c_children_0_children[0] == WORKFLOW_CHILD:
                        # both named and nameless workflows
                        workflows.append(extract_nextflow_workflow(c_children[1]))
                        unprocessed = False
                    elif c_children_0_children[0] == INCLUDE_CHILD:
                        includes.extend(extract_nextflow_includes(c_children[-1]))
                        unprocessed = False
            
            if unprocessed:
                c_processes, c_includes, c_workflows = extract_nextflow_features(child)
                processes.extend(c_processes)
                includes.extend(c_includes)
                workflows.extend(c_workflows)
    
    return processes, includes, workflows
        

def analyze_nf_source(filename, jsonfile, resultfile):
    with open(filename, mode="r", encoding="utf-8") as wfH:
        
        content = wfH.read()
    
    tree = parse_groovy_content(content)

    #tokens = list(filter(lambda t: all(map(lambda tc: not str(t[0]).startswith(str(tc)), FilteredOutTokens)), gLex.get_tokens(wfH.read())))
    #raw_tokens = [t for t in gLex.get_tokens(wfH.read())]
    #tokens = list(filter(lambda t: all(map(lambda tc: not str(t[0]).startswith(str(tc)), FilteredOutTokens)), raw_tokens))        

    #logging.debug(tokens)

    # This one can be written as JSON
    t_tree = digest_lark_tree(tree)
        
    # These are for debugging purposes
    #logging.debug(tree.pretty())
    #with open(jsonfile, mode="w", encoding="utf-8") as jH:
    #    json.dump(tree, jH, indent=4, cls=LarkFilteringTreeEncoder)
    with open(jsonfile, mode="w", encoding="utf-8") as jH:
        json.dump(t_tree, jH, indent=4)
    
    # res = None
    #res = ParseNextflowTreeToDict().transform(tree)
    #import json
    #json.dump(res, sys.stdout, indent=4, sort_keys=True)
    # 
    # logging.debug('-->')
    # logging.debug(res) # prints {'alice': [1, 27, 3], 'bob': [4], 'carrie': [], 'dan': [8, 6]}
    processes, includes, workflows = extract_nextflow_features(t_tree)
    with open(resultfile, mode="w", encoding="utf-8") as rW:
        print(f"P {processes}", file=rW)
        print(f"I {includes}", file=rW)
        print(f"W {workflows}", file=rW)
    
    return t_tree


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
    )
    log = logging.getLogger()  # root logger
    for filename in sys.argv[1:]:
        print(f"* Parsing {filename}")
        logfile = filename + '.lark'
        jsonfile = logfile + '.json'
        resultfile = logfile + '.result'
        fH = logging.FileHandler(logfile, mode="w", encoding="utf-8")
        for hdlr in log.handlers[:]:  # remove all old handlers
            log.removeHandler(hdlr)
        log.addHandler(fH)      # set the new handler
        try:
            analyze_nf_source(filename, jsonfile, resultfile)
        except Exception as e:
            print(f"\tParse failed, see {logfile}")
            logging.exception("Parse failed")
        fH.close()
