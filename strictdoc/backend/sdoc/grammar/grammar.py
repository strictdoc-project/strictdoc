STRICTDOC_GRAMMAR = r"""
Document[noskipws]:
  '[DOCUMENT]' '\n'
  // NAME: is deprecated. Both documents and sections now have TITLE:.
  (('NAME: ' name = /.*$/ '\n') | ('TITLE: ' title = /.*$/ '\n')?)
  (config = DocumentConfig)?
  ('\n' grammar = DocumentGrammar)?
  free_texts *= SpaceThenFreeText
  section_contents *= SectionOrRequirement
;

ReservedKeyword[noskipws]:
  'DOCUMENT' | 'GRAMMAR'
;

DocumentGrammar[noskipws]:
  '[GRAMMAR]' '\n'
  'ELEMENTS:' '\n'
  elements += GrammarElement
;

GrammarElement[noskipws]:
  '- TAG: ' tag = RequirementType '\n'
  '  FIELDS:' '\n'
  fields += GrammarElementField
;

GrammarElementField[noskipws]:
  GrammarElementFieldString |
  GrammarElementFieldSingleChoice |
  GrammarElementFieldMultipleChoice |
  GrammarElementFieldTag
;

GrammarElementFieldString[noskipws]:
  '  - TITLE: ' title=FieldName '\n'
  '    TYPE: String' '\n'
  '    REQUIRED: ' (required = BooleanChoice) '\n'
;

GrammarElementFieldSingleChoice[noskipws]:
  '  - TITLE: ' title=FieldName '\n'
  '    TYPE: SingleChoice'
    '(' ((options = ChoiceOption) (options *= ChoiceOptionXs)) ')' '\n'
  '    REQUIRED: ' (required = BooleanChoice) '\n'
;

GrammarElementFieldMultipleChoice[noskipws]:
  '  - TITLE: ' title=FieldName '\n'
  '    TYPE: MultipleChoice'
    '(' ((options = ChoiceOption) (options *= ChoiceOptionXs)) ')' '\n'
  '    REQUIRED: ' (required = BooleanChoice) '\n'
;

GrammarElementFieldTag[noskipws]:
  '  - TITLE: ' title=FieldName '\n'
  '    TYPE: Tag' '\n'
  '    REQUIRED: ' (required = BooleanChoice) '\n'
;

BooleanChoice[noskipws]:
  ('True' | 'False')
;

DocumentConfig[noskipws]:
  ('VERSION: ' version = /.*$/ '\n')?
  ('NUMBER: ' number = /.*$/ '\n')?

  ('OPTIONS:' '\n'
    ('  MARKUP: ' (markup = MarkupChoice) '\n')?
    ('  AUTO_LEVELS: ' (auto_levels = AutoLevelsChoice) '\n')?
  )?
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

ReservedKeyword[noskipws]:
  'DOCUMENT' | 'GRAMMAR' | 'SECTION' | 'FREETEXT'
;

Requirement[noskipws]:
  '[' !CompositeRequirementTagName requirement_type = RequirementType ']' '\n'
  fields *= RequirementField
;

CompositeRequirementTagName[noskipws]:
  'COMPOSITE_'
;

RequirementType[noskipws]:
  !ReservedKeyword /[A-Z]+(_[A-Z]+)*/
;

RequirementField[noskipws]:
  (
    field_name = 'REFS' ':' '\n'
    (field_value_references += Reference)
  ) |
  (
    field_name = FieldName ':'
    (
      ((' ' field_value = SingleLineString | field_value = '') '\n') |
      (' ' (field_value_multiline = MultiLineString) '\n')
    )
  )
;

CompositeRequirement[noskipws]:
  '[COMPOSITE_' requirement_type = RequirementType ']' '\n'

  fields *= RequirementField

  requirements *= SpaceThenRequirement

  '\n'
  '[/COMPOSITE_REQUIREMENT]' '\n'
;

ChoiceOption[noskipws]:
  /[\w\/-]+( *[\w\/-]+)*/
;

ChoiceOptionXs[noskipws]:
  /, /- ChoiceOption
;

RequirementStatus[noskipws]:
  'Draft' | 'Active' | 'Deleted';

RequirementComment[noskipws]:
  'COMMENT: ' (
    comment_single = SingleLineString | comment_multiline = MultiLineString
  ) '\n'
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
  InlineLinkStart value = /[^\]]*/ ']'
;

"""
