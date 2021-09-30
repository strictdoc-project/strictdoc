import string


# Strings with embedded variables in Python
# https://stackoverflow.com/a/16553401/598057
class RubyTemplate(string.Template):
    delimiter = "##"


COMMENT_REGEX = "/\\s*(#|(\\/\\/))\\s*/"

SOURCE_FILE_GRAMMAR = RubyTemplate(
    """
SourceFileTraceabilityInfo[noskipws]:
    (nosdoc_blocks += NoSDocBlock |
    (pragmas += RangePragma) |
    SingleLineString)*
;

RangePragma[noskipws]:
  !NoSDocBlockStart
  ##COMMENT_REGEX
  (begin_or_end = "[/" | begin_or_end = "[")
  (reqs_objs += Req[', ']) ']' '\n'?
;

Req[noskipws]:
  uid = /[A-Za-z][A-Z0-9-]+/
;

SingleLineString[noskipws]:
  !NoSDocBlockStart !NoSDocBlockEnd /.*/ '\n'?
;

NoSDocBlockStart[noskipws]:
  ##COMMENT_REGEX '[nosdoc]' '\n'
;

NoSDocBlockEnd[noskipws]:
  ##COMMENT_REGEX '[/nosdoc]' '\n'
;

NoSDocBlock[noskipws]:
    NoSDocBlockStart
    SingleLineString*
    NoSDocBlockEnd
;
"""
).substitute(COMMENT_REGEX=COMMENT_REGEX)
