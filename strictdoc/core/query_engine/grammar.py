QUERY_GRAMMAR = r"""
Query:
 root_expression = BooleanExpression
;

AndExpression:
  '('
  expressions += BooleanExpression
  ('and' expressions += BooleanExpression)+
  ')'
;

OrExpression:
  '('
  expressions += BooleanExpression
  ('or' expressions += BooleanExpression)+
  ')'
;

NotExpression:
  'not'
  expression = BooleanExpression
;

BooleanExpression:
  AndExpression
  |
  OrExpression
  |
  NotExpression
  |
  NodeHasParentRequirementsExpression
  |
  InExpression
  |
  NodeIsRequirementExpression
  |
  NodeIsSectionExpression
  |
  EqualExpression
  |
  NotEqualExpression
;

StringExpression:
  '"' string = /[^"]+/ '"'
;

NodeFieldExpression:
  'node["' field_name = /[A-Za-z0-9]+/ '"]'
;

NodeHasParentRequirementsExpression:
  _ = 'node.has_parent_requirements'
;

NodeIsRequirementExpression:
  _ = 'node.is_requirement'
;

NodeIsSectionExpression:
  _ = 'node.is_section'
;

EqualExpression:
  lhs_expr = ComparableExpression '==' rhs_expr = ComparableExpression
;

NotEqualExpression:
  lhs_expr = ComparableExpression '!=' rhs_expr = ComparableExpression
;

ComparableExpression:
  NodeFieldExpression | StringExpression
;

InExpression:
  lhs_expr = InableLHSExpression 'in' rhs_expr = InableRHSExpression
;

InableLHSExpression:
  NodeFieldExpression | StringExpression
;

InableRHSExpression:
  NodeFieldExpression | StringExpression
;

"""
