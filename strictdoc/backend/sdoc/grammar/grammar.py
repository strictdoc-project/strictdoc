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
SDocDocument[noskipws]:
  '[DOCUMENT]' '\n'
  ('MID: ' mid = SingleLineString '\n')?
  'TITLE: ' title = SingleLineString '\n'
  (config = DocumentConfig)?
  (view = DocumentView)?
  ('\n' grammar = DocumentGrammar)?
  ('\n' bibliography = DocumentBibliography)?
  free_texts *= SpaceThenFreeText
  section_contents *= SectionOrRequirement
;

ReservedKeyword[noskipws]:
  'DOCUMENT' | 'GRAMMAR' | 'BIBLIOGRAPHY'
;

DocumentBibliography[noskipws]:
  '[BIBLIOGRAPHY]' '\n'
  ( 'BIBFILES:' '\n'
    bib_files *= BibFileEntry )?
  ( 'ENTRIES:' '\n'
    bib_entries += BibEntry )?
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
  (
    '  RELATIONS:' '\n'
    relations += GrammarElementRelation
  )?
;

GrammarElementRelation[noskipws]:
  (GrammarElementRelationParent | GrammarElementRelationChild | GrammarElementRelationFile | GrammarElementRelationBibtex)
;

GrammarElementRelationParent[noskipws]:
  '  - TYPE: ' relation_type='Parent' '\n'
  ('    ROLE: ' relation_role=/.+/ '\n')?
;

GrammarElementRelationChild[noskipws]:
  '  - TYPE: ' relation_type='Child' '\n'
  ('    ROLE: ' relation_role=/.+/ '\n')?
;

GrammarElementRelationFile[noskipws]:
  '  - TYPE: ' relation_type='File' '\n'
;

GrammarElementRelationBibtex[noskipws]:
  '  - TYPE: ' relation_type='BibTex' '\n'
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
  ('    HUMAN_TITLE: ' human_title=SingleLineString '\n')?
  '    TYPE: String' '\n'
  '    REQUIRED: ' (required = BooleanChoice) '\n'
;

GrammarElementFieldSingleChoice[noskipws]:
  '  - TITLE: ' title=FieldName '\n'
  ('    HUMAN_TITLE: ' human_title=SingleLineString '\n')?
  '    TYPE: SingleChoice'
    '(' ((options = ChoiceOption) (options *= ChoiceOptionXs)) ')' '\n'
  '    REQUIRED: ' (required = BooleanChoice) '\n'
;

GrammarElementFieldMultipleChoice[noskipws]:
  '  - TITLE: ' title=FieldName '\n'
  ('    HUMAN_TITLE: ' human_title=SingleLineString '\n')?
  '    TYPE: MultipleChoice'
    '(' ((options = ChoiceOption) (options *= ChoiceOptionXs)) ')' '\n'
  '    REQUIRED: ' (required = BooleanChoice) '\n'
;

GrammarElementFieldTag[noskipws]:
  '  - TITLE: ' title=FieldName '\n'
  ('    HUMAN_TITLE: ' human_title=SingleLineString '\n')?
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
  ('ROOT: ' (root = BooleanChoice) '\n')?
  ('OPTIONS:' '\n'
    ('  ENABLE_MID: ' (enable_mid = BooleanChoice) '\n')?
    ('  MARKUP: ' (markup = MarkupChoice) '\n')?
    ('  AUTO_LEVELS: ' (auto_levels = AutoLevelsChoice) '\n')?
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
"""

FRAGMENT_GRAMMAR = r"""
Fragment[noskipws]:
  '[FRAGMENT]' '\n'
  section_contents *= SectionOrRequirement
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
  free_texts *= SpaceThenFreeText
  section_contents *= SectionOrRequirement
  '\n'
  '[/SECTION]'
  '\n'
;

SectionOrRequirement[noskipws]:
  '\n' (SDocSection | SDocNode | CompositeRequirement | FragmentFromFile)
;

FragmentFromFile[noskipws]:
  '[DOCUMENT_FROM_FILE]' '\n'
  'FILE: ' file = /.+$/ '\n'
;

SpaceThenRequirement[noskipws]:
  '\n' (SDocNode | CompositeRequirement)
;

SpaceThenFreeText[noskipws]:
  '\n' (FreeText)
;

ReservedKeyword[noskipws]:
  'DOCUMENT' | 'GRAMMAR' | 'SECTION' | 'DOCUMENT_FROM_FILE' | 'FREETEXT'
;

SDocNode[noskipws]:
  '[' !CompositeRequirementTagName requirement_type = RequirementType ']' '\n'
  ('MID: ' mid = SingleLineString '\n')?
  fields *= SDocNodeField
;

CompositeRequirementTagName[noskipws]:
  'COMPOSITE_'
;

RequirementType[noskipws]:
  !ReservedKeyword /[A-Z]+(_[A-Z]+)*/
;

SDocNodeField[noskipws]:
  (
    (field_name = 'REFS' | field_name = 'RELATIONS') ':' '\n'
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

  ('MID: ' mid = SingleLineString '\n')?

  fields *= SDocNodeField

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
