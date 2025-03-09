STRICTDOC_BASIC_TYPE_SYSTEM = r"""
BooleanChoice[noskipws]:
  ('True' | 'False')
;

ChoiceOption[noskipws]:
  /[\w\/-]+( *[\w\/-]+)*/
;

ChoiceOptionXs[noskipws]:
  /, /- ChoiceOption
;

RequirementType[noskipws]:
  !ReservedKeyword /[A-Z]+(_[A-Z]+)*/
;

ReservedKeyword[noskipws]:
  'DOCUMENT' | 'GRAMMAR'
;

Reference[noskipws]:
  // FileReference is an early, experimental feature. Do not use yet.
  ParentReqReference | ChildReqReference | FileReference
;

ParentReqReference[noskipws]:
  '- TYPE: Parent' '\n'
  '  VALUE: ' ref_uid = /.*$/ '\n'
  ('  ROLE: ' role = /.+$/ '\n')?
;

ChildReqReference[noskipws]:
  '- TYPE: Child' '\n'
  '  VALUE: ' ref_uid = /.*$/ '\n'
  ('  ROLE: ' role = /.+$/ '\n')?
;


FileReference[noskipws]:
  // FileReference is an early, experimental feature. Do not use yet.
  '- TYPE: File' '\n'
  ('  ROLE: ' role = /.+$/ '\n')?
  g_file_entry = FileEntry
;

FileEntry[noskipws]:
  ('  FORMAT: ' g_file_format = FileEntryFormat '\n')?
   '  VALUE: ' g_file_path = /.*$/ '\n'
  ('  LINE_RANGE: ' g_line_range = /.*$/ '\n')?
  ('  FUNCTION: ' function = /.*$/ '\n')?
  ('  CLASS: ' clazz = /.*$/ '\n')?
;

FileEntryFormat[noskipws]:
  'Sourcecode' | 'Python' | /[A-Z]+[A-Z_]*/
;

"""
