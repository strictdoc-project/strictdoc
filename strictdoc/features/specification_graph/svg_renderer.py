"""
Render the Specification graph as hand-written SVG, from the layout
produced by `layout.compute_document_layout()` and the edges produced by
`relations.get_document_relation_edges()`.

Per task.md, no Python SVG library dependency is used for V1 — plain
string templates are enough for boxes, arrows, and text.
"""

import html
import textwrap
from typing import Dict, List, Set

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


def _render_normal_edge(
    edge: DocumentRelationEdge,
    layout: Dict[SDocDocumentIF, DocumentPosition],
) -> str:
    child_document_, parent_document_ = edge
    child_row, child_column = layout[child_document_]
    parent_row, parent_column = layout[parent_document_]

    x1 = _box_x(child_column) + BOX_WIDTH / 2
    y1 = _box_y(child_row)
    x2 = _box_x(parent_column) + BOX_WIDTH / 2
    y2 = _box_y(parent_row) + BOX_HEIGHT

    return (
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="black" '
        'marker-end="url(#specification_graph_arrow)" />'
    )


def _render_skip_edge(
    edge: DocumentRelationEdge,
    layout: Dict[SDocDocumentIF, DocumentPosition],
    lane_x: float,
) -> str:
    """
    Route a skip edge out to the right of the child box, straight down/up
    a dedicated vertical lane, then into the right side of the parent
    box — instead of a straight line — so it doesn't overlap the normal
    edges of the direct chain it bypasses.
    """
    child_document_, parent_document_ = edge
    child_row, child_column = layout[child_document_]
    parent_row, parent_column = layout[parent_document_]

    start_x = _box_x(child_column) + BOX_WIDTH
    start_y = _box_y(child_row) + BOX_HEIGHT / 2
    end_x = _box_x(parent_column) + BOX_WIDTH
    end_y = _box_y(parent_row) + BOX_HEIGHT / 2

    path = (
        f"M {start_x},{start_y} "
        f"L {lane_x},{start_y} "
        f"L {lane_x},{end_y} "
        f"L {end_x},{end_y}"
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

    rightmost_box_edge_x = _box_x(max_column) + BOX_WIDTH
    lane_x_by_edge: Dict[DocumentRelationEdge, float] = {
        edge_: rightmost_box_edge_x + SKIP_LANE_START_GAP + index_ * SKIP_LANE_GAP
        for index_, edge_ in enumerate(skip_edges)
    }
    if skip_edges:
        width = max(
            width,
            rightmost_box_edge_x
            + SKIP_LANE_START_GAP
            + len(skip_edges) * SKIP_LANE_GAP
            + MARGIN,
        )

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

    for edge_ in edges:
        if edge_ in skip_edge_set:
            parts.append(
                _render_skip_edge(edge_, layout, lane_x_by_edge[edge_])
            )
        else:
            parts.append(_render_normal_edge(edge_, layout))

    for document_, position_ in layout.items():
        parts.append(_render_document_box(document_, position_))

    parts.append("</svg>")
    return "\n".join(parts)
