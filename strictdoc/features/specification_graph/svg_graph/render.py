"""
Public entry point of the graph generator.

The function runs all stages for the mode of the graph and returns the SVG,
the diagnostics, and the styles of the relation types that the SVG draws.
spec.md, section "Результат", defines the result.
"""

from dataclasses import dataclass
from typing import Dict, Mapping, Tuple

from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    compute_levels_geometry,
)
from strictdoc.features.specification_graph.svg_graph.levels_routing import (
    RoutingOptions,
    compute_levels_routing,
)
from strictdoc.features.specification_graph.svg_graph.levels_structure import (
    compute_levels_structure,
)
from strictdoc.features.specification_graph.svg_graph.model import (
    DEFAULT_RELATION_TYPE,
    Graph,
    LayoutMode,
    RelationStyle,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    Diagnostic,
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
    CSS_PREFIX,
    serialize_levels_svg,
    serialize_structure_svg,
    structure_style_relation_type,
    style_relation_type,
)


@dataclass(frozen=True)
class RenderedGraph:
    svg: str
    diagnostics: Tuple[Diagnostic, ...]
    # Styles of the relation types that the SVG draws, by type ID, sorted by
    # type ID. A legend shows these entries.
    relation_styles: Mapping[str, RelationStyle]


def render_graph(
    graph: Graph, svg_id: str = CSS_PREFIX, debug: bool = False
) -> RenderedGraph:
    """
    Render a graph to SVG.

    Raises GraphModelError if the input is invalid. Each SVG on a page needs
    its own SVG ID.
    """

    normalized_graph = normalize_graph(graph)
    if normalized_graph.mode is LayoutMode.STRUCTURE:
        layout = compute_structure_layout(normalized_graph)
        structure_routing = compute_structure_routing(normalized_graph, layout)
        structure_geometry = compute_structure_geometry(
            normalized_graph,
            layout,
            lane_counts=structure_routing.lane_counts,
            bottom_segments=structure_routing.bottom_segments,
            side_entries=structure_routing.side_entries,
            gate_port_lists=structure_routing.gate_port_lists,
        )
        edge_paths = compute_structure_edge_paths(
            structure_routing, structure_geometry
        )
        svg = serialize_structure_svg(
            normalized_graph,
            structure_routing,
            structure_geometry,
            edge_paths,
            debug=debug,
            svg_id=svg_id,
        )
        style_types = {
            edge_.edge_id: structure_style_relation_type(
                edge_, normalized_graph.parent_ids
            )
            for edge_ in normalized_graph.edges
            if edge_.edge_id in edge_paths
        }
    elif normalized_graph.mode is LayoutMode.LEVELS:
        structure = compute_levels_structure(normalized_graph)
        levels_routing = compute_levels_routing(
            normalized_graph, structure, RoutingOptions()
        )
        levels_geometry = compute_levels_geometry(structure, levels_routing)
        svg = serialize_levels_svg(
            normalized_graph,
            structure,
            levels_routing,
            levels_geometry,
            debug=debug,
            svg_id=svg_id,
        )
        style_types = {
            edge_.edge_id: style_relation_type(edge_, structure)
            for edge_ in normalized_graph.edges
        }
    else:
        raise NotImplementedError(
            f"The generator does not support the mode {graph.mode.value}."
        )
    return RenderedGraph(
        svg=svg,
        diagnostics=normalized_graph.diagnostics,
        relation_styles=_drawn_relation_styles(normalized_graph, style_types),
    )


def _drawn_relation_styles(
    normalized_graph: NormalizedGraph, style_types: Mapping[str, str]
) -> Dict[str, RelationStyle]:
    relation_types = normalized_graph.relation_types
    return {
        type_id_: relation_types.get(
            type_id_, relation_types[DEFAULT_RELATION_TYPE]
        )
        for type_id_ in sorted(set(style_types.values()))
    }
