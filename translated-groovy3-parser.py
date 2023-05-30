#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# SPDX-License-Identifier: Apache-2.0
# groovy-parser, a proof of concept Groovy parser based on Pygments and Lark
# Copyright (C) 2023 Barcelona Supercomputinh Center, José M. Fernández
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

import sys
from pygments.token import Token

from groovy_parser.parser import (
    parse_groovy_content,
)

from lark import Lark, Transformer, v_args
from lark.visitors import Discard


def handle_errors(err):
    print(f"JARL {err}",file=sys.stderr)
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


def analyze_nf_source(filename):
    with open(filename, mode="r", encoding="utf-8") as wfH:
        
        content = wfH.read()
    
    tree = parse_groovy_content(content)

    #tokens = list(filter(lambda t: all(map(lambda tc: not str(t[0]).startswith(str(tc)), FilteredOutTokens)), gLex.get_tokens(wfH.read())))
    #raw_tokens = [t for t in gLex.get_tokens(wfH.read())]
    #tokens = list(filter(lambda t: all(map(lambda tc: not str(t[0]).startswith(str(tc)), FilteredOutTokens)), raw_tokens))        

    #print(tokens)

    
    print(tree.pretty())
    
    res = None
    #res = ParseNextflowTreeToDict().transform(tree)
    #import json
    #json.dump(res, sys.stdout, indent=4, sort_keys=True)
    # 
    # print('-->')
    # print(res) # prints {'alice': [1, 27, 3], 'bob': [4], 'carrie': [], 'dan': [8, 6]}
    return tree, res


if __name__ == '__main__':
    analyze_nf_source(sys.argv[1])
