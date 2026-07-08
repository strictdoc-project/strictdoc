from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory
from strictdoc.core.query_engine.query_object import QueryObject
from strictdoc.core.query_engine.query_reader import QueryReader
from tests.unit.helpers.document_builder import DocumentBuilder


def evaluate_query(query: str) -> bool:
    parsed_query = QueryReader.read(query)
    return QueryObject(parsed_query, None).evaluate(None)


def evaluate_node_query(query: str, node) -> bool:
    parsed_query = QueryReader.read(query)
    return QueryObject(parsed_query, None).evaluate(node)


def test_10_any_all_none_in_expressions_evaluate_string_rhs():
    assert evaluate_query('any(["X", "B"]) in "ABC"') is True
    assert evaluate_query('all(["A", "B"]) in "ABC"') is True
    assert evaluate_query('none(["X", "Y"]) in "ABC"') is True


def test_20_any_all_none_in_expressions_evaluate_string_rhs_no_match():
    assert evaluate_query('any(["X", "Y"]) in "ABC"') is False
    assert evaluate_query('all(["A", "X"]) in "ABC"') is False
    assert evaluate_query('none(["X", "A"]) in "ABC"') is False


def test_30_in_expressions_evaluate_string_rhs_order_independent():
    assert evaluate_query('any(["X", "B", "A"]) in "ABC"') is True
    assert evaluate_query('all(["B", "A"]) in "ABC"') is True
    assert evaluate_query('none(["Y", "X"]) in "ABC"') is True


def test_40_any_in_expression_matches_tags_exactly():
    builder = DocumentBuilder()
    node = SDocObjectFactory.create_requirement(
        parent=builder.document,
        tags="tag_a, tag_b",
    )

    assert evaluate_node_query('any(["tag_a"]) in node["TAGS"]', node) is True
    assert evaluate_node_query('any(["tag"]) in node["TAGS"]', node) is False


def test_45_scalar_in_expression_matches_tags_by_substring():
    builder = DocumentBuilder()
    node = SDocObjectFactory.create_requirement(
        parent=builder.document,
        tags="tag_a, tag_b",
    )

    assert evaluate_node_query('"tag" in node["TAGS"]', node) is True


def test_50_all_in_expression_matches_tags_exactly():
    builder = DocumentBuilder()
    node = SDocObjectFactory.create_requirement(
        parent=builder.document,
        tags="tag_a, tag_b",
    )

    assert (
        evaluate_node_query('all(["tag_a", "tag_b"]) in node["TAGS"]', node)
        is True
    )
    assert evaluate_node_query('all(["tag"]) in node["TAGS"]', node) is False


def test_60_none_in_expression_matches_tags_exactly():
    builder = DocumentBuilder()
    node = SDocObjectFactory.create_requirement(
        parent=builder.document,
        tags="tag_a, tag_b",
    )

    assert evaluate_node_query('none(["tag"]) in node["TAGS"]', node) is True
    assert evaluate_node_query('none(["tag_a"]) in node["TAGS"]', node) is False


def test_70_any_all_none_in_expressions_evaluate_node_text_field():
    builder = DocumentBuilder()
    node = SDocObjectFactory.create_requirement(
        parent=builder.document,
        title="System ABC",
    )

    assert (
        evaluate_node_query('any(["System", "Other"]) in node["TITLE"]', node)
        is True
    )
    assert (
        evaluate_node_query('all(["System", "ABC"]) in node["TITLE"]', node)
        is True
    )
    assert evaluate_node_query('none(["Other"]) in node["TITLE"]', node) is True
