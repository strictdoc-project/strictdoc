from typing import Dict, List, Mapping, Optional, Tuple

import pytest

from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CASES,
    GalleryCase,
)
from strictdoc.features.specification_graph.svg_graph.gate_ports import Face
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
    compute_structure_geometry,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    ChannelKind,
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
from tests.unit.strictdoc.features.specification_graph.svg_graph.geometry_checks import (
    crossing_count,
    geometry_problems,
    off_grid_segments,
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
        normalized_graph,
        layout,
        lane_counts=routing.lane_counts,
        bottom_segments=routing.bottom_segments,
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


def test_line_enters_the_outer_vertical_channel_of_a_section() -> None:
    """
    A line crosses a side face straight and turns in the outer vertical
    channel of the section behind it.

    A1 -> X1 goes from the space under A1 into the section L1 at the same
    height and turns down in the left vertical channel of L1. It does not
    climb to the top corridor of L1 first.

    Code: structure_routing._side_face_links,
    structure_routing._Router._turn_fits, structure_routing._Router._face_x.
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
    right = paths[_edge_id(normalized_graph, "B2", "C2")]
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


def test_nested_opposite_segment_does_not_make_a_loop() -> None:
    """
    A nested segment of the other direction leaves right-hand traffic
    instead of crossing the outer segment twice.

    C2 -> A2 goes left over S inside A1 -> C1, which goes right. Both
    legs of C2 -> A2 go down. Right-hand traffic would put C2 -> A2 above
    A1 -> C1, so both legs would cross A1 -> C1.

    Code: lane_assignment._yield_to_nesting.
    Fails if:
    - right-hand traffic puts the nested segment on the side of the loop.
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
    vertical channel left of C, so they share one channel only.

    Code: structure_stretches.shared_stretch_orders,
    gate_ports.number_gate_ports, lane_assignment.assign_lanes.
    Fails if:
    - the rule is not applied.
    - the port order at the shared face does not follow the rule.
    """

    normalized_graph, _, _, paths = _result(_case("Steps beside a pocket"))

    def crossings(first: Tuple[str, str], second: Tuple[str, str]) -> int:
        return crossing_count(
            paths[_edge_id(normalized_graph, *first)],
            paths[_edge_id(normalized_graph, *second)],
        )

    assert crossings(("C2", "A2"), ("A2", "R2")) == 0
    assert crossings(("C2", "A2"), ("L2", "C2")) == 0
    assert crossings(("C3", "A3"), ("C1", "C3")) == 1


def test_foreign_line_does_not_split_a_ribbon() -> None:
    """
    A foreign line passes a ribbon from one side, if this costs no crossing.

    C2 -> A2 and L2 -> C2 run side by side from the top face of C2 through
    the vertical channel left of C. C1 -> C3 goes down the same vertical
    channel. It crosses both lines in either order, so it takes the side of
    the smaller lanes and the two lines of C2 stay together.

    Code: lane_assignment._keep_ribbons.
    Fails if:
    - a foreign line with free orders stays between the lines of a ribbon.
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
_ChannelSegment = Tuple[Point, Point, int, Optional[bool]]


@pytest.mark.parametrize(
    "case", STRUCTURE_CASES, ids=[case_.title for case_ in STRUCTURE_CASES]
)
def test_structure_routes_follow_right_hand_traffic(case: GalleryCase) -> None:
    """
    In one channel, the lanes of both directions follow right-hand traffic.

    A horizontal lane that goes left lies above a lane that goes right. A
    vertical lane that goes up lies right of a lane that goes down. Only a
    segment nested in a segment of the other direction, in its channel or on
    a shared stretch, may leave its half.

    Code: structure_routing._Router._assign_horizontal_lanes,
    structure_routing._Router._assign_vertical_lanes,
    lane_assignment._yield_to_nesting,
    structure_stretches.shared_stretch_orders.
    Fails if:
    - the halves of a horizontal or a vertical channel are swapped.
    - a segment that is not nested leaves its half.
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
                legs_ = {before_.y > start_.y, after_.y > end_.y}
            else:
                goes_low_ = end_.y < start_.y
                legs_ = {before_.x > start_.x, after_.x > end_.x}
            if (route_.edge_id, index_) in stretch_inner_keys:
                continue
            directions.setdefault(channel_, ([], []))[
                0 if goes_low_ else 1
            ].append(
                (start_, end_, lane_, legs_.pop() if len(legs_) == 1 else None)
            )
    for channel_, (low_, high_) in directions.items():
        is_horizontal_ = channel_.is_horizontal  # type: ignore[attr-defined]
        for first_ in low_:
            for second_ in high_:
                # Left in the top half: smaller lanes. Up in the right half:
                # larger lanes.
                in_order_ = (
                    first_[2] < second_[2]
                    if is_horizontal_
                    else first_[2] > second_[2]
                )
                if not in_order_:
                    assert any(
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

    A segment that continues a column channel lane straight belongs to the
    row of that lane. The other segments form the corridor.

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
        segment_.key: not _continues_a_column_lane(
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


def _continues_a_column_lane(
    routing: StructureRouting,
    geometry: StructureGeometry,
    key: Tuple[str, int],
) -> bool:
    edge_id, position = key
    route = routing.routes[edge_id]
    points = route_channel_points(route, geometry)
    # Point i + 1 starts the segment in channel i.
    return any(
        0 <= other_ < len(route.channels)
        and route.channels[other_].kind is ChannelKind.COLUMN
        and points[other_ + 1].y == points[position + 1].y
        for other_ in (position - 2, position + 2)
    )


@pytest.mark.parametrize(
    "case", STRUCTURE_CASES, ids=[case_.title for case_ in STRUCTURE_CASES]
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
