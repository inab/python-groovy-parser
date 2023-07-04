// converted on THU APR 20, 2023, 02:11 (UTC+02) by antlr_4-to-w3c v0.64 which is COPYRIGHT (c) 2011-2023 by GUNTHER RADEMACHER <grd@gmx.net>

compilation_unit : nls ( package_declaration sep? )? script_statements?

script_statements : script_statement ( sep script_statement )* sep?

script_statement : import_declaration
           | type_declaration
           | method_declaration
           | statement

package_declaration : annotations_opt PACKAGE qualified_name

import_declaration : annotations_opt IMPORT STATIC? qualified_name ( DOT MUL | AS identifier )?

type_declaration : class_or_interface_modifiers_opt class_declaration

modifier : class_or_interface_modifier
           | NATIVE
           | SYNCHRONIZED
           | TRANSIENT
           | VOLATILE
           | DEF
           | VAR

modifiers_opt : ( modifiers nls )?

modifiers : modifier ( nls modifier )*

class_or_interface_modifiers_opt : ( class_or_interface_modifiers nls )?

class_or_interface_modifiers : class_or_interface_modifier ( nls class_or_interface_modifier )*

class_or_interface_modifier : annotation
           | PUBLIC
           | PROTECTED
           | PRIVATE
           | STATIC
           | ABSTRACT
           | FINAL
           | STRICTFP
           | DEFAULT

variable_modifier : annotation
           | FINAL
           | DEF
           | VAR
           | PUBLIC
           | PROTECTED
           | PRIVATE
           | STATIC
           | ABSTRACT
           | STRICTFP

variable_modifiers_opt : ( variable_modifiers nls )?

variable_modifiers : variable_modifier ( nls variable_modifier )*

type_parameters : LT nls type_parameter ( COMMA nls type_parameter )* nls GT

// type_parameter : class_name ( EXTENDS nls type_bound )?

type_parameter : annotations_opt class_name ( EXTENDS nls type_bound )?

type_bound : type ( BITAND nls type )*

type_list : type ( COMMA nls type )*

class_declaration : ( CLASS | AT? INTERFACE | ENUM | TRAIT ) identifier nls ( type_parameters nls )? ( EXTENDS nls type_list nls )? ( IMPLEMENTS nls type_list nls )? class_body

class_body : LBRACE nls ( enum_constants ( nls COMMA )? sep? )? ( class_body_declaration ( sep class_body_declaration )* )? sep? RBRACE

enum_constants : enum_constant ( nls COMMA nls enum_constant )*

enum_constant : annotations_opt identifier arguments? anonymous_inner_class_declaration?

class_body_declaration : ( STATIC nls )? block
           | member_declaration

member_declaration : method_declaration
           | field_declaration
           | modifiers_opt class_declaration

method_declaration : modifiers_opt type_parameters? ( return_type nls )? method_name formal_parameters ( DEFAULT nls element_value | ( nls THROWS nls qualified_class_name_list )? ( nls method_body )? )?

// This rule contains a static_gstring to model what it is found in real life, but not in original grammar
method_name : identifier
           | string_literal
           | static_gstring

return_type : standard_type
           | VOID

field_declaration : variable_declaration

variable_declarators : variable_declarator ( COMMA nls variable_declarator )*

variable_declarator : variable_declarator_id ( nls ASSIGN nls variable_initializer )?

variable_declarator_id : identifier

variable_initializer : enhanced_statement_expression

variable_initializers : variable_initializer ( nls COMMA nls variable_initializer )* nls COMMA?

// This rule also differs from the original grammar, due real life cases found 
empty_dims : ( annotations_opt LBRACK nls RBRACK )+

empty_dims_opt : empty_dims?

standard_type : annotations_opt ( primitive_type | standard_class_or_interface_type ) empty_dims_opt

type : annotations_opt ( primitive_type | VOID | general_class_or_interface_type ) empty_dims_opt

class_or_interface_type : ( qualified_class_name | qualified_standard_class_name ) type_arguments?

general_class_or_interface_type : qualified_class_name type_arguments?

standard_class_or_interface_type : qualified_standard_class_name type_arguments?

primitive_type : built_in_primitive_type

type_arguments : LT nls type_argument ( COMMA nls type_argument )* nls GT

type_argument : type
           | annotations_opt QUESTION ( ( EXTENDS | SUPER ) nls type )?

annotated_qualified_class_name : annotations_opt qualified_class_name

qualified_class_name_list : annotated_qualified_class_name ( COMMA nls annotated_qualified_class_name )*

formal_parameters : LPAREN formal_parameter_list? rparen

formal_parameter_list : ( formal_parameter | this_formal_parameter ) ( COMMA nls formal_parameter )*

this_formal_parameter : type THIS

formal_parameter : variable_modifiers_opt type? ELLIPSIS? variable_declarator_id ( nls ASSIGN nls expression )?

method_body : block

qualified_name : qualified_name_element ( DOT qualified_name_element )*

qualified_name_element : identifier
           | DEF
           | IN
           | AS
// This one already appears under 'identifier' definition
//           | TRAIT

// Next three rules were changed to something more meaningful according
// 'qualified_name_elements' names, as it is not finished with '_opt'
qualified_name_elements : ( qualified_name_element DOT )+

qualified_class_name : qualified_name_elements? identifier

qualified_standard_class_name : qualified_name_elements? class_name ( DOT class_name )*

literal : INTEGER_LITERAL
           | FLOATING_POINT_LITERAL
           | string_literal
           | BOOLEAN_LITERAL
           | NULL_LITERAL

// This definition is not in the original grammar
static_gstring : GSTRING_BEGIN STRING_LITERAL_PART+ GSTRING_END

// This definition vastly differs from the original grammar due the way
// the tokenizer had to be built in order to capture the mangling details
// of correct gstrings (specially, slashy ones)
// gstring : GSTRING_BEGIN gstring_value (GSTRING_PART  gstring_value)* GSTRING_END

// First implementation
//gstring : GSTRING_BEGIN STRING_LITERAL_PART* (GSTRING_PART gstring_value STRING_LITERAL_PART* )* GSTRING_END

// Current one, which seems to consume sometimes more memory
gstring : GSTRING_BEGIN GSTRING_END
        | static_gstring
        | GSTRING_BEGIN STRING_LITERAL_PART* (GSTRING_PART gstring_value STRING_LITERAL_PART*)+ GSTRING_END

gstring_value : gstring_path
           | closure

// This rule was rewritten to accommodate to the lexer limitations
// gstring_path : identifier GSTRING_PATH_PART*

gstring_path : identifier
             | identifier DOT gstring_path

lambda_expression : lambda_parameters nls ARROW nls lambda_body

standard_lambda_expression : standard_lambda_parameters nls ARROW nls lambda_body

lambda_parameters : formal_parameters

standard_lambda_parameters : formal_parameters
           | variable_declarator_id

lambda_body : block
           | statement_expression

// This one differs in order to optimize
closure : block
        | LBRACE nls ( formal_parameter_list nls )? ARROW sep? block_statements_opt RBRACE

closure_or_lambda_expression : closure
           | lambda_expression

block_statements_opt : block_statements?

block_statements : block_statement ( sep block_statement )* sep?

annotations_opt : (annotation (nls annotation)* nls)?

annotation : AT annotation_name ( nls LPAREN element_values? rparen )?

element_values : element_value_pairs
           | element_value

annotation_name : qualified_class_name

element_value_pairs : element_value_pair ( COMMA element_value_pair )*

element_value_pair : element_value_pair_name nls ASSIGN nls element_value

element_value_pair_name : identifier
           | keywords

element_value : element_value_array_initializer
           | annotation
           | expression

// This one has additional nls elements due the way the differences
// in the tokenizer and lexer implementation
element_value_array_initializer : LBRACK ( nls element_value ( nls COMMA element_value )* nls COMMA? )? nls RBRACK

block : LBRACE sep? block_statements_opt RBRACE

block_statement : local_variable_declaration
           | statement

local_variable_declaration : variable_declaration

variable_declaration : modifiers nls ( type? variable_declarators | type_name_pairs nls ASSIGN nls variable_initializer )
           | type variable_declarators

type_name_pairs : LPAREN type_name_pair ( COMMA type_name_pair )* rparen

type_name_pair : type? variable_declarator_id

variable_names : LPAREN variable_declarator_id ( COMMA variable_declarator_id )+ rparen

conditional_statement : if_else_statement
           | switch_statement

if_else_statement : IF expression_in_par nls statement ( ( nls | sep ) ELSE nls statement )?

switch_statement : SWITCH expression_in_par nls LBRACE nls ( switch_block_statement_group+ nls )? RBRACE

loop_statement : FOR LPAREN for_control rparen nls statement
            | WHILE expression_in_par nls statement
            | DO nls statement nls WHILE expression_in_par

continue_statement : CONTINUE identifier?

break_statement : BREAK identifier?

try_catch_statement : TRY resources? nls block ( nls catch_clause )* ( nls finally_block )?

assert_statement : ASSERT expression ( nls ( COLON | COMMA ) nls expression )?

// Originally generated
// statement : ( identifier COLON nls )* ( ( SYNCHRONIZED expression_in_par nls )? block | conditional_statement | loop_statement | try_catch_statement | RETURN expression? | THROW expression | break_statement | continue_statement | assert_statement | local_variable_declaration | statement_expression | SEMI )

statement : block
        |   conditional_statement
        |   loop_statement
        |   try_catch_statement
        |   SYNCHRONIZED expression_in_par nls block
        |   RETURN expression?
        |   THROW expression
        |   break_statement
        |   continue_statement
        |   identifier COLON nls statement
        |   assert_statement
        |   local_variable_declaration
        |   statement_expression
        |   SEMI

catch_clause : CATCH LPAREN variable_modifiers_opt catch_type? identifier rparen nls block

catch_type : qualified_class_name ( BITOR qualified_class_name )*

finally_block : FINALLY nls block

resources : LPAREN nls resource_list sep? rparen

resource_list : resource ( sep resource )*

resource : local_variable_declaration
           | expression

switch_block_statement_group : switch_label (nls switch_label)* nls block_statements

switch_label : CASE expression COLON
            | DEFAULT COLON

for_control : enhanced_for_control
           | classical_for_control

enhanced_for_control : variable_modifiers_opt type? variable_declarator_id ( COLON | IN ) expression

classical_for_control : for_init? SEMI expression? SEMI for_update?

for_init : local_variable_declaration
           | expression_list

for_update : expression_list

cast_par_expression : LPAREN type rparen

par_expression : expression_in_par

// Next two rules have additional nls in order to be adapted to the tokenizer and lexer
expression_in_par : LPAREN nls enhanced_statement_expression nls rparen

expression_list : expression_list_element ( nls COMMA nls expression_list_element nls )*

expression_list_element : MUL? expression

enhanced_statement_expression : statement_expression
           | standard_lambda_expression

statement_expression : command_expression

postfix_expression : path_expression ( INC | DEC )?

// The originally translated block is commented out in favour of
// the block based in the base parser, but including the one line IF expressions
//expression : ( cast_par_expression ( cast_par_expression | ( BITNOT | NOT ) nls | INC | DEC | ADD | SUB )* )? postfix_expression
//           | ( ( BITNOT | NOT ) nls | INC | DEC | ADD | SUB ) expression
//           | IF nls expression nls COLON nls expression (nls ELSE nls expression)? 
//           | expression ( ( POWER | ADD | SUB ) nls expression | nls ( ( MUL | DIV | MOD | LT | LSHIFT | GT (GT GT?)? | RSHIFT | URSHIFT | RANGE_INCLUSIVE | RANGE_EXCLUSIVE_LEFT | RANGE_EXCLUSIVE_RIGHT | RANGE_EXCLUSIVE_FULL | LE | GE | IN | NOT_IN | IDENTICAL | NOT_IDENTICAL | EQUAL | NOTEQUAL | SPACESHIP | REGEX_FIND | REGEX_MATCH | BITAND | XOR | BITOR | AND | OR | QUESTION nls expression nls COLON | ELVIS ) nls expression | ( AS | INSTANCEOF | NOT_INSTANCEOF ) nls type | ( ASSIGN | ADD_ASSIGN | SUB_ASSIGN | MUL_ASSIGN | DIV_ASSIGN | AND_ASSIGN | OR_ASSIGN | XOR_ASSIGN | RSHIFT_ASSIGN | URSHIFT_ASSIGN | LSHIFT_ASSIGN | MOD_ASSIGN | POWER_ASSIGN | ELVIS_ASSIGN ) nls enhanced_statement_expression ) )
//           | variable_names nls ASSIGN nls statement_expression

expression : cast_par_expression cast_operand_expression
            | postfix_expression
            | (BITNOT | NOT) nls expression
            | expression POWER nls expression
            | (INC | DEC | ADD | SUB) expression
            | expression nls (MUL | DIV | MOD) nls expression
            | expression (ADD | SUB) nls expression
            | expression nls ( ( LSHIFT | GT GT GT | GT GT ) | ( RANGE_INCLUSIVE | RANGE_EXCLUSIVE_LEFT | RANGE_EXCLUSIVE_RIGHT | RANGE_EXCLUSIVE_FULL ) ) nls expression
            | expression nls (AS | INSTANCEOF | NOT_INSTANCEOF) nls type
            | expression nls (LE | GE | GT | LT | IN | NOT_IN) nls expression
            | expression nls ( IDENTICAL | NOT_IDENTICAL | EQUAL | NOTEQUAL | SPACESHIP ) nls expression
            | expression nls (REGEX_FIND | REGEX_MATCH) nls expression
            | expression nls BITAND nls expression
            | expression nls XOR nls expression
            | expression nls BITOR nls expression
            | expression nls AND nls expression
            | expression nls OR nls expression
            | expression nls ( QUESTION nls expression nls COLON nls | ELVIS nls ) expression
            | IF nls expression nls COLON nls expression nls ELSE nls expression 
            | variable_names nls ASSIGN nls statement_expression
            | expression nls ( ASSIGN | ADD_ASSIGN | SUB_ASSIGN | MUL_ASSIGN | DIV_ASSIGN | AND_ASSIGN | OR_ASSIGN | XOR_ASSIGN | RSHIFT_ASSIGN | URSHIFT_ASSIGN | LSHIFT_ASSIGN | MOD_ASSIGN | POWER_ASSIGN | ELVIS_ASSIGN ) nls enhanced_statement_expression

cast_operand_expression : cast_par_expression cast_operand_expression
                        | postfix_expression
                        | (BITNOT | NOT) nls cast_operand_expression
                        | (INC | DEC | ADD | SUB) cast_operand_expression

command_expression : expression argument_list? command_argument*

// Fixed according official grammar
command_argument : command_primary ( path_element+ | argument_list )?

path_expression : ( primary | STATIC ) path_element*

path_element : nls ( DOT nls NEW creator | ( ( DOT | SPREAD_DOT | SAFE_DOT | SAFE_CHAIN_DOT ) nls ( AT | non_wildcard_type_arguments )? | ( METHOD_POINTER | METHOD_REFERENCE ) nls ) name_part | closure_or_lambda_expression )
           | arguments
           | index_property_args
           | named_property_args

name_part : identifier
           | string_literal
           | dynamic_member_name
           | keywords

dynamic_member_name : par_expression
           | gstring

index_property_args : (SAFE_INDEX | LBRACK) expression_list? RBRACK

// This rule has extra nls to adequate to what it is emitted by the
// tokenizer and lexer (are they really needed?)
named_property_args : (SAFE_INDEX | LBRACK) nls ( named_property_arg_list | COLON ) nls RBRACK

primary : identifier type_arguments?
           | literal
           | gstring
           | NEW nls creator
           | THIS
           | SUPER
           | par_expression
           | closure_or_lambda_expression
           | list
           | map
           | built_in_type

named_property_arg_primary : identifier
                           | literal
                           | gstring
                           | par_expression
                           | list
                           | map

named_arg_primary : identifier
                   | literal
                   | gstring

command_primary : identifier
               | literal
               | gstring

// Next 3 rules have extra nls to adequate to what it is emitted by the
// tokenizer and lexer (are they really needed?)
list : LBRACK nls expression_list? nls COMMA? nls RBRACK

map : LBRACK nls ( map_entry_list nls COMMA? | COLON ) nls RBRACK

map_entry_list : map_entry nls ( COMMA nls map_entry )*

named_property_arg_list : named_property_arg ( COMMA named_property_arg )*

mul_colon_expression : MUL COLON nls expression

map_entry : map_entry_label COLON nls expression
            | mul_colon_expression

named_property_arg : named_property_arg_label COLON nls expression
                    | mul_colon_expression

named_arg : named_arg_label COLON nls expression
            | mul_colon_expression

map_entry_label : keywords
                | primary

named_property_arg_label : keywords
                        | named_property_arg_primary

named_arg_label : keywords
                | named_arg_primary

creator : created_name ( nls arguments anonymous_inner_class_declaration? | dim+ ( nls array_initializer )? )

dim : annotations_opt LBRACK expression? RBRACK

array_initializer : LBRACE nls ( variable_initializers nls )? RBRACE

anonymous_inner_class_declaration : class_body

created_name : annotations_opt ( primitive_type | qualified_class_name type_arguments_or_diamond? )

non_wildcard_type_arguments : LT nls type_list nls GT

type_arguments_or_diamond : LT GT
           | type_arguments

// Next rule has extra nls to adequate to what it is emitted by the
// tokenizer and lexer (are they really needed?)
arguments : LPAREN nls enhanced_argument_list_in_par? nls COMMA? nls rparen

argument_list : first_argument_list_element ( COMMA nls argument_list_element )*

enhanced_argument_list : first_enhanced_argument_list_element ( COMMA nls enhanced_argument_list_element )*

enhanced_argument_list_in_par : enhanced_argument_list_element ( COMMA nls enhanced_argument_list_element )*

first_argument_list_element : expression_list_element
                            | named_arg

argument_list_element : expression_list_element
                        | named_property_arg

// These seem to consume more memory
// first_enhanced_argument_list_element : first_argument_list_element
//                                     | standard_lambda_expression
//  
// enhanced_argument_list_element : argument_list_element
//                                 | standard_lambda_expression

first_enhanced_argument_list_element : expression_list_element
                                    | standard_lambda_expression
                                    | named_arg

enhanced_argument_list_element : expression_list_element
                                | standard_lambda_expression
                                | named_property_arg

string_literal : STRING_LITERAL

class_name : CAPITALIZED_IDENTIFIER

identifier : IDENTIFIER
           | CAPITALIZED_IDENTIFIER
           | VAR
           | IN
           | TRAIT
           | AS

built_in_type : built_in_primitive_type
           | VOID

keywords : ABSTRACT
           | AS
           | ASSERT
           | BREAK
           | CASE
           | CATCH
           | CLASS
           | CONST
           | CONTINUE
           | DEF
           | DEFAULT
           | DO
           | ELSE
           | ENUM
           | EXTENDS
           | FINAL
           | FINALLY
           | FOR
           | GOTO
           | IF
           | IMPLEMENTS
           | IMPORT
           | IN
           | INSTANCEOF
           | INTERFACE
           | NATIVE
           | NEW
           | PACKAGE
           | RETURN
           | STATIC
           | STRICTFP
           | SUPER
           | SWITCH
           | SYNCHRONIZED
           | THIS
           | THROW
           | THROWS
           | TRANSIENT
           | TRAIT
           | THREADSAFE
           | TRY
           | VAR
           | VOLATILE
           | WHILE
           | NULL_LITERAL
           | BOOLEAN_LITERAL
           | built_in_primitive_type
           | VOID
           | PUBLIC
           | PROTECTED
           | PRIVATE

// This one is borrowed from the original ANTLR lexer
built_in_primitive_type: BOOLEAN
                        |   CHAR
                        |   BYTE
                        |   SHORT
                        |   INT
                        |   LONG
                        |   FLOAT
                        |   DOUBLE

rparen : RPAREN

nls : NL*

sep : ( NL | SEMI )+


%declare BOOLEAN
%declare CHAR
%declare BYTE
%declare SHORT
%declare INT
%declare LONG
%declare FLOAT
%declare DOUBLE

%declare ABSTRACT
%declare ADD
%declare ADD_ASSIGN
%declare AND
%declare AND_ASSIGN
%declare APR
%declare ARROW
%declare AS
%declare ASSERT
%declare ASSIGN
%declare AT
%declare BITAND
%declare BITNOT
%declare BITOR
%declare BOOLEAN_LITERAL
%declare BREAK
%declare CAPITALIZED_IDENTIFIER
%declare CASE
%declare CATCH
%declare CLASS
%declare COLON
%declare COMMA
%declare CONST
%declare CONTINUE
%declare COPYRIGHT
%declare DEC
%declare DEF
%declare DEFAULT
%declare DIV
%declare DIV_ASSIGN
%declare DO
%declare DOT
%declare ELLIPSIS
%declare ELSE
%declare ELVIS
%declare ELVIS_ASSIGN
%declare ENUM
%declare EQUAL
%declare EXTENDS
%declare FINAL
%declare FINALLY
%declare FLOATING_POINT_LITERAL
%declare FOR
%declare GE
%declare GOTO
%declare GSTRING_BEGIN
%declare GSTRING_END
%declare GSTRING_PART
%declare GSTRING_PATH
// This symbol is not emitted by the lexer
%declare GSTRING_PATH_PART
%declare GT
%declare GUNTHER
%declare IDENTICAL
%declare IDENTIFIER
%declare IF
%declare IMPLEMENTS
%declare IMPORT
%declare IN
%declare INC
%declare INSTANCEOF
%declare INTEGER_LITERAL
%declare INTERFACE
%declare LBRACE
%declare LBRACK
%declare LE
%declare LPAREN
%declare LSHIFT
%declare LSHIFT_ASSIGN
%declare LT
%declare METHOD_POINTER
%declare METHOD_REFERENCE
%declare MOD
%declare MOD_ASSIGN
%declare MUL
%declare MUL_ASSIGN
%declare NATIVE
%declare NEW
%declare NL
%declare NOT
%declare NOTEQUAL
%declare NOT_IDENTICAL
%declare NOT_IN
%declare NOT_INSTANCEOF
%declare NULL_LITERAL
%declare OR
%declare OR_ASSIGN
%declare PACKAGE
%declare POWER
%declare POWER_ASSIGN
%declare PRIVATE
%declare PROTECTED
%declare PUBLIC
%declare QUESTION
%declare RADEMACHER
// This symbol is not emitted by the lexer
// but the RANGE_EXCLUSIVE_RIGHT one
%declare RANGE_EXCLUSIVE
%declare RANGE_EXCLUSIVE_FULL
%declare RANGE_EXCLUSIVE_LEFT
%declare RANGE_EXCLUSIVE_RIGHT
%declare RANGE_INCLUSIVE
%declare RBRACE
%declare RBRACK
%declare REGEX_FIND
%declare REGEX_MATCH
%declare RETURN
%declare RPAREN
%declare RSHIFT
%declare RSHIFT_ASSIGN
%declare SAFE_CHAIN_DOT
%declare SAFE_DOT
%declare SAFE_INDEX
%declare SEMI
%declare SPACESHIP
%declare SPREAD_DOT
%declare STATIC
%declare STRICTFP
%declare STRING_LITERAL
%declare STRING_LITERAL_PART
%declare SUB
%declare SUB_ASSIGN
%declare SUPER
%declare SWITCH
%declare SYNCHRONIZED
%declare THIS
%declare THREADSAFE
%declare THROW
%declare THROWS
%declare THU
%declare TRAIT
%declare TRANSIENT
%declare TRY
%declare URSHIFT
%declare URSHIFT_ASSIGN
%declare UTC
%declare VAR
%declare VOID
%declare VOLATILE
%declare WHILE
%declare XOR
%declare XOR_ASSIGN
