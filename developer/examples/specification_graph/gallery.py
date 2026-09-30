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
from typing import List

from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CASES,
    GalleryCase,
)
from strictdoc.features.specification_graph.svg_graph import svg_serializer
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    compute_levels_geometry,
)
from strictdoc.features.specification_graph.svg_graph.levels_routing import (
    Orientation,
    RoutingOptions,
    compute_levels_routing,
)
from strictdoc.features.specification_graph.svg_graph.levels_structure import (
    LevelsStructure,
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
from strictdoc.features.specification_graph.svg_graph.structure_geometry import (
    compute_structure_geometry,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    compute_structure_layout,
)
from strictdoc.features.specification_graph.svg_graph.svg_serializer import (
    serialize_levels_svg,
    serialize_structure_svg,
)

OUTPUT_FILE_NAME = "gallery.html"


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
.columns { display: flex; gap: 24px; flex-wrap: wrap; align-items: start; }
.panel { border: 1px solid #ddd; padding: 8px 12px; background: #fafafa; }
.panel h3 { margin: 0 0 8px; font-size: 14px; }
pre { margin: 0; font-size: 13px; line-height: 1.4; }
table { border-collapse: collapse; font-size: 13px; }
td, th { border: 1px solid #ddd; padding: 2px 6px; text-align: left; }
.no { color: #b00; }
.preview { margin: 8px 0 16px; }
figure { margin: 0; }
.figures { display: flex; gap: 24px; flex-wrap: wrap; align-items: start; }
figure h3 { margin: 0 0 4px; font-size: 14px; }
figure.rejected { padding: 8px; border: 2px dashed #b00; background: #fff5f5; }
figure.rejected h3 { color: #b00; }
figure .note { max-width: 520px; font-size: 12px; color: #444; }
ul.conflicts { margin: 4px 0; font-size: 12px; color: #a50; }
.preview p { margin: 4px 0; color: #666; font-size: 12px; }
"""


# Constant styles of the generator SVG.
GENERATOR_CSS_PATH = os.path.join(
    os.path.dirname(svg_serializer.__file__), "specification_graph.css"
)


def main() -> None:
    with open(GENERATOR_CSS_PATH, encoding="utf-8") as css_file:
        generator_css = css_file.read()
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
<style>{generator_css}</style>
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
    return f"""
<section id="case-{index}">
<h2>{html.escape(case.title)}</h2>
<div>{badges}</div>
<p class="description">{html.escape(case.description)}</p>
{_render_routes(index, case, normalized_graph)}
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


def _render_routes(
    index: int, case: GalleryCase, normalized_graph: NormalizedGraph
) -> str:
    if normalized_graph.mode is LayoutMode.STRUCTURE:
        return _render_structure(index, normalized_graph)
    if normalized_graph.mode is not LayoutMode.LEVELS:
        return ""
    structure = compute_levels_structure(normalized_graph)
    figures = _render_levels_svg(
        normalized_graph,
        structure,
        RoutingOptions(),
        f"case-{index}-result",
        "Generator result",
    )
    alternative = case.rejected_alternative
    if alternative is not None:
        figures += _render_levels_svg(
            normalized_graph,
            structure,
            alternative.options,
            f"case-{index}-rejected",
            "Rejected alternative: the generator does not use this route",
            (
                f"{html.escape(alternative.description)} Rendered only here, "
                f"with the option <code>"
                f"{html.escape(alternative.option_code)}</code>."
            ),
        )
    return f"""<div class="preview">
<div class="figures">{figures}</div>
<p>Built-in relation types: warning (dashed) marks a relation across
levels, danger (red) marks a cycle. The "!" sign marks a node with a
diagnostic.</p>
</div>"""


def _render_structure(index: int, normalized_graph: NormalizedGraph) -> str:
    layout = compute_structure_layout(normalized_graph)
    geometry = compute_structure_geometry(normalized_graph, layout)
    svg = serialize_structure_svg(
        normalized_graph, geometry, svg_id=f"case-{index}-result"
    )
    return f"""<div class="preview">
<figure>
<h3>Generator result</h3>
{svg}
</figure>
<p>The routing of the structure mode is not implemented yet. The picture
shows the layout of the nodes and containers without relations.</p>
</div>"""


def _render_levels_svg(
    normalized_graph: NormalizedGraph,
    structure: LevelsStructure,
    options: RoutingOptions,
    svg_id: str,
    caption: str,
    note: str = "",
) -> str:
    routing = compute_levels_routing(normalized_graph, structure, options)
    geometry = compute_levels_geometry(structure, routing)
    svg = serialize_levels_svg(
        normalized_graph, structure, routing, geometry, svg_id=svg_id
    )

    conflicts = "".join(
        f"<li>{html.escape(conflict_.outer_edge_id)} crosses "
        f"{html.escape(conflict_.inner_edge_id)} in "
        + (
            "H"
            if conflict_.channel.orientation is Orientation.HORIZONTAL
            else "V"
        )
        + f"({conflict_.channel.index})</li>"
        for conflict_ in routing.conflicts
    )
    conflict_list = (
        "<p class='note'>Unavoidable crossings of nested segments:</p>"
        f"<ul class='conflicts'>{conflicts}</ul>"
        if len(conflicts) > 0
        else ""
    )
    is_rejected = options != RoutingOptions()
    figure_class = ' class="rejected"' if is_rejected else ""
    note_html = f'<p class="note">{note}</p>' if len(note) > 0 else ""
    return f"""<figure{figure_class}>
<h3>{html.escape(caption)}</h3>
{note_html}
{svg}
{conflict_list}
</figure>"""


if __name__ == "__main__":
    main()
