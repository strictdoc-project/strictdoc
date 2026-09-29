"""
Specification graph gallery.

Run from the repository root:
    uv run python -m developer.examples.specification_graph.gallery

The script runs the graph generator on each gallery case and writes
gallery.html next to this script. Each case shows its title, description,
input, and the result of every implemented generator stage.
"""

import html
import os
from typing import List, Tuple

from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CASES,
    GalleryCase,
)
from strictdoc.features.specification_graph.svg_graph.levels_structure import (
    compute_levels_structure,
)
from strictdoc.features.specification_graph.svg_graph.model import (
    GraphNode,
    LayoutMode,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedGraph,
    normalize_graph,
)

OUTPUT_FILE_NAME = "gallery.html"

# Stage 2 preview geometry, in pixels.
PREVIEW_CELL_WIDTH = 150
PREVIEW_CELL_HEIGHT = 70
PREVIEW_NODE_WIDTH = 120
PREVIEW_NODE_HEIGHT = 36
PREVIEW_MARGIN = 10

PAGE_STYLE = """
body { font-family: sans-serif; margin: 24px; color: #222; }
nav ol { columns: 2; }
section {
  margin-bottom: 40px; padding-bottom: 24px; border-bottom: 1px solid #ddd;
}
h2 { margin-bottom: 4px; }
p.description { color: #444; max-width: 800px; }
.badge {
  display: inline-block; padding: 1px 6px; margin-right: 6px;
  border-radius: 4px; background: #eee; font-size: 12px;
}
.badge.question { background: #ffe8b3; }
.columns { display: flex; gap: 24px; flex-wrap: wrap; align-items: start; }
.panel { border: 1px solid #ddd; padding: 8px 12px; background: #fafafa; }
.panel h3 { margin: 0 0 8px; font-size: 14px; }
pre { margin: 0; font-size: 13px; line-height: 1.4; }
table { border-collapse: collapse; font-size: 13px; }
td, th { border: 1px solid #ddd; padding: 2px 6px; text-align: left; }
.no { color: #b00; }
.preview { margin: 8px 0 16px; }
.preview p { margin: 4px 0; color: #666; font-size: 12px; }
"""


def main() -> None:
    sections: List[str] = []
    for index_, case_ in enumerate(GALLERY_CASES):
        sections.append(_render_case(index_, case_))

    navigation = "\n".join(
        f'<li><a href="#case-{index_}">{html.escape(case_.title)}</a></li>'
        for index_, case_ in enumerate(GALLERY_CASES)
    )
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Specification graph gallery</title>
<style>{PAGE_STYLE}</style>
</head>
<body>
<h1>Specification graph gallery</h1>
<p>Regenerate from the repository root: <code>uv run python -m
developer.examples.specification_graph.gallery</code></p>
<nav><ol>
{navigation}
</ol></nav>
{"".join(sections)}
</body>
</html>
"""
    output_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE_NAME)
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(page)
    print(f"Written: {output_path}")  # noqa: T201


def _render_case(index: int, case: GalleryCase) -> str:
    normalized_graph = normalize_graph(case.graph)
    badges = f'<span class="badge">mode: {case.graph.mode.value}</span>'
    if case.open_question is not None:
        badges += (
            f'<span class="badge question">'
            f"open question {case.open_question}</span>"
        )
    return f"""
<section id="case-{index}">
<h2>{html.escape(case.title)}</h2>
<div>{badges}</div>
<p class="description">{html.escape(case.description)}</p>
{_render_structure_preview(normalized_graph)}
<div class="columns">
{_render_input(case)}
{_render_normalization(normalized_graph)}
</div>
</section>
"""


def _render_input(case: GalleryCase) -> str:
    lines: List[str] = []
    for node_ in case.graph.root:
        _append_node_lines(node_, 0, lines)
    lines.append("")
    for edge_ in case.graph.edges:
        lines.append(
            f"{edge_.source_id} -> {edge_.target_id} ({edge_.relation_type})"
        )
    return f"""<div class="panel">
<h3>Input: nodes, then edges</h3>
<pre>{html.escape(chr(10).join(lines))}</pre>
</div>"""


def _append_node_lines(node: GraphNode, depth: int, lines: List[str]) -> None:
    group = f" [group: {node.group_id}]" if node.group_id is not None else ""
    lines.append(f"{'  ' * depth}{node.node_id}{group}")
    for child_ in node.children:
        _append_node_lines(child_, depth + 1, lines)


def _render_normalization(normalized_graph: NormalizedGraph) -> str:
    rows = "\n".join(
        "<tr>"
        f"<td>{edge_.edge_id}</td>"
        f"<td>{html.escape(edge_.source_id)}</td>"
        f"<td>{html.escape(edge_.target_id)}</td>"
        f"<td>{html.escape(edge_.relation_type)}</td>"
        f"<td{'' if edge_.is_level_edge else ' class=no'}>"
        f"{'yes' if edge_.is_level_edge else 'no'}</td>"
        f"<td>{edge_.cycle_id if edge_.cycle_id is not None else ''}</td>"
        f"<td>{'yes' if edge_.is_ancestor_link else ''}</td>"
        "</tr>"
        for edge_ in normalized_graph.edges
    )
    diagnostics = "\n".join(
        f"<li>{html.escape(diagnostic_.message)}</li>"
        for diagnostic_ in normalized_graph.diagnostics
    )
    if len(diagnostics) == 0:
        diagnostics = "<li>None.</li>"
    return f"""<div class="panel">
<h3>Stage 1: normalization</h3>
<table>
<tr><th>ID</th><th>Source</th><th>Target</th><th>Type</th>
<th>Level edge</th><th>Cycle</th><th>Ancestor link</th></tr>
{rows}
</table>
<h3>Diagnostics</h3>
<ul>{diagnostics}</ul>
</div>"""


def _render_structure_preview(normalized_graph: NormalizedGraph) -> str:
    """
    Render the stage 2 result: nodes in grid cells and straight relations.

    The preview shows the logical grid only. The lines are straight segments
    between node centers. The preview does not route the relations.
    """

    if normalized_graph.mode is not LayoutMode.LEVELS:
        return ""
    structure = compute_levels_structure(normalized_graph)
    cyclic_node_ids = {
        node_id_
        for cycle_ in normalized_graph.cycles
        for node_id_ in cycle_.node_ids
    }

    def node_box(node_id: str) -> Tuple[float, float]:
        position = structure.positions[node_id]
        return (
            PREVIEW_MARGIN
            + position.column * PREVIEW_CELL_WIDTH
            + (PREVIEW_CELL_WIDTH - PREVIEW_NODE_WIDTH) / 2,
            PREVIEW_MARGIN
            + position.row * PREVIEW_CELL_HEIGHT
            + (PREVIEW_CELL_HEIGHT - PREVIEW_NODE_HEIGHT) / 2,
        )

    elements: List[str] = []
    if structure.standalone_row_count > 0:
        elements.append(
            f'<rect x="{PREVIEW_MARGIN / 2}" y="{PREVIEW_MARGIN / 2}" '
            f'width="{structure.column_count * PREVIEW_CELL_WIDTH + PREVIEW_MARGIN}" '
            f'height="{structure.standalone_row_count * PREVIEW_CELL_HEIGHT + PREVIEW_MARGIN}" '
            'fill="#f3f3f3" stroke="#ccc" stroke-dasharray="4 3"/>'
        )
    for edge_ in normalized_graph.edges:
        source_x_, source_y_ = node_box(edge_.source_id)
        target_x_, target_y_ = node_box(edge_.target_id)
        color_ = "#c00" if edge_.cycle_id is not None else "#555"
        dash_ = (
            ' stroke-dasharray="6 4"'
            if edge_.edge_id in structure.skip_edge_ids
            else ""
        )
        elements.append(
            f'<line x1="{source_x_ + PREVIEW_NODE_WIDTH / 2}" '
            f'y1="{source_y_ + PREVIEW_NODE_HEIGHT / 2}" '
            f'x2="{target_x_ + PREVIEW_NODE_WIDTH / 2}" '
            f'y2="{target_y_ + PREVIEW_NODE_HEIGHT / 2}" '
            f'stroke="{color_}" stroke-width="1.5"{dash_} '
            f'marker-end="url(#preview-arrow)">'
            f"<title>{html.escape(edge_.edge_id)}: "
            f"{html.escape(edge_.source_id)} -&gt; "
            f"{html.escape(edge_.target_id)}</title></line>"
        )
    for node_ in normalized_graph.nodes:
        x_, y_ = node_box(node_.node_id)
        stroke_ = "#c00" if node_.node_id in cyclic_node_ids else "#333"
        stroke_width_ = (
            "3" if node_.node_id in structure.corrected_root_ids else "1"
        )
        elements.append(
            f'<rect x="{x_}" y="{y_}" width="{PREVIEW_NODE_WIDTH}" '
            f'height="{PREVIEW_NODE_HEIGHT}" rx="4" fill="#e8f0fb" '
            f'stroke="{stroke_}" stroke-width="{stroke_width_}"/>'
            f'<text x="{x_ + PREVIEW_NODE_WIDTH / 2}" '
            f'y="{y_ + PREVIEW_NODE_HEIGHT / 2}" text-anchor="middle" '
            f'dominant-baseline="middle" font-size="12">'
            f"{html.escape(node_.title)}</text>"
        )

    width = structure.column_count * PREVIEW_CELL_WIDTH + 2 * PREVIEW_MARGIN
    height = structure.row_count * PREVIEW_CELL_HEIGHT + 2 * PREVIEW_MARGIN
    return f"""<div class="preview">
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
<defs><marker id="preview-arrow" viewBox="0 0 10 10" refX="10" refY="5"
markerWidth="7" markerHeight="7" orient="auto-start-reverse">
<path d="M 0 0 L 10 5 L 0 10 z" fill="#555"/></marker></defs>
{chr(10).join(elements)}
</svg>
<p>Stage 2 preview: grid cells and straight lines between node centers,
without routing. Dashed: relation across levels. Red: cycle. Thick border:
corrected root. Grey area: standalone nodes.</p>
</div>"""


if __name__ == "__main__":
    main()
