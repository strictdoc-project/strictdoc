import string


# Strings with embedded variables in Python
# https://stackoverflow.com/a/16553401/598057
class RubyTemplate(string.Template):
    delimiter = '#'


REQUIREMENT_FIELDS = """
  ('UID: ' uid = /.*$/ '\n')? 

  ('STATUS: ' status = RequirementStatus '\n')?

  ('TAGS: ' (tags = TagRegex) tags *= TagXs '\n')?

  ('REFS:' '\n' references *= Reference)?

  ('TITLE: ' title = /.*$/ '\n')?

  ('STATEMENT: ' (statement = SingleLineString | statement_multiline = MultiLineString) '\n')?

  ('BODY: ' body = MultiLineString '\n' )?

  comments *= ReqComment
"""

STRICTDOC_GRAMMAR = RubyTemplate("""
Document[noskipws]:
  '[DOCUMENT]' '\n'
  'NAME: ' name = /.*$/ '\n'
  section_contents *= SectionOrRequirement
;

SectionOrRequirement[noskipws]:
  '\n' (Section | Requirement | CompositeRequirement | FreeText)
;

Section[noskipws]:
  '[SECTION]' 
  '\n'
  'LEVEL: ' level = /[1-6]/ '\n'
  'TITLE: ' title = /.*$/ '\n'
  section_contents *= SectionOrRequirement
  '\n'
  '[/SECTION]'
  '\n'
;

SpaceThenRequirement[noskipws]:
  '\n' (Requirement | CompositeRequirement)
;

Requirement[noskipws]:
  '[REQUIREMENT]' '\n'

  #{REQUIREMENT_FIELDS}
;

CompositeRequirement[noskipws]:
  '[COMPOSITE-REQUIREMENT]' '\n'

  #{REQUIREMENT_FIELDS}
  
  requirements *= SpaceThenRequirement

  '\n'
  '[/COMPOSITE-REQUIREMENT]' '\n'
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
  'COMMENT: ' (comment_single = SingleLineString | comment_multiline = MultiLineString) '\n'
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
  text = /(?ms)\[FREETEXT\]\n(.*?)\n\[\/FREETEXT\]/ '\n'
;
""").substitute(REQUIREMENT_FIELDS=REQUIREMENT_FIELDS)
