STRICTDOC_GRAMMAR = """
Document[noskipws]:
  '[DOCUMENT]' '\n'
  'NAME: ' name = /.*$/ '\n'
  section_contents *= SectionOrRequirement
;

SectionOrRequirement[noskipws]:
  '\n' (Section | Requirement)
;

Section[noskipws]:
  '[SECTION]' 
  '\n'
  'LEVEL: ' level = INT '\n'
  'TITLE: ' title = /.*$/ '\n'
  section_contents *= SectionOrRequirement
  '\n'
  '[/SECTION]'
;

Requirement[noskipws]:
  '[REQUIREMENT]' '\n'

  ('UID: ' uid = /.*$/ '\n')? 

  ('STATUS: ' status = RequirementStatus '\n')?

  ('TAGS: ' (tags = TagRegex) tags *= TagXs '\n')?

  ('REFS:' '\n' references *= Reference)?

  ('TITLE: ' title = /.*$/ '\n')?

  'STATEMENT: ' statement = /.*$/ '\n'

  ('BODY: ' 
    body = Body '\n'
  )?

  comments *= ReqComment
;

TagRegex[noskipws]:
  /\w+( *\w+)?/
;

TagXs[noskipws]:
  /, /- TagRegex
;

RequirementStatus[noskipws]:
  'Draft' | 'Active' | 'Deleted';

ReqComment[noskipws]:
  'COMMENT: ' comment = /.*$/ '\n'
;

Body[noskipws]:
    content = /(?ms)>>>(.*?)<<</
;

Reference[noskipws]:
  '- TYPE: ' ref_type = ReferenceType '\n'
  '  VALUE: ' path = /.*$/ '\n'
;

ReferenceType[noskipws]:
  'File' | 'Parent'
;
"""
