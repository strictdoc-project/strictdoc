"""
Specification graph rules gallery.

Run from the repository root:
    uv run python -m developer.examples.specification_graph.rules_gallery
    uv run python -m developer.examples.specification_graph.rules_gallery --find

Each rule of the structure mode routing has a mutation in mutations.py that
switches the rule off. The page shows each rule on the smallest graph found
where the rule changes the drawing, rendered twice by the generator: with
the rule, and with its mutation applied. The edges that differ are
highlighted.

--find searches the structure cases of the gallery and small random graphs
and writes rules_gallery_cases.json.
The default command reads that file and writes rules.html. Both commands
apply mutations to the package files for a moment, like mutations.py: run
them alone, not together with tests, the gallery, or the mutation check.
"""

import html
import itertools
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from developer.examples.specification_graph.gallery import (
    GENERATOR_CSS_PATH,
    PAGE_STYLE,
)
from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CASES,
    StructureSpec,
    _structure_case,
)
from developer.examples.specification_graph.mutations import (
    MUTATIONS,
    Mutation,
)
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    Point,
)
from strictdoc.features.specification_graph.svg_graph.model import (
    GraphNode,
    LayoutMode,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
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
    CSS_PREFIX,
    serialize_structure_svg,
)
from tests.unit.strictdoc.features.specification_graph.svg_graph.geometry_checks import (
    _collinear_contact,
    crossing_count,
)

HERE = os.path.dirname(os.path.abspath(__file__))
CASES_FILE = os.path.join(HERE, "rules_gallery_cases.json")
OUTPUT_FILE = os.path.join(HERE, "rules.html")
MODULE = "developer.examples.specification_graph.rules_gallery"

# The search: how many random graphs, and the seed that makes them repeat.
SEARCH_COUNT = 400
SEARCH_SEED = 1

# A graph of the gallery as JSON: the tree of the root and the edges.
GraphData = Dict[str, Any]
# Edge ID -> polyline as a list of [x, y].
PathsData = Dict[str, List[List[float]]]


@dataclass(frozen=True)
class Rule:
    # The mutation that switches the rule off.
    mutation_id: str
    title: str
    text: str


RULES: Tuple[Rule, ...] = (
    Rule(
        "LO1",
        "Ends at one point",
        "Two ends at the same point go to different sides: the segment "
        "whose end goes up lies higher. The other order lays the two lines "
        "on top of each other.",
    ),
    Rule(
        "EX1",
        "Stand-in positions do not coincide",
        "A position that stands for a lane not known yet can equal another "
        "one while the lanes differ, so it never counts as the same point.",
    ),
    Rule(
        "LO2",
        "Reasons by strength",
        "Each order between two segments has a reason. The stronger "
        "reasons are taken first.",
    ),
    Rule(
        "LO3",
        "A weaker order gives way",
        "An order that contradicts the stronger orders already taken is "
        "dropped.",
    ),
    Rule(
        "LO5",
        "Pocket first",
        "Under the columns, of two overlapping segments, the one with the "
        "higher base height lies higher. A pocket is empty space for every "
        "line that fits. A row keeps the height of its lane and has no base "
        "height.",
    ),
    Rule(
        "LO6",
        "Base heights before ends at one point",
        "The base heights under the columns are the strongest reason for "
        "the order of two segments, stronger than two ends at one point: "
        "under the columns the heights, not a choice, decide which segment "
        "lies higher.",
    ),
    Rule(
        "TR1",
        "Right-hand traffic",
        "Two overlapping segments of different directions whose ends set "
        "no order: the one that goes left lies above, the one that goes up "
        "lies right.",
    ),
    Rule(
        "R2",
        "Exit priority",
        "An unavoidable crossing of a segment nested in another one lies "
        "near the source.",
    ),
    Rule(
        "ST1",
        "Shared stretch",
        "Two routes that pass the same chain of channels keep one order on "
        "the whole chain.",
    ),
    Rule(
        "ST3",
        "Stretch only where the segments overlap",
        "A channel at the end of a stretch where the segments only touch "
        "does not belong to the stretch.",
    ),
    Rule(
        "ST4",
        "A stretch of one channel",
        "A single common channel is a stretch too.",
    ),
    Rule(
        "ST5",
        "A stretch trimmed to one channel",
        "A stretch that keeps one channel after the trimming is still a "
        "stretch.",
    ),
    Rule(
        "ST8",
        "No stretch inside a stretch",
        "A single channel inside a longer stretch is no stretch of its "
        "own: it could order the pair against the whole stretch.",
    ),
    Rule(
        "ST6",
        "A through pass is no turn",
        "A route goes on straight through a through pass and leaves the "
        "stretch where it really turns.",
    ),
    Rule(
        "ST7",
        "Turns to different sides",
        "At an end of a stretch where the routes turn off to different "
        "sides, each route lies on the side it turns to.",
    ),
    Rule(
        "ST9",
        "A pair between shared faces",
        "A pair whose stretch ends on shared faces at both ends keeps the "
        "order of right-hand traffic on the whole stretch.",
    ),
    Rule(
        "ST10",
        "A pair that must cross",
        "Two routes that go the same way and must cross keep the order of "
        "the end where they come together, and cross where they part.",
    ),
    Rule(
        "GP1",
        "Port orders hold together",
        "All forced port orders of one face hold at once.",
    ),
    Rule(
        "CL1",
        "Lanes of a column channel",
        "Lanes = max(segments to the left, segments to the right) + "
        "segments across. Segments to the left and to the right share "
        "lanes, whatever their directions.",
    ),
)


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "--worker":
        _worker(sys.argv[2])
    elif len(sys.argv) >= 2 and sys.argv[1] == "--find":
        _find()
    else:
        _write_page()


def _find() -> None:
    """
    Find for each rule the smallest graph where the rule changes the
    drawing, and write them to the cases file.
    """

    graphs = _gallery_graphs() + _random_graphs(SEARCH_SEED, SEARCH_COUNT)
    baseline = [_route(graph_)[0] for graph_ in graphs]
    mutations = _mutations_by_id()
    found: Dict[str, Optional[GraphData]] = {}
    for rule_ in RULES:
        mutated_ = _route_mutated(mutations[rule_.mutation_id], graphs, [])
        # (graph, the drawing without the rule is worse).
        changed_ = [
            (graph_, _quality(other_["paths"]) > _quality(base_))
            for graph_, base_, other_ in zip(graphs, baseline, mutated_)
            if other_ is not None and base_ != other_["paths"]
        ]
        # Without a changed drawing, a graph where the generator fails
        # without the rule shows the rule too.
        failed_ = [
            (graph_, True)
            for graph_, other_ in zip(graphs, mutated_)
            if other_ is None
        ]
        candidates_ = changed_ if len(changed_) > 0 else failed_
        # A graph where the drawing gets worse without the rule shows it
        # best; among those, the smallest.
        found[rule_.mutation_id] = (
            min(
                candidates_,
                key=lambda candidate_: (
                    not candidate_[1],
                    _graph_size(candidate_[0]),
                ),
            )[0]
            if len(candidates_) > 0
            else None
        )
        print(  # noqa: T201
            f"{rule_.mutation_id}: {len(changed_)} of {len(graphs)} graphs "
            f"change, the generator fails on {len(failed_)}"
        )
    with open(CASES_FILE, "w", encoding="utf-8") as cases_file:
        json.dump(found, cases_file, indent=1)
        cases_file.write("\n")


def _write_page() -> None:
    with open(CASES_FILE, encoding="utf-8") as cases_file:
        found: Dict[str, Optional[GraphData]] = json.load(cases_file)
    with open(GENERATOR_CSS_PATH, encoding="utf-8") as css_file:
        generator_css = css_file.read()
    mutations = _mutations_by_id()
    cards: List[str] = []
    for index_, rule_ in enumerate(RULES):
        mutation_ = mutations[rule_.mutation_id]
        graph_ = found.get(rule_.mutation_id)
        cards.append(_render_card(index_, rule_, mutation_, graph_))
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Specification graph rules</title>
<style>{PAGE_STYLE}</style>
<style>{generator_css}</style>
</head>
<body>
<main class="content">
<h1>Specification graph rules</h1>
<p>Each rule on the smallest graph found where it changes the drawing.
Both pictures come from the generator: with the rule, and with the rule
switched off by its mutation. The edges that differ are blue.</p>
{"".join(cards)}
</main>
</body>
</html>
"""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as output_file:
        output_file.write(page)
    print(f"Written: {OUTPUT_FILE}")  # noqa: T201


def _render_card(
    index: int, rule: Rule, mutation: Mutation, graph: Optional[GraphData]
) -> str:
    header = (
        f'<section class="case" id="{html.escape(rule.mutation_id)}">'
        f"<h2>{html.escape(rule.title)} "
        f"<small>({html.escape(rule.mutation_id)})</small></h2>"
        f"<p>{html.escape(rule.text)}</p>"
    )
    if graph is None:
        return (
            header + "<p class='note'>No graph found where the rule changes "
            "the drawing.</p></section>"
        )
    with_id = f"rule-{index}-with"
    without_id = f"rule-{index}-without"
    with_paths, with_svg = _route(graph, with_id)
    without = _route_mutated(mutation, [graph], [without_id])[0]
    if without is None:
        return (
            header + "<p class='note'>The generator fails without the rule "
            "on this graph.</p></section>"
        )
    without_paths: PathsData = without["paths"]
    changed = [
        edge_id_
        for edge_id_, path_ in without_paths.items()
        if with_paths.get(edge_id_) != path_
    ]
    return (
        header
        + f"<p class='note'>Without the rule: {html.escape(mutation.description)}."
        f"</p>"
        f'<div class="figures">'
        f"{_figure('With the rule', with_svg, with_paths)}"
        f"{_figure('Without the rule', without['svg'], without_paths)}"
        f"</div>"
        f"{_changed_style(with_id, changed)}"
        f"{_changed_style(without_id, changed)}"
        f"<details><summary>Input</summary><pre>"
        f"{html.escape(json.dumps(graph))}</pre></details>"
        f"</section>"
    )


def _quality(paths: PathsData) -> Tuple[int, int]:
    """
    Return the overlaps and the crossings of a drawing.

    A larger value is a worse drawing: overlaps count first.
    """

    polylines = [_points(path_) for path_ in paths.values()]
    crossings = sum(
        crossing_count(first_, second_)
        for first_, second_ in itertools.combinations(polylines, 2)
    )
    overlaps = sum(
        1
        for first_, second_ in itertools.combinations(polylines, 2)
        if any(
            _collinear_contact(first_segment_, second_segment_)
            for first_segment_ in zip(first_, first_[1:])
            for second_segment_ in zip(second_, second_[1:])
        )
    )
    return overlaps, crossings


def _figure(caption: str, svg: str, paths: PathsData) -> str:
    overlaps, crossings = _quality(paths)
    return (
        f"<figure><h3>{html.escape(caption)}</h3>{svg}"
        f"<p class='note'>Crossings: {crossings}. Overlaps: {overlaps}.</p>"
        f"</figure>"
    )


def _changed_style(svg_id: str, edge_ids: Sequence[str]) -> str:
    if len(edge_ids) == 0:
        return ""
    selectors = ",\n".join(
        f'#{svg_id} [data-edge-id="{html.escape(edge_id_)}"] '
        f".{CSS_PREFIX}-edge__line"
        for edge_id_ in edge_ids
    )
    return (
        f"<style>\n{selectors} {{ stroke: #1f6fd1 !important; "
        "stroke-width: 3px !important; }\n</style>"
    )


def _route(graph: GraphData, svg_id: str = "") -> Tuple[PathsData, str]:
    """
    Return the edge paths of a graph and, with an SVG ID, its SVG.
    """

    normalized_graph = normalize_graph(
        _structure_case("rule", "", _tree(graph["tree"]), _edges(graph)).graph
    )
    layout = compute_structure_layout(normalized_graph)
    routing = compute_structure_routing(normalized_graph, layout)
    geometry = compute_structure_geometry(
        normalized_graph,
        layout,
        lane_counts=routing.lane_counts,
        bottom_segments=routing.bottom_segments,
        side_entries=routing.side_entries,
        gate_port_lists=routing.gate_port_lists,
    )
    edge_paths = compute_structure_edge_paths(routing, geometry)
    paths = {
        edge_id_: [[point_.x, point_.y] for point_ in path_]
        for edge_id_, path_ in edge_paths.items()
    }
    svg = (
        serialize_structure_svg(
            normalized_graph, routing, geometry, edge_paths, svg_id=svg_id
        )
        if len(svg_id) > 0
        else ""
    )
    return paths, svg


def _route_mutated(
    mutation: Mutation, graphs: List[GraphData], svg_ids: List[str]
) -> List[Optional[Dict[str, Any]]]:
    """
    Route the graphs with a mutation applied to the package.

    A separate process imports the mutated file. The file is restored
    afterwards. A graph where the mutated generator fails gives None.
    """

    with open(mutation.path, encoding="utf-8") as source_file:
        source = source_file.read()
    if source.count(mutation.original) != 1:
        raise ValueError(f"{mutation.identifier}: code not found")
    with tempfile.NamedTemporaryFile(
        "w", suffix=".json", delete=False, encoding="utf-8"
    ) as job_file:
        json.dump({"graphs": graphs, "svg_ids": svg_ids}, job_file)
        job_path = job_file.name
    backup_path = mutation.path + ".mutation_backup"
    shutil.copy2(mutation.path, backup_path)
    try:
        with open(mutation.path, "w", encoding="utf-8") as source_file:
            source_file.write(
                source.replace(mutation.original, mutation.replacement)
                + mutation.appendix
            )
        completed = subprocess.run(
            [sys.executable, "-m", MODULE, "--worker", job_path],
            capture_output=True,
            text=True,
            check=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
    finally:
        shutil.move(backup_path, mutation.path)
        os.remove(job_path)
    results: List[Optional[Dict[str, Any]]] = json.loads(completed.stdout)
    return results


def _worker(job_path: str) -> None:
    """
    Route the graphs of a job file and print the results as JSON.
    """

    with open(job_path, encoding="utf-8") as job_file:
        job = json.load(job_file)
    svg_ids: List[str] = job["svg_ids"]
    results: List[Optional[Dict[str, Any]]] = []
    for index_, graph_ in enumerate(job["graphs"]):
        svg_id_ = svg_ids[index_] if index_ < len(svg_ids) else ""
        try:
            paths_, svg_ = _route(graph_, svg_id_)
        except Exception:  # noqa: BLE001
            results.append(None)
            continue
        results.append({"paths": paths_, "svg": svg_})
    sys.stdout.write(json.dumps(results))


def _gallery_graphs() -> List[GraphData]:
    """
    Return the structure cases of the gallery as graphs of the search.
    """

    def item(node: GraphNode) -> Any:
        if len(node.children) == 0:
            return node.node_id
        return [node.node_id, [item(child_) for child_ in node.children]]

    return [
        {
            "tree": [item(node_) for node_ in case_.graph.root],
            "edges": [
                [edge_.source_id, edge_.target_id] for edge_ in case_.graph.edges
            ],
        }
        for case_ in GALLERY_CASES
        if case_.graph.mode is LayoutMode.STRUCTURE
    ]


def _random_graphs(seed: int, count: int) -> List[GraphData]:
    """
    Return small random graphs of the structure mode.

    Columns of simple nodes alternate with sections; some sections hold a
    nested section. The names avoid the letters of the channels.
    """

    generator = random.Random(seed)
    graphs: List[GraphData] = []
    for _ in range(count):
        items: List[Any] = []
        names: List[str] = []
        column_count = generator.randint(2, 3)
        for column_ in range(column_count):
            letter_ = "ADE"[column_]
            nodes_ = [
                f"{letter_}{number_ + 1}"
                for number_ in range(generator.randint(1, 3))
            ]
            names += nodes_
            items += nodes_
            if column_ == column_count - 1:
                continue
            section_ = "SQ"[column_]
            children_: List[Any] = [f"{section_}1"]
            names.append(f"{section_}1")
            if generator.random() < 0.5:
                nested_ = [
                    f"{section_}{number_ + 2}"
                    for number_ in range(generator.randint(1, 2))
                ]
                names += nested_
                children_.append([section_ + "R", nested_])
            elif generator.random() < 0.5:
                children_.append(f"{section_}2")
                names.append(f"{section_}2")
            items.append([section_, children_])
        edges: List[List[str]] = []
        while len(edges) < generator.randint(2, 5):
            source_, target_ = generator.sample(names, 2)
            if [source_, target_] not in edges:
                edges.append([source_, target_])
        graphs.append({"tree": [["Doc", items]], "edges": sorted(edges)})
    return graphs


def _graph_size(graph: GraphData) -> int:
    def count(items: List[Any]) -> int:
        return sum(
            1 + count(item_[1]) if isinstance(item_, list) else 1
            for item_ in items
        )

    return count(graph["tree"]) + len(graph["edges"])


def _tree(items: List[Any]) -> List[StructureSpec]:
    return [
        (item_[0], _tree(item_[1])) if isinstance(item_, list) else item_
        for item_ in items
    ]


def _edges(graph: GraphData) -> List[Tuple[str, str]]:
    return [(source_, target_) for source_, target_ in graph["edges"]]


def _points(path: List[List[float]]) -> Tuple[Point, ...]:
    return tuple(Point(x_, y_) for x_, y_ in path)


def _mutations_by_id() -> Mapping[str, Mutation]:
    return {mutation_.identifier: mutation_ for mutation_ in MUTATIONS}


if __name__ == "__main__":
    main()
