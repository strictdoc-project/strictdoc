STRICTDOC_BASIC_TYPE_SYSTEM = r"""
FieldName[noskipws]:
  /[A-Z]+[A-Z_]*/
;

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
  ((!MultiLineStringEnd /(?ms)./)+ | '')
  MultiLineStringEnd-
;

Reference[noskipws]:
  // FileReference is an early, experimental feature. Do not use yet.
  ParentReqReference | FileReference
;

ParentReqReference[noskipws]:
  '- TYPE: ' ref_type = 'Parent' '\n'
  '  VALUE: ' path = /.*$/ '\n'
;

FileReference[noskipws]:
  // FileReference is an early, experimental feature. Do not use yet.
  '- TYPE: ' ref_type = 'File' '\n'
  '  VALUE: ' path = /.*$/ '\n'
;
"""
