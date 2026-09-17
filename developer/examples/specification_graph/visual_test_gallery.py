"""
Visual test gallery for the Specification Graph SVG renderer.

Builds hand-crafted (row, column) layouts and edge lists directly -
bypassing relations.py/TraceabilityIndex and any real .sdoc project - so
routing edge cases (highway conflicts, clear vs. blocked skip edges,
shared/independent lanes, wide-row isolation) can be reviewed side by
side in one page, without constructing a fixture project per case.

Run:
    uv run python developer/examples/specification_graph/visual_test_gallery.py

Writes visual_test_gallery.html next to this script; open it in a browser.
"""

import os
from typing import Dict, List, Tuple

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.features.specification_graph.layout import (
    DocumentPosition,
    get_skip_edges,
)
from strictdoc.features.specification_graph.relations import (
    DocumentRelationEdge,
)
from strictdoc.features.specification_graph.svg_renderer import render_svg
from tests.unit.helpers.document_builder import DocumentBuilder

Scenario = Tuple[str, str, List[List[str]], List[Tuple[str, str]]]

# (name, description, rows (top to bottom, each a list of document names
# left to right), edges (child_name, parent_name))
SCENARIOS: List[Scenario] = [
    (
        "Simple chain",
        "No detours: A <- B <- C, one document per row.",
        [["A"], ["B"], ["C"]],
        [("B", "A"), ("C", "B")],
    ),
    (
        "Basic highway conflict",
        (
            "D relates to both A (directly) and C (via B) - the deepest "
            "chain (through C) wins, so the D->A relation becomes a skip "
            "edge."
        ),
        [["A"], ["B"], ["C"], ["D"]],
        [("B", "A"), ("C", "B"), ("D", "A"), ("D", "C")],
    ),
    (
        "Narrow row in the middle - local lane",
        (
            "Row B has a single document; C1 and C2 both detour around "
            "it, each with its own short, local lane (not sized to row "
            "C's width)."
        ),
        [["A1", "A2"], ["B"], ["C1", "C2"], ["D1", "D2"]],
        [
            ("B", "A1"),
            ("C1", "B"),
            ("C2", "B"),
            ("D1", "C1"),
            ("D2", "C2"),
            ("C1", "A1"),
            ("C2", "A2"),
        ],
    ),
    (
        "No diagonal: right -> left, nothing to dodge",
        (
            "C2 (right document) -> A1 (left document). Directly above "
            "C2, row B is empty, so edge 2 (the detour) has zero length: "
            "edges 1 and 3 sit on the same vertical, and edge 4 just "
            "carries the arrowhead left to A1."
        ),
        [["A1", "A2"], ["B"], ["C1", "C2"]],
        [
            ("B", "A1"),
            ("B", "A2"),
            ("C1", "B"),
            ("C2", "B"),
            ("C1", "A1"),
            ("C2", "A1"),
        ],
    ),
    (
        "Still no diagonal when a detour IS needed",
        (
            "C1 (left document) -> A2 (right). Row B sits directly above "
            "C1 (column 0) - a detour is required, but the path stays "
            "orthogonal (edge 2 is non-zero), never diagonal."
        ),
        [["A1", "A2"], ["B"], ["C1", "C2"]],
        [
            ("B", "A1"),
            ("B", "A2"),
            ("C1", "B"),
            ("C2", "B"),
            ("C1", "A2"),
        ],
    ),
    (
        "Independent detours share one lane",
        (
            "Two unrelated groups (A0-B1-C2 and A4-B5-C6, separated by "
            "filler documents) don't overlap in rows - their skip edges "
            "reuse the same lane instead of drifting further right one "
            "after another."
        ),
        [
            ["A0", "F0"],
            ["B1", "F1"],
            ["C2", "F2"],
            ["", "F3"],
            ["", "F4"],
            ["", "A5"],
            ["", "B6"],
            ["", "C7"],
        ],
        [
            ("B1", "A0"),
            ("C2", "B1"),
            ("C2", "A0"),
            ("F1", "F0"),
            ("F2", "F1"),
            ("F3", "F2"),
            ("F4", "F3"),
            ("A5", "F4"),
            ("B6", "A5"),
            ("C7", "B6"),
            ("C7", "A5"),
        ],
    ),
    (
        "Overlapping detours - different lanes",
        (
            "C1->A1 and C2->A2 both span rows 1-3 (they overlap each "
            "other) - they must get different lanes. D1->B spans rows "
            "2-4 (overlaps both) - a third lane."
        ),
        [["A1", "A2"], ["B"], ["C1", "C2"], ["D1", "D2"]],
        [
            ("B", "A1"),
            ("B", "A2"),
            ("C1", "B"),
            ("C2", "B"),
            ("D1", "C1"),
            ("D2", "C2"),
            ("C1", "A1"),
            ("C2", "A2"),
            ("D1", "B"),
        ],
    ),
    (
        "Isolated document + hierarchy",
        (
            "E has no relations at all - it stays alone in row 0. The "
            "A-B-C-D hierarchy starts at row 1 (not row 0), since A is "
            "the top of the hierarchy (incoming relations only)."
        ),
        [["E"], ["A"], ["B"], ["C"], ["D"]],
        [("B", "A"), ("C", "B"), ("D", "A"), ("D", "C")],
    ),
    (
        "A wide row doesn't affect an unrelated narrow detour",
        (
            "Row 0 has 5 unrelated documents (just to widen the canvas). "
            "A separate, narrow A-B-C chain detours around B: its lane is "
            "sized to that chain's own local width, not row 0's width."
        ),
        [
            ["W0", "W1", "W2", "W3", "W4"],
            ["A"],
            ["B"],
            ["C"],
        ],
        [("B", "A"), ("C", "B"), ("C", "A")],
    ),
]


def _build_layout_and_edges(
    rows: List[List[str]], edge_names: List[Tuple[str, str]]
) -> Tuple[
    Dict[SDocDocument, DocumentPosition],
    List[DocumentRelationEdge],
]:
    documents_by_name: Dict[str, SDocDocument] = {}
    layout: Dict[SDocDocument, DocumentPosition] = {}
    for row_index, names_in_row in enumerate(rows):
        for column_index, name in enumerate(names_in_row):
            if not name:
                continue
            document = DocumentBuilder(name).build()
            document.title = name
            documents_by_name[name] = document
            layout[document] = (row_index, column_index)

    edges: List[DocumentRelationEdge] = [
        (documents_by_name[child_name], documents_by_name[parent_name])
        for child_name, parent_name in edge_names
    ]
    return layout, edges


def _render_scenario(name: str, description: str, svg: str) -> str:
    return f"""
    <section>
      <h2>{name}</h2>
      <p>{description}</p>
      <div class="svg-wrap">{svg}</div>
    </section>
    """


def main() -> None:
    sections = []
    for name, description, rows, edge_names in SCENARIOS:
        layout, edges = _build_layout_and_edges(rows, edge_names)
        skip_edges = get_skip_edges(edges, layout)
        svg = render_svg(layout=layout, edges=edges, skip_edges=skip_edges)
        sections.append(_render_scenario(name, description, svg))

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Specification Graph - visual test gallery</title>
<style>
  body {{ font-family: sans-serif; margin: 24px; color: #222; }}
  section {{ margin-bottom: 48px; padding-bottom: 24px; border-bottom: 1px solid #ddd; }}
  h2 {{ margin-bottom: 4px; }}
  p {{ color: #555; max-width: 800px; }}
  .svg-wrap {{ overflow: auto; border: 1px dashed #ccc; padding: 8px; }}
  svg {{ display: block; }}
</style>
</head>
<body>
<h1>Specification Graph - visual test gallery</h1>
<p>Regenerate: <code>uv run python developer/examples/specification_graph/visual_test_gallery.py</code></p>
{"".join(sections)}
</body>
</html>
"""

    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "visual_test_gallery.html",
    )
    with open(output_path, "w", encoding="utf-8") as file_:
        file_.write(html)
    print(f"Wrote {output_path}")  # noqa: T201


if __name__ == "__main__":
    main()
