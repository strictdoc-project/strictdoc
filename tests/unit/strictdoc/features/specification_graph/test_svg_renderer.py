import re

from strictdoc.features.specification_graph.layout import (
    compute_document_layout,
    get_skip_edges,
)
from strictdoc.features.specification_graph.svg_renderer import (
    BOX_WIDTH,
    render_svg,
)
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

    # 3 normal edges rendered as straight <line>s, 1 skip edge rendered as
    # a routed <path> (see svg_renderer._render_skip_edge) so it doesn't
    # overlap the normal edges of the chain it bypasses. There are also 2
    # <path> elements inside <defs> for the arrowhead markers themselves.
    assert svg.count("<line") == 3
    assert svg.count("<path") == 3
    assert svg.count("stroke-dasharray") == 1


def test_skip_edge_does_not_overlap_the_chain_it_bypasses():
    # Regression test: when every row has a single document, the direct
    # chain's edges and a skip edge that bypasses part of it used to be
    # drawn as straight lines sharing the exact same x coordinate,
    # visually overlapping. The skip edge must be routed through a
    # separate lane instead.
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

    line_xs = {
        float(x_) for x_ in re.findall(r'<line x[12]="([\d.]+)"', svg)
    }

    skip_path = re.search(
        r'<path d="([^"]+)" fill="none" stroke="#b45309"', svg
    )
    assert skip_path is not None
    points = re.findall(r"[ML] ([\d.]+),([\d.]+)", skip_path.group(1))
    # points[2] and points[3] are the two ends of the lane's long vertical
    # run, which spans the same rows as the direct chain and so is the
    # only segment that could visually overlap it.
    lane_x = float(points[2][0])
    assert lane_x == float(points[3][0])
    assert lane_x not in line_xs


def test_multiple_edges_on_the_same_box_edge_get_distinct_attachment_points():
    # Doc D has two outgoing edges (to Doc A and to Doc C) that both leave
    # from Doc D's top edge. Per the "evenly spaced, k/(N+1)" attachment
    # rule, with 2 edges they must land at 1/3 and 2/3 of the box width,
    # not both at the center.
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
    svg = render_svg(layout=layout, edges=edges, skip_edges=skip_edges)

    _, doc_d_column = layout[doc_d]
    box_x = 20 + doc_d_column * BOX_WIDTH  # MARGIN, single column per row
    expected_xs = {box_x + BOX_WIDTH / 3, box_x + 2 * BOX_WIDTH / 3}

    # d->a (skip) leaves from the first attachment point, d->c (normal)
    # from the second.
    line_x1 = {float(x_) for x_ in re.findall(r'<line x1="([\d.]+)"', svg)}
    skip_path = re.search(
        r'<path d="([^"]+)" fill="none" stroke="#b45309"', svg
    )
    assert skip_path is not None
    skip_start_match = re.match(r"M ([\d.]+),", skip_path.group(1))
    assert skip_start_match is not None
    skip_start_x = float(skip_start_match.group(1))

    assert skip_start_x in expected_xs
    assert expected_xs & line_x1
    assert skip_start_x not in line_x1


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
