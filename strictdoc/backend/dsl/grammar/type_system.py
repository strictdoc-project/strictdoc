STRICTDOC_BASIC_TYPE_SYSTEM = """
SingleLineString:
  (!MultiLineStringStart /./)*
;

MultiLineStringStart[noskipws]:
  '>>>' '\n'
;

MultiLineStringEnd[noskipws]:
  '<<<'
;

MultiLineString[noskipws]:
  MultiLineStringStart-
  (!MultiLineStringEnd /(?ms)./)*
  MultiLineStringEnd-
;
\n
"""
