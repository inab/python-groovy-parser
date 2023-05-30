# python-groovy-parser
Repo with a proof of concept of Groovy parser

The tokenizer is an evolution from Pygments Groovy lexer https://github.com/pygments/pygments/blob/b7c8f35440f591c6687cb912aa223f5cf37b6704/pygments/lexers/jvm.py#L543-L618

The Lark grammar has been created from https://github.com/apache/groovy/blob/3b6909a3dbb574e66f5d0fb6aafb6e28316033a8/src/antlr/GroovyParser.g4 ,
converting it to EBNF using https://bottlecaps.de/convert/ ,
translating the EBNF representation to Lark format partially by hand.

The grammar is being fine tuned to be able to properly parse Nextflow files from
 https://github.com/nf-core/modules.git ,
 https://github.com/nf-core/rnaseq.git ,
 https://github.com/nf-core/viralintegration.git ,
 https://github.com/nf-core/viralrecon ,
 https://github.com/wombat-p/WOMBAT-Pipelines.git
 and others.

Some fixes were inspired on https://github.com/daniellansun/groovy-antlr4-grammar-optimized/tree/master/src/main/antlr4/org/codehaus/groovy/parser/antlr4