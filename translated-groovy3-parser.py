#!/usr/bin/env python3

import sys
from pygments.token import Token
from groovy_parser.tokenizer import (
    GroovyLexer,
    GroovyRestrictedLexer,
)

from lark import Lark, Transformer, v_args
import lark.exceptions
from lark.lexer import Lexer, Token as LarkToken
from lark.visitors import Discard

# https://github.com/daniellansun/groovy-antlr4-grammar-optimized/tree/master/src/main/antlr4/org/codehaus/groovy/parser/antlr4

# Mapping between Pygment tokens and TERMINALS
# used in groovy grammar
GMAPPER = {
    Token.Name: {
        #"include": 'INCLUDE',
        #"from": 'FROM',
        #"template": 'TEMPLATE',
        #"container": 'CONTAINER',
        #"conda": 'CONDA',
        #"process": 'PROCESS',
        #"workflow": 'WORKFLOW',
        None: 'IDENTIFIER',
    },
    Token.Name.Attribute: {
        None: 'IDENTIFIER',
    },
    #Token.Name.Label: {
    #    "take:": 'TAKE_LABEL',
    #    "main:": 'MAIN_LABEL',
    #    "emit:": 'EMIT_LABEL',
    #    "input:": 'INPUT_LABEL',
    #    "output:": 'OUTPUT_LABEL',
    #    "when:": 'WHEN_LABEL',
    #    "script:": 'SCRIPT_LABEL',
    #    "shell:": 'SHELL_LABEL',
    #    "exec:": 'EXEC_LABEL',
    #    "stub:": 'STUB_LABEL',
    #    None: 'LABEL',
    #},
    Token.Text.Whitespace: {
         "\n": 'NL',
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
        "as": 'AS',
        "def": 'DEF',
        "in": 'IN',
        "trait": 'TRAIT',
        "threadsafe": 'THREADSAFE',
        "var": 'VAR',
        
        "null": 'NULL_LITERAL',
        "true": 'BOOLEAN_LITERAL',
        "false": 'BOOLEAN_LITERAL',

        'abstract': "ABSTRACT",
        'assert': "ASSERT",
        'boolean': "BOOLEAN",
        'break': "BREAK",
        'yield': "YIELD",
        'byte': "BYTE",
        'case': "CASE",
        'catch': "CATCH",
        'char': "CHAR",
        'class': "CLASS",
        'const': "CONST",
        'continue': "CONTINUE",
        'default': "DEFAULT",
        'do': "DO",
        'double': "DOUBLE",
        'else': "ELSE",
        'enum': "ENUM",
        'extends': "EXTENDS",
        'final': "FINAL",
        'finally': "FINALLY",
        'float': "FLOAT",
        'for': "FOR",
        'if': "IF",
        'goto': "GOTO",
        'implements': "IMPLEMENTS",
        'import': "IMPORT",
        'instanceof': "INSTANCEOF",
        'int': "INT",
        'interface': "INTERFACE",
        'long': "LONG",
        'native': "NATIVE",
        'new': "NEW",
        'non-sealed': "NON_SEALED",
        'package': "PACKAGE",
        'permits': "PERMITS",
        'private': "PRIVATE",
        'protected': "PROTECTED",
        'public': "PUBLIC",
        'record': "RECORD",
        'return': "RETURN",
        'sealed': "SEALED",
        'short': "SHORT",
        'static': "STATIC",
        'strictfp': "STRICTFP",
        'super': "SUPER",
        'switch': "SWITCH",
        'synchronized': "SYNCHRONIZED",
        'this': "THIS",
        'throw': "THROW",
        'throws': "THROWS",
        'transient': "TRANSIENT",
        'try': "TRY",
        'void': "VOID",
        'volatile': "VOLATILE",
        'while': "WHILE",


        None: 'KEYWORD',
    },
    Token.Operator: {
        "{": 'LBRACE',
        "}": 'RBRACE',
        "[": 'LBRACK',
        "]": 'RBRACK',
        "(": 'LPAREN',
        ")": 'RPAREN',
        ",": 'COMMA',
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
        ">>": "RSHIFT",
        ">>>": "URSHIFT",
        
        '..': "RANGE_INCLUSIVE",
        '<..': "RANGE_EXCLUSIVE_LEFT",
        '..<': "RANGE_EXCLUSIVE_RIGHT",
        '<..<': "RANGE_EXCLUSIVE_FULL",
        '*.': "SPREAD_DOT",
        '?.': "SAFE_DOT",
        '?[': "SAFE_INDEX",
        '??.': "SAFE_CHAIN_DOT",
        '?:': "ELVIS",
        '.&': "METHOD_POINTER",
        '::': "METHOD_REFERENCE",
        '=~': "REGEX_FIND",
        '==~': "REGEX_MATCH",
        '**': "POWER",
        '**=': "POWER_ASSIGN",
        '<=>': "SPACESHIP",
        '===': "IDENTICAL", 
        '!==': "NOT_IDENTICAL",
        '->': "ARROW",
        '!instanceof': "NOT_INSTANCEOF", 
        '!in': "NOT_IN", 
        '==': "EQUAL",
        '<=': "LE",
        '>=': "GE",
        '!=': "NOTEQUAL",
        '&&': "AND",
        '||': "OR" ,
        '++': "INC",
        '--': "DEC",
        '+=': "ADD_ASSIGN", 
        '-=': "SUB_ASSIGN", 
        '*=': "MUL_ASSIGN", 
        '/=': "DIV_ASSIGN", 
        '&=': "AND_ASSIGN", 
        '|=': "OR_ASSIGN", 
        '^=': "XOR_ASSIGN", 
        '%=': "MOD_ASSIGN", 
        '<<=': "LSHIFT_ASSIGN",
        '>>=': "RSHIFT_ASSIGN",
        '>>>=': "URSHIFT_ASSIGN",
        '?=': "ELVIS_ASSIGN",
        '...': "ELLIPSIS",
        None: 'OPERATOR',
    },
    Token.Literal.Number.Integer: {
        None: 'INTEGER_LITERAL',
    },
    Token.Literal.Number.Float: {
        None: 'FLOATING_POINT_LITERAL',
    },
    Token.Literal.Number: {
        None: 'NUMBER',
    },
}

class PygmentsNextflowLexer(Lexer):
    def __init__(self, lexer_conf):
        pass

    def lex(self, data):
        # Operators like == are not properly emitted
        tokens = list()
        prev_token = None
        for token in data:
            if prev_token is not None:
                # Possible combined operator
                join_token = prev_token[1] + token[1]
                combined_operators = COMBINED_OPERATORS_HASH[join_token[0]]
                
                do_combine = False
                for combined_operator in combined_operators:
                    if combined_operator.startswith(join_token):
                        # Save it
                        prev_token[1] = join_token
                        do_combine = True
                        break
                
                if do_combine:
                    # As it was combined, jump
                    continue
                else:
                    # Emit previous, and continue the processing
                    tokens.append((prev_token[0],prev_token[1]))
                    prev_token = None
            
            if token[0] == Token.Operator:
                # Possible combined operator
                if token[1][0] in COMBINED_OPERATORS_HASH:
                    prev_token = [token[0], token[1]]
                else:
                    tokens.append(token)
            else:
                tokens.append(token)
        
        if prev_token is not None:
            tokens.append(prev_token)

        # Lex itself
        start_pos = 0
        start_row = 1
        start_column = 0
        for token_type, raw_token in tokens:
            base_token_type = token_type
            token_map = None
            
            the_tokens = [ ]
            
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
            if token_type == Token.Name.Label:
                the_tokens = [
                    ('IDENTIFIER', raw_token[0:-1], raw_token[0:-1]),
                    ('COLON', ":", ":")
                ]
            elif token_map is not None:
                ltok = token_map.get(token)
                if ltok is None:
                    ltok = token_map.get(None)
            elif token_type == Token.Literal.String.Single:
                if token.startswith("'''"):
                    token = raw_token[3:-3]
                else:
                    token = raw_token[1:-1]
                ltok = 'STRING_LITERAL'
            elif token_type == Token.Literal.String.GString.GStringBegin:
                ltok = 'GSTRING_BEGIN'
            elif token_type == Token.Literal.String.GString.GStringPath:
                the_tokens = [
                    ('GSTRING_PART', "$", "$"),
                ]
                for identifier in raw_token[1:].split("."):
                    the_tokens.append(('IDENTIFIER', identifier, identifier))
                    the_tokens.append(('DOT', ".", "."))
                the_tokens.pop()
                    
            elif token_type == Token.Literal.String.Escape:
                if len(raw_token) == 2:
                    token = raw_token[1:]
                else:
                    token = raw_token.encode('ascii').decode('unicode-escape')
                ltok = 'STRING_LITERAL_PART'
            elif token_type == Token.Literal.String.GString.ClosureBegin:
                the_tokens = [
                    ('GSTRING_PART', "$", "$"),
                    ('LBRACE', "{", "{"),
                ]
            elif token_type == Token.Literal.String.GString.ClosureEnd:
                ltok = 'RBRACE'
            elif token_type == Token.Literal.String.GString.GStringEnd:
                ltok = 'GSTRING_END'
            elif token_type == Token.Literal.String.Double:
                #if token.startswith('"""') and token.endswith('"""'):
                #    token = raw_token[3:-3]
                #    ltok = 'STRING_LITERAL'
                #elif token.startswith('"'):
                #    token = raw_token[1:-1]
                #    ltok = 'STRING_LITERAL'
                #else:
                ltok = 'STRING_LITERAL_PART'
            elif token_type == Token.Literal.String:
                if token.startswith('/') and token.endswith('/'):
                    token = raw_token[1:-1]
                    ltok = 'STRING_LITERAL'
                else:
                    ltok = 'SKIPPABLE'
            else:
                ltok = 'SKIPPABLE'
            
            if len(the_tokens) == 0:
                the_tokens.append((ltok, token, raw_token))
            
            for ltok, the_token, the_raw_token in the_tokens:
                next_start_pos = start_pos + len(the_raw_token)
                next_row = start_row + the_raw_token.count("\n")
                
                lastnl = the_raw_token.rfind("\n")
                if lastnl >= 0:
                    next_column = len(the_raw_token) - lastnl - 1
                else:
                    next_column = start_column + len(the_raw_token)
                if ltok is not None:
                    print(f"=> Yielding {ltok} {the_token} {token_type}")
                    sys.stdout.flush()
                    yield LarkToken(
                        ltok,
                        (token_type, the_token, raw_token),
                        start_pos=start_pos,
                        end_pos=next_start_pos,
                        line=start_row,
                        column=start_column,
                    )
                else:
                    print(f"\tFiltered out {token_type} {the_token}")
                    sys.stdout.flush()
                
                start_pos = next_start_pos
                start_row = next_row
                start_column = next_column

def handle_errors(err):
    print(f"JARL {err}",file=sys.stderr)
    sys.stderr.flush()
    
    #if err.token.type == 'LABEL':
    #    return True
    
    #return False
    return True

parser = Lark.open("GROOVY_3_0_X/master_groovy_parser.g",
    rel_to=__file__,
    lexer=PygmentsNextflowLexer,
#    parser='lalr',
#    debug=True,
    start='compilation_unit',
    #lexer_callbacks={
    #    'square_bracket_block': jarlmethod
    #}
)


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

COMBINED_OPERATORS = [
    '..',
    '<..',
    '..<',
    '<..<',
    '*.',
    '?.',
    '?[',
    '??.',
    '?:',
    '.&',
    '::',
    '=~',
    '==~',
    '**',
    '**=',
    '<=>',
    '===',
    '!==',
    '->',
    '!instanceof',
    '!in',
    '==',
    '<=',
    '>=',
    '!=',
    '&&',
    '||',
    '++',
    '--',
    '+=',
    '-=',
    '*=',
    '/=',
    '&=',
    '|=',
    '^=',
    '%=',
    '<<=',
    '>>=',
    '>>>=',
    '?=',
    '...',
]

COMBINED_OPERATORS_HASH = dict()
for c in COMBINED_OPERATORS:
    COMBINED_OPERATORS_HASH.setdefault(c[0],[]).append(c)

def analyze_nf_source(filename):
    with open(filename, mode="r", encoding="utf-8") as wfH:
        
        content = wfH.read()
    
    try:
        gResLex = GroovyRestrictedLexer()
        tokens = list(gResLex.get_tokens(content))
        tree = parser.parse(
            tokens,
        #    on_error=handle_errors
        )
    except lark.exceptions.ParseError as pe:
        raise pe
        #gLex = GroovyLexer()
        #tokens = list(gLex.get_tokens(content))
        #tree = parser.parse(
        #    tokens,
        ##    on_error=handle_errors
        #)

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
