import string


# Strings with embedded variables in Python
# https://stackoverflow.com/a/16553401/598057
class RubyTemplate(string.Template):
    delimiter = "#"


SOURCE_FILE_GRAMMAR = """
SourceFileTraceabilityInfo[noskipws]:
    (SingleLineString | pragmas += RangePragma)*
;

RangePragma[noskipws]:
  /.*STRICTDOC / (pragma_type = 'RANGE') ' ' (begin_or_end = 'BEGIN' | begin_or_end = 'END') ': ' (reqs += Req[', ']) '\n'
;

Req[noskipws]:
  /[A-Za-z][A-Z0-9-]+/
;

SingleLineString[noskipws]:
  /(?!.*STRICTDOC RANGE).*/ '\n'
;
"""
