STRICTDOC_GRAMMAR = """
Document[noskipws]:
  '[DOCUMENT]' '\n'
  'NAME: ' name = /.*$/ '\n'
  section_contents *= SectionOrRequirement
;

SectionOrRequirement[noskipws]:
  '\n' (Section | Requirement | FreeText)
;

Section[noskipws]:
  '[SECTION]' 
  '\n'
  'LEVEL: ' level = INT '\n'
  'TITLE: ' title = /.*$/ '\n'
  section_contents *= SectionOrRequirement
  '\n'
  '[/SECTION]'
  '\n'
;

Requirement[noskipws]:
  '[REQUIREMENT]' '\n'

  ('UID: ' uid = /.*$/ '\n')? 

  ('STATUS: ' status = RequirementStatus '\n')?

  ('TAGS: ' (tags = TagRegex) tags *= TagXs '\n')?

  ('REFS:' '\n' references *= Reference)?

  ('TITLE: ' title = /.*$/ '\n')?

  ('STATEMENT: ' (statement = SingleLineString | statement_multiline = MultiLineString) '\n')?

  ('BODY: ' body = MultiLineString '\n' )?

  comments *= ReqComment
;

TagRegex[noskipws]:
  /[\w\/-]+( *[\w\/-]+)*/
;

TagXs[noskipws]:
  /, /- TagRegex
;

RequirementStatus[noskipws]:
  'Draft' | 'Active' | 'Deleted';

ReqComment[noskipws]:
  'COMMENT: ' (comment = SingleLineString | comment = MultiLineString) '\n'
;

SingleLineString:
  /[^>]{3}.*$/
;

MultiLineString:
  /(?ms)>>>\n(.*?)\n<<</
;

Reference[noskipws]:
  '- TYPE: ' ref_type = ReferenceType '\n'
  '  VALUE: ' path = /.*$/ '\n'
;

ReferenceType[noskipws]:
  'File' | 'Parent'
;

FreeText[noskipws]:
  text = /(?ms)\[FREETEXT\](.*?)\[\/FREETEXT\]/ '\n'
;
"""
