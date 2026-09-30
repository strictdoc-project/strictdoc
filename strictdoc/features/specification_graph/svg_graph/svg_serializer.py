"""
Stage 8 of the graph generator for the levels mode: serialization.

The serializer converts the result of stages 1 to 7 into an SVG string. The
serializer does not change the geometry. spec.md, section "Сериализация",
defines the markup.
"""

import html
import json
from typing import Dict, List, Mapping, Optional, Set, Tuple

from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    GeometryConfig,
    LevelsGeometry,
    Point,
    Rect,
)
from strictdoc.features.specification_graph.svg_graph.levels_routing import (
    LevelsRouting,
    Orientation,
)
from strictdoc.features.specification_graph.svg_graph.levels_structure import (
    LevelsStructure,
)
from strictdoc.features.specification_graph.svg_graph.model import (
    DANGER_RELATION_TYPE,
    DEFAULT_RELATION_TYPE,
    WARNING_RELATION_TYPE,
    GraphNode,
    RelationStyle,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    DiagnosticKind,
    NormalizedEdge,
    NormalizedGraph,
)

CSS_PREFIX = "specification-graph"

# Size of the diagnostic sign in the top right corner of a node.
WARNING_SIGN_SIZE = 14


def serialize_levels_svg(
    normalized_graph: NormalizedGraph,
    structure: LevelsStructure,
    routing: LevelsRouting,
    geometry: LevelsGeometry,
    config: Optional[GeometryConfig] = None,
    debug: bool = False,
    svg_id: str = CSS_PREFIX,
) -> str:
    """
    Serialize the levels mode result.

    The SVG ID scopes the arrowhead markers and the type styles, so several
    SVGs on one page do not affect each other. Each SVG on a page needs its
    own ID.
    """

    if config is None:
        config = GeometryConfig()

    style_types = {
        edge_.edge_id: style_relation_type(edge_, structure)
        for edge_ in normalized_graph.edges
    }
    # Class index of each type. Sorted type IDs keep the class names
    # independent of the input order.
    type_indexes = {
        type_id_: index_
        for index_, type_id_ in enumerate(
            sorted(set(style_types.values()) | {DANGER_RELATION_TYPE})
        )
    }

    elements: List[str] = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" id="{_escape(svg_id)}" '
            f'class="{CSS_PREFIX}" '
            f'width="{_number(geometry.width)}" '
            f'height="{_number(geometry.height)}" '
            f'viewBox="0 0 {_number(geometry.width)} '
            f'{_number(geometry.height)}">'
        ),
        _render_defs(
            normalized_graph.relation_types, type_indexes, config, svg_id
        ),
    ]
    if debug:
        elements.append(_render_debug_layer(geometry))
    elements.append(_render_nodes(normalized_graph, geometry))
    elements.append(
        _render_edges(
            normalized_graph,
            routing,
            geometry,
            style_types,
            type_indexes,
            debug,
            svg_id,
        )
    )
    elements.append(_render_warning_signs(normalized_graph, geometry))
    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def style_relation_type(
    edge: NormalizedEdge, structure: LevelsStructure
) -> str:
    """
    Return the type that gives an edge its style.

    A situation of the generator replaces the input type with a built-in
    type. The stronger type wins: danger, then warning, then the input type.
    """

    if edge.cycle_id is not None:
        return DANGER_RELATION_TYPE
    if edge.edge_id in structure.skip_edge_ids:
        return WARNING_RELATION_TYPE
    return edge.relation_type


def _render_defs(
    relation_types: Mapping[str, RelationStyle],
    type_indexes: Dict[str, int],
    config: GeometryConfig,
    svg_id: str,
) -> str:
    """
    Render the input-dependent styles: type classes and arrowhead markers.
    """

    style_rules: List[str] = []
    markers: List[str] = []
    for type_id_, index_ in type_indexes.items():
        style_ = relation_types.get(
            type_id_, relation_types[DEFAULT_RELATION_TYPE]
        )
        dash_ = (
            f" stroke-dasharray: {style_.dash};"
            if style_.dash is not None
            else ""
        )
        style_rules.append(
            f"#{svg_id} .{CSS_PREFIX}-edge--type-{index_} "
            f".{CSS_PREFIX}-edge__line {{ stroke: {style_.color};{dash_} }}"
        )
        markers.append(
            f'<marker id="{_escape(svg_id)}-arrow-{index_}" '
            f'viewBox="0 0 10 10" '
            f'refX="10" refY="5" markerUnits="userSpaceOnUse" '
            f'markerWidth="{_number(config.arrow_width)}" '
            f'markerHeight="{_number(config.arrow_width)}" '
            f'orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{style_.color}"/>'
            f"</marker>"
        )
    danger_style = relation_types[DANGER_RELATION_TYPE]
    style_rules.append(
        f"#{svg_id} .{CSS_PREFIX}-node--danger .{CSS_PREFIX}-node__box "
        f"{{ stroke: {danger_style.color}; }}"
    )
    return (
        "<defs>\n<style>\n"
        + "\n".join(style_rules)
        + "\n</style>\n"
        + "\n".join(markers)
        + "\n</defs>"
    )


def _render_debug_layer(geometry: LevelsGeometry) -> str:
    rects: List[str] = []
    for channel_id_, rect_ in sorted(
        geometry.channel_rects.items(),
        key=lambda item_: (item_[0].orientation.value, item_[0].index),
    ):
        letter_ = (
            "H" if channel_id_.orientation is Orientation.HORIZONTAL else "V"
        )
        rects.append(
            f'<rect class="{CSS_PREFIX}-debug__channel" '
            f'data-debug-channel="{letter_}{channel_id_.index}" '
            f"{_rect_attributes(rect_)}/>"
        )
    return f'<g class="{CSS_PREFIX}-debug">\n' + "\n".join(rects) + "\n</g>"


def _render_nodes(
    normalized_graph: NormalizedGraph, geometry: LevelsGeometry
) -> str:
    cycle_id_by_node: Dict[str, str] = {
        node_id_: cycle_.cycle_id
        for cycle_ in normalized_graph.cycles
        for node_id_ in cycle_.node_ids
    }
    messages_by_node = _warning_messages_by_node(normalized_graph)
    nodes: List[str] = []
    for node_ in normalized_graph.nodes:
        rect_ = geometry.node_rects[node_.node_id]
        cycle_id_ = cycle_id_by_node.get(node_.node_id)
        classes_ = f"{CSS_PREFIX}-node"
        attributes_ = [f'data-node-id="{_escape(node_.node_id)}"']
        if node_.link is not None:
            attributes_.append(f'data-node-link="{_escape(node_.link)}"')
        attributes_.append(
            f'data-node-details="{_escape(_json(node_.details))}"'
        )
        if cycle_id_ is not None:
            classes_ += f" {CSS_PREFIX}-node--danger"
            attributes_.append(f'data-cycle-id="{_escape(cycle_id_)}"')
        messages_ = messages_by_node.get(node_.node_id)
        if messages_ is not None:
            attributes_.append(
                f'data-diagnostics="{_escape(_json(messages_))}"'
            )
        nodes.append(
            f'<g class="{classes_}" {" ".join(attributes_)}>\n'
            f'<rect class="{CSS_PREFIX}-node__box" rx="4" '
            f"{_rect_attributes(rect_)}/>\n"
            f"{_render_node_title(node_, rect_)}\n"
            f"<title>{_escape(node_.title)}</title>\n"
            "</g>"
        )
    return f'<g class="{CSS_PREFIX}-nodes">\n' + "\n".join(nodes) + "\n</g>"


def _render_node_title(node: GraphNode, rect: Rect) -> str:
    """
    Render the node title as HTML in a foreignObject.

    The browser wraps the title and cuts it after three lines (spec.md,
    section "Размеры нод и текст"). Outside a browser, a foreignObject shows
    no text. To keep the text in an exported SVG file, this function has to
    render the lines as SVG <text> elements instead. That requires the
    generator to wrap the title itself, with the font metrics of the page.
    """

    return (
        f'<foreignObject class="{CSS_PREFIX}-node__title-box" '
        f"{_rect_attributes(rect)}>"
        f'<div xmlns="http://www.w3.org/1999/xhtml" '
        f'class="{CSS_PREFIX}-node__title">'
        f'<span class="{CSS_PREFIX}-node__title-text">'
        f"{_escape(node.title)}</span></div></foreignObject>"
    )


def _render_edges(
    normalized_graph: NormalizedGraph,
    routing: LevelsRouting,
    geometry: LevelsGeometry,
    style_types: Dict[str, str],
    type_indexes: Dict[str, int],
    debug: bool,
    svg_id: str,
) -> str:
    edges: List[str] = []
    for edge_ in normalized_graph.edges:
        type_index_ = type_indexes[style_types[edge_.edge_id]]
        attributes_ = [
            f'data-edge-id="{_escape(edge_.edge_id)}"',
            f'data-source-id="{_escape(edge_.source_id)}"',
            f'data-target-id="{_escape(edge_.target_id)}"',
            f'data-relation-type="{_escape(edge_.relation_type)}"',
        ]
        if edge_.cycle_id is not None:
            attributes_.append(f'data-cycle-id="{_escape(edge_.cycle_id)}"')
        if debug:
            route_ = routing.routes[edge_.edge_id]
            lanes_ = " ".join(
                (
                    "H"
                    if lane_.channel.orientation is Orientation.HORIZONTAL
                    else "V"
                )
                + f"{lane_.channel.index}:{lane_.lane}"
                for lane_ in route_.lanes
            )
            ports_ = " ".join(
                f"{port_.node_id}:{port_.face.value}:{port_.slot}"
                for port_ in (route_.source_port, route_.target_port)
            )
            attributes_.append(f'data-debug-lanes="{_escape(lanes_)}"')
            attributes_.append(f'data-debug-ports="{_escape(ports_)}"')
        path_ = _path_data(geometry.edge_paths[edge_.edge_id])
        edges.append(
            f'<g class="{CSS_PREFIX}-edge {CSS_PREFIX}-edge--type-'
            f'{type_index_}" {" ".join(attributes_)}>\n'
            f'<path class="{CSS_PREFIX}-edge__line" d="{path_}" '
            f'marker-end="url(#{_escape(svg_id)}-arrow-{type_index_})"/>\n'
            f'<path class="{CSS_PREFIX}-edge__hit-area" d="{path_}"/>\n'
            "</g>"
        )
    return f'<g class="{CSS_PREFIX}-edges">\n' + "\n".join(edges) + "\n</g>"


def _render_warning_signs(
    normalized_graph: NormalizedGraph, geometry: LevelsGeometry
) -> str:
    signs: List[str] = []
    messages_by_node = _warning_messages_by_node(normalized_graph)
    for node_ in normalized_graph.nodes:
        messages_ = messages_by_node.get(node_.node_id)
        if messages_ is None:
            continue
        rect_ = geometry.node_rects[node_.node_id]
        size_ = WARNING_SIGN_SIZE
        # The sign sits on the top right corner of the frame, like a badge,
        # so that it does not cover the title.
        right_ = rect_.x + rect_.width + size_ / 2
        top_ = rect_.y - size_ / 2
        triangle_ = (
            f"M {_number(right_ - size_ / 2)} {_number(top_)} "
            f"L {_number(right_)} {_number(top_ + size_)} "
            f"L {_number(right_ - size_)} {_number(top_ + size_)} Z"
        )
        signs.append(
            f'<g class="{CSS_PREFIX}-warning-sign" '
            f'data-node-id="{_escape(node_.node_id)}">'
            f'<path d="{triangle_}"/>'
            f'<text x="{_number(right_ - size_ / 2)}" '
            f'y="{_number(top_ + size_ - 2)}">!</text>'
            f"<title>{_escape(chr(10).join(messages_))}</title></g>"
        )
    return (
        f'<g class="{CSS_PREFIX}-warning-signs">\n'
        + "\n".join(signs)
        + "\n</g>"
    )


def _warning_messages_by_node(
    normalized_graph: NormalizedGraph,
) -> Dict[str, List[str]]:
    """
    Collect the non-critical diagnostics of each node.

    A cycle is not a warning: the danger type shows it.
    """

    result: Dict[str, List[str]] = {}
    seen: Set[Tuple[str, str]] = set()
    for diagnostic_ in normalized_graph.diagnostics:
        if diagnostic_.kind is DiagnosticKind.CYCLE:
            continue
        for node_id_ in diagnostic_.node_ids:
            if (node_id_, diagnostic_.message) in seen:
                continue
            seen.add((node_id_, diagnostic_.message))
            result.setdefault(node_id_, []).append(diagnostic_.message)
    return result


def _path_data(points: Tuple[Point, ...]) -> str:
    return "M " + " L ".join(
        f"{_number(point_.x)} {_number(point_.y)}" for point_ in points
    )


def _rect_attributes(rect: Rect) -> str:
    return (
        f'x="{_number(rect.x)}" y="{_number(rect.y)}" '
        f'width="{_number(rect.width)}" height="{_number(rect.height)}"'
    )


def _number(value: float) -> str:
    """
    Format a coordinate with at most two decimals and no trailing zeros.
    """

    text = f"{round(value, 2):.2f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def _escape(text: str) -> str:
    return html.escape(text, quote=True)


def _json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
