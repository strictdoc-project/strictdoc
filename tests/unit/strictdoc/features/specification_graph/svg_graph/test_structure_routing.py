from typing import Dict, List, Mapping, Tuple

import pytest

from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CASES,
    GalleryCase,
)
from strictdoc.features.specification_graph.svg_graph.gate_ports import Face
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    Point,
    Rect,
)
from strictdoc.features.specification_graph.svg_graph.model import LayoutMode
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedGraph,
    normalize_graph,
)
from strictdoc.features.specification_graph.svg_graph.structure_geometry import (
    StructureGeometry,
    compute_structure_geometry,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    ChannelKind,
    compute_structure_layout,
)
from strictdoc.features.specification_graph.svg_graph.structure_paths import (
    compute_structure_edge_paths,
)
from strictdoc.features.specification_graph.svg_graph.structure_routing import (
    StructureRouting,
    compute_structure_routing,
)
from tests.unit.strictdoc.features.specification_graph.svg_graph.geometry_checks import (
    crossing_count,
    geometry_problems,
)

STRUCTURE_CASES = [
    case_ for case_ in GALLERY_CASES if case_.graph.mode is LayoutMode.STRUCTURE
]


def _case(title: str) -> GalleryCase:
    return next(case_ for case_ in GALLERY_CASES if case_.title == title)


def _result(
    case: GalleryCase,
) -> Tuple[
    NormalizedGraph,
    StructureRouting,
    StructureGeometry,
    Dict[str, Tuple[Point, ...]],
]:
    normalized_graph = normalize_graph(case.graph)
    layout = compute_structure_layout(normalized_graph)
    routing = compute_structure_routing(normalized_graph, layout)
    geometry = compute_structure_geometry(
        normalized_graph, layout, lane_counts=routing.lane_counts
    )
    return (
        normalized_graph,
        routing,
        geometry,
        compute_structure_edge_paths(routing, geometry),
    )


def _edge_id(
    normalized_graph: NormalizedGraph, source_id: str, target_id: str
) -> str:
    return next(
        edge_.edge_id
        for edge_ in normalized_graph.edges
        if edge_.source_id == source_id and edge_.target_id == target_id
    )


def test_neighbors_in_one_column_are_straight() -> None:
    """
    A relation between neighbors in one column is a straight line.

    Code: structure_routing._Router._plan, structure_routing._Router
    ._assign_ports.
    Fails if:
    - the gate does not give the straight relation the center slots.
    """

    normalized_graph, routing, _, paths = _result(
        _case("Relations inside one container")
    )

    for source_id_, target_id_ in (("A3", "A2"), ("S2", "S1")):
        route_ = routing.routes[
            _edge_id(normalized_graph, source_id_, target_id_)
        ]
        assert route_.lanes == ()
        assert route_.source_port.slot == 0
        assert route_.target_port.slot == 0
        assert len(paths[route_.edge_id]) == 2


def test_routes_take_the_fewest_bends() -> None:
    """
    A route takes the fewest bends, then the shortest length.

    Nodes on the same side of the section connect over a corridor. A route
    around the section uses the vertical channels.

    Code: structure_routing._Router._plan, structure_routing._Router
    ._best_path.
    Fails if:
    - the path cost compares the length before the bends.
    """

    normalized_graph, routing, _, _ = _result(
        _case("Relations inside one container")
    )

    def kinds(source_id: str, target_id: str) -> List[ChannelKind]:
        route_ = routing.routes[
            _edge_id(normalized_graph, source_id, target_id)
        ]
        return [channel_.kind for channel_ in route_.channels]

    assert kinds("A1", "C1") == [ChannelKind.TOP_CORRIDOR]
    assert kinds("C3", "A3") == [ChannelKind.BOTTOM_CORRIDOR]
    assert kinds("C2", "A2") == [
        ChannelKind.COLUMN,
        ChannelKind.VERTICAL,
        ChannelKind.TOP_CORRIDOR,
        ChannelKind.VERTICAL,
        ChannelKind.COLUMN,
    ]


def test_fewest_bends_win_over_the_shortest_length() -> None:
    """
    A route with fewer bends wins over a shorter route with more bends.

    Code: structure_routing._Router._plan, structure_routing._Router
    ._best_path.
    Fails if:
    - the path cost compares the length before the bends.
    """

    normalized_graph, routing, _, _ = _result(
        _case("Fewest bends before the shortest length")
    )

    route = routing.routes[_edge_id(normalized_graph, "A2", "B2")]
    assert [channel_.kind for channel_ in route.channels] == [
        ChannelKind.BOTTOM_CORRIDOR
    ]


def test_relations_that_turn_together_do_not_cross() -> None:
    """
    Two relations that climb one vertical channel and turn together nest.

    Code: structure_routing._Router._assign_vertical_lanes,
    structure_routing._Router._assign_horizontal_lanes.
    Fails if:
    - a horizontal segment is seen from the wrong side, so the lanes of the
      vertical channel get the wrong order.
    """

    normalized_graph, routing, _, paths = _result(
        _case("Relations that turn together")
    )

    first = _edge_id(normalized_graph, "A2", "B1")
    second = _edge_id(normalized_graph, "A3", "B1")
    assert [channel_.kind for channel_ in routing.routes[first].channels] == [
        channel_.kind for channel_ in routing.routes[second].channels
    ]
    assert crossing_count(paths[first], paths[second]) == 0


@pytest.mark.parametrize(
    "case", STRUCTURE_CASES, ids=[case_.title for case_ in STRUCTURE_CASES]
)
def test_structure_routes_follow_right_hand_traffic(case: GalleryCase) -> None:
    """
    In one channel, the lanes of both directions follow right-hand traffic.

    A horizontal lane that goes left lies above a lane that goes right. A
    vertical lane that goes up lies right of a lane that goes down.

    Code: structure_routing._Router._assign_horizontal_lanes,
    structure_routing._Router._assign_vertical_lanes.
    Fails if:
    - the halves of a horizontal or a vertical channel are swapped.
    """

    _, routing, _, paths = _result(case)

    # Channel -> list of (goes toward the low side, lane).
    directions: Dict[object, List[Tuple[bool, int]]] = {}
    for route_ in routing.routes.values():
        path_ = paths[route_.edge_id]
        # Point i + 1 of the path starts the segment in channel i.
        for index_, (channel_, lane_) in enumerate(
            zip(route_.channels, route_.lanes)
        ):
            start_, end_ = path_[index_ + 1], path_[index_ + 2]
            if channel_.is_horizontal:
                goes_low_ = end_.x < start_.x
            else:
                goes_low_ = end_.y < start_.y
            directions.setdefault(channel_, []).append((goes_low_, lane_))
    for channel_, entries_ in directions.items():
        low_lanes_ = [lane_ for goes_low_, lane_ in entries_ if goes_low_]
        high_lanes_ = [lane_ for goes_low_, lane_ in entries_ if not goes_low_]
        if len(low_lanes_) == 0 or len(high_lanes_) == 0:
            continue
        if channel_.is_horizontal:  # type: ignore[attr-defined]
            # Left in the top half: smaller lanes.
            assert max(low_lanes_) < min(high_lanes_)
        else:
            # Up in the right half: larger lanes.
            assert min(low_lanes_) > max(high_lanes_)


@pytest.mark.parametrize(
    "case", STRUCTURE_CASES, ids=[case_.title for case_ in STRUCTURE_CASES]
)
def test_structure_route_invariants(case: GalleryCase) -> None:
    """
    Result invariants of the structure mode routes on every structure case.

    Code: structure_routing.compute_structure_routing,
    structure_paths.compute_structure_edge_paths.
    Fails if:
    - a route passes through a node or through a container that does not
      hold its endpoints.
    - two routes share or touch a segment, or a bend lies on another route.
    - the last segment is shorter than the lane clearance.
    """

    normalized_graph, routing, geometry, paths = _result(case)

    ancestors = _ancestors(normalized_graph)

    def obstacles_for_edge(edge_id: str) -> Mapping[str, Rect]:
        edge_ = next(
            edge_
            for edge_ in normalized_graph.edges
            if edge_.edge_id == edge_id
        )
        holders_ = ancestors[edge_.source_id] | ancestors[edge_.target_id]
        return {
            node_id_: rect_
            for node_id_, rect_ in geometry.node_rects.items()
            if node_id_ not in holders_
        }

    assert (
        geometry_problems(
            paths, geometry.width, geometry.height, obstacles_for_edge
        )
        == []
    )
    clearance = geometry.config.lane_clearance
    for route_ in routing.routes.values():
        path_ = paths[route_.edge_id]
        for port_, point_ in (
            (route_.source_port, path_[0]),
            (route_.target_port, path_[-1]),
        ):
            rect_ = geometry.node_rects[port_.node_id]
            assert point_.y == (
                rect_.y if port_.face is Face.TOP else rect_.y + rect_.height
            )
            assert rect_.x < point_.x < rect_.x + rect_.width
        last_ = abs(path_[-1].x - path_[-2].x) + abs(path_[-1].y - path_[-2].y)
        assert last_ >= clearance - 1e-9


def _ancestors(normalized_graph: NormalizedGraph) -> Dict[str, set[str]]:
    """
    Return the containers that hold each node.
    """

    result: Dict[str, set[str]] = {}
    for node_ in normalized_graph.nodes:
        parent_id_ = normalized_graph.parent_ids[node_.node_id]
        result[node_.node_id] = (
            set() if parent_id_ is None else result[parent_id_] | {parent_id_}
        )
    return result
