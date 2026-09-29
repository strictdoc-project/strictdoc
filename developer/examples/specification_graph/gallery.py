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
from strictdoc.features.specification_graph.svg_graph.model import GraphNode
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedGraph,
    normalize_graph,
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
.badge.question { background: #ffe8b3; }
.columns { display: flex; gap: 24px; flex-wrap: wrap; align-items: start; }
.panel { border: 1px solid #ddd; padding: 8px 12px; background: #fafafa; }
.panel h3 { margin: 0 0 8px; font-size: 14px; }
pre { margin: 0; font-size: 13px; line-height: 1.4; }
table { border-collapse: collapse; font-size: 13px; }
td, th { border: 1px solid #ddd; padding: 2px 6px; text-align: left; }
.no { color: #b00; }
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


if __name__ == "__main__":
    main()
