TEXT_TYPES_GRAMMAR = r"""
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

FreeTextEnd: /^/ '[/FREETEXT]' '\n';
"""

FREE_TEXT_PARSER_GRAMMAR = r"""
FreeTextContainer[noskipws]:
  parts+=TextPart
;
"""

DOCUMENT_GRAMMAR = r"""
Document[noskipws]:
  '[DOCUMENT]' '\n'
  'TITLE: ' title = /.*$/ '\n'
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
  GrammarElementFieldTag |
  GrammarElementFieldReference
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

GrammarElementFieldReference[noskipws]:
  '  - TITLE: ' title=FieldName '\n'
  '    TYPE: Reference'
    '(' ((types = ReferenceType) (types *= ReferenceTypeXs)) ')' '\n'
  '    REQUIRED: ' (required = BooleanChoice) '\n'
;

ReferenceType[noskipws]:
  ('ParentReqReference' | 'FileReference' | 'BibReference')
;

ReferenceTypeXs[noskipws]:
  /, /- ReferenceType
;

BooleanChoice[noskipws]:
  ('True' | 'False')
;

DocumentConfig[noskipws]:
  ('UID: ' uid = /.*$/ '\n')?
  ('VERSION: ' version = /.*$/ '\n')?
  ('CLASSIFICATION: ' classification = /.*$/ '\n')?

  ('OPTIONS:' '\n'
    ('  MARKUP: ' (markup = MarkupChoice) '\n')?
    ('  AUTO_LEVELS: ' (auto_levels = AutoLevelsChoice) '\n')?
    ('  REQUIREMENT_STYLE: ' (requirement_style = RequirementStyleChoice) '\n')?
    ('  REQUIREMENT_IN_TOC: '
        (requirement_in_toc = RequirementHasTitleChoice) '\n'
    )?
  )?
;

MarkupChoice[noskipws]:
  'RST' | 'Text' | 'HTML'
;

RequirementStyleChoice[noskipws]:
  'Inline' | 'Table'
;

RequirementHasTitleChoice[noskipws]:
  'True' | 'False'
;

AutoLevelsChoice[noskipws]:
  'On' | 'Off'
;
"""

FRAGMENT_GRAMMAR = r"""
Fragment[noskipws]:
  '[FRAGMENT]' '\n'
  section_contents *= SectionOrRequirement
;

"""

SECTION_GRAMMAR = r"""
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
  '\n' (Section | Requirement | CompositeRequirement | FragmentFromFile)
;

FragmentFromFile[noskipws]:
  '[FRAGMENT_FROM_FILE]' '\n'
  'FILE: ' file = /.+$/ '\n'
;

SpaceThenRequirement[noskipws]:
  '\n' (Requirement | CompositeRequirement)
;

SpaceThenFreeText[noskipws]:
  '\n' (FreeText)
;

ReservedKeyword[noskipws]:
  'DOCUMENT' | 'GRAMMAR' | 'SECTION' | 'FRAGMENT_FROM_FILE' | 'FREETEXT'
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
"""

STRICTINC_GRAMMAR = FRAGMENT_GRAMMAR + SECTION_GRAMMAR + TEXT_TYPES_GRAMMAR
STRICTDOC_GRAMMAR = DOCUMENT_GRAMMAR + SECTION_GRAMMAR + TEXT_TYPES_GRAMMAR
FREE_TEXT_GRAMMAR = FREE_TEXT_PARSER_GRAMMAR + TEXT_TYPES_GRAMMAR
