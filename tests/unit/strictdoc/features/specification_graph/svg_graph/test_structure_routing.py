from typing import Any, Dict, List, Mapping, Optional, Tuple

import pytest

from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CASES,
    GalleryCase,
)
from strictdoc.features.specification_graph.svg_graph import structure_routing
from strictdoc.features.specification_graph.svg_graph.gate_ports import (
    Face,
    GateEndpoint,
    number_gate_ports,
)
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    GeometryConfig,
    Point,
    Rect,
)
from strictdoc.features.specification_graph.svg_graph.levels_routing import (
    RoutingOptions,
)
from strictdoc.features.specification_graph.svg_graph.model import LayoutMode
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedGraph,
    normalize_graph,
)
from strictdoc.features.specification_graph.svg_graph.structure_geometry import (
    StructureGeometry,
    centered_lane_offset,
    compute_structure_geometry,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    ChannelKind,
    StructureChannelId,
    compute_structure_layout,
)
from strictdoc.features.specification_graph.svg_graph.structure_paths import (
    compute_structure_edge_paths,
    route_channel_points,
)
from strictdoc.features.specification_graph.svg_graph.structure_routing import (
    StructureRouting,
    _Router,
    compute_structure_routing,
)
from strictdoc.features.specification_graph.svg_graph.structure_stretches import (
    _common_runs,
)
from tests.unit.strictdoc.features.specification_graph.svg_graph.geometry_checks import (
    _collinear_contact,
    crossing_count,
    geometry_problems,
    off_grid_segments,
)

STRUCTURE_CASES = [
    case_ for case_ in GALLERY_CASES if case_.graph.mode is LayoutMode.STRUCTURE
]


def _invariant_cases(test_name: str) -> List[Any]:
    """
    Return the structure cases for an invariant test.

    A case with a known problem that breaks this invariant is expected to
    fail. The mark is strict: when the problem is fixed, the test fails
    until the case drops the invariant from its broken ones.
    """

    return [
        pytest.param(
            case_,
            id=case_.title,
            marks=pytest.mark.xfail(
                strict=True, reason="known problem, see the case description"
            )
            if test_name in case_.broken_invariants
            else (),
        )
        for case_ in STRUCTURE_CASES
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
        normalized_graph,
        layout,
        lane_counts=routing.lane_counts,
        bottom_segments=routing.bottom_segments,
        side_entries=routing.side_entries,
        gate_port_lists=routing.gate_port_lists,
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
        _case("Fewest bends under a tall section")
    )

    route = routing.routes[_edge_id(normalized_graph, "A2", "B2")]
    assert [channel_.kind for channel_ in route.channels] == [
        ChannelKind.BOTTOM_CORRIDOR
    ]


def test_relation_enters_a_section_straight() -> None:
    """
    A relation leaves a section and enters the next one straight.

    The other side of a vertical channel is a column. For a column of a
    container on the chain, the line continues in a channel of the
    container at the facing side face, at the same height.

    Code: structure_geometry._GeometryBuilder._through_lane_y.
    Fails if:
    - the height of a lane in a child container is counted wrong.
    """

    normalized_graph, _, _, paths = _result(
        _case("Relation between two sections")
    )

    assert len(paths[_edge_id(normalized_graph, "S1", "T2")]) == 4


def test_side_of_the_exit_follows_the_whole_path() -> None:
    """
    One path search over the channels of the chain chooses the exit side.

    S1 -> B1 leaves the section S through its top corridor to the right
    and reaches B1 at once. The way down under the tall section Q would be
    much longer.

    Code: structure_routing._Router._best_path,
    structure_routing._Router._through_passes.
    Fails if:
    - a segment under the columns continues straight into the space
      under another column, so the search undercounts the bends of a long
      path.
    """

    normalized_graph, routing, _, _ = _result(_case("Side of the exit"))

    route = routing.routes[_edge_id(normalized_graph, "S1", "B1")]
    assert route.channels[0].kind is ChannelKind.TOP_CORRIDOR
    assert route.channels[0].container_id == "S"


def test_opposite_relations_take_the_same_channels() -> None:
    """
    Two opposite relations between the same places take the same channels.

    Both paths have equal bends and length. The path with fewer channels
    inside nested containers wins, and this rule does not depend on the
    direction. The pair shares one whole stretch and does not cross.

    Code: structure_routing._Router._best_path.
    Fails if:
    - the tie between paths of equal cost depends on the order of the
      search queue.
    """

    normalized_graph, routing, _, paths = _result(
        _case("Opposite relations between a node and a section")
    )

    forward_id = _edge_id(normalized_graph, "A1", "Y1")
    backward_id = _edge_id(normalized_graph, "Y1", "A1")
    assert routing.routes[backward_id].channels == tuple(
        reversed(routing.routes[forward_id].channels)
    )
    assert crossing_count(paths[forward_id], paths[backward_id]) == 0


def test_line_enters_the_outer_vertical_channel_of_a_section() -> None:
    """
    A line crosses a side face straight and turns in the outer vertical
    channel of the section behind it.

    A1 -> X1 goes from the space under A1 into the section L1 at the same
    height and turns down in the left vertical channel of L1. It does not
    climb to the top corridor of L1 first.

    Code: structure_routing._side_face_links,
    structure_routing._Router._face_x.
    Fails if:
    - a horizontal channel of the parent does not link to the outer
      vertical channel of a child through the side face.
    - the columns under the segment include the child it enters.
    """

    normalized_graph, _, _, paths = _result(
        _case("Relations through two levels")
    )

    path = paths[_edge_id(normalized_graph, "A1", "X1")]
    heights = [point_.y for point_ in path]
    assert heights == sorted(heights)


def test_line_enters_a_section_from_a_column_channel() -> None:
    """
    A line from a column channel of the parent crosses a side face straight
    into the outer vertical channel of the section, and a line from that
    vertical channel leaves into the column channel the same way.

    A1 -> X2 goes from the column channel between A1 and A2 into the left
    vertical channel of L1 and down to L2. X2 -> A1 takes the same channels
    in the opposite direction. Neither climbs to the top corridor of L1.

    Code: structure_routing._side_face_links,
    structure_routing._Router._fits_side_face.
    Fails if:
    - a column channel of the parent does not link to the outer vertical
      channel of a child through the side face.
    - the height check rejects a lane within the vertical channel.
    """

    normalized_graph, routing, _, _ = _result(
        _case("Side entry from a column channel")
    )

    column_channel = StructureChannelId(ChannelKind.COLUMN, "Doc", 0, 0)
    vertical = StructureChannelId(ChannelKind.VERTICAL, "L1", 0)
    for source_id_, target_id_ in (("A1", "X2"), ("X2", "A1")):
        channels_ = routing.routes[
            _edge_id(normalized_graph, source_id_, target_id_)
        ].channels
        assert len(channels_) == 3
        assert column_channel in channels_
        assert channels_[1] == vertical


def test_path_under_the_columns_goes_down_from_the_faces() -> None:
    """
    The length of a path under the columns goes from the bottom faces down
    to the segment.

    A4 and E4 lie in pockets below the shortest column of the container.
    The path A4[bottom] - E4[bottom] goes down from each face to the
    segment under the columns between them, and along the segment.

    Code: structure_routing._Router._stub_length.
    Fails if:
    - the length from a face below the lowest height of the bottom
      corridor goes up to that height and back down.
    """

    normalized_graph = normalize_graph(
        _case("Many lines in one pocket").graph
    )
    layout = compute_structure_layout(normalized_graph)
    router = _Router(
        normalized_graph,
        layout,
        compute_structure_geometry(normalized_graph, layout),
        GeometryConfig(),
        RoutingOptions(),
    )
    corridor = StructureChannelId(ChannelKind.BOTTOM_CORRIDOR, "Doc")
    first = router.estimate.node_rects["A4"]
    second = router.estimate.node_rects["E4"]
    assert first.y + first.height > router._channel_y(corridor)

    path = router._best_path(
        "A4", Face.BOTTOM, "E4", Face.BOTTOM, router._chain("A4", "E4")
    )
    assert path is not None
    (bends, length), channels, levels = path
    assert bends == 2
    assert channels == (corridor,)
    segment_y = levels[0]
    assert length == (
        abs(
            (second.x + second.width / 2) - (first.x + first.width / 2)
        )
        + (segment_y - (first.y + first.height))
        + (segment_y - (second.y + second.height))
    )


def test_side_entry_fits_the_height_of_the_vertical_channel() -> None:
    """
    A segment of the parent enters the outer vertical channel of a section
    through its side face only within the height of that vertical channel.

    - A lane of a column channel above the top of the vertical channel would
      lie opposite the top corridor of the section.
    - A segment under the columns may lie higher: the geometry lowers it.
    - Below the bottom of the vertical channel, a segment would lie opposite
      the bottom corridor of the section, although still above the bottom
      of its frame.

    Code: structure_routing._Router._fits_side_face.
    Fails if:
    - the check ignores the top of the vertical channel for a column
      channel.
    - the check takes the bottom of the frame instead of the bottom of the
      vertical channel.
    """

    normalized_graph = normalize_graph(
        _case("Side entry from a column channel").graph
    )
    layout = compute_structure_layout(normalized_graph)
    router = _Router(
        normalized_graph,
        layout,
        compute_structure_geometry(normalized_graph, layout),
        GeometryConfig(),
        RoutingOptions(),
    )
    column_channel = StructureChannelId(ChannelKind.COLUMN, "Doc", 0, 0)
    corridor = StructureChannelId(ChannelKind.BOTTOM_CORRIDOR, "Doc")
    vertical = StructureChannelId(ChannelKind.VERTICAL, "L1", 0)
    rect = router.channel_rects[vertical]
    frame = router.estimate.node_rects["L1"]
    bottom = rect.y + rect.height
    assert bottom < frame.y + frame.height

    assert router._fits_side_face(column_channel, vertical, rect.y)
    assert not router._fits_side_face(column_channel, vertical, rect.y - 1)
    assert router._fits_side_face(corridor, vertical, rect.y - 1)
    for horizontal_ in (column_channel, corridor):
        assert router._fits_side_face(horizontal_, vertical, bottom - 1)
        assert not router._fits_side_face(horizontal_, vertical, bottom)


def test_side_entry_from_a_column_channel_lies_below_the_top_corridor() -> (
    None
):
    """
    A lane of a column channel that enters a section through its side face
    lies opposite the outer vertical channel of the section, even when the
    top corridor of the section gets more lanes than the path search
    expected.

    The top corridor of L1 has two lanes. A1 -> X2 enters L1 from the column
    channel between A1 and A2. By the nodes of its column alone, the lane
    would lie above the top of the left vertical channel of L1.

    Code: structure_geometry._GeometryBuilder._side_entry_size,
    structure_routing._column_side_entries.
    Fails if:
    - the column channel does not grow for a side entry.
    """

    normalized_graph, _, geometry, paths = _result(
        _case("Side entry from a column channel below a full top corridor")
    )

    vertical = geometry.channel_rect(
        StructureChannelId(ChannelKind.VERTICAL, "L1", 0)
    )
    frame = geometry.node_rects["L1"]
    path = paths[_edge_id(normalized_graph, "A1", "X2")]
    crossing_y = next(
        start_.y
        for start_, end_ in zip(path, path[1:])
        if start_.y == end_.y and start_.x < frame.x < end_.x
    )
    assert vertical.y <= crossing_y <= vertical.y + vertical.height


def test_line_leaves_a_section_off_the_lanes_that_enter_it() -> None:
    """
    A corridor segment that leaves a section through its side face does not
    cross the face at the height of a lane of a column channel of the
    parent that enters the section through the same face.

    A2 -> S1 enters S from the column channel between A2 and A3. S1 -> A3
    leaves the pocket under S1 through the same face. By the pocket alone,
    it would cross the face at the height of the lane of A2 -> S1.

    Code: structure_geometry._GeometryBuilder._face_entry_lanes,
    structure_geometry._GeometryBuilder._bottom_corridor.
    Fails if:
    - a corridor segment that leaves through a side face ignores the lanes
      of the column channel that enter through that face.
    """

    normalized_graph, routing, geometry, paths = _result(
        _case("Two lines cross a side face at one point")
    )

    channel = StructureChannelId(ChannelKind.COLUMN, "Doc", 0, 1)
    rect = geometry.channel_rect(channel)
    lane_heights = [
        rect.y
        + centered_lane_offset(
            rect.height, routing.lane_counts[channel], lane_, geometry.config
        )
        for lane_ in range(routing.lane_counts[channel])
    ]
    face_x = geometry.node_rects["S"].x
    path = paths[_edge_id(normalized_graph, "S1", "A3")]
    crossing_y = next(
        start_.y
        for start_, end_ in zip(path, path[1:])
        if start_.y == end_.y and end_.x < face_x < start_.x
    )
    assert all(
        abs(crossing_y - lane_y_) >= geometry.config.lane_pitch
        for lane_y_ in lane_heights
    )


@pytest.mark.parametrize(
    "case", STRUCTURE_CASES, ids=lambda case_: case_.title
)
def test_gate_halves_follow_right_hand_traffic(
    case: GalleryCase, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    The half of the channel that a gate expects for each port follows the
    direction of its horizontal segment: left in the top half, right in the
    bottom half. A forced order of a shared stretch does not change it.

    The gate decides by the halves whether the ports of its two faces may
    stand on one vertical. The lane assignment does not keep halves, so a
    half changed by a forced order can put two ports on one vertical whose
    lines then cross twice, as G3 -> A1 and G3 -> E2 once did in "Stress:
    staircase of columns and pockets".

    Code: structure_routing._Router._assign_ports.
    Fails if:
    - a forced order changes the half that a gate expects.
    """

    # The halves that the gates of one layer get, and the directions of the
    # plans of that layer.
    expected: Dict[Tuple[str, int], int] = {}
    mismatches: List[Tuple[str, int]] = []
    assign_ports = _Router._assign_ports

    def capture_ports(router: _Router, plans: Any, *args: Any) -> Any:
        expected.clear()
        for plan_ in plans:
            last_ = len(plan_.channels) - 1
            for role_, position_ in ((0, 0), (1, last_)):
                goes_left_ = router._goes_left(plan_, position_)
                expected[(plan_.edge.edge_id, role_)] = 0 if goes_left_ else 1
        return assign_ports(router, plans, *args)

    def capture_endpoints(
        endpoints: List[GateEndpoint], forced: Any = ()
    ) -> Dict[Any, Any]:
        mismatches.extend(
            endpoint_.endpoint_key
            for endpoint_ in endpoints
            if endpoint_.half != expected[endpoint_.endpoint_key]
        )
        return number_gate_ports(endpoints, forced)

    monkeypatch.setattr(_Router, "_assign_ports", capture_ports)
    monkeypatch.setattr(structure_routing, "number_gate_ports", capture_endpoints)
    _result(case)

    assert mismatches == []


@pytest.mark.parametrize(
    "case", STRUCTURE_CASES, ids=lambda case_: case_.title
)
def test_gate_port_side_agrees_with_the_segment_direction(
    case: GalleryCase, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    The side of a port and the direction of its horizontal segment agree:
    a source port on the left side sends its segment left, a target port on
    the left side receives a segment that goes right.

    The side comes from the vertical channel where the line turns, the
    direction from the two ends of the segment. Both use the estimate.
    Taking one end from the exact geometry, where the nodes stand elsewhere,
    gives a wrong direction for some segments.

    Code: structure_routing._Router._goes_left.
    Fails if:
    - the direction compares a position of the estimate with a position of
      the exact geometry.
    """

    mismatches: List[Tuple[str, int]] = []

    def capture(
        endpoints: List[GateEndpoint], forced: Any = ()
    ) -> Dict[Any, Any]:
        for endpoint_ in endpoints:
            if endpoint_.side == 0:
                continue
            goes_left_ = (endpoint_.side < 0) == (
                endpoint_.endpoint_key[1] == 0
            )
            if endpoint_.half != (0 if goes_left_ else 1):
                mismatches.append(endpoint_.endpoint_key)
        return number_gate_ports(endpoints, forced)

    monkeypatch.setattr(structure_routing, "number_gate_ports", capture)
    _result(case)

    assert mismatches == []


@pytest.mark.parametrize(
    "case", STRUCTURE_CASES, ids=lambda case_: case_.title
)
def test_vertical_lane_ends_take_the_side_of_the_drawing(
    case: GalleryCase, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    The side of each end of a vertical segment, as the lane assignment sees
    it, is the side where the horizontal segment at that end goes in the
    drawing.

    The side compares the far end of the horizontal segment with the
    vertical channel. Both positions come from the estimate. Taking the
    vertical channel from the geometry of a layer, where the nodes stand
    elsewhere, gives a wrong side for some ends.

    Code: structure_routing._Router._assign_vertical_lanes.
    Fails if:
    - the side compares a position of the estimate with a position of the
      geometry of a layer.
    """

    sides: Dict[Tuple[str, int], Tuple[bool, bool]] = {}
    assign = structure_routing.assign_lanes

    def capture(segments: Any, *args: Any) -> Any:
        for segment_ in segments:
            # The vertical segments stand at the odd positions of a route.
            if segment_.key[1] % 2 == 1:
                entry_, exit_ = segment_.members
                sides[segment_.key] = (
                    entry_.to_high_side,
                    exit_.to_high_side,
                )
        return assign(segments, *args)

    monkeypatch.setattr(structure_routing, "assign_lanes", capture)
    _, routing, geometry, _ = _result(case)

    wrong: List[Tuple[str, int]] = []
    for route_ in routing.routes.values():
        points_ = route_channel_points(route_, geometry)
        for position_ in range(1, len(route_.channels), 2):
            key_ = (route_.edge_id, position_)
            if key_ not in sides:
                continue
            vertical_x_ = points_[position_ + 1].x
            for far_x_, to_high_side_ in (
                (points_[position_].x, sides[key_][0]),
                (points_[position_ + 3].x, sides[key_][1]),
            ):
                if far_x_ != vertical_x_ and (far_x_ > vertical_x_) != (
                    to_high_side_
                ):
                    wrong.append(key_)
    assert wrong == []


@pytest.mark.parametrize(
    "case", STRUCTURE_CASES, ids=lambda case_: case_.title
)
def test_horizontal_lane_halves_follow_the_direction_of_the_drawing(
    case: GalleryCase, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    The half of each horizontal segment, as the lane assignment sees it,
    follows the direction of the segment in the drawing: right-hand
    traffic. A segment that goes left lies in the top half, one that goes
    right in the bottom half.

    Code: structure_routing._Router._assign_horizontal_lanes.
    Fails if:
    - the halves of the horizontal channels are swapped.
    """

    halves: Dict[Tuple[str, int], int] = {}
    assign = structure_routing.assign_lanes

    def capture(segments: Any, *args: Any) -> Any:
        for segment_ in segments:
            halves[segment_.key] = segment_.half
        return assign(segments, *args)

    monkeypatch.setattr(structure_routing, "assign_lanes", capture)
    _, routing, geometry, _ = _result(case)

    wrong: List[Tuple[str, int]] = []
    for route_ in routing.routes.values():
        points_ = route_channel_points(route_, geometry)
        for position_ in range(0, len(route_.channels), 2):
            key_ = (route_.edge_id, position_)
            if key_ not in halves:
                continue
            start_, end_ = points_[position_ + 1], points_[position_ + 2]
            if start_.x == end_.x:
                continue
            if halves[key_] != (0 if end_.x < start_.x else 1):
                wrong.append(key_)
    assert wrong == []


@pytest.mark.parametrize(
    "case",
    _invariant_cases(
        "test_vertical_lane_halves_follow_the_direction_of_the_drawing"
    ),
)
def test_vertical_lane_halves_follow_the_direction_of_the_drawing(
    case: GalleryCase, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    The half of each vertical segment, as the lane assignment sees it,
    follows the direction of the segment in the drawing: right-hand
    traffic. A segment that goes up lies in the right half, one that goes
    down in the left half.

    The lanes of the vertical channels are assigned by the final heights
    of the horizontal segments, so the direction is the one of the
    drawing.

    Code: structure_routing._Router._assign_vertical_lanes,
    structure_routing._Router._final_vertical_lanes.
    Fails if:
    - the halves of the vertical channels are swapped.
    - the direction of a vertical segment changes after its lane is
      assigned.
    """

    halves: Dict[Tuple[str, int], int] = {}
    assign = structure_routing.assign_lanes

    def capture(segments: Any, *args: Any) -> Any:
        for segment_ in segments:
            halves[segment_.key] = segment_.half
        return assign(segments, *args)

    monkeypatch.setattr(structure_routing, "assign_lanes", capture)
    _, routing, geometry, _ = _result(case)

    wrong: List[Tuple[str, int]] = []
    for route_ in routing.routes.values():
        points_ = route_channel_points(route_, geometry)
        for position_ in range(1, len(route_.channels), 2):
            key_ = (route_.edge_id, position_)
            if key_ not in halves:
                continue
            start_, end_ = points_[position_ + 1], points_[position_ + 2]
            if start_.y == end_.y:
                continue
            if halves[key_] != (1 if end_.y < start_.y else 0):
                wrong.append(key_)
    assert wrong == []


def test_vertical_lanes_follow_the_final_heights() -> None:
    """
    The order of the lanes in a vertical channel follows the final heights
    of the horizontal segments on both sides.

    S2 -> Q1 steps down by one lane pitch from the space under D1 into the
    pocket under Q1, to the height where S2 -> Q2 passes under D1. With
    the right lane, the segment of S2 -> Q1 in the pocket starts right of
    the end of S2 -> Q2 under D1, and the two segments do not meet. The
    estimate gives this step the other direction.

    Code: structure_routing._Router._final_vertical_lanes.
    Fails if:
    - the lanes of the vertical channels stay as the layers assign them.
    """

    normalized_graph, routing, _, paths = _result(
        _case("Short step into the pocket of a section")
    )

    first_id = _edge_id(normalized_graph, "S2", "Q1")
    second_id = _edge_id(normalized_graph, "S2", "Q2")
    vertical = StructureChannelId(ChannelKind.VERTICAL, "Doc", 3)

    def vertical_lane(edge_id: str) -> int:
        route_ = routing.routes[edge_id]
        return route_.lanes[route_.channels.index(vertical)]

    assert vertical_lane(first_id) > vertical_lane(second_id)
    assert not any(
        _collinear_contact(first_segment_, second_segment_)
        for first_segment_ in zip(paths[first_id], paths[first_id][1:])
        for second_segment_ in zip(paths[second_id], paths[second_id][1:])
    )


def test_lines_on_both_sides_of_a_vertical_channel_do_not_meet() -> None:
    """
    Two lines with segments at one height on opposite sides of a vertical
    channel take the lanes on their own sides.

    A2 -> Q2 turns right under S and E1 -> A3 turns left into the gap
    between A2 and A3, at one height. The lane of A2 -> Q2 lies right of
    the lane of E1 -> A3, so the two segments do not meet.

    Code: structure_routing._Router._horizontal_far_x,
    structure_routing._Router._assign_vertical_lanes.
    Fails if:
    - the far end of a middle horizontal segment is seen from the wrong
      side.
    """

    normalized_graph, routing, _, paths = _result(
        _case("Lines on both sides of a vertical channel at one height")
    )

    first_id = _edge_id(normalized_graph, "A2", "Q2")
    second_id = _edge_id(normalized_graph, "E1", "A3")
    vertical = StructureChannelId(ChannelKind.VERTICAL, "Doc", 1)

    def vertical_lane(edge_id: str) -> int:
        route_ = routing.routes[edge_id]
        return route_.lanes[route_.channels.index(vertical)]

    assert vertical_lane(first_id) > vertical_lane(second_id)
    assert not any(
        _collinear_contact(first_segment_, second_segment_)
        for first_segment_ in zip(paths[first_id], paths[first_id][1:])
        for second_segment_ in zip(paths[second_id], paths[second_id][1:])
    )

def test_lines_at_different_final_heights_share_a_vertical_lane() -> None:
    """
    Two lines that cross a vertical channel at different final heights
    share its lane.

    Q1 -> D1 leaves the gap between Q1 and Q2 into the pocket under D1,
    and S1 -> Q2 crosses the pocket below it into the next lane of the same
    gap. Both cross the vertical channel between D1 and Q straight, at two
    heights one lane pitch apart. By the heights of the layer, their
    segments in this channel overlap.

    Code: structure_routing._Router._final_vertical_lanes.
    Fails if:
    - the lanes of a vertical channel take the heights of a layer.
    """

    _, routing, _, _ = _result(
        _case("Two sections leave into one pocket at one height")
    )

    vertical = StructureChannelId(ChannelKind.VERTICAL, "Doc", 3)
    assert routing.lane_counts[vertical] == 1

def test_turned_step_takes_the_order_of_the_drawing() -> None:
    """
    A nested pair takes the order of the drawing at a step that goes the
    other way in the drawing than on its shared stretch.

    The step of S2 -> Q1 in a vertical channel goes up on the shared
    stretch with Q1 -> A2 and down in the drawing. With the order of the
    stretch, the two lines cross twice.

    Code: structure_routing._turned_steps,
    structure_routing._with_turned_steps.
    Fails if:
    - a nested pair keeps the order of its shared stretch at a step that
      goes the other way in the drawing.
    """

    normalized_graph, _, _, paths = _result(
        _case("Stress: three levels of sections")
    )

    assert (
        crossing_count(
            paths[_edge_id(normalized_graph, "S2", "Q1")],
            paths[_edge_id(normalized_graph, "Q1", "A2")],
        )
        == 0
    )

def test_row_has_no_base_height_in_the_lane_order() -> None:
    """
    A row, a segment under the columns that continues a lane straight,
    keeps the height of its lane. The lane assignment does not order it by
    a base height against the corridor segments.

    A3 -> B3 and A4 -> B4 pass under the short section S straight at the
    heights of their gaps.

    Code: structure_routing._Router._assign_horizontal_lanes,
    lane_assignment._base_order.
    Fails if:
    - a row gets a base height in the lane assignment.
    """

    normalized_graph = normalize_graph(
        _case("Through pass under a short section").graph
    )
    layout = compute_structure_layout(normalized_graph)
    router = _Router(
        normalized_graph,
        layout,
        compute_structure_geometry(normalized_graph, layout),
        GeometryConfig(),
        RoutingOptions(),
    )
    base_levels: Dict[Tuple[str, int], Optional[float]] = {}
    assign = structure_routing.assign_lanes

    def capture(segments: Any, *args: Any) -> Any:
        for segment_ in segments:
            base_levels[segment_.key] = segment_.base_level
        return assign(segments, *args)

    with pytest.MonkeyPatch.context() as monkeypatch_:
        monkeypatch_.setattr(structure_routing, "assign_lanes", capture)
        router.route()

    assert len(router.row_keys) > 0
    assert all(base_levels[key_] is None for key_ in router.row_keys)


def test_side_entry_lies_below_the_top_corridor() -> None:
    """
    A line that enters a section through its side face into the outer
    vertical channel lies below the top corridor of the section.

    The top corridor of L1 has three lanes. A1 -> X1 is the only line
    under A1, so the space under A1 alone would put it at the height of the
    lowest lane.

    Code: structure_geometry._GeometryBuilder._side_entry_floor,
    structure_geometry._GeometryBuilder._bottom_corridor.
    Fails if:
    - the height of a side entry ignores the top corridor of the section.
    """

    normalized_graph, _, geometry, paths = _result(
        _case("Side entry below a top corridor, one line under the node")
    )

    corridor = geometry.channel_rect(
        StructureChannelId(ChannelKind.TOP_CORRIDOR, "L1")
    )
    path = paths[_edge_id(normalized_graph, "A1", "X1")]
    assert path[1].y >= corridor.y + corridor.height


def test_bottom_segment_lies_below_the_columns_it_passes_over() -> None:
    """
    A segment in the bottom corridor lies the clearance below the columns
    it passes over.

    Code: structure_geometry._GeometryBuilder._bottom_corridor,
    structure_geometry.corridor_contour, structure_paths._route_path.
    Fails if:
    - the segment lies below the tallest column of the container.
    - the contour counts a column that the segment does not pass over.
    """

    normalized_graph, _, geometry, paths = _result(
        _case("Bottom corridor follows the columns")
    )

    clearance = geometry.config.lane_clearance
    for source_id_, target_id_, column_id_ in (
        ("A2", "B1", "S"),
        ("A2", "C1", "T"),
    ):
        path_ = paths[_edge_id(normalized_graph, source_id_, target_id_)]
        column_ = geometry.node_rects[column_id_]
        assert path_[1].y == path_[2].y
        assert path_[1].y == column_.y + column_.height + clearance


def test_face_toward_the_target_wins_a_near_tie() -> None:
    """
    Of two paths with equal bends and lengths within two node heights, the
    path from the faces that look toward each other wins.

    S2 lies below Q1. The path of Q1 -> S2 from the top face of Q1 is 48
    pixels shorter than the path from the bottom face, less than two node
    heights, so the bottom face wins: the line goes down into the free
    space under Q1 and does not open the top corridor of Q for one turn.

    Code: structure_routing._Router._best_candidate.
    Fails if:
    - the faces toward the target do not win a near tie.
    - a few pixels of length decide over the faces.
    """

    normalized_graph, routing, _, _ = _result(
        _case("Line from a section into a pocket")
    )

    route = routing.routes[_edge_id(normalized_graph, "Q1", "S2")]
    assert route.source_port.face is Face.BOTTOM


def test_segment_between_two_sections_uses_the_pocket() -> None:
    """
    A segment under the columns that enters a section at each end passes
    under the columns between the two side faces only.

    Q1 -> S3 runs from the left face of Q to the right face of S, under D1
    only. Its base height lies in the pocket under D1, so it lies above
    S1 -> E2, which passes under Q and the column of E1 and E2.

    Code: structure_routing._Router._exact_levels,
    structure_routing._Router._face_x, lane_assignment._base_order.
    Fails if:
    - an order of a shared stretch wins over the base heights.
    """

    normalized_graph, _, _, paths = _result(
        _case("Pocket between two sections")
    )

    def bottom_y(source_id: str, target_id: str) -> float:
        return max(
            point_.y
            for point_ in paths[_edge_id(normalized_graph, source_id, target_id)]
        )

    assert bottom_y("Q1", "S3") < bottom_y("S1", "E2")


def test_rows_from_a_section_keep_the_heights_of_their_lanes() -> None:
    """
    Segments under the columns that leave a section continue straight into
    a column gap.

    S2 -> E2 and S3 -> E2 leave S through its right face, pass under Q and
    enter the gap between E2 and E3 at the heights of their lanes there.
    Each line has four bends: no step on the way.

    Code: structure_routing._Router._exact_levels,
    structure_routing._Router._face_x.
    Fails if:
    - the base height of a segment counts the sections it enters as
      columns it passes under.
    """

    normalized_graph, _, _, paths = _result(
        _case("Rows from a section into a column gap")
    )

    for source_id_ in ("S2", "S3"):
        path_ = paths[_edge_id(normalized_graph, source_id_, "E2")]
        assert len(path_) - 2 == 4


def test_row_is_not_moved_by_the_lane_order_of_the_corridor() -> None:
    """
    A row, a segment under the columns that continues a lane straight,
    keeps its height against the corridor segments with smaller lanes.

    Q3 -> S4 leaves Q at the height of its lane and passes under the
    columns straight, so it has four bends.

    Code: structure_geometry._GeometryBuilder._bottom_corridor.
    Fails if:
    - the lane order of the corridor segments moves the rows.
    """

    normalized_graph, _, _, paths = _result(
        _case("Stress: three levels of sections")
    )

    assert len(paths[_edge_id(normalized_graph, "Q3", "S4")]) - 2 == 4

def test_lines_into_a_section_at_one_point_do_not_overlap() -> None:
    """
    Two lines that enter a section at one point keep the order of their
    base heights, and their verticals do not meet.

    D1 -> S2 lies in the pocket under D1 and goes down to S2. A3 -> S3
    comes from under S and goes up to S3. Both use one lane of the right
    vertical channel of S. The rule of ends at one point would put the
    line that goes up above the other one; under the columns the base
    heights win, because the side of an end is known only at the base
    height.

    Code: lane_assignment._base_order, lane_assignment.assign_lanes.
    Fails if:
    - two ends at one point win over the base heights.
    """

    normalized_graph, _, _, paths = _result(
        _case("Two lines into a section at one point")
    )
    first = paths[_edge_id(normalized_graph, "A3", "S3")]
    second = paths[_edge_id(normalized_graph, "D1", "S2")]

    assert not any(
        _collinear_contact(first_segment_, second_segment_)
        for first_segment_ in zip(first, first[1:])
        for second_segment_ in zip(second, second[1:])
    )


def test_line_crosses_the_face_of_a_section_straight() -> None:
    """
    A line under the columns that leaves a section through its side face
    goes on straight under the columns outside, at the height of its
    segment in the section, if that height fits there.

    Q1 -> S2 lies under Q1 at its height in Q and keeps it under D1 up to
    the face of S: the pocket under D1 is deep enough. No step at the face
    of Q.

    Code: structure_geometry._GeometryBuilder._child_segment_y,
    structure_routing._through_segments.
    Fails if:
    - the segment outside a section does not continue the segment inside.
    """

    normalized_graph, _, geometry, paths = _result(
        _case("Line from a section into a pocket")
    )

    path = paths[_edge_id(normalized_graph, "Q1", "S2")]
    face_of_s = geometry.node_rects["S"]
    # From the port of Q1 down, then one horizontal up to the face of S.
    assert path[1].y == path[2].y
    assert path[2].x <= face_of_s.x + face_of_s.width


def test_bottom_corridor_keeps_the_lane_order() -> None:
    """
    Of two overlapping segments in the bottom corridor, the larger lane lies
    lower, and the corridor fits the lowest segment.

    Code: structure_geometry._GeometryBuilder._bottom_corridor.
    Fails if:
    - a segment ignores an overlapping segment with a smaller lane.
    - the corridor size does not fit the lowest segment.
    """

    normalized_graph, _, geometry, paths = _result(
        _case("Lane order in the bottom corridor")
    )

    left = paths[_edge_id(normalized_graph, "C2", "A2")]
    right = paths[_edge_id(normalized_graph, "A2", "C2")]
    assert right[1].y == left[1].y + geometry.config.lane_pitch
    corridor = next(
        channel_.rect
        for channel_ in geometry.channels
        if channel_.kind is ChannelKind.BOTTOM_CORRIDOR
        and channel_.container_id == "Doc"
    )
    assert corridor.y + corridor.height == (
        right[1].y + geometry.config.lane_clearance
    )


def test_through_pass_goes_straight_under_a_short_section() -> None:
    """
    A line crosses the vertical channels and the pocket under a short
    section straight, at the height of the column channel lane.

    Code: structure_routing._Router._through_passes,
    structure_routing._Router._best_path,
    structure_routing._Router._segment_y,
    structure_geometry._GeometryBuilder._bottom_corridor.
    Fails if:
    - a through pass counts as a bend.
    - the segment under the section does not keep the height of the column
      channel lane.
    """

    normalized_graph, routing, _, paths = _result(
        _case("Through pass under a short section")
    )

    for source_id_, target_id_ in (("A3", "B3"), ("A4", "B4")):
        edge_id_ = _edge_id(normalized_graph, source_id_, target_id_)
        assert [
            channel_.kind for channel_ in routing.routes[edge_id_].channels
        ] == [
            ChannelKind.COLUMN,
            ChannelKind.VERTICAL,
            ChannelKind.BOTTOM_CORRIDOR,
            ChannelKind.VERTICAL,
            ChannelKind.COLUMN,
        ]
        assert len(paths[edge_id_]) == 4


def test_two_relations_into_one_node_nest() -> None:
    """
    Two relations into one node over a section nest in the vertical channel.

    The lane order in a vertical channel uses the far end of each
    horizontal segment next to it: the next vertical channel or the port.

    Code: structure_routing._Router._horizontal_far_x,
    structure_routing._Router._assign_vertical_lanes.
    Fails if:
    - the far end of a middle horizontal segment is seen from the wrong
      side.
    """

    normalized_graph, _, _, paths = _result(
        _case("Two relations into one node over a section")
    )

    assert (
        crossing_count(
            paths[_edge_id(normalized_graph, "C2", "A2")],
            paths[_edge_id(normalized_graph, "C3", "A2")],
        )
        == 0
    )


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


def test_lines_without_overlap_share_a_lane() -> None:
    """
    Two segments without overlap share a lane, whatever their directions.

    C2 -> A2 goes left and C2 -> E2 goes right in the channel between C2
    and C3. The direction of travel orders only overlapping segments.

    Code: lane_assignment.assign_lanes,
    structure_routing._Router._column_lane_counts.
    Fails if:
    - segments of different directions never share a lane.
    """

    _, routing, _, _ = _result(_case("Lines to both sides share a lane"))

    assert (
        routing.lane_counts[
            StructureChannelId(ChannelKind.COLUMN, "Doc", index=2, gap=1)
        ]
        == 1
    )


def test_nested_opposite_segment_does_not_make_a_loop() -> None:
    """
    A nested segment of the other direction leaves right-hand traffic
    instead of crossing the outer segment twice.

    C2 -> A2 goes left over S inside A1 -> C1, which goes right. Both
    legs of C2 -> A2 go down. Right-hand traffic would put C2 -> A2 above
    A1 -> C1, so both legs would cross A1 -> C1. The ends are a stronger
    reason than the direction of travel.

    Code: lane_assignment.assign_lanes,
    lane_assignment._order_free_pairs_by_direction.
    Fails if:
    - right-hand traffic wins over the ends of a pair.
    """

    normalized_graph, _, _, paths = _result(
        _case("Relations inside one container")
    )

    assert (
        crossing_count(
            paths[_edge_id(normalized_graph, "A1", "C1")],
            paths[_edge_id(normalized_graph, "C2", "A2")],
        )
        == 0
    )


def test_shared_stretch_keeps_the_nested_route_inside() -> None:
    """
    A route nested in another on a shared stretch keeps its side on the
    whole stretch: in every channel and at the shared face.

    C2 -> A2 and A2 -> R2 share the top face of A2, the column channel above
    A2, the vertical channel left of S, and the top corridor. C2 -> A2 turns
    off earlier, so it stays inside. The same holds for C2 -> A2 and
    L2 -> C2 at the top face of C2. C1 -> C3 and C3 -> A3 only touch in the
    vertical channel left of C, so they share one channel only: the column
    channel above C3. That stretch of one channel follows the same rule.

    Code: structure_stretches.shared_stretch_orders,
    gate_ports.number_gate_ports, lane_assignment.assign_lanes.
    Fails if:
    - the rule is not applied.
    - the port order at the shared face does not follow the rule.
    - a stretch of one channel with lanes is not a stretch.
    """

    normalized_graph, _, _, paths = _result(_case("Steps beside a pocket"))

    def crossings(first: Tuple[str, str], second: Tuple[str, str]) -> int:
        return crossing_count(
            paths[_edge_id(normalized_graph, *first)],
            paths[_edge_id(normalized_graph, *second)],
        )

    assert crossings(("C2", "A2"), ("A2", "R2")) == 0
    assert crossings(("C2", "A2"), ("L2", "C2")) == 0
    assert crossings(("C3", "A3"), ("C1", "C3")) == 0


def test_channel_inside_a_longer_stretch_is_no_stretch_of_its_own() -> None:
    """
    Two routes that pass the same chain of channels have one shared stretch
    over the whole chain, not also a stretch for each of its channels.

    A separate stretch of one channel could order the pair against the
    stretch of the whole chain.

    Code: structure_stretches._common_runs.
    Fails if:
    - a single channel inside a longer stretch is a stretch of its own.
    """

    chain = (
        StructureChannelId(ChannelKind.BOTTOM_CORRIDOR, "Doc"),
        StructureChannelId(ChannelKind.VERTICAL, "Doc", 1),
        StructureChannelId(ChannelKind.TOP_CORRIDOR, "S"),
    )

    assert _common_runs(chain, chain) == [(0, 0, 3, 1)]
    assert _common_runs(chain, tuple(reversed(chain))) == [(0, 2, 3, -1)]


def test_shared_stretch_of_one_channel_under_the_columns() -> None:
    """
    A shared stretch of one channel under the columns follows the shared
    stretch rule.

    C2 -> A2 and B2 -> C2 run under the columns only; B2 -> C2 is nested.
    A1 -> S1 and S1 -> A1 also share the vertical channel left of S, but
    S1 -> A1 crosses it by a through pass, so only the space under A1 is
    shared. S1 -> A1 goes on straight past the through pass and turns off
    later, so A1 -> S1 is nested.

    Code: structure_stretches._common_runs,
    structure_stretches._trimmed_run, structure_stretches._route_end.
    Fails if:
    - a single common channel under the columns is not a stretch.
    - a stretch trimmed to one channel under the columns is dropped.
    - a through pass counts as the place where a route turns off.
    """

    for title_, first_, second_ in (
        ("Nested pair under the columns", ("C2", "A2"), ("B2", "C2")),
        (
            "One face: two relations out, an opposite line between",
            ("A1", "S1"),
            ("S1", "A1"),
        ),
    ):
        normalized_graph, _, _, paths = _result(_case(title_))
        assert (
            crossing_count(
                paths[_edge_id(normalized_graph, *first_)],
                paths[_edge_id(normalized_graph, *second_)],
            )
            == 0
        ), title_


def test_routes_that_turn_off_to_different_sides_keep_their_sides() -> None:
    """
    An end of a shared stretch where the routes turn off to different
    sides sets their order: each route lies on the side it turns to.

    A1 -> S2 and A2 -> S2 start in one column, so which one turns off
    earlier is not known. A1 -> S2 turns up to A1, A2 -> S2 turns down to
    A2, so A2 -> S2 lies below and the routes do not cross. In the other
    case, S1 -> C1 lies above both lines of C2: each line of C2 lies on the
    side of S1 -> C1 that its own ends require.

    Code: structure_stretches._nesting, lane_assignment.assign_lanes.
    Fails if:
    - an end where the routes turn off to different sides sets no order.
    - the direction of travel wins over the ends of a pair.
    """

    for title_, first_, second_ in (
        (
            "One face: relations out and in, a line between",
            ("A1", "S2"),
            ("A2", "S2"),
        ),
        (
            "One face: two relations out, an opposite line between",
            ("C2", "S2"),
            ("S1", "C1"),
        ),
    ):
        normalized_graph, _, _, paths = _result(_case(title_))
        assert (
            crossing_count(
                paths[_edge_id(normalized_graph, *first_)],
                paths[_edge_id(normalized_graph, *second_)],
            )
            == 0
        ), title_


def test_pair_that_must_cross_keeps_the_order_where_it_joins() -> None:
    """
    Two routes that go the same way and must cross keep the order of the
    end where they come together, and cross where they part.

    N1 -> T1, S3-1 -> T2, and N4 -> T3 come together in the top corridor
    of Section 1 and part at the column of T1, T2, T3. In the corridor,
    from the right of the travel direction (left): N4, S3-1, N1. After the
    turn down, the right of the travel direction is the left side, so the
    vertical channel holds them from left to right in the same order.

    Code: structure_stretches._nesting, structure_routing._turned_steps.
    Fails if:
    - a pair whose ends require different orders gets no order.
    - a step that is straight in the drawing drops the order of the pair.
    """

    normalized_graph, routing, _, _ = _result(
        _case("Document tree from the sketch")
    )

    def vertical_lane(source_id: str, target_id: str) -> int:
        route_ = routing.routes[
            _edge_id(normalized_graph, source_id, target_id)
        ]
        return next(
            lane_
            for channel_, lane_ in zip(route_.channels, route_.lanes)
            if channel_.kind is ChannelKind.VERTICAL
            and channel_.container_id is None
        )

    assert (
        vertical_lane("N4", "T3")
        < vertical_lane("S3-1", "T2")
        < vertical_lane("N1", "T1")
    )


def test_foreign_line_does_not_split_a_ribbon() -> None:
    """
    A foreign line passes two lines that run together from one side.

    There is no separate rule for this: the foreign line shares a stretch
    with each of the two lines, and each stretch keeps one order.

    C2 -> A2 and L2 -> C2 run side by side from the top face of C2 through
    the vertical channel left of C. C1 -> C3 goes down the same vertical
    channel and passes them from one side.

    In "One face: two relations out, a line between", C3 -> S1 and
    C3 -> S2 leave the top face of C3 to the left. C2 -> S2 crosses one of
    them. It runs above both in the channel between C2 and C3, and on one
    side of both in the vertical channel.

    Code: structure_stretches.shared_stretch_orders.
    Fails if:
    - a foreign line stays between two lines that run together.
    """

    normalized_graph, routing, _, _ = _result(
        _case("Relations inside one container, more ports")
    )

    def vertical_lane(source_id: str, target_id: str) -> int:
        route_ = routing.routes[
            _edge_id(normalized_graph, source_id, target_id)
        ]
        return next(
            lane_
            for channel_, lane_ in zip(route_.channels, route_.lanes)
            if channel_.kind is ChannelKind.VERTICAL and channel_.index == 4
        )

    ribbon = sorted((vertical_lane("C2", "A2"), vertical_lane("L2", "C2")))
    assert vertical_lane("C1", "C3") < ribbon[0]
    assert ribbon[1] - ribbon[0] == 1

    normalized_graph, _, _, paths = _result(
        _case("One face: two relations out, a line between")
    )

    def first_horizontal_y(source_id: str, target_id: str) -> float:
        return paths[_edge_id(normalized_graph, source_id, target_id)][1].y

    def first_vertical_x(source_id: str, target_id: str) -> float:
        return paths[_edge_id(normalized_graph, source_id, target_id)][2].x

    assert first_horizontal_y("C2", "S2") < min(
        first_horizontal_y("C3", "S1"), first_horizontal_y("C3", "S2")
    )
    ribbon_x = sorted(
        (first_vertical_x("C3", "S1"), first_vertical_x("C3", "S2"))
    )
    assert not ribbon_x[0] < first_vertical_x("C2", "S2") < ribbon_x[1]


def test_lane_order_decides_where_segments_under_the_columns_meet() -> None:
    """
    Two segments under the columns that meet take the order of their lanes.

    A2 -> L2 and L2 -> A2 run under the section U in opposite directions.
    L2 -> A2 can keep the height of its column channel lane, A2 -> L2 lies
    by the contour. Their heights are closer than one lane pitch. A2 -> L2
    goes left, so right-hand traffic puts it above. The pair does not make
    a loop.

    Code: structure_geometry._GeometryBuilder._bottom_corridor.
    Fails if:
    - the segments meet by height instead of by lane order.
    """

    normalized_graph, _, _, paths = _result(_case("Steps beside a pocket"))

    left = paths[_edge_id(normalized_graph, "A2", "L2")]
    right = paths[_edge_id(normalized_graph, "L2", "A2")]
    assert crossing_count(left, right) == 0


@pytest.mark.parametrize(
    "case", STRUCTURE_CASES, ids=[case_.title for case_ in STRUCTURE_CASES]
)
def test_segments_lie_on_the_lane_grid(case: GalleryCase) -> None:
    """
    Every segment between the port stubs lies on the grid of the lane pitch.

    All sizes of the layout are multiples of the lane pitch, so two parallel
    segments of one relation lie on one line or at least one lane pitch
    apart.

    Code: levels_geometry.GeometryConfig,
    levels_geometry.vertical_channel_size,
    structure_geometry.compute_structure_geometry.
    Fails if:
    - a size of the layout is not a multiple of the lane pitch.
    - the centered lanes of a vertical channel miss the grid.
    """

    _, _, geometry, paths = _result(case)

    assert off_grid_segments(paths, geometry.config.lane_pitch) == []


# One segment of a route in a channel: the start and the end of the
# segment, the lane, and whether its two legs go to the high side (down or
# right) or None if they go to different sides.
# Start, end, lane, the side of both legs if they go to one side, and each
# leg: (position along the channel, goes toward the high side).
_ChannelSegment = Tuple[
    Point, Point, int, Optional[bool], Tuple[Tuple[float, bool], ...]
]


@pytest.mark.parametrize(
    "case", _invariant_cases("test_structure_routes_follow_right_hand_traffic")
)
def test_structure_routes_follow_right_hand_traffic(case: GalleryCase) -> None:
    """
    In one channel, the lanes of both directions follow right-hand traffic.

    Of two overlapping segments of different directions, a horizontal one
    that goes left lies above the one that goes right, and a vertical one
    that goes up lies right of the one that goes down. The other order is
    allowed only where the ends require it: the segment is nested in the
    other one, in its channel or on a shared stretch, or the order of
    right-hand traffic would make a leg of the pair cross the other
    segment. Segments without overlap share lanes in any order.

    Code: lane_assignment._order_free_pairs_by_direction,
    structure_stretches.shared_stretch_orders.
    Fails if:
    - right-hand traffic is mirrored.
    - right-hand traffic wins over the ends of a pair.
    """

    normalized_graph, routing, geometry, _ = _result(case)
    stretch_inner_keys = _stretch_inner_keys(normalized_graph)

    # Channel -> segments that go toward the low side, toward the high side.
    directions: Dict[object, Tuple[List[_ChannelSegment], ...]] = {}
    for route_ in routing.routes.values():
        path_ = route_channel_points(route_, geometry)
        # Point i + 1 of the path starts the segment in channel i.
        for index_, (channel_, lane_) in enumerate(
            zip(route_.channels, route_.lanes)
        ):
            before_, start_ = path_[index_], path_[index_ + 1]
            end_, after_ = path_[index_ + 2], path_[index_ + 3]
            if start_ == end_:
                # A through pass.
                continue
            if channel_.is_horizontal:
                goes_low_ = end_.x < start_.x
                leg_list_ = (
                    (start_.x, before_.y > start_.y),
                    (end_.x, after_.y > end_.y),
                )
            else:
                goes_low_ = end_.y < start_.y
                leg_list_ = (
                    (start_.y, before_.x > start_.x),
                    (end_.y, after_.x > end_.x),
                )
            legs_ = {goes_high_ for _, goes_high_ in leg_list_}
            if (route_.edge_id, index_) in stretch_inner_keys:
                continue
            directions.setdefault(channel_, ([], []))[
                0 if goes_low_ else 1
            ].append(
                (
                    start_,
                    end_,
                    lane_,
                    legs_.pop() if len(legs_) == 1 else None,
                    leg_list_,
                )
            )
    for channel_, (low_, high_) in directions.items():
        is_horizontal_ = channel_.is_horizontal  # type: ignore[attr-defined]
        for first_ in low_:
            for second_ in high_:
                if not _spans_overlap(first_, second_, is_horizontal_):
                    # Segments without overlap may share a lane in any order.
                    continue
                # Left in the top half: smaller lanes. Up in the right half:
                # larger lanes.
                in_order_ = (
                    first_[2] < second_[2]
                    if is_horizontal_
                    else first_[2] > second_[2]
                )
                if not in_order_:
                    assert _traffic_order_crosses(
                        first_, second_, is_horizontal_
                    ) or any(
                        _is_nested(first_, outer_, is_horizontal_)
                        for outer_ in high_
                    ) or any(
                        _is_nested(second_, outer_, is_horizontal_)
                        for outer_ in low_
                    )


def _stretch_inner_keys(
    normalized_graph: NormalizedGraph,
) -> set[Tuple[str, int]]:
    """
    Return the segments that the shared stretch rule puts on a forced side.
    """

    layout = compute_structure_layout(normalized_graph)
    router = _Router(
        normalized_graph,
        layout,
        compute_structure_geometry(normalized_graph, layout),
        GeometryConfig(),
        RoutingOptions(),
    )
    router.route()
    return {
        order_.inner
        for orders_ in router.forced_orders.values()
        for order_ in orders_
    }


def _spans_overlap(
    first: _ChannelSegment, second: _ChannelSegment, is_horizontal: bool
) -> bool:
    def span(segment: _ChannelSegment) -> Tuple[float, float]:
        start_, end_ = segment[0], segment[1]
        values_ = (start_.x, end_.x) if is_horizontal else (start_.y, end_.y)
        return min(values_), max(values_)

    first_low, first_high = span(first)
    second_low, second_high = span(second)
    return first_low <= second_high and second_low <= first_high


def _traffic_order_crosses(
    low: _ChannelSegment, high: _ChannelSegment, is_horizontal: bool
) -> bool:
    """
    Return True if the order of right-hand traffic makes a leg of one
    segment cross the other one.

    low goes toward the low side of the channel, high toward the high side.
    Right-hand traffic puts low on the low side of high in a horizontal
    channel (above) and on the high side in a vertical channel (right).
    """

    def span(segment: _ChannelSegment) -> Tuple[float, float]:
        start_, end_ = segment[0], segment[1]
        values_ = (start_.x, end_.x) if is_horizontal else (start_.y, end_.y)
        return min(values_), max(values_)

    low_on_high_side = not is_horizontal
    high_low, high_high = span(high)
    low_low, low_high = span(low)
    # Two legs at one point that go to different sides: the order of
    # right-hand traffic would lay them on top of each other.
    if any(
        low_position_ == high_position_ and low_goes_ != high_goes_
        for low_position_, low_goes_ in low[4]
        for high_position_, high_goes_ in high[4]
    ):
        return True
    return any(
        high_low < position_ < high_high and goes_high_ != low_on_high_side
        for position_, goes_high_ in low[4]
    ) or any(
        low_low < position_ < low_high and goes_high_ == low_on_high_side
        for position_, goes_high_ in high[4]
    )


def _is_nested(
    inner: _ChannelSegment, outer: _ChannelSegment, is_horizontal: bool
) -> bool:
    def span(segment: _ChannelSegment) -> Tuple[float, float]:
        start_, end_ = segment[0], segment[1]
        values_ = (start_.x, end_.x) if is_horizontal else (start_.y, end_.y)
        return min(values_), max(values_)

    inner_low, inner_high = span(inner)
    outer_low, outer_high = span(outer)
    return (
        inner[3] is not None
        and outer_low < inner_low
        and inner_high < outer_high
    )


@pytest.mark.parametrize(
    "case", _invariant_cases("test_structure_route_invariants")
)
def test_structure_route_invariants(case: GalleryCase) -> None:
    """
    Result invariants of the structure mode routes on every structure case.

    Code: structure_routing.compute_structure_routing,
    structure_paths.compute_structure_edge_paths.
    Fails if:
    - a route passes through a node or through a container that does not
      hold its endpoints.
    - a route crosses the top or the bottom edge of a container frame, or
      crosses a side face at the height of the header.
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
    for container_id_, header_ in geometry.header_rects.items():
        frame_ = geometry.node_rects[container_id_]
        for path_ in paths.values():
            for start_, end_ in zip(path_, path_[1:]):
                if start_.x == end_.x and frame_.x < start_.x < (
                    frame_.x + frame_.width
                ):
                    low_, high_ = sorted((start_.y, end_.y))
                    for edge_y_ in (frame_.y, frame_.y + frame_.height):
                        assert not low_ < edge_y_ < high_
                if start_.y == end_.y and frame_.y < start_.y < (
                    frame_.y + frame_.height
                ):
                    low_, high_ = sorted((start_.x, end_.x))
                    for face_x_ in (frame_.x, frame_.x + frame_.width):
                        if low_ < face_x_ < high_:
                            assert start_.y > header_.y + header_.height
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


@pytest.mark.parametrize(
    "case", STRUCTURE_CASES, ids=[case_.title for case_ in STRUCTURE_CASES]
)
def test_bottom_corridor_invariants(case: GalleryCase) -> None:
    """
    Invariants of the segments under the columns on every structure case.

    A segment that continues a lane straight, or a segment under the
    columns of a section across its side face, belongs to a row. The other
    segments form the corridor.

    Code: structure_geometry._GeometryBuilder._bottom_corridor,
    structure_geometry._free_y.
    Fails if:
    - a segment lies closer than the clearance to a column above it.
    - two overlapping segments lie closer than one lane pitch.
    - of two overlapping corridor segments, the larger lane does not lie
      lower.
    """

    normalized_graph, routing, geometry, _ = _result(case)

    config = geometry.config
    lines = geometry.bottom_segment_lines
    in_corridor = {
        segment_.key: not _belongs_to_a_row(
            routing, geometry, segment_.key
        )
        for segment_ in routing.bottom_segments
    }
    for segment_ in routing.bottom_segments:
        low_, high_, y_ = lines[segment_.key]
        for node_ in normalized_graph.nodes:
            if normalized_graph.parent_ids[node_.node_id] != (
                segment_.container_id
            ):
                continue
            rect_ = geometry.node_rects[node_.node_id]
            if low_ < rect_.x + rect_.width and high_ > rect_.x:
                assert y_ >= rect_.y + rect_.height + config.lane_clearance
        for other_ in routing.bottom_segments:
            other_low_, other_high_, other_y_ = lines[other_.key]
            if (
                other_.key == segment_.key
                or other_.container_id != segment_.container_id
                or high_ < other_low_
                or other_high_ < low_
            ):
                continue
            assert abs(other_y_ - y_) >= config.lane_pitch
            if (
                in_corridor[segment_.key]
                and in_corridor[other_.key]
                and other_.lane > segment_.lane
            ):
                assert other_y_ > y_


def _belongs_to_a_row(
    routing: StructureRouting,
    geometry: StructureGeometry,
    key: Tuple[str, int],
) -> bool:
    """
    Return True if a segment under the columns belongs to a row.

    The segment continues straight, at the same height, a column channel
    lane, a top corridor lane, or a segment under the columns of a section
    across its side face.
    """

    edge_id, position = key
    route = routing.routes[edge_id]
    points = route_channel_points(route, geometry)
    container_id = route.channels[position].container_id

    def continues(other: int) -> bool:
        channel_ = route.channels[other]
        return channel_.kind in (
            ChannelKind.COLUMN,
            ChannelKind.TOP_CORRIDOR,
        ) or (
            channel_.kind is ChannelKind.BOTTOM_CORRIDOR
            and channel_.container_id != container_id
        )

    # Point i + 1 starts the segment in channel i.
    return any(
        0 <= other_ < len(route.channels)
        and continues(other_)
        and points[other_ + 1].y == points[position + 1].y
        for other_ in (position - 2, position + 2)
    )


@pytest.mark.parametrize(
    "case", _invariant_cases("test_column_lane_count_rule_matches_the_lanes")
)
def test_column_lane_count_rule_matches_the_lanes(case: GalleryCase) -> None:
    """
    The lane count of each column channel, known right after the routes are
    chosen, equals the count that the lane assignment gives.

    The routing takes the exact heights of the columns from this rule.

    Code: structure_routing._Router._column_lane_counts.
    Fails if:
    - the rule counts the lanes of the two sides of a half separately.
    - the lane assignment stops sharing lanes between the two sides.
    """

    normalized_graph = normalize_graph(case.graph)
    layout = compute_structure_layout(normalized_graph)
    router = _Router(
        normalized_graph,
        layout,
        compute_structure_geometry(normalized_graph, layout),
        GeometryConfig(),
        RoutingOptions(),
    )
    plans = [
        plan_
        for plan_ in (
            router._plan(index_, edge_)
            for index_, edge_ in enumerate(normalized_graph.edges)
        )
        if plan_ is not None
    ]
    expected = router._column_lane_counts(plans, router._straight_ids(plans))
    routing = compute_structure_routing(normalized_graph, layout)
    assert expected == {
        channel_: count_
        for channel_, count_ in routing.lane_counts.items()
        if channel_.kind is ChannelKind.COLUMN
    }


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
