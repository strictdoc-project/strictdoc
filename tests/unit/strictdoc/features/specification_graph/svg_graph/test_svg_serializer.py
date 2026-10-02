import json
import re
import xml.etree.ElementTree as ET
from typing import Dict, List

import pytest

from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CASES,
    GalleryCase,
)
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    GeometryConfig,
    compute_levels_geometry,
)
from strictdoc.features.specification_graph.svg_graph.levels_routing import (
    compute_levels_routing,
)
from strictdoc.features.specification_graph.svg_graph.levels_structure import (
    compute_levels_structure,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    normalize_graph,
)
from strictdoc.features.specification_graph.svg_graph.svg_serializer import (
    serialize_levels_svg,
)

SVG_NAMESPACE = "{http://www.w3.org/2000/svg}"


def _case(title: str) -> GalleryCase:
    return next(case_ for case_ in GALLERY_CASES if case_.title == title)


def _svg(case: GalleryCase, debug: bool = False, svg_id: str = "graph") -> str:
    normalized_graph = normalize_graph(case.graph)
    structure = compute_levels_structure(normalized_graph)
    routing = compute_levels_routing(normalized_graph, structure)
    geometry = compute_levels_geometry(structure, routing)
    return serialize_levels_svg(
        normalized_graph,
        structure,
        routing,
        geometry,
        debug=debug,
        svg_id=svg_id,
    )


def _groups(root: ET.Element, css_class: str) -> List[ET.Element]:
    return [
        element_
        for element_ in root.iter(f"{SVG_NAMESPACE}g")
        if css_class in element_.get("class", "").split(" ")
    ]


def _edge_classes_by_pair(svg: str) -> Dict[str, str]:
    root = ET.fromstring(svg)
    return {
        f"{group_.get('data-source-id')}->{group_.get('data-target-id')}": (
            group_.get("class", "")
        )
        for group_ in _groups(root, "specification-graph-edge")
    }


def _type_rule(svg: str, edge_class: str) -> str:
    """
    Return the style rule of an edge type class, without the SVG ID scope.
    """

    type_class = next(
        class_
        for class_ in edge_class.split(" ")
        if class_.startswith("specification-graph-edge--type-")
    )
    return next(
        line_.split("{", 1)[1]
        for line_ in svg.splitlines()
        if f".{type_class} " in line_
    )


def test_nodes_and_edges_carry_their_data_attributes() -> None:
    """
    Each node and each edge is one group with its data attributes.

    Code: svg_serializer._render_nodes, svg_serializer._render_edges.
    Fails if:
    - a node group loses data-node-id, data-node-link, or data-node-details.
    - an edge group loses data-source-id or data-target-id.
    """

    case = _case("Titles, relation types, and diagnostics")

    root = ET.fromstring(_svg(case))

    nodes = {
        group_.get("data-node-id"): group_
        for group_ in _groups(root, "specification-graph-node")
    }
    assert list(nodes) == ["A", "B", "C"]
    assert nodes["A"].get("data-node-link") == "https://example.com/A"
    assert json.loads(nodes["A"].get("data-node-details", "")) == [
        ["UID", "REQ-A"],
        ["Document", "Spec"],
    ]
    assert nodes["B"].get("data-node-link") is None
    edges = [
        (
            group_.get("data-edge-id"),
            group_.get("data-source-id"),
            group_.get("data-target-id"),
            group_.get("data-relation-type"),
        )
        for group_ in _groups(root, "specification-graph-edge")
    ]
    assert edges == [
        ("edge-1", "B", "A", "verifies"),
        ("edge-2", "C", "A", "unknown"),
    ]
    assert list(root.iter(f"{SVG_NAMESPACE}a")) == []


def test_input_type_style_and_default_style() -> None:
    """
    An input type uses its own style. A type without a style uses default.

    Code: svg_serializer._render_defs.
    Fails if:
    - a type without a style does not fall back to the default style.
    - an input style does not reach the type class.
    """

    svg = _svg(_case("Titles, relation types, and diagnostics"))
    classes = _edge_classes_by_pair(svg)

    assert "#1f6fd1" in _type_rule(svg, classes["B->A"])
    assert "#222222" in _type_rule(svg, classes["C->A"])


def test_situation_type_replaces_the_input_type() -> None:
    """
    A relation across levels is warning. A cycle relation is danger.

    Code: svg_serializer.style_relation_type.
    Fails if:
    - a relation across levels keeps its input type.
    - warning wins over danger for a cycle relation across levels.
    """

    highway_svg = _svg(_case("Basic highway conflict"))
    highway_classes = _edge_classes_by_pair(highway_svg)
    assert "stroke-dasharray: 6 4" in _type_rule(
        highway_svg, highway_classes["D->A"]
    )
    assert "stroke-dasharray" not in _type_rule(
        highway_svg, highway_classes["B->A"]
    )

    # C -> A closes the cycle and goes down across levels: danger wins.
    cycle_svg = _svg(_case("Three-document cycle with an incoming branch"))
    cycle_classes = _edge_classes_by_pair(cycle_svg)
    assert "#c00000" in _type_rule(cycle_svg, cycle_classes["C->A"])
    assert "stroke-dasharray" not in _type_rule(
        cycle_svg, cycle_classes["C->A"]
    )


def test_warning_sign_marks_non_critical_diagnostics_only() -> None:
    """
    A warning sign marks the nodes of a self-loop and of a duplicate edge.

    A cycle is shown by the danger type, not by a warning sign.

    Code: svg_serializer._warning_messages_by_node,
    svg_serializer._render_warning_signs.
    Fails if:
    - a cycle gets a warning sign.
    - a node with a self-loop or a duplicate edge gets no warning sign.
    """

    root = ET.fromstring(_svg(_case("Titles, relation types, and diagnostics")))
    signed_node_ids = [
        group_.get("data-node-id")
        for group_ in _groups(root, "specification-graph-warning-sign")
    ]
    assert signed_node_ids == ["A", "B", "C"]
    node_c = next(
        group_
        for group_ in _groups(root, "specification-graph-node")
        if group_.get("data-node-id") == "C"
    )
    assert json.loads(node_c.get("data-diagnostics", "")) == [
        "Node C has a relation to itself: parent."
    ]

    cycle_root = ET.fromstring(
        _svg(_case("Three-document cycle with an incoming branch"))
    )
    assert _groups(cycle_root, "specification-graph-warning-sign") == []


def test_debug_attributes_exist_only_in_debug_mode() -> None:
    """
    Debug attributes and the channel layer exist only in the debug mode.

    Code: svg_serializer._render_edges, svg_serializer._render_debug_layer.
    Fails if:
    - the debug attributes are written without the debug mode.
    - the debug mode does not write lanes and ports.
    """

    case = _case("Basic highway conflict")

    assert "data-debug" not in _svg(case)
    debug_root = ET.fromstring(_svg(case, debug=True))
    edge = next(
        group_
        for group_ in _groups(debug_root, "specification-graph-edge")
        if group_.get("data-source-id") == "D"
        and group_.get("data-target-id") == "A"
    )
    assert edge.get("data-debug-lanes") == "H2:0 V-1:0 H0:0"
    assert edge.get("data-debug-ports") == "D:top:-1 A:bottom:-1"
    assert len(_groups(debug_root, "specification-graph-debug")) == 1


def test_svg_id_scopes_markers_and_type_styles() -> None:
    """
    The SVG ID scopes the arrowhead markers and the type style rules.

    Code: svg_serializer.serialize_levels_svg, svg_serializer._render_defs.
    Fails if:
    - a marker ID or a type style rule is not scoped by the SVG ID.
    """

    svg = _svg(_case("Basic highway conflict"), svg_id="first")

    root = ET.fromstring(svg)
    assert root.get("id") == "first"
    marker_ids = [
        marker_.get("id", "") for marker_ in root.iter(f"{SVG_NAMESPACE}marker")
    ]
    assert len(marker_ids) > 0
    assert all(marker_id_.startswith("first-") for marker_id_ in marker_ids)
    type_rules = [
        line_
        for line_ in svg.splitlines()
        if "specification-graph-edge--type-" in line_ and "{" in line_
    ]
    assert len(type_rules) > 0
    assert all(rule_.startswith("#first ") for rule_ in type_rules)
    for line_ in _groups(root, "specification-graph-edge"):
        path_ = line_.find(f"{SVG_NAMESPACE}path")
        assert path_ is not None
        assert path_.get("marker-end", "").startswith("url(#first-")


def test_serialization_is_deterministic_with_compact_numbers() -> None:
    """
    The same input gives the same SVG. Coordinates have no trailing zeros.

    Code: svg_serializer._number.
    Fails if:
    - a coordinate keeps trailing zeros, for example 40.00.
    """

    case = _case("Complete 3 by 3 relation grid")

    svg = _svg(case)

    assert svg == _svg(case)
    # A decimal number that ends with 0, for example 40.0 or 40.50.
    assert re.search(r"\d\.\d*0(?!\d)", svg) is None


LEVELS_CASES = [
    case_ for case_ in GALLERY_CASES if case_.graph.mode.value == "levels"
]


@pytest.mark.parametrize(
    "case", LEVELS_CASES, ids=[case_.title for case_ in LEVELS_CASES]
)
def test_svg_matches_the_model(case: GalleryCase) -> None:
    """
    The SVG of every levels mode case is valid XML and matches the model.

    Code: svg_serializer.serialize_levels_svg.
    Fails if:
    - the SVG is not valid XML.
    - a node or an edge is missing, repeated, or out of input order.
    """

    normalized_graph = normalize_graph(case.graph)

    root = ET.fromstring(_svg(case))

    assert [
        group_.get("data-node-id")
        for group_ in _groups(root, "specification-graph-node")
    ] == [node_.node_id for node_ in normalized_graph.nodes]
    assert [
        (
            group_.get("data-edge-id"),
            group_.get("data-source-id"),
            group_.get("data-target-id"),
        )
        for group_ in _groups(root, "specification-graph-edge")
    ] == [
        (edge_.edge_id, edge_.source_id, edge_.target_id)
        for edge_ in normalized_graph.edges
    ]


def test_arrowhead_follows_the_geometry_config() -> None:
    """
    The arrowhead size comes from the configuration of the geometry.

    Code: svg_serializer.serialize_levels_svg, levels_geometry.GeometryConfig.
    Fails if:
    - the serializer uses the default configuration instead of the
      configuration of the geometry.
    """

    case = _case("Simple chain")
    config = GeometryConfig(lane_clearance_pitches=3, min_port_pitch=10)
    normalized_graph = normalize_graph(case.graph)
    structure = compute_levels_structure(normalized_graph)
    routing = compute_levels_routing(normalized_graph, structure)
    geometry = compute_levels_geometry(structure, routing, config)

    root = ET.fromstring(
        serialize_levels_svg(normalized_graph, structure, routing, geometry)
    )

    for marker_ in root.iter(f"{SVG_NAMESPACE}marker"):
        assert marker_.get("markerWidth") == "14"
        assert marker_.get("markerHeight") == "8"
