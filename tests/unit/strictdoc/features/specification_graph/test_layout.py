from strictdoc.features.specification_graph.layout import (
    compute_document_layout,
    get_skip_edges,
)
from tests.unit.helpers.document_builder import DocumentBuilder


def _doc(uid: str):
    builder = DocumentBuilder(uid)
    return builder.build()


def test_isolated_documents_are_all_at_row_0_in_tree_order():
    doc_a = _doc("DOC-A")
    doc_b = _doc("DOC-B")

    layout = compute_document_layout(
        documents=[doc_a, doc_b],
        edges=[],
    )

    assert layout == {
        doc_a: (0, 0),
        doc_b: (0, 1),
    }


def test_simple_chain():
    # A <- B <- C  (B's parent is A, C's parent is B). A has an incoming
    # edge (from B) and no outgoing edge, so it is the top of a hierarchy
    # and sits at row 1, not row 0 (row 0 is reserved for documents with
    # no relations at all).
    doc_a = _doc("DOC-A")
    doc_b = _doc("DOC-B")
    doc_c = _doc("DOC-C")

    layout = compute_document_layout(
        documents=[doc_a, doc_b, doc_c],
        edges=[(doc_b, doc_a), (doc_c, doc_b)],
    )

    assert layout[doc_a] == (1, 0)
    assert layout[doc_b] == (2, 0)
    assert layout[doc_c] == (3, 0)


def test_documents_with_no_relations_at_all_are_at_row_0():
    # A is isolated (no relations). B has a relation to C, so neither B
    # nor C qualifies for row 0: B is the top of a hierarchy (row 1), C
    # is below it (row 2).
    doc_a = _doc("DOC-A")
    doc_b = _doc("DOC-B")
    doc_c = _doc("DOC-C")

    layout = compute_document_layout(
        documents=[doc_a, doc_b, doc_c],
        edges=[(doc_c, doc_b)],
    )

    assert layout[doc_a] == (0, 0)
    assert layout[doc_b] == (1, 0)
    assert layout[doc_c] == (2, 0)


def test_highway_rule_deepest_chain_wins():
    # A is the top of the hierarchy (incoming edges only) -> row 1.
    # B's parent is A -> B at row 2.
    # C's parent is B -> C at row 3.
    # D has two parent edges: a direct one to A (row 1) and one to C
    # (row 3). The deepest chain (via C) wins: D ends up at row 4, not 2.
    doc_a = _doc("DOC-A")
    doc_b = _doc("DOC-B")
    doc_c = _doc("DOC-C")
    doc_d = _doc("DOC-D")

    edges = [
        (doc_b, doc_a),
        (doc_c, doc_b),
        (doc_d, doc_a),
        (doc_d, doc_c),
    ]
    layout = compute_document_layout(
        documents=[doc_a, doc_b, doc_c, doc_d],
        edges=edges,
    )

    assert layout[doc_a] == (1, 0)
    assert layout[doc_b] == (2, 0)
    assert layout[doc_c] == (3, 0)
    assert layout[doc_d][0] == 4

    skip_edges = get_skip_edges(edges, layout)
    assert skip_edges == [(doc_d, doc_a)]


def test_row_order_follows_project_tree_order():
    # Three documents with no relations to each other end up in the same
    # row (0); their left-to-right column order must follow the order
    # they were passed in (project tree order), not e.g. alphabetical.
    doc_c = _doc("DOC-C")
    doc_a = _doc("DOC-A")
    doc_b = _doc("DOC-B")

    layout = compute_document_layout(
        documents=[doc_c, doc_a, doc_b],
        edges=[],
    )

    assert layout[doc_c] == (0, 0)
    assert layout[doc_a] == (0, 1)
    assert layout[doc_b] == (0, 2)


def test_get_skip_edges_empty_when_layout_has_no_conflicts():
    doc_a = _doc("DOC-A")
    doc_b = _doc("DOC-B")

    edges = [(doc_b, doc_a)]
    layout = compute_document_layout(documents=[doc_a, doc_b], edges=edges)

    assert get_skip_edges(edges, layout) == []
