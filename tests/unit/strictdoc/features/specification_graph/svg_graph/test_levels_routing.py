from typing import Dict, Tuple

from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CASES,
    GalleryCase,
)
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    GeometryConfig,
    compute_levels_geometry,
)
from strictdoc.features.specification_graph.svg_graph.levels_routing import (
    LaneConflictPriority,
    LevelsRouting,
    Orientation,
    RoutingOptions,
    SkipChannelChoice,
    compute_levels_routing,
)
from strictdoc.features.specification_graph.svg_graph.levels_structure import (
    compute_levels_structure,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    normalize_graph,
)


def _case(title: str) -> GalleryCase:
    return next(case_ for case_ in GALLERY_CASES if case_.title == title)


def _routing(case: GalleryCase, options: RoutingOptions) -> LevelsRouting:
    normalized_graph = normalize_graph(case.graph)
    structure = compute_levels_structure(normalized_graph)
    return compute_levels_routing(normalized_graph, structure, options)


def _edge_ids_by_name(case: GalleryCase) -> Dict[Tuple[str, str], str]:
    return {
        (edge_.source_id, edge_.target_id): edge_.edge_id
        for edge_ in normalize_graph(case.graph).edges
    }


def test_straight_edge_has_no_lanes() -> None:
    case = _case("Simple chain")

    routing = _routing(case, RoutingOptions())

    for route_ in routing.routes.values():
        assert route_.lanes == ()
        assert route_.source_port.slot == 0
        assert route_.target_port.slot == 0


def test_nested_segment_priority_decides_the_crossed_vertical() -> None:
    case = _case("Nested relations in one channel")
    edge_ids = _edge_ids_by_name(case)
    outer_id = edge_ids[("X", "D")]
    inner_id = edge_ids[("Y", "C")]

    entry_routing = _routing(
        case, RoutingOptions(lane_conflict_priority=LaneConflictPriority.ENTRY)
    )
    exit_routing = _routing(
        case, RoutingOptions(lane_conflict_priority=LaneConflictPriority.EXIT)
    )

    for routing_ in (entry_routing, exit_routing):
        assert [
            (conflict_.outer_edge_id, conflict_.inner_edge_id)
            for conflict_ in routing_.conflicts
        ] == [(outer_id, inner_id)]
    # Entry priority: the outer segment stays above the inner one, so the
    # entry vertical of the inner segment stays uncrossed.
    assert (
        entry_routing.routes[outer_id].lanes[0].lane
        < entry_routing.routes[inner_id].lanes[0].lane
    )
    assert (
        exit_routing.routes[outer_id].lanes[0].lane
        > exit_routing.routes[inner_id].lanes[0].lane
    )


def test_skip_channel_choice_selects_the_vertical_channel() -> None:
    case = _case("Relations across levels from far columns")
    edge_ids = _edge_ids_by_name(case)

    def vertical_channels(options: RoutingOptions) -> Tuple[int, int]:
        routing = _routing(case, options)
        channels = []
        for pair_ in (("M3", "P1"), ("Q3", "P1")):
            lanes_ = routing.routes[edge_ids[pair_]].lanes
            assert lanes_[1].channel.orientation is Orientation.VERTICAL
            channels.append(lanes_[1].channel.index)
        return channels[0], channels[1]

    assert vertical_channels(
        RoutingOptions(skip_channel_choice=SkipChannelChoice.NEAR_SOURCE)
    ) == (0, 1)
    assert vertical_channels(
        RoutingOptions(skip_channel_choice=SkipChannelChoice.NEAR_TARGET)
    ) == (0, 0)


def _slots(
    case: GalleryCase, routing: LevelsRouting
) -> Dict[Tuple[str, str], Tuple[int, int]]:
    return {
        pair_: (
            routing.routes[edge_id_].source_port.slot,
            routing.routes[edge_id_].target_port.slot,
        )
        for pair_, edge_id_ in _edge_ids_by_name(case).items()
    }


def test_unsafe_group_shares_one_slot_list() -> None:
    case = _case("Opposite ports in one gate")

    slots = _slots(case, _routing(case, RoutingOptions()))

    # Gate of column 1, left group. B -> U arrives at U from the left: its
    # segment runs right, in the bottom half. L -> A leaves L to the left:
    # its segment runs left, in the top half. The verticals would overlap on
    # one x, so the two faces share one slot list.
    assert slots[("L", "U")] == (0, 0)
    assert slots[("L", "A")][0] == -2
    assert slots[("B", "U")][1] == -1


def test_safe_group_keeps_one_rhythm_on_both_faces() -> None:
    case = _case("Opposite ports in one gate")

    slots = _slots(case, _routing(case, RoutingOptions()))

    # Gate of column 0, right group. L -> A arrives at A from the right: its
    # segment runs left, in the top half. B -> U leaves B to the right: its
    # segment runs right, in the bottom half. The verticals cannot meet, so
    # each face numbers its ports on its own.
    assert slots[("B", "A")] == (0, 0)
    assert slots[("L", "A")][1] == 1
    assert slots[("B", "U")][0] == 1


def test_many_ports_of_one_gate() -> None:
    case = _case("Many ports in one gate")
    normalized_graph = normalize_graph(case.graph)
    structure = compute_levels_structure(normalized_graph)
    routing = compute_levels_routing(normalized_graph, structure)
    geometry = compute_levels_geometry(structure, routing)
    edge_ids = _edge_ids_by_name(case)
    config = GeometryConfig()

    rect = geometry.node_rects["U"]
    center = rect.x + rect.width / 2
    incoming_x = [
        geometry.edge_paths[edge_ids[(source_id_, "U")]][-1].x
        for source_id_ in ("L", "L2", "L3", "L4", "L5")
    ]
    outgoing_x = [
        geometry.edge_paths[edge_ids[("L", target_id_)]][0].x
        for target_id_ in ("U", "U2", "U3", "U4", "U5")
    ]

    # The right group of the gate between U and L is safe: both faces use
    # slots 1-4 with the normal pitch.
    expected_x = [
        center + slot_ * config.port_pitch for slot_ in (0, 1, 2, 3, 4)
    ]
    assert incoming_x == expected_x
    assert outgoing_x == expected_x

    # The left group of the gate between U2 and L2 is unsafe: the faces
    # share one slot list.
    slots = _slots(case, routing)
    assert slots[("L", "U2")][1] == -2
    assert slots[("L2", "U")][0] == -1
