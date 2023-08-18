REGEX_UID = r"([A-Za-z0-9]+[A-Za-z0-9_\-]*)"
NEGATIVE_FREETEXT_END = "(?!^\\[\\/FREETEXT\\]\n)"
NEGATIVE_INLINE_LINK_START = rf"(?!\[LINK: {REGEX_UID})"
NEGATIVE_ANCHOR_START = rf"(?!^\[ANCHOR: {REGEX_UID})"

TEXT_TYPES_GRAMMAR = rf"""
TextPart[noskipws]:
  (Anchor | InlineLink | NormalString)
;

NormalString[noskipws]:
  (/(?ms){NEGATIVE_FREETEXT_END}{NEGATIVE_INLINE_LINK_START}{NEGATIVE_ANCHOR_START}./)+
;

InlineLink[noskipws]:
  '[LINK: ' value = /{REGEX_UID}/ ']'
;

Anchor[noskipws]:
  /^\[ANCHOR: /
  value = /{REGEX_UID}/ (', ' title = /\w+[\s\w+]*/)?
  /\](\Z|\n)/
;
"""

FREE_TEXT_PARSER_GRAMMAR = r"""
FreeTextContainer[noskipws]:
  parts*=TextPart
;
"""

DOCUMENT_GRAMMAR = rf"""
Document[noskipws]:
  '[DOCUMENT]' '\n'
  'TITLE: ' title = SingleLineString '\n'
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
  ('ParentReqReference' | 'ChildReqReference' | 'FileReference' | 'BibReference')
;

ReferenceTypeXs[noskipws]:
  /, /- ReferenceType
;

BooleanChoice[noskipws]:
  ('True' | 'False')
;

DocumentConfig[noskipws]:
  ('UID: ' uid = /{REGEX_UID}/ '\n')?
  ('VERSION: ' version = SingleLineString '\n')?
  ('CLASSIFICATION: ' classification = SingleLineString '\n')?
  ('REQ_PREFIX: ' requirement_prefix = SingleLineString '\n')?

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
  'Inline' | 'Simple' | 'Table' | 'Zebra'
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

SECTION_GRAMMAR = rf"""
Section[noskipws]:
  '[SECTION]'
  '\n'
  ('UID: ' uid = /{REGEX_UID}/ '\n')?
  ('LEVEL: ' custom_level = SingleLineString '\n')?
  'TITLE: ' title = SingleLineString '\n'
  ('REQ_PREFIX: ' requirement_prefix = SingleLineString '\n')?
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
      ((' ' field_value = SingleLineString) '\n') |
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

FreeText[noskipws]:
  /\[FREETEXT\]\n/
  parts*=TextPart
  /\[\/FREETEXT\]\n/
;
"""

STRICTINC_GRAMMAR = FRAGMENT_GRAMMAR + SECTION_GRAMMAR + TEXT_TYPES_GRAMMAR
STRICTDOC_GRAMMAR = DOCUMENT_GRAMMAR + SECTION_GRAMMAR + TEXT_TYPES_GRAMMAR
FREE_TEXT_GRAMMAR = FREE_TEXT_PARSER_GRAMMAR + TEXT_TYPES_GRAMMAR
