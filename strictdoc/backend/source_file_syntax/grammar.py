import string


# Strings with embedded variables in Python
# https://stackoverflow.com/a/16553401/598057
class RubyTemplate(string.Template):
    delimiter = "#"


SOURCE_FILE_GRAMMAR = """
SourceFileTraceabilityInfo[noskipws]:
    ((pragmas += RangePragma) | SingleLineString)*
;

RangePragma[noskipws]:
  / *(#|(\\/\\/)) */
  (begin_or_end = "[/" | begin_or_end = "[")
  (reqs_objs += Req[', ']) ']' '\n'?
;

Req[noskipws]:
  uid = /[A-Za-z][A-Z0-9-]+/
;

SingleLineString[noskipws]:
  !RangePragma /.*/ '\n'?
;
"""
