"""
Specification graph gallery.

Run from the repository root:
    uv run python -m developer.examples.specification_graph.gallery

The script runs the graph generator on each gallery case and writes
gallery.html next to this script. Each case shows its title, description,
input, and the result of every implemented generator stage.
"""

import html
import itertools
import os
import re
from typing import Dict, List

from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CHAPTERS,
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
from strictdoc.features.specification_graph.svg_graph.structure_paths import (
    compute_structure_edge_paths,
)
from strictdoc.features.specification_graph.svg_graph.structure_routing import (
    compute_structure_routing,
)
from strictdoc.features.specification_graph.svg_graph.svg_serializer import (
    serialize_levels_svg,
    serialize_structure_svg,
)
from tests.unit.strictdoc.features.specification_graph.svg_graph.geometry_checks import (
    _collinear_contact,
    crossing_count,
)

OUTPUT_FILE_NAME = "gallery.html"


PAGE_STYLE = """
body { font-family: sans-serif; margin: 0; color: #222; }
.layout { display: flex; align-items: start; }
aside.sidebar {
  position: sticky; top: 0; flex: 0 0 222px; height: 100vh;
  overflow-y: auto; box-sizing: border-box; padding: 16px;
  border-right: 1px solid #ddd; background: #fafafa; font-size: 13px;
}
aside.sidebar h1 { margin: 0 0 12px; font-size: 18px; }
aside.sidebar input[type=search] {
  width: 100%; box-sizing: border-box; margin: 8px 0 12px; padding: 4px 6px;
}
aside.sidebar details { margin-bottom: 8px; }
aside.sidebar summary { font-weight: bold; cursor: pointer; }
aside.sidebar ol { margin: 4px 0 0; padding-left: 20px; }
aside.sidebar li { margin: 2px 0; }
aside.sidebar a { color: #235; text-decoration: none; }
aside.sidebar a.active { font-weight: bold; color: #b00; }
main { flex: 1; min-width: 0; padding: 16px 24px; }
h2.chapter {
  margin: 32px 0 16px; padding: 6px 10px; background: #333; color: #fff;
  font-size: 18px;
}
details.panels { margin-top: 8px; }
details.panels > summary { cursor: pointer; color: #555; font-size: 13px; }
details.panels > .columns { margin-top: 8px; }
@media (max-width: 900px) {
  .layout { display: block; }
  aside.sidebar {
    position: static; height: auto; border-right: none;
    border-bottom: 1px solid #ddd;
  }
}
section {
  margin-bottom: 40px; padding-bottom: 24px; border-bottom: 1px solid #ddd;
}
section h2 { margin-bottom: 4px; }
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
body:not(.show-debug) .specification-graph-debug { display: none; }
.debug-toggle { display: inline-block; margin: 0 0 16px; font-size: 14px; }
.preview { margin: 8px 0 16px; }
figure { margin: 0; }
.figures { display: flex; gap: 24px; flex-wrap: wrap; align-items: start; }
figure h3 { margin: 0 0 4px; font-size: 14px; }
figure.rejected { padding: 8px; border: 2px dashed #b00; background: #fff5f5; }
figure.rejected h3 { color: #b00; }
figure .note { max-width: 520px; font-size: 12px; color: #444; }
ul.conflicts { margin: 4px 0; font-size: 12px; color: #a50; }
.preview p { margin: 4px 0; color: #666; font-size: 12px; }
a.to-top {
  position: fixed; right: 24px; bottom: 24px; padding: 8px 12px;
  border-radius: 6px; background: #333; color: #fff; text-decoration: none;
  font-size: 14px; opacity: 0.8;
}
a.to-top:hover { opacity: 1; }
"""


# Constant styles of the generator SVG.
GENERATOR_CSS_PATH = os.path.join(
    os.path.dirname(svg_serializer.__file__), "specification_graph.css"
)


def main() -> None:
    with open(GENERATOR_CSS_PATH, encoding="utf-8") as css_file:
        generator_css = css_file.read()
    anchors = _case_anchors()
    content: List[str] = []
    navigation: List[str] = []
    index = 0
    for chapter_ in GALLERY_CHAPTERS:
        content.append(
            f'<h2 class="chapter">{html.escape(chapter_.title)}</h2>'
        )
        items_: List[str] = []
        for case_ in chapter_.cases:
            anchor_ = anchors[case_.title]
            content.append(_render_case(index, anchor_, case_))
            items_.append(
                f'<li><a href="#{anchor_}">{html.escape(case_.title)}</a></li>'
            )
            index += 1
        navigation.append(
            f"<details open><summary>{html.escape(chapter_.title)}</summary>"
            f"<ol>{''.join(items_)}</ol></details>"
        )
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Specification graph gallery</title>
<style>{PAGE_STYLE}</style>
<style>{generator_css}</style>
</head>
<body id="top" class="show-debug">
<a class="to-top" href="#top">&uarr; Top</a>
<div class="layout">
<aside class="sidebar">
<h1>Specification graph gallery</h1>
<label class="debug-toggle"><input type="checkbox" id="debug-toggle" checked>
Show debug layer</label>
<input type="search" id="case-filter" placeholder="Filter cases">
<nav>
{"".join(navigation)}
</nav>
</aside>
<main>
<p>Debug layer: channels (blue) and lanes (pink). Regenerate from the
repository root: <code>uv run python -m
developer.examples.specification_graph.gallery</code></p>
{"".join(content)}
</main>
</div>
<script>{PAGE_SCRIPT}</script>
</body>
</html>
"""
    output_path = os.path.join(os.path.dirname(__file__), OUTPUT_FILE_NAME)
    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(page)
    print(f"Written: {output_path}")  # noqa: T201


# The debug toggle, the case filter, and the highlight of the current case
# in the navigation.
PAGE_SCRIPT = """
document.getElementById("debug-toggle").addEventListener("change", (event) => {
  document.body.classList.toggle("show-debug", event.target.checked);
});
document.getElementById("case-filter").addEventListener("input", (event) => {
  const query = event.target.value.trim().toLowerCase();
  for (const chapter of document.querySelectorAll("aside nav details")) {
    let visible = 0;
    for (const item of chapter.querySelectorAll("li")) {
      const match = item.textContent.toLowerCase().includes(query);
      item.hidden = !match;
      visible += match ? 1 : 0;
    }
    chapter.hidden = visible === 0;
    if (query.length > 0) {
      chapter.open = true;
    }
  }
});
const links = new Map();
for (const link of document.querySelectorAll("aside nav a")) {
  links.set(link.getAttribute("href").slice(1), link);
}
const observer = new IntersectionObserver((entries) => {
  for (const entry of entries) {
    if (entry.isIntersecting) {
      for (const link of links.values()) {
        link.classList.remove("active");
      }
      const link = links.get(entry.target.id);
      if (link !== undefined) {
        link.classList.add("active");
        link.scrollIntoView({block: "nearest"});
      }
    }
  }
}, {rootMargin: "0px 0px -70% 0px"});
for (const section of document.querySelectorAll("main section")) {
  observer.observe(section);
}
"""


def _case_anchors() -> Dict[str, str]:
    """
    Return a stable anchor for each case, made from its title.
    """

    result: Dict[str, str] = {}
    used: Dict[str, int] = {}
    for chapter_ in GALLERY_CHAPTERS:
        for case_ in chapter_.cases:
            slug_ = re.sub(r"[^a-z0-9]+", "-", case_.title.lower()).strip("-")
            count_ = used.get(slug_, 0)
            used[slug_] = count_ + 1
            result[case_.title] = slug_ if count_ == 0 else f"{slug_}-{count_}"
    return result


def _render_case(index: int, anchor: str, case: GalleryCase) -> str:
    normalized_graph = normalize_graph(case.graph)
    badges = f'<span class="badge">mode: {case.graph.mode.value}</span>'
    return f"""
<section id="{anchor}">
<h2>{html.escape(case.title)}</h2>
<div>{badges}</div>
<p class="description">{html.escape(case.description)}</p>
{_render_routes(index, case, normalized_graph)}
<details class="panels">
<summary>Input and stage 1: normalization</summary>
<div class="columns">
{_render_input(case)}
{_render_normalization(normalized_graph)}
</div>
</details>
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
    routing = compute_structure_routing(normalized_graph, layout)
    geometry = compute_structure_geometry(
        normalized_graph,
        layout,
        lane_counts=routing.lane_counts,
        bottom_segments=routing.bottom_segments,
        side_entries=routing.side_entries,
    )
    edge_paths = compute_structure_edge_paths(routing, geometry)
    svg = serialize_structure_svg(
        normalized_graph,
        routing,
        geometry,
        edge_paths,
        debug=True,
        svg_id=f"case-{index}-result",
    )
    unrouted = ", ".join(html.escape(id_) for id_ in routing.unrouted_edge_ids)
    note = (
        "<p>Not routed yet (relations across containers or with a "
        f"section): {unrouted}.</p>"
        if len(unrouted) > 0
        else ""
    )
    paths = list(edge_paths.values())
    crossings = sum(
        crossing_count(first_, second_)
        for first_, second_ in itertools.combinations(paths, 2)
    )
    overlaps = sum(
        1
        for first_, second_ in itertools.combinations(paths, 2)
        if any(
            _collinear_contact(first_segment_, second_segment_)
            for first_segment_ in zip(first_, first_[1:])
            for second_segment_ in zip(second_, second_[1:])
        )
    )
    return f"""<div class="preview">
<figure>
<h3>Generator result</h3>
{svg}
<p class="note">Crossings: {crossings}. Overlaps: {overlaps}.</p>
</figure>
{note}
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
        normalized_graph,
        structure,
        routing,
        geometry,
        debug=True,
        svg_id=svg_id,
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
