from strictdoc.core.query_engine.query_object import (
    EqualExpression,
    InExpression,
    NodeFieldExpression,
    NodeHasParentRequirementsExpression,
    NodeIsRequirementExpression,
    NodeIsSectionExpression,
    NotEqualExpression,
    NotExpression,
    OrExpression,
    Query,
    StringExpression,
)
from strictdoc.core.query_engine.query_reader import QueryReader


def test_30_equal_expression_two_node_field_expressions():
    query = """\
node["TITLE"] == node["TITLE2"]\
"""
    query_object = QueryReader.read(query)
    assert isinstance(query_object, Query)
    assert isinstance(query_object.root_expression, EqualExpression)
    assert isinstance(
        query_object.root_expression.lhs_expr, NodeFieldExpression
    )
    assert query_object.root_expression.lhs_expr.field_name == "TITLE"
    assert isinstance(
        query_object.root_expression.rhs_expr, NodeFieldExpression
    )
    assert query_object.root_expression.rhs_expr.field_name == "TITLE2"


def test_31_equal_expression_node_field_expression_and_string():
    query = """\
node["TITLE"] == "FOO"\
"""
    query_object = QueryReader.read(query)
    assert isinstance(query_object, Query)
    assert isinstance(query_object.root_expression, EqualExpression)
    assert isinstance(
        query_object.root_expression.lhs_expr, NodeFieldExpression
    )
    assert query_object.root_expression.lhs_expr.field_name == "TITLE"
    assert isinstance(query_object.root_expression.rhs_expr, StringExpression)
    assert query_object.root_expression.rhs_expr.string == "FOO"


def test_40_non_equal_expression():
    query = """\
node["TITLE"] != node["TITLE2"]\
"""
    query_object = QueryReader.read(query)
    assert isinstance(query_object, Query)
    assert isinstance(query_object.root_expression, NotEqualExpression)
    assert isinstance(
        query_object.root_expression.lhs_expr, NodeFieldExpression
    )
    assert query_object.root_expression.lhs_expr.field_name == "TITLE"
    assert isinstance(
        query_object.root_expression.rhs_expr, NodeFieldExpression
    )
    assert query_object.root_expression.rhs_expr.field_name == "TITLE2"


def test_50_in_expression_two_node_field_expressions():
    query = """\
node["TITLE"] in node["TITLE2"]\
"""
    query_object = QueryReader.read(query)
    assert isinstance(query_object, Query)
    assert isinstance(query_object.root_expression, InExpression)
    assert isinstance(
        query_object.root_expression.lhs_expr, NodeFieldExpression
    )
    assert query_object.root_expression.lhs_expr.field_name == "TITLE"
    assert isinstance(
        query_object.root_expression.rhs_expr, NodeFieldExpression
    )
    assert query_object.root_expression.rhs_expr.field_name == "TITLE2"


def test_51_in_expression_node_field_expression_and_string():
    query = """\
node["TITLE"] in "FOO"\
"""
    query_object = QueryReader.read(query)
    assert isinstance(query_object, Query)
    assert isinstance(query_object.root_expression, InExpression)
    assert isinstance(
        query_object.root_expression.lhs_expr, NodeFieldExpression
    )
    assert query_object.root_expression.lhs_expr.field_name == "TITLE"
    assert isinstance(query_object.root_expression.rhs_expr, StringExpression)
    assert query_object.root_expression.rhs_expr.string == "FOO"


def test_52_in_expression_with_string_and_node_field_expression():
    query = """\
"CRUD" in node["TITLE"]\
"""
    query_object = QueryReader.read(query)
    assert isinstance(query_object, Query)
    assert isinstance(query_object.root_expression, InExpression)
    assert isinstance(query_object.root_expression.lhs_expr, StringExpression)
    assert query_object.root_expression.lhs_expr.string == "CRUD"
    assert isinstance(
        query_object.root_expression.rhs_expr, NodeFieldExpression
    )
    assert query_object.root_expression.rhs_expr.field_name == "TITLE"


def test_61_node_has_parent_requirements():
    query = """\
node.has_parent_requirements\
"""
    query_object = QueryReader.read(query)
    assert isinstance(query_object, Query)
    assert isinstance(
        query_object.root_expression, NodeHasParentRequirementsExpression
    )


def test_62_node_is_requirement():
    query = """\
node.is_requirement\
"""
    query_object = QueryReader.read(query)
    assert isinstance(query_object, Query)
    assert isinstance(query_object.root_expression, NodeIsRequirementExpression)


def test_63_node_is_section():
    query = """\
node.is_section\
"""
    query_object = QueryReader.read(query)
    assert isinstance(query_object, Query)
    assert isinstance(query_object.root_expression, NodeIsSectionExpression)


def test_81_or_expression():
    query = """\
(node["TITLE"] == "FOO" or node["TITLE2"] == "BAR")\
"""
    query_object = QueryReader.read(query)
    assert isinstance(query_object, Query)
    assert isinstance(query_object.root_expression, OrExpression)
    assert isinstance(
        query_object.root_expression.expressions[0], EqualExpression
    )
    assert isinstance(
        query_object.root_expression.expressions[1], EqualExpression
    )


def test_82_nested_or_expression():
    query = """\
("FOO" == "FOO" or ("FOO" == "FOO" or "FOO" == "FOO"))\
"""
    query_object = QueryReader.read(query)
    assert isinstance(query_object, Query)
    assert isinstance(query_object.root_expression, OrExpression)
    assert isinstance(
        query_object.root_expression.expressions[0], EqualExpression
    )
    assert isinstance(query_object.root_expression.expressions[1], OrExpression)


def test_90_not_expression():
    query = """\
not node["TITLE"] == "FOO"\
"""
    query_object = QueryReader.read(query)
    assert isinstance(query_object, Query)
    assert isinstance(query_object.root_expression, NotExpression)
    assert isinstance(query_object.root_expression.expression, EqualExpression)
