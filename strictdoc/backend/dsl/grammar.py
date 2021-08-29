import string


# Strings with embedded variables in Python
# https://stackoverflow.com/a/16553401/598057
class RubyTemplate(string.Template):
    delimiter = "#"


REQUIREMENT_FIELDS = """
  ('UID: ' uid = /.+$/ '\n')?

  ('STATUS: ' status = RequirementStatus '\n')?

  ('TAGS: ' (tags = TagRegex) tags *= TagXs '\n')?

  ('SPECIAL_FIELDS:' '\n' special_fields += SpecialField)?

  ('REFS:' '\n' references *= Reference)?

  ('TITLE: ' title = /.*$/ '\n')?

  ('STATEMENT: ' (
    statement = SingleLineString | statement_multiline = MultiLineString
  ) '\n')?

  ('BODY: ' body = MultiLineString '\n' )?

  ('RATIONALE: ' (
    rationale = SingleLineString | rationale_multiline = MultiLineString
  ) '\n')?

  comments *= RequirementComment
"""

STRICTDOC_GRAMMAR = RubyTemplate(
    """
Document[noskipws]:
  '[DOCUMENT]' '\n'
  // NAME: is deprecated. Both documents and sections now have TITLE:.
  (('NAME: ' name = /.*$/ '\n') | ('TITLE: ' title = /.*$/ '\n')?)
  (config = DocumentConfig)?
  free_texts *= SpaceThenFreeText
  section_contents *= SectionOrRequirement
;

DocumentConfig[noskipws]:
  ('VERSION: ' version = /.*$/ '\n')?
  ('NUMBER: ' number = /.*$/ '\n')?
  ('SPECIAL_FIELDS:' '\n' special_fields += ConfigSpecialField)?

  ('OPTIONS:' '\n'
    ('  MARKUP: ' (markup = MarkupChoice) '\n')
  )?
;

ConfigSpecialField[noskipws]:
'- NAME: ' field_name = /.*$/ '\n'
'  TYPE: ' field_type = 'String' '\n'
('  REQUIRED: ' field_required = 'Yes' '\n')?
;

MarkupChoice[noskipws]:
  'RST' | 'Text'
;

Section[noskipws]:
  '[SECTION]'
  '\n'
  ('UID: ' uid = /.+$/ '\n')?
  ('LEVEL: ' level = /[1-6]/ '\n')?
  'TITLE: ' title = /.*$/ '\n'
  free_texts *= SpaceThenFreeText
  section_contents *= SectionOrRequirement
  '\n'
  '[/SECTION]'
  '\n'
;

SectionOrRequirement[noskipws]:
  '\n' (Section | Requirement | CompositeRequirement)
;

SpaceThenRequirement[noskipws]:
  '\n' (Requirement | CompositeRequirement)
;

SpaceThenFreeText[noskipws]:
  '\n' (FreeText)
;

Requirement[noskipws]:
  '[REQUIREMENT]' '\n'

  #{REQUIREMENT_FIELDS}
;

CompositeRequirement[noskipws]:
  '[COMPOSITE_REQUIREMENT]' '\n'

  #{REQUIREMENT_FIELDS}

  requirements *= SpaceThenRequirement

  '\n'
  '[/COMPOSITE_REQUIREMENT]' '\n'
;

SpecialField[noskipws]:
  '  ' field_name = /[A-Z][A-Z0-9_]+/ ': ' field_value = /.*$/ '\n'
;

TagRegex[noskipws]:
  /[\\w\\/-]+( *[\\w\\/-]+)*/
;

TagXs[noskipws]:
  /, /- TagRegex
;

RequirementStatus[noskipws]:
  'Draft' | 'Active' | 'Deleted';

RequirementComment[noskipws]:
  'COMMENT: ' (
    comment_single = SingleLineString | comment_multiline = MultiLineString
  ) '\n'
;

SingleLineString:
  /[^>]{3}.*$/
;

MultiLineString:
  /(?ms)>>>\n(.*?)\n<<</
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

FreeText[noskipws]:
  '[FREETEXT]' '\n'
  parts+=TextPart
  FreeTextEnd
;

FreeTextEnd: /^/ '[/FREETEXT]' '\n';

TextPart[noskipws]:
  (InlineLink | NormalString)
;

NormalString[noskipws]:
  (!SpecialKeyword !FreeTextEnd /(?ms)./)*
;

SpecialKeyword:
  InlineLinkStart // more keywords are coming later
;

InlineLinkStart: '[LINK: ';

InlineLink[noskipws]:
  InlineLinkStart value = /[^\\]]*/ ']'
;
"""
).substitute(REQUIREMENT_FIELDS=REQUIREMENT_FIELDS)
