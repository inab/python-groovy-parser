sed -e 's#\([a-z]\)\([A-Z]\)#\1_\L\2#g' -i GroovyParser.ebnf.lark_raw
sed -e 's#\([A-Z][a-z][A-Za-z_]*\)#\U\1#g' GroovyParser.ebnf.lark_raw > GroovyParser.ebnf.lark_raw_2
cp GroovyParser.ebnf.lark_raw_2 master_groovy_parser.g
grep -o -w '[A-Z_]*' GroovyParser.ebnf.lark_raw_2 | sort -u | sed 's#^#%declare #g' >> master_groovy_parser.g