SOURCE_FILE_GRAMMAR = """
SourceFileTraceabilityInfo[noskipws]:
  parts += Part
;

Part[noskipws]:
  // The EmptyLine is needed in addition to the SingleLineString because
  // otherwise textX's get_location() ignores the whitespaces.
  // TODO: Maybe there is a trick to disable that and only use SingleLineString.
  EmptyLine | RangePragma | SingleLineString
;

EmptyLine[noskipws]:
  '\n'
;

RangePragma[noskipws]:
  // It is a hard-won result: it is important that the "@sdoc" is within the
  // regex. Putting it next to the regex as "@sdoc" does not work.
  // TODO: It would be great to check this with the TextX developers.
  /^.*?@sdoc/
  (begin_or_end = "[/" | begin_or_end = "[")
  (reqs_objs += Req[', ']) ']' '\n'?
;

Req[noskipws]:
  uid = /[A-Za-z][A-Za-z0-9\\-]+/
;

SingleLineString[noskipws]:
  !RangePragma /.+/ '\n'?
;
"""
