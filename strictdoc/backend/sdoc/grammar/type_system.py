STRICTDOC_BASIC_TYPE_SYSTEM = r"""
FieldName[noskipws]:
  // TBD: reqif import brings in new Capelle datatypes which can contain spaces, dots and have small chars
  //      couldn't find a reqif->sdoc mappings yet. therefore using this to stop textx to complain.
  /[A-Z]+[A-Za-z_. ]*/
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
