GRAMMAR_GRAMMAR = r"""
DocumentGrammar[noskipws]:
  '[GRAMMAR]' '\n'

  (
    (
      'ELEMENTS:' '\n'
      elements += GrammarElement
    )? |
    (
      'IMPORT_FROM_FILE: ' import_from_file = /.+$/ '\n'
    )?
  )
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
  (GrammarElementRelationParent | GrammarElementRelationChild | GrammarElementRelationFile)
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

GrammarElementField[noskipws]:
  GrammarElementFieldString |
  GrammarElementFieldSingleChoice |
  GrammarElementFieldMultipleChoice |
  GrammarElementFieldTag
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

ReferenceType[noskipws]:
  ('ParentReqReference' | 'ChildReqReference' | 'FileReference')
;

ReferenceTypeXs[noskipws]:
  /, /- ReferenceType
;
"""

GRAMMAR_WRAPPER = """
DocumentGrammarWrapper[noskipws]:
    grammar = DocumentGrammar
;
"""
