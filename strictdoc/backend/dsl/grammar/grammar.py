import string


# Strings with embedded variables in Python
# https://stackoverflow.com/a/16553401/598057
class RubyTemplate(string.Template):
    delimiter = "#"


REQUIREMENT_FIELDS = """
  ('UID: ' uid = /.+$/ '\n')?

  ('LEVEL: ' level = /.*/ '\n')?

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
  ('\n' grammar = DocumentGrammar)?
  free_texts *= SpaceThenFreeText
  section_contents *= SectionOrRequirement
;

DocumentGrammar[noskipws]:
  '[GRAMMAR]' '\n'
  'ELEMENTS:' '\n'
  elements += GrammarElement
;

GrammarElement[noskipws]:
  '- TAG: ' tag = /.*$/ '\n'
  '  FIELDS:' '\n'
  fields += GrammarElementField
;

GrammarElementField[noskipws]:
  '  - TITLE: ' title=/.*$/ '\n'
  '    TYPE: ' field_type = /.*$/ '\n'
  '    REQUIRED: ' (required = BooleanChoice) '\n'
;

BooleanChoice[noskipws]:
  ('True' | 'False')
;

DocumentConfig[noskipws]:
  ('VERSION: ' version = /.*$/ '\n')?
  ('NUMBER: ' number = /.*$/ '\n')?
  ('SPECIAL_FIELDS:' '\n' special_fields += ConfigSpecialField)?

  ('OPTIONS:' '\n'
    ('  MARKUP: ' (markup = MarkupChoice) '\n')?
    ('  AUTO_LEVELS: ' (auto_levels = AutoLevelsChoice) '\n')?
  )?
;

ConfigSpecialField[noskipws]:
'- NAME: ' field_name = /.*$/ '\n'
'  TYPE: ' field_type = 'String' '\n'
('  REQUIRED: ' field_required = 'Yes' '\n')?
;

MarkupChoice[noskipws]:
  'RST' | 'Text' | 'HTML'
;

AutoLevelsChoice[noskipws]:
  'On' | 'Off'
;

Section[noskipws]:
  '[SECTION]'
  '\n'
  ('UID: ' uid = /.+$/ '\n')?
  ('LEVEL: ' level = /.*/ '\n')?
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
  '[' requirement_type = /[A-Z]+[A-Z_]*?/ ']' '\n'

  #{REQUIREMENT_FIELDS}
;

CompositeRequirement[noskipws]:
  '[COMPOSITE_' requirement_type = /[A-Z]+[A-Z_]*?/ ']' '\n'

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
\n
"""
).substitute(REQUIREMENT_FIELDS=REQUIREMENT_FIELDS)
