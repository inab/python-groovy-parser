# python-groovy-parser

Python package which implements a Groovy 3.0.X parser, using both Pygments, Lark and the corresponding grammar.

The tokenizer, lexer and grammar have being tested, stressed and fine tuned
to be able to properly parse both Nextflow (i.e. `*.nf`), `nextflow.config`-like files
and real Groovy code from:

* https://github.com/nf-core/modules.git
* https://github.com/nf-core/rnaseq.git
* https://github.com/nf-core/viralintegration.git
* https://github.com/nf-core/viralrecon.git
* https://github.com/wombat-p/WOMBAT-Pipelines.git
* https://github.com/nextflow-io/nextflow.git

## Install
You can install the development version of this package through pip just running:

```bash
pip install git+https://github.com/inab/python-groovy-parser.git
```

## Test program

This repo contains a test program called [translated-groovy3-parser.py](translated-groovy3-parser.py),
which demonstrates how to use the parser and digest it a bit.

The program takes one or more files as input.

```bash
git pull https://github.com/nf-core/rnaseq.git
translated-groovy3-parser.py $(find rnaseq -type f -name "*.nf")
```

If an input file is for instance `rnaseq/modules/local/bedtools_genomecov.nf`,
the program generates a log file `rnaseq/modules/local/bedtools_genomecov.nf.lark`,
where the parsing traces are stored (emitted tokens, parsing errors, etc...).

Also, when the parsing task worked properly, it condenses and serializes
the parse tree into a file with extension `.lark.json` (for instance,
`rnaseq/modules/local/bedtools_genomecov.nf.lark.json`).

And as a proof of concept, it tries to identify features from Nextflow files,
like the declared processes, includes and workflows, and they are roughly printed
at a file with extension `.lark.result` (for instance `rnaseq/modules/local/bedtools_genomecov.nf.lark.result`).

# Acknowledgements

The tokenizer is an evolution from Pygments Groovy lexer https://github.com/pygments/pygments/blob/b7c8f35440f591c6687cb912aa223f5cf37b6704/pygments/lexers/jvm.py#L543-L618

The Lark grammar has been created from https://github.com/apache/groovy/blob/3b6909a3dbb574e66f5d0fb6aafb6e28316033a8/src/antlr/GroovyParser.g4 ,
converting it to EBNF using https://bottlecaps.de/convert/ ,
translating the EBNF representation to Lark format partially by hand.

Some fixes were inspired on https://github.com/daniellansun/groovy-antlr4-grammar-optimized/tree/master/src/main/antlr4/org/codehaus/groovy/parser/antlr4
