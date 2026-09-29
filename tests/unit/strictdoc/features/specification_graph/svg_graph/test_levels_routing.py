from typing import Dict, Tuple

from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CASES,
    GalleryCase,
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
