"""
Stage invariants on every gallery case.
"""

from itertools import combinations
from typing import Dict, List, Set, Tuple

import pytest

from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CASES,
    GalleryCase,
)
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    GeometryConfig,
    LevelsGeometry,
    Point,
    compute_levels_geometry,
)
from strictdoc.features.specification_graph.svg_graph.levels_routing import (
    Face,
    LaneConflictPriority,
    LevelsRouting,
    RoutingOptions,
    SkipChannelChoice,
    compute_levels_routing,
)
from strictdoc.features.specification_graph.svg_graph.levels_structure import (
    LevelsStructure,
    compute_levels_structure,
)
from strictdoc.features.specification_graph.svg_graph.model import LayoutMode
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedGraph,
    normalize_graph,
)

LEVELS_CASES = [
    case_ for case_ in GALLERY_CASES if case_.graph.mode is LayoutMode.LEVELS
]


@pytest.mark.parametrize(
    "case", GALLERY_CASES, ids=[case_.title for case_ in GALLERY_CASES]
)
def test_normalization_invariants(case: GalleryCase) -> None:
    normalized_graph = normalize_graph(case.graph)

    edge_ids = [edge_.edge_id for edge_ in normalized_graph.edges]
    assert len(edge_ids) == len(set(edge_ids))

    _assert_level_edges_are_acyclic(normalized_graph)

    cycle_members: Dict[str, Set[str]] = {
        cycle_.cycle_id: set(cycle_.node_ids)
        for cycle_ in normalized_graph.cycles
    }
    for edge_ in normalized_graph.edges:
        if edge_.cycle_id is not None:
            assert edge_.source_id in cycle_members[edge_.cycle_id]
            assert edge_.target_id in cycle_members[edge_.cycle_id]

    assert normalize_graph(case.graph) == normalized_graph


@pytest.mark.parametrize(
    "case", LEVELS_CASES, ids=[case_.title for case_ in LEVELS_CASES]
)
def test_levels_structure_invariants(case: GalleryCase) -> None:
    normalized_graph = normalize_graph(case.graph)
    structure = compute_levels_structure(normalized_graph)

    assert set(structure.positions) == {
        node_.node_id for node_ in normalized_graph.nodes
    }
    cells = [
        (position_.row, position_.column)
        for position_ in structure.positions.values()
    ]
    assert len(cells) == len(set(cells))
    for row_, column_ in cells:
        assert 0 <= row_ < structure.row_count
        assert 0 <= column_ < structure.column_count

    for edge_ in normalized_graph.edges:
        if edge_.is_level_edge:
            assert (
                structure.positions[edge_.target_id].row
                < structure.positions[edge_.source_id].row
            )

    standalone_node_ids = set(structure.standalone_node_ids)
    for node_id_, position_ in structure.positions.items():
        is_standalone_row_ = position_.row < structure.standalone_row_count
        assert is_standalone_row_ == (node_id_ in standalone_node_ids)

    assert compute_levels_structure(normalized_graph) == structure


ROUTING_VARIANTS = [
    RoutingOptions(priority_, choice_)
    for priority_ in LaneConflictPriority
    for choice_ in SkipChannelChoice
]


@pytest.mark.parametrize(
    "options",
    ROUTING_VARIANTS,
    ids=[
        f"{options_.lane_conflict_priority.value}-"
        f"{options_.skip_channel_choice.value}"
        for options_ in ROUTING_VARIANTS
    ],
)
@pytest.mark.parametrize(
    "case", LEVELS_CASES, ids=[case_.title for case_ in LEVELS_CASES]
)
def test_levels_geometry_invariants(
    case: GalleryCase, options: RoutingOptions
) -> None:
    normalized_graph = normalize_graph(case.graph)
    structure = compute_levels_structure(normalized_graph)
    routing = compute_levels_routing(normalized_graph, structure, options)
    geometry = compute_levels_geometry(structure, routing)

    assert _geometry_problems(geometry) == []
    _assert_ports_stay_on_faces(routing, geometry)
    _assert_gate_ports_are_distinct(structure, routing, geometry)

    ports = [
        (route_.edge_id, port_)
        for route_ in routing.routes.values()
        for port_ in (route_.source_port, route_.target_port)
    ]
    assert len({port_ for _, port_ in ports}) == len(ports)


_Segment = Tuple[Point, Point]


def _assert_ports_stay_on_faces(
    routing: LevelsRouting, geometry: LevelsGeometry
) -> None:
    margin = GeometryConfig().port_margin
    for route_ in routing.routes.values():
        path_ = geometry.edge_paths[route_.edge_id]
        for port_, point_ in (
            (route_.source_port, path_[0]),
            (route_.target_port, path_[-1]),
        ):
            rect_ = geometry.node_rects[port_.node_id]
            face_y_ = (
                rect_.y if port_.face is Face.TOP else rect_.y + rect_.height
            )
            assert point_.y == face_y_
            assert (
                rect_.x + margin <= point_.x <= rect_.x + rect_.width - margin
            )


def _assert_gate_ports_are_distinct(
    structure: LevelsStructure,
    routing: LevelsRouting,
    geometry: LevelsGeometry,
) -> None:
    """
    Check the port rule of a gate.

    A gate is the pair of faces that open into one channel in one column.
    Two relations may share a port position in a gate only if their
    verticals do not meet: one vertical ends above the other one starts.
    The two ends of one straight relation share a position.
    """

    verticals_by_gate_position: Dict[
        Tuple[int, int, float], List[Tuple[str, float, float]]
    ] = {}
    for route_ in routing.routes.values():
        path_ = geometry.edge_paths[route_.edge_id]
        for port_, point_, next_point_ in (
            (route_.source_port, path_[0], path_[1]),
            (route_.target_port, path_[-1], path_[-2]),
        ):
            position_ = structure.positions[port_.node_id]
            channel_ = (
                position_.row - 1 if port_.face is Face.TOP else position_.row
            )
            verticals_by_gate_position.setdefault(
                (position_.column, channel_, point_.x), []
            ).append(
                (
                    route_.edge_id,
                    min(point_.y, next_point_.y),
                    max(point_.y, next_point_.y),
                )
            )
    for verticals_ in verticals_by_gate_position.values():
        for (first_id_, first_top_, first_bottom_), (
            second_id_,
            second_top_,
            second_bottom_,
        ) in combinations(verticals_, 2):
            if first_id_ == second_id_:
                continue
            assert first_bottom_ < second_top_ or second_bottom_ < first_top_


def _geometry_problems(geometry: LevelsGeometry) -> List[str]:
    """
    Check the result invariants from spec.md, section "Инварианты результата".

    Two relations may cross only perpendicularly inside the segments of both
    relations.
    """

    problems: List[str] = []
    segments_by_edge: Dict[str, List[_Segment]] = {
        edge_id_: [
            (start_, end_)
            for start_, end_ in zip(path_, path_[1:])
            if start_ != end_
        ]
        for edge_id_, path_ in geometry.edge_paths.items()
    }
    for edge_id_, segments_ in segments_by_edge.items():
        for start_, end_ in segments_:
            if start_.x != end_.x and start_.y != end_.y:
                problems.append(f"{edge_id_}: diagonal segment")
            for point_ in (start_, end_):
                if not (
                    0 <= point_.x <= geometry.width
                    and 0 <= point_.y <= geometry.height
                ):
                    problems.append(f"{edge_id_}: point outside the SVG")
            for node_id_, rect_ in geometry.node_rects.items():
                if (
                    max(start_.x, end_.x) > rect_.x
                    and min(start_.x, end_.x) < rect_.x + rect_.width
                    and max(start_.y, end_.y) > rect_.y
                    and min(start_.y, end_.y) < rect_.y + rect_.height
                ):
                    problems.append(f"{edge_id_}: passes through {node_id_}")

    for (first_id_, first_), (second_id_, second_) in combinations(
        segments_by_edge.items(), 2
    ):
        for first_segment_ in first_:
            for second_segment_ in second_:
                if _collinear_contact(first_segment_, second_segment_):
                    problems.append(
                        f"{first_id_} and {second_id_}: shared or touching "
                        "segment"
                    )
        for bend_owner_, bends_, other_id_, other_segments_ in (
            (
                first_id_,
                geometry.edge_paths[first_id_][1:-1],
                second_id_,
                second_,
            ),
            (
                second_id_,
                geometry.edge_paths[second_id_][1:-1],
                first_id_,
                first_,
            ),
        ):
            for bend_ in bends_:
                if any(
                    _point_on_segment(bend_, segment_)
                    for segment_ in other_segments_
                ):
                    problems.append(
                        f"{bend_owner_}: bend on {other_id_} at "
                        f"({bend_.x}, {bend_.y})"
                    )
    return problems


def _collinear_contact(first: _Segment, second: _Segment) -> bool:
    for axis_, other_axis_ in (("y", "x"), ("x", "y")):
        values_ = {getattr(point_, axis_) for point_ in (*first, *second)}
        if len(values_) != 1:
            continue
        low_ = max(
            min(getattr(point_, other_axis_) for point_ in first),
            min(getattr(point_, other_axis_) for point_ in second),
        )
        high_ = min(
            max(getattr(point_, other_axis_) for point_ in first),
            max(getattr(point_, other_axis_) for point_ in second),
        )
        if low_ <= high_:
            return True
    return False


def _point_on_segment(point: Point, segment: _Segment) -> bool:
    start, end = segment
    if start.x == end.x == point.x:
        return min(start.y, end.y) <= point.y <= max(start.y, end.y)
    if start.y == end.y == point.y:
        return min(start.x, end.x) <= point.x <= max(start.x, end.x)
    return False


def _assert_level_edges_are_acyclic(normalized_graph: NormalizedGraph) -> None:
    successors: Dict[str, List[str]] = {
        node_.node_id: [] for node_ in normalized_graph.nodes
    }
    incoming_count: Dict[str, int] = {
        node_.node_id: 0 for node_ in normalized_graph.nodes
    }
    for edge_ in normalized_graph.edges:
        if edge_.is_level_edge:
            successors[edge_.source_id].append(edge_.target_id)
            incoming_count[edge_.target_id] += 1

    ready = [
        node_id_ for node_id_, count_ in incoming_count.items() if count_ == 0
    ]
    visited_count = 0
    while len(ready) > 0:
        node_id = ready.pop()
        visited_count += 1
        for successor_id_ in successors[node_id]:
            incoming_count[successor_id_] -= 1
            if incoming_count[successor_id_] == 0:
                ready.append(successor_id_)
    assert visited_count == len(normalized_graph.nodes)
