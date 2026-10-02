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
from strictdoc.features.specification_graph.svg_graph.gate_ports import Face
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    GeometryConfig,
    LevelsGeometry,
    compute_levels_geometry,
)
from strictdoc.features.specification_graph.svg_graph.levels_routing import (
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
from tests.unit.strictdoc.features.specification_graph.svg_graph.geometry_checks import (
    geometry_problems,
    off_grid_segments,
)

LEVELS_CASES = [
    case_ for case_ in GALLERY_CASES if case_.graph.mode is LayoutMode.LEVELS
]


@pytest.mark.parametrize(
    "case", GALLERY_CASES, ids=[case_.title for case_ in GALLERY_CASES]
)
def test_normalization_invariants(case: GalleryCase) -> None:
    """
    Stage 1 invariants on every gallery case.

    Code: normalization.normalize_graph.
    Fails if:
    - the level edges have a cycle.
    Not verified by a mutation: unique edge IDs, cycle membership of cyclic
    edges, determinism.
    """

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
    """
    Stage 2 invariants on every levels mode gallery case.

    Code: levels_structure.compute_levels_structure.
    Fails if:
    - two nodes share a grid cell.
    - a parent does not stand above its child.
    Not verified by a mutation: standalone rows, determinism.
    """

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
    """
    Result invariants of stages 3 to 7 on every levels mode case.

    The test runs every routing option combination.

    Code: levels_routing.compute_levels_routing,
    levels_geometry.compute_levels_geometry.
    Fails if:
    - two segments of one lane overlap.
    - the halves of the right-hand traffic are swapped.
    - an unsafe group is numbered per face.
    - a shared list interleaves the faces.
    - the gate center does not shift.
    - the column does not widen.
    - the outermost port ignores the port margin.
    - a horizontal channel gives the outermost lane less room than the lane
      clearance.
    - a segment between the port stubs misses the grid of the lane pitch.
    """

    normalized_graph = normalize_graph(case.graph)
    structure = compute_levels_structure(normalized_graph)
    routing = compute_levels_routing(normalized_graph, structure, options)
    geometry = compute_levels_geometry(structure, routing)

    assert (
        off_grid_segments(geometry.edge_paths, geometry.config.lane_pitch) == []
    )
    assert (
        geometry_problems(
            geometry.edge_paths,
            geometry.width,
            geometry.height,
            lambda _: geometry.node_rects,
        )
        == []
    )
    _assert_ports_stay_on_faces(routing, geometry)
    _assert_gate_ports_are_distinct(structure, routing, geometry)
    _assert_face_ports_form_ordered_bundles(structure, routing)
    _assert_face_ports_keep_the_minimum_pitch(routing, geometry)
    _assert_last_segments_keep_the_lane_clearance(geometry)

    ports = [
        (route_.edge_id, port_)
        for route_ in routing.routes.values()
        for port_ in (route_.source_port, route_.target_port)
    ]
    assert len({port_ for _, port_ in ports}) == len(ports)


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


def _assert_last_segments_keep_the_lane_clearance(
    geometry: LevelsGeometry,
) -> None:
    """
    Check the room for the arrowhead on the last segment of each relation.

    The last segment ends with the arrowhead at the target face. The segment
    is at least the lane clearance long.
    """

    lane_clearance = GeometryConfig().lane_clearance
    for path_ in geometry.edge_paths.values():
        before_last_, last_ = path_[-2], path_[-1]
        length_ = abs(last_.x - before_last_.x) + abs(last_.y - before_last_.y)
        assert length_ >= lane_clearance - 1e-9


def _assert_face_ports_keep_the_minimum_pitch(
    routing: LevelsRouting, geometry: LevelsGeometry
) -> None:
    """
    Check the minimum distance between neighbor ports on one face.

    At the minimum port pitch, two arrowheads never overlap.
    """

    min_pitch = GeometryConfig().min_port_pitch
    x_by_face: Dict[Tuple[str, Face], List[float]] = {}
    for route_ in routing.routes.values():
        path_ = geometry.edge_paths[route_.edge_id]
        for port_, point_ in (
            (route_.source_port, path_[0]),
            (route_.target_port, path_[-1]),
        ):
            x_by_face.setdefault((port_.node_id, port_.face), []).append(
                point_.x
            )
    for positions_ in x_by_face.values():
        positions_.sort()
        for first_, second_ in zip(positions_, positions_[1:]):
            assert second_ - first_ >= min_pitch - 1e-9


def _assert_face_ports_form_ordered_bundles(
    structure: LevelsStructure, routing: LevelsRouting
) -> None:
    """
    Check the bundle rule of the ports.

    On each side of a gate, no port of the other face stands between the
    ports of one face. A port of the other face on the same slot is aligned,
    not between. Within a face, the ports follow the order of the positions
    where the relations go.
    """

    slots_by_gate_side: Dict[Tuple[int, int, int], List[Tuple[int, Face]]] = {}
    for route_ in routing.routes.values():
        for port_ in (route_.source_port, route_.target_port):
            if port_.slot == 0:
                continue
            position_ = structure.positions[port_.node_id]
            channel_ = (
                position_.row - 1 if port_.face is Face.TOP else position_.row
            )
            side_ = -1 if port_.slot < 0 else 1
            slots_by_gate_side.setdefault(
                (position_.column, channel_, side_), []
            ).append((abs(port_.slot), port_.face))
    for slots_ in slots_by_gate_side.values():
        for face_ in (Face.TOP, Face.BOTTOM):
            own_slots_ = {
                slot_ for slot_, slot_face_ in slots_ if slot_face_ is face_
            }
            if len(own_slots_) == 0:
                continue
            other_slots_ = {
                slot_ for slot_, slot_face_ in slots_ if slot_face_ is not face_
            }
            between_ = {
                slot_
                for slot_ in other_slots_
                if min(own_slots_) < slot_ < max(own_slots_)
                and slot_ not in own_slots_
            }
            assert between_ == set()

    for route_ in routing.routes.values():
        source_position_ = structure.positions[route_.source_port.node_id]
        target_position_ = structure.positions[route_.target_port.node_id]
        for port_, own_position_, other_position_ in (
            (route_.source_port, source_position_, target_position_),
            (route_.target_port, target_position_, source_position_),
        ):
            if port_.slot < 0:
                assert other_position_.column <= own_position_.column
            if port_.slot > 0 and len(route_.lanes) != 3:
                assert other_position_.column >= own_position_.column


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
