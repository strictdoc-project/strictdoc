"""
Render the Specification graph as hand-written SVG, from the layout
produced by `layout.compute_document_layout()` and the edges produced by
`relations.get_document_relation_edges()`.

Per task.md, no Python SVG library dependency is used for V1 — plain
string templates are enough for boxes, arrows, and text.
"""

import html
import textwrap
from typing import Dict, List, Optional, Set, Tuple

from strictdoc.backend.sdoc.models.model import SDocDocumentIF
from strictdoc.features.specification_graph.layout import DocumentPosition
from strictdoc.features.specification_graph.relations import (
    DocumentRelationEdge,
)

BOX_WIDTH = 180
BOX_HEIGHT = 60
COLUMN_GAP = 40
ROW_GAP = 80
MARGIN = 20
FONT_SIZE = 13
LINE_HEIGHT = 16
MAX_TITLE_LINES = 2
TITLE_WRAP_WIDTH = 24

# Skip edges (see layout.get_skip_edges()) are routed through a dedicated
# vertical "lane" to the right of all document columns, instead of as a
# straight line, so they don't visually overlap the direct chain of
# normal edges they bypass (both can otherwise land on the same x
# coordinate when every row has a single document).
SKIP_LANE_START_GAP = 30
SKIP_LANE_GAP = 30

# Minimum distance a line may come to a boundary it must not touch: a
# box's own edge (for arrow/stub attachment points) or the midpoint of an
# inter-row gap (for skip-edge stubs, via SKIP_STUB_DEAD_ZONE below).
EDGE_MARGIN = 24

# An inter-row gap is split in half at its midpoint: the half nearer the
# row above is reserved for stubs ENDING there (edges whose parent is
# that row); the half nearer the row below is reserved for stubs
# STARTING there (edges whose child is that row). A dead zone straddles
# the midpoint so the two halves never meet. This guarantees a stub
# leaving the lower row always stays below (closer to the lower row
# than) any stub ending in the row above, regardless of how many edges
# are on either side.
SKIP_STUB_DEAD_ZONE = 16

EMPTY_GRAPH_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 60" '
    'width="320" height="60" role="img" '
    'aria-label="Specification graph: no documents">'
    '<text x="10" y="35" font-size="13">'
    "This project has no documents to display."
    "</text></svg>"
)


def _wrap_title(title: str) -> List[str]:
    lines = textwrap.wrap(title, width=TITLE_WRAP_WIDTH) or [""]
    if len(lines) > MAX_TITLE_LINES:
        lines = lines[:MAX_TITLE_LINES]
        last_line = lines[-1]
        if len(last_line) > TITLE_WRAP_WIDTH - 1:
            last_line = last_line[: TITLE_WRAP_WIDTH - 1]
        lines[-1] = last_line.rstrip() + "…"
    return lines


def _box_x(column: int) -> float:
    return MARGIN + column * (BOX_WIDTH + COLUMN_GAP)


def _box_y(row: int) -> float:
    return MARGIN + row * (BOX_HEIGHT + ROW_GAP)


def _render_document_box(
    document_: SDocDocumentIF, position: DocumentPosition
) -> str:
    row_, column_ = position
    x = _box_x(column_)
    y = _box_y(row_)
    title = document_.get_display_title(include_toc_number=False)
    lines = _wrap_title(title)

    center_x = x + BOX_WIDTH / 2
    first_line_y = y + BOX_HEIGHT / 2 - (len(lines) - 1) * LINE_HEIGHT / 2

    tspans = "".join(
        f'<tspan x="{center_x}" dy="{0 if index_ == 0 else LINE_HEIGHT}">'
        f"{html.escape(line_)}</tspan>"
        for index_, line_ in enumerate(lines)
    )

    return (
        f'<rect x="{x}" y="{y}" width="{BOX_WIDTH}" height="{BOX_HEIGHT}" '
        f'fill="white" stroke="black" />'
        f'<text x="{center_x}" y="{first_line_y}" text-anchor="middle" '
        f'font-size="{FONT_SIZE}">{tspans}</text>'
    )


def _distribute_evenly_inclusive(
    start: float, end: float, count: int
) -> List[float]:
    """
    Distribute `count` points evenly across [start, end]: 1 point sits at
    the center; 2 or more points are spread evenly with the two outermost
    points sitting exactly at `start` and `end`. Used both for arrow
    attachment points along a box's edge (start/end are the edge's ends,
    inset by EDGE_MARGIN) and for skip-edge stub offsets within their
    half of an inter-row gap (start/end are the near-box and
    near-dead-zone bounds of that half).
    """
    if count == 1:
        return [(start + end) / 2]
    return [
        start + (end - start) * index_ / (count - 1) for index_ in range(count)
    ]


def _distribute_attachment_points(
    edges_on_edge_face: Dict[SDocDocumentIF, List[DocumentRelationEdge]],
    layout: Dict[SDocDocumentIF, DocumentPosition],
) -> Dict[DocumentRelationEdge, float]:
    """
    Arrows may not share an attachment point on a box's edge (top or
    bottom face). For the N edges attaching to one face, points are
    spread evenly within the face inset by EDGE_MARGIN on both sides -
    see _distribute_evenly_inclusive().
    """
    attach_x: Dict[DocumentRelationEdge, float] = {}
    for document_, edges_ in edges_on_edge_face.items():
        _, column_ = layout[document_]
        box_x = _box_x(column_)
        xs = _distribute_evenly_inclusive(
            box_x + EDGE_MARGIN,
            box_x + BOX_WIDTH - EDGE_MARGIN,
            len(edges_),
        )
        for edge_, x_ in zip(edges_, xs):
            attach_x[edge_] = x_
    return attach_x


def _compute_edge_attachment_points(
    edges: List[DocumentRelationEdge],
    layout: Dict[SDocDocumentIF, DocumentPosition],
) -> Tuple[
    Dict[DocumentRelationEdge, float], Dict[DocumentRelationEdge, float]
]:
    """
    Returns (child_attach_x, parent_attach_x): for each edge, the x
    coordinate where it attaches to its child's top edge and to its
    parent's bottom edge, respectively.
    """
    top_edges_of: Dict[SDocDocumentIF, List[DocumentRelationEdge]] = {}
    bottom_edges_of: Dict[SDocDocumentIF, List[DocumentRelationEdge]] = {}
    for edge_ in edges:
        child_document_, parent_document_ = edge_
        top_edges_of.setdefault(child_document_, []).append(edge_)
        bottom_edges_of.setdefault(parent_document_, []).append(edge_)

    child_attach_x = _distribute_attachment_points(top_edges_of, layout)
    parent_attach_x = _distribute_attachment_points(bottom_edges_of, layout)
    return child_attach_x, parent_attach_x


def _distribute_stub_offsets(count: int) -> List[float]:
    """
    Same _distribute_evenly_inclusive() used for arrow attachment points,
    applied to how far a skip edge's stub runs from its box before
    turning into the lane. The stub stays within its own half of the
    inter-row gap (see SKIP_STUB_DEAD_ZONE): nearest-to-box bound is
    EDGE_MARGIN, farthest-from-box bound is the edge of the dead zone at
    the gap's midpoint.
    """
    nearest_bound = EDGE_MARGIN
    farthest_bound = ROW_GAP / 2 - SKIP_STUB_DEAD_ZONE / 2
    return _distribute_evenly_inclusive(nearest_bound, farthest_bound, count)


def _compute_skip_stub_offsets(
    skip_edges: List[DocumentRelationEdge],
    layout: Dict[SDocDocumentIF, DocumentPosition],
    child_attach_x: Dict[DocumentRelationEdge, float],
    parent_attach_x: Dict[DocumentRelationEdge, float],
) -> Tuple[
    Dict[DocumentRelationEdge, float], Dict[DocumentRelationEdge, float]
]:
    """
    Returns (child_stub_offset, parent_stub_offset): how far each skip
    edge's initial/final stub runs from its box before turning into the
    lane. Skip edges whose initial (or final) stub lands in the same
    inter-row gap get distinct offsets so their horizontal runs don't
    overlap, ordered so the edge attaching farther to the left runs
    farther from the box - "left starts higher" on the child side,
    "left ends lower" on the parent side - which fans the stubs out
    instead of letting them cross close to a shared box.
    """
    by_child_row: Dict[int, List[DocumentRelationEdge]] = {}
    by_parent_row: Dict[int, List[DocumentRelationEdge]] = {}
    for edge_ in skip_edges:
        child_document_, parent_document_ = edge_
        child_row, _ = layout[child_document_]
        parent_row, _ = layout[parent_document_]
        by_child_row.setdefault(child_row, []).append(edge_)
        by_parent_row.setdefault(parent_row, []).append(edge_)

    child_stub_offset: Dict[DocumentRelationEdge, float] = {}
    for edges_ in by_child_row.values():
        edges_by_x = sorted(edges_, key=lambda edge_: child_attach_x[edge_])
        # Farthest offset (last in the ascending list) goes to the
        # leftmost-attaching edge.
        for edge_, offset_ in zip(
            edges_by_x, reversed(_distribute_stub_offsets(len(edges_by_x)))
        ):
            child_stub_offset[edge_] = offset_

    parent_stub_offset: Dict[DocumentRelationEdge, float] = {}
    for edges_ in by_parent_row.values():
        edges_by_x = sorted(edges_, key=lambda edge_: parent_attach_x[edge_])
        for edge_, offset_ in zip(
            edges_by_x, reversed(_distribute_stub_offsets(len(edges_by_x)))
        ):
            parent_stub_offset[edge_] = offset_

    return child_stub_offset, parent_stub_offset


def _skip_edge_row_span(
    edge: DocumentRelationEdge,
    layout: Dict[SDocDocumentIF, DocumentPosition],
) -> Tuple[int, int]:
    child_document_, parent_document_ = edge
    child_row, _ = layout[child_document_]
    parent_row, _ = layout[parent_document_]
    return parent_row, child_row


def _local_rightmost_edge_x(
    parent_row: int, child_row: int, row_max_column: Dict[int, int]
) -> float:
    """
    The lane's vertical run only needs to clear rows strictly BETWEEN the
    parent and the child - at the parent/child rows themselves, the route
    is already a short stub tucked in the gap next to their own box, not
    a pass alongside the row's full height. A skip edge spanning e.g.
    rows 1..3 only needs to clear row 2, even if rows 1 and 3 are wider.
    """
    intermediate_rows = range(parent_row + 1, child_row)
    columns = [row_max_column.get(row_, 0) for row_ in intermediate_rows]
    if not columns:
        return 0.0
    return _box_x(max(columns)) + BOX_WIDTH


def _skip_edge_direct_lane_x(
    edge: DocumentRelationEdge,
    layout: Dict[SDocDocumentIF, DocumentPosition],
    row_max_column: Dict[int, int],
    child_attach_x: Dict[DocumentRelationEdge, float],
) -> Optional[float]:
    """
    The skip-edge path is always orthogonal, never diagonal (see
    _render_skip_edge()'s edges 1-5). Edge 2 (the horizontal detour out
    of the child's own column) only needs to exist to dodge a box in an
    intermediate row. If a plain vertical line straight up from the
    child's own attachment point (no detour at all, edge 2 has zero
    length, edges 1 and 3 sit on the same vertical) already clears every
    intermediate row, that vertical IS the lane - return its x. Columns
    in a row are filled contiguously from 0, so a row's occupied span is
    [leftmost column's left edge, widest column's right edge].
    """
    child_document_, parent_document_ = edge
    child_row, _ = layout[child_document_]
    parent_row, _ = layout[parent_document_]
    x_child = child_attach_x[edge]

    for row_ in range(parent_row + 1, child_row):
        if row_ not in row_max_column:
            continue
        row_left = _box_x(0)
        row_right = _box_x(row_max_column[row_]) + BOX_WIDTH
        if row_left <= x_child <= row_right:
            return None
    return x_child


def _assign_skip_lanes(
    skip_edges: List[DocumentRelationEdge],
    layout: Dict[SDocDocumentIF, DocumentPosition],
    row_max_column: Dict[int, int],
    child_attach_x: Dict[DocumentRelationEdge, float],
    parent_attach_x: Dict[DocumentRelationEdge, float],
) -> Dict[DocumentRelationEdge, float]:
    """
    Pack skip edges into shared vertical "tracks" (classic interval/track
    packing, as in a git branch graph): two edges may share a track only
    if the rows they span don't overlap (touching at a shared row is
    fine - their lanes never occupy that row's height at the same time,
    only the gaps on either side of it). This lets unrelated skip edges
    reuse the same lane instead of every edge claiming a new one further
    right, which used to push the whole diagram out whenever any single
    edge had to clear a wide row.

    Edges are considered left-to-right (by child attachment x) and each
    is placed in the leftmost compatible track, so a track's x position
    roughly tracks the horizontal position of the edges that use it. A
    track's x clears the local rightmost column of every edge ever
    placed in it (see _local_rightmost_edge_x()), and never sits to the
    left of any of those edges' own attachment points (so a stub never
    has to double back past where it started); different tracks are kept
    apart by SKIP_LANE_GAP.
    """
    ordered_edges = sorted(skip_edges, key=lambda edge_: child_attach_x[edge_])

    track_spans: List[List[Tuple[int, int]]] = []
    track_of_edge: Dict[DocumentRelationEdge, int] = {}
    for edge_ in ordered_edges:
        parent_row, child_row = _skip_edge_row_span(edge_, layout)
        track_index = next(
            (
                index_
                for index_, spans_ in enumerate(track_spans)
                if all(
                    child_row <= span_parent_ or span_child_ <= parent_row
                    for span_parent_, span_child_ in spans_
                )
            ),
            len(track_spans),
        )
        if track_index == len(track_spans):
            track_spans.append([])
        track_spans[track_index].append((parent_row, child_row))
        track_of_edge[edge_] = track_index

    edge_required_x = {
        edge_: max(
            _local_rightmost_edge_x(
                *_skip_edge_row_span(edge_, layout), row_max_column
            ),
            child_attach_x[edge_],
            parent_attach_x[edge_],
        )
        for edge_ in skip_edges
    }

    lane_x_by_track: List[float] = []
    next_available_lane_x = 0.0
    for track_index_ in range(len(track_spans)):
        required_x = (
            max(
                edge_required_x[edge_]
                for edge_ in skip_edges
                if track_of_edge[edge_] == track_index_
            )
            + SKIP_LANE_START_GAP
        )
        lane_x = max(required_x, next_available_lane_x)
        lane_x_by_track.append(lane_x)
        next_available_lane_x = lane_x + SKIP_LANE_GAP

    return {
        edge_: lane_x_by_track[track_of_edge[edge_]] for edge_ in skip_edges
    }


def _render_normal_edge(
    edge: DocumentRelationEdge,
    layout: Dict[SDocDocumentIF, DocumentPosition],
    child_attach_x: Dict[DocumentRelationEdge, float],
    parent_attach_x: Dict[DocumentRelationEdge, float],
) -> str:
    child_document_, parent_document_ = edge
    child_row, _ = layout[child_document_]
    parent_row, _ = layout[parent_document_]

    x1 = child_attach_x[edge]
    y1 = _box_y(child_row)
    x2 = parent_attach_x[edge]
    y2 = _box_y(parent_row) + BOX_HEIGHT

    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" '
        'marker-end="url(#specification_graph_arrow)" />'
    )


def _render_skip_edge(
    edge: DocumentRelationEdge,
    layout: Dict[SDocDocumentIF, DocumentPosition],
    lane_x: float,
    child_attach_x: Dict[DocumentRelationEdge, float],
    parent_attach_x: Dict[DocumentRelationEdge, float],
    child_stub_offset: Dict[DocumentRelationEdge, float],
    parent_stub_offset: Dict[DocumentRelationEdge, float],
) -> str:
    """
    Route a skip edge straight out of the child box's top edge, sideways
    into a dedicated vertical "lane" to the right of all document
    columns, down/up the lane, then sideways back into the parent box's
    bottom edge — instead of a straight line — so it doesn't overlap the
    normal edges of the direct chain it bypasses.
    """
    child_document_, parent_document_ = edge
    child_row, _ = layout[child_document_]
    parent_row, _ = layout[parent_document_]

    x_child = child_attach_x[edge]
    x_parent = parent_attach_x[edge]
    child_top_y = _box_y(child_row)
    child_stub_y = child_top_y - child_stub_offset[edge]
    parent_bottom_y = _box_y(parent_row) + BOX_HEIGHT
    parent_stub_y = parent_bottom_y + parent_stub_offset[edge]

    path = (
        f"M {x_child},{child_top_y} "
        f"L {x_child},{child_stub_y} "
        f"L {lane_x},{child_stub_y} "
        f"L {lane_x},{parent_stub_y} "
        f"L {x_parent},{parent_stub_y} "
        f"L {x_parent},{parent_bottom_y}"
    )

    return (
        f'<path d="{path}" fill="none" stroke="#b45309" '
        'stroke-dasharray="6,4" '
        'marker-end="url(#specification_graph_arrow_skip)" />'
    )


def render_svg(
    layout: Dict[SDocDocumentIF, DocumentPosition],
    edges: List[DocumentRelationEdge],
    skip_edges: List[DocumentRelationEdge],
) -> str:
    if not layout:
        return EMPTY_GRAPH_SVG

    max_row = max(row_ for row_, _ in layout.values())
    max_column = max(column_ for _, column_ in layout.values())

    width: float = (
        MARGIN * 2 + (max_column + 1) * BOX_WIDTH + max_column * COLUMN_GAP
    )
    height = MARGIN * 2 + (max_row + 1) * BOX_HEIGHT + max_row * ROW_GAP

    skip_edge_set: Set[DocumentRelationEdge] = set(skip_edges)

    # A skip edge's lane only needs to clear the widest row it actually
    # spans (from its parent's row down to its child's row), not the
    # widest row in the whole diagram - otherwise a skip edge confined to
    # narrow rows would still loop out past an unrelated wide row.
    row_max_column: Dict[int, int] = {}
    for row_, column_ in layout.values():
        row_max_column[row_] = max(row_max_column.get(row_, 0), column_)

    child_attach_x, parent_attach_x = _compute_edge_attachment_points(
        edges, layout
    )

    # A skip edge whose child column has nothing in the way straight
    # above it doesn't need to detour into a shared lane at all - its
    # own vertical is already the "lane" (edge 2 has zero length).
    direct_lane_x: Dict[DocumentRelationEdge, float] = {}
    routed_skip_edges: List[DocumentRelationEdge] = []
    for edge_ in skip_edges:
        direct_x = _skip_edge_direct_lane_x(
            edge_, layout, row_max_column, child_attach_x
        )
        if direct_x is not None:
            direct_lane_x[edge_] = direct_x
        else:
            routed_skip_edges.append(edge_)

    lane_x_by_edge = _assign_skip_lanes(
        routed_skip_edges, layout, row_max_column, child_attach_x, parent_attach_x
    )
    lane_x_by_edge.update(direct_lane_x)

    if lane_x_by_edge:
        width = max(width, max(lane_x_by_edge.values()) + MARGIN)

    parts: List[str] = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
            'role="img" aria-label="Specification graph">'
        ),
        "<defs>",
        (
            '<marker id="specification_graph_arrow" markerWidth="10" '
            'markerHeight="10" refX="8" refY="5" orient="auto">'
            '<path d="M0,0 L10,5 L0,10 z" />'
            "</marker>"
        ),
        (
            '<marker id="specification_graph_arrow_skip" markerWidth="10" '
            'markerHeight="10" refX="8" refY="5" orient="auto">'
            '<path d="M0,0 L10,5 L0,10 z" fill="#b45309" />'
            "</marker>"
        ),
        "</defs>",
    ]

    child_stub_offset, parent_stub_offset = _compute_skip_stub_offsets(
        skip_edges, layout, child_attach_x, parent_attach_x
    )
    for edge_ in edges:
        if edge_ in skip_edge_set:
            parts.append(
                _render_skip_edge(
                    edge_,
                    layout,
                    lane_x_by_edge[edge_],
                    child_attach_x,
                    parent_attach_x,
                    child_stub_offset,
                    parent_stub_offset,
                )
            )
        else:
            parts.append(
                _render_normal_edge(
                    edge_, layout, child_attach_x, parent_attach_x
                )
            )

    for document_, position_ in layout.items():
        parts.append(_render_document_box(document_, position_))

    parts.append("</svg>")
    return "\n".join(parts)
