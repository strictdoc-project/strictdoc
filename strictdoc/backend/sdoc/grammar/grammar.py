REGEX_UID = r"([\w]+[\w()\-. ]*)"

NEGATIVE_MULTILINE_STRING_START = "(?!>>>\n)"
NEGATIVE_MULTILINE_STRING_END = "(?!^<<<)"
NEGATIVE_RELATIONS = "(?!^RELATIONS)"
NEGATIVE_UID = "(?!^UID)"
NEGATIVE_INLINE_LINK_START = rf"(?!\[LINK: {REGEX_UID})"
NEGATIVE_ANCHOR_START = rf"(?!^\[ANCHOR: {REGEX_UID})"

TEXT_TYPES_GRAMMAR = rf"""
TextPart[noskipws]:
  (Anchor | InlineLink | NormalString)
;

SingleLineTextPart[noskipws]:
  (Anchor | InlineLink | /{NEGATIVE_MULTILINE_STRING_START}\S.*/)
;

NormalString[noskipws]:
  (/(?ms){NEGATIVE_MULTILINE_STRING_END}{NEGATIVE_INLINE_LINK_START}{NEGATIVE_ANCHOR_START}./)+
;

InlineLink[noskipws]:
  '[LINK: ' value = /{REGEX_UID}/ ']'
;

Anchor[noskipws]:
  /^\[ANCHOR: /
  value = /{REGEX_UID}/ (', ' title = /\w+[\s\w+]*/)?
  /\](\Z|\n)/
;

// According to the Strict Grammar Rule #3, both SingleLineString and
// MultiLineString can never be empty strings.
// Both must eventualy start with a non-space character.
SingleLineString:
  /{NEGATIVE_MULTILINE_STRING_START}\S.*$/
;

MultiLineString[noskipws]:
  />>>\n/-
    parts*=TextPart
  /^<<</-
;

FieldName[noskipws]:
  /{NEGATIVE_UID}{NEGATIVE_RELATIONS}[A-Z]+[A-Z_]*/
;
"""

FREE_TEXT_PARSER_GRAMMAR = r"""
FreeTextContainer[noskipws]:
  parts*=TextPart
;
"""

DOCUMENT_GRAMMAR = rf"""
SDocDocument[noskipws]:
  '[DOCUMENT]' '\n'
  ('MID: ' mid = SingleLineString '\n')?
  'TITLE: ' title = SingleLineString '\n'
  (config = DocumentConfig)?
  (view = DocumentView)?
  ('\n' grammar = DocumentGrammar)?
  section_contents *= SectionOrRequirement
;

DocumentConfig[noskipws]:
  ('UID: ' uid = /{REGEX_UID}/ '\n')?
  ('VERSION: ' version = SingleLineString '\n')?
  ('DATE: ' date = SingleLineString '\n')?
  ('CLASSIFICATION: ' classification = SingleLineString '\n')?
  ('REQ_PREFIX: ' requirement_prefix = SingleLineString '\n')?
  ('ROOT: ' (root = BooleanChoice) '\n')?
  ('OPTIONS:' '\n'
    ('  ENABLE_MID: ' (enable_mid = BooleanChoice) '\n')?
    ('  MARKUP: ' (markup = MarkupChoice) '\n')?
    ('  AUTO_LEVELS: ' (auto_levels = AutoLevelsChoice) '\n')?
    ('  LAYOUT: ' (layout = LayoutChoice) '\n')?
    ('  REQUIREMENT_STYLE: ' (requirement_style = RequirementStyleChoice) '\n')?
    ('  REQUIREMENT_IN_TOC: '
        (requirement_in_toc = RequirementHasTitleChoice) '\n'
    )?
    ('  DEFAULT_VIEW: ' default_view = SingleLineString '\n')?
  )?
;

DocumentView[noskipws]:
  'VIEWS:' '\n'
  views += ViewElement
;

ViewElement[noskipws]:
  '- ID: ' view_id = /{REGEX_UID}/ '\n'
  ('  NAME: ' name = SingleLineString '\n')?
  '  TAGS:' '\n'
  tags += ViewElementTags
  ('  HIDDEN_TAGS:' '\n'
  hidden_tags += ViewElementHiddenTag)?
;

ViewElementTags[noskipws]:
  '  - OBJECT_TYPE: ' object_type = SingleLineString '\n'
  '    VISIBLE_FIELDS:' '\n'
  visible_fields += ViewElementField
;

ViewElementField[noskipws]:
  '    - NAME: ' name = SingleLineString '\n'
  ('      PLACEMENT: ' placement = SingleLineString '\n')?
;

ViewElementHiddenTag[noskipws]:
  '  - ' hidden_tag = SingleLineString '\n'
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

LayoutChoice[noskipws]:
  'Default' | 'Website'
;
"""

SECTION_GRAMMAR = rf"""
SDocSection[noskipws]:
  '[SECTION]'
  '\n'
  ('MID: ' mid = SingleLineString '\n')?
  ('UID: ' uid = /{REGEX_UID}/ '\n')?
  ('LEVEL: ' custom_level = SingleLineString '\n')?
  'TITLE: ' title = SingleLineString '\n'
  ('REQ_PREFIX: ' requirement_prefix = SingleLineString '\n')?
  section_contents *= SectionOrRequirement
  '\n'
  '[/SECTION]'
  '\n'
;

SectionOrRequirement[noskipws]:
  '\n' (SDocSection | SDocNode | SDocCompositeNode | DocumentFromFile)
;

DocumentFromFile[noskipws]:
  '[DOCUMENT_FROM_FILE]' '\n'
  'FILE: ' file = /.+$/ '\n'
;

SpaceThenRequirement[noskipws]:
  '\n' (SDocNode | SDocCompositeNode)
;

ReservedKeyword[noskipws]:
  'DOCUMENT' | 'GRAMMAR' | 'SECTION' | 'DOCUMENT_FROM_FILE'
;

SDocNode[noskipws]:
  '[' !'SECTION' !SDocCompositeNodeTagName node_type = RequirementType ']' '\n'
  fields *= SDocNodeField
  (
    'RELATIONS:' '\n'
    (relations += Reference)
  )?
;

SDocCompositeNodeTagName[noskipws]:
  'COMPOSITE_'
;

SDocNodeField[noskipws]:
  (
    field_name = 'MID' ': ' parts+=SingleLineString '\n'
    |
    field_name = 'UID' ': ' parts+=/{REGEX_UID}/ '\n'
    |
    field_name = FieldName ':'
    (
        (' ' parts+=SingleLineTextPart '\n')
        |
        (
          ' '
          (
            multiline__ = />>>\n/
            parts+=TextPart
            /^<<</
          )
          '\n'
        )
    )
  )
;

SDocCompositeNode[noskipws]:
  '[COMPOSITE_' node_type = RequirementType ']' '\n'

  fields *= SDocNodeField
  (
    'RELATIONS:' '\n'
    (relations += Reference)
  )?

  requirements *= SpaceThenRequirement

  '\n'
  '[/COMPOSITE_REQUIREMENT]' '\n'
;

RequirementStatus[noskipws]:
  'Draft' | 'Active' | 'Deleted';

"""
