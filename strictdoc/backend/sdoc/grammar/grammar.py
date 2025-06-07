REGEX_UID = r"([\w]+[\w()\-\/.: ]*)"

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
  /{NEGATIVE_UID}{NEGATIVE_RELATIONS}[A-Z]+[A-Z_0-9]*/
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
  (/(REQ_)?PREFIX/ ': ' requirement_prefix = SingleLineString '\n')?
  ('ROOT: ' (root = BooleanChoice) '\n')?
  ('OPTIONS:' '\n'
    ('  ENABLE_MID: ' (enable_mid = BooleanChoice) '\n')?
    ('  MARKUP: ' (markup = MarkupChoice) '\n')?
    ('  AUTO_LEVELS: ' (auto_levels = AutoLevelsChoice) '\n')?
    ('  LAYOUT: ' (layout = LayoutChoice) '\n')?
    ('  ' view_style_tag = /(VIEW_STYLE|REQUIREMENT_STYLE)/ ': '
        (requirement_style = RequirementStyleChoice) '\n')?
    ('  ' node_in_toc_tag = /(NODE_IN_TOC|REQUIREMENT_IN_TOC)/ ': '
        (requirement_in_toc = RequirementHasTitleChoice) '\n'
    )?
    ('  DEFAULT_VIEW: ' default_view = SingleLineString '\n')?
  )?
  ('METADATA:' '\n' custom_metadata = DocumentCustomMetadata)?
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
  'Plain' | 'Inline' | 'Simple' | 'Narrative' | 'Table' | 'Zebra'
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

DocumentCustomMetadata[noskipws]:
  (entries+=DocumentCustomMetadataKeyValuePair)*
;

DocumentCustomMetadataKeyValuePair[noskipws]:
  '  ' key=DocumentCustomMetadataKey ': ' value=SingleLineString '\n'
;

DocumentCustomMetadataKey: /[a-zA-Z_][a-zA-Z0-9_-]*/;

"""

SECTION_GRAMMAR = rf"""
SDocSection[noskipws]:
  '[SECTION]'
  '\n'
  ('MID: ' mid = SingleLineString '\n')?
  ('UID: ' uid = /{REGEX_UID}/ '\n')?
  ('LEVEL: ' custom_level = SingleLineString '\n')?
  'TITLE: ' title = SingleLineString '\n'
  (/(REQ_)?PREFIX/ ': ' requirement_prefix = SingleLineString '\n')?
  section_contents *= SectionOrRequirement
  '\n'
  '[/SECTION]'
  '\n'
;

SectionOrRequirement[noskipws]:
  '\n' (SDocSection | SDocCompositeNode | SDocNode | DocumentFromFile)
;

DocumentFromFile[noskipws]:
  '[DOCUMENT_FROM_FILE]' '\n'
  'FILE: ' file = /.+$/ '\n'
;

ReservedKeyword[noskipws]:
  'DOCUMENT' | 'GRAMMAR' | 'SECTION' | 'DOCUMENT_FROM_FILE'
;

SDocNode[noskipws]:
  '[' !'SECTION' node_type = RequirementType ']' '\n'
  fields += SDocNodeField
  (
    'RELATIONS:' '\n'
    (relations += Reference)
  )?
;

SDocCompositeNode[noskipws]:
  '[[' node_type = RequirementType ']]' '\n'

  fields += SDocNodeField
  (
    'RELATIONS:' '\n'
    (relations += Reference)
  )?

  section_contents *= SectionOrRequirement

  '\n'
  '[[/' node_type_close = RequirementType ']]' '\n'
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

RequirementStatus[noskipws]:
  'Draft' | 'Active' | 'Deleted';

"""
