from strictdoc.features.specification_graph.layout import (
    compute_document_layout,
    get_skip_edges,
)
from strictdoc.features.specification_graph.svg_renderer import render_svg
from tests.unit.helpers.document_builder import DocumentBuilder


def _doc(uid: str):
    return DocumentBuilder(uid).build()


def test_empty_layout_renders_placeholder_message():
    svg = render_svg(layout={}, edges=[], skip_edges=[])

    assert "<svg" in svg
    assert "no documents" in svg.lower()
    assert "<rect" not in svg


def test_renders_one_box_per_document_and_one_line_per_edge():
    doc_a = _doc("DOC-A")
    doc_b = _doc("DOC-B")
    edges = [(doc_b, doc_a)]
    layout = compute_document_layout(documents=[doc_a, doc_b], edges=edges)
    skip_edges = get_skip_edges(edges, layout)

    svg = render_svg(layout=layout, edges=edges, skip_edges=skip_edges)

    assert svg.count("<rect") == 2
    assert svg.count("<line") == 1
    assert "stroke-dasharray" not in svg


def test_skip_edge_gets_dashed_styling():
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
        documents=[doc_a, doc_b, doc_c, doc_d], edges=edges
    )
    skip_edges = get_skip_edges(edges, layout)
    assert skip_edges == [(doc_d, doc_a)]

    svg = render_svg(layout=layout, edges=edges, skip_edges=skip_edges)

    assert svg.count("<line") == 4
    assert svg.count("stroke-dasharray") == 1


def test_long_title_is_wrapped_and_truncated_with_ellipsis():
    document_builder = DocumentBuilder("DOC-A")
    document = document_builder.build()
    document.title = (
        "A very long document title that will not fit into two lines "
        "inside a fixed-width box no matter how it is wrapped"
    )

    layout = compute_document_layout(documents=[document], edges=[])

    svg = render_svg(layout=layout, edges=[], skip_edges=[])

    assert svg.count("<tspan") == 2
    assert "…" in svg
