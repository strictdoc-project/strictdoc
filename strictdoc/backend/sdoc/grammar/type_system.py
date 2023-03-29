STRICTDOC_BASIC_TYPE_SYSTEM = r"""
FieldName[noskipws]:
  /[A-Z]+[A-Z_]*/
;

SingleLineString:
  (!MultiLineStringStart /\S/) (!MultiLineStringStart /./)*
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
  ParentReqReference | FileReference | BibReference
;

ParentReqReference[noskipws]:
  '- TYPE: Parent' '\n'
  '  VALUE: ' ref_uid = /.*$/ '\n'
;

FileReference[noskipws]:
  // FileReference is an early, experimental feature. Do not use yet.
  '- TYPE: File' '\n'
  g_file_entry = FileEntry
;

FileEntry[noskipws]:
  ('  FORMAT: ' g_file_format = FileEntryFormat '\n')?
   '  VALUE: ' g_file_path = /.*$/ '\n'
;

FileEntryFormat[noskipws]:
  'Sourcecode' | 'Python' | /[A-Z]+[A-Z_]*/
;

BibReference[noskipws]:
  '- TYPE: BibRef' '\n'
  bib_entry = BibEntry
;

BibEntry[noskipws]:
  ('  FORMAT: ' bib_format = BibEntryFormat '\n')?
   '  VALUE: ' bib_value = /.*$/ '\n'
;

BibEntryFormat[noskipws]:
  'String' | 'BibTex' | 'Citation'
;

"""
