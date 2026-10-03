"""
Shared stretches of the structure mode routes.

spec.md, section "Общий участок", defines the rule. Two routes that pass the
same chain of channels one after another run side by side. A route nested in
the other keeps its side on the whole stretch. This module finds the nested
pairs and returns their lane orders and their port orders.
"""

from typing import Dict, List, Optional, Protocol, Sequence, Tuple

from strictdoc.features.specification_graph.svg_graph.gate_ports import (
    EndpointKey,
    Face,
    ForcedPortOrder,
)
from strictdoc.features.specification_graph.svg_graph.lane_assignment import (
    ForcedOrder,
)
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    Rect,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedEdge,
)
from strictdoc.features.specification_graph.svg_graph.structure_geometry import (
    StructureGeometry,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    ChannelKind,
    StructureChannelId,
)

# The role of an endpoint in its key: see gate_ports.EndpointKey.
_SOURCE = 0
_TARGET = 1


class PlannedRoute(Protocol):
    """
    A route with its channels and the level of each channel.

    The level is the y of a horizontal segment or the x of a vertical one.
    """

    @property
    def index(self) -> int: ...

    @property
    def edge(self) -> NormalizedEdge: ...

    @property
    def source_face(self) -> Face: ...

    @property
    def target_face(self) -> Face: ...

    @property
    def channels(self) -> Tuple[StructureChannelId, ...]: ...

    @property
    def levels(self) -> Tuple[float, ...]: ...


_Point = Tuple[float, float]


def shared_stretch_orders(
    plans: Sequence[PlannedRoute], exact: StructureGeometry
) -> Tuple[Dict[StructureChannelId, List[ForcedOrder]], List[ForcedPortOrder]]:
    """
    Return the forced lane orders of the nested pairs on shared stretches.

    This function is the only place of the rule for the stretches of two or
    more channels, and for the stretches of one channel under the columns.
    spec.md, section "Общий участок". A shared stretch is the
    longest chain of channels that two routes pass one after another, in
    the same direction or toward each other. A route is nested in the other
    if at both ends of the stretch it turns off earlier and to the same
    side. An end where both routes reach the same face of the same node sets
    no condition. A nested route keeps its side on the whole stretch: in
    each channel of the stretch, it takes the lane on that side of the
    other route, and on a face where the stretch ends, its port stands on
    that side.

    The stretches of one channel with lanes follow the same rule in
    lane_assignment._yield_to_nesting. Under the columns, the segments have
    no lanes of their own, so this function serves those stretches too.
    """

    points = {plan_.index: _plan_points(plan_, exact) for plan_ in plans}
    result: Dict[StructureChannelId, List[ForcedOrder]] = {}
    port_orders: List[ForcedPortOrder] = []
    for first_index_, first_ in enumerate(plans):
        for second_ in plans[first_index_ + 1 :]:
            first_points_ = points[first_.index]
            second_points_ = points[second_.index]
            # Different runs can trim to the same stretch of one channel
            # under the columns. Each stretch counts once.
            stretches_ = []
            for run_ in _common_runs(first_.channels, second_.channels):
                trimmed_ = _trimmed_run(
                    first_, first_points_, second_points_, run_
                )
                if trimmed_ is not None and trimmed_ not in stretches_:
                    stretches_.append(trimmed_)
            for stretch_ in stretches_:
                _add_stretch_orders(
                    first_,
                    second_,
                    first_points_,
                    second_points_,
                    stretch_,
                    result,
                    port_orders,
                )
    return result, port_orders


def _plan_points(plan: PlannedRoute, exact: StructureGeometry) -> List[_Point]:
    """
    Return the polyline of a plan: the ports and one point per channel.

    Point i + 1 starts the segment in channel i.
    """

    source = exact.node_rects[plan.edge.source_id]
    target = exact.node_rects[plan.edge.target_id]
    x = _center_x(source)
    y = source.y if plan.source_face is Face.TOP else source.y + source.height
    result = [(x, y)]
    for channel_, level_ in zip(plan.channels, plan.levels):
        if channel_.is_horizontal:
            y = level_
        else:
            x = level_
        result.append((x, y))
    target_x = _center_x(target)
    result.append((target_x, y))
    result.append(
        (
            target_x,
            target.y
            if plan.target_face is Face.TOP
            else target.y + target.height,
        )
    )
    return result


def _common_runs(
    first: Tuple[StructureChannelId, ...],
    second: Tuple[StructureChannelId, ...],
) -> List[Tuple[int, int, int, int]]:
    """
    Return the maximal common runs of two or more channels.

    A run is (start in first, start in second, length, step in second). The
    step is 1 for the same direction and -1 for routes toward each other.
    A single common channel under the columns is a run too, with both
    steps: _trimmed_run picks the step by the travel directions.
    """

    result = []
    for first_start_ in range(len(first)):
        for second_start_ in range(len(second)):
            for step_ in (1, -1):
                previous_ = second_start_ - step_
                if (
                    first_start_ > 0
                    and 0 <= previous_ < len(second)
                    and first[first_start_ - 1] == second[previous_]
                ):
                    continue
                length_ = 0
                while (
                    first_start_ + length_ < len(first)
                    and 0 <= second_start_ + step_ * length_ < len(second)
                    and first[first_start_ + length_]
                    == second[second_start_ + step_ * length_]
                ):
                    length_ += 1
                if length_ >= 2 or (
                    length_ == 1
                    and first[first_start_].kind is ChannelKind.BOTTOM_CORRIDOR
                ):
                    result.append((first_start_, second_start_, length_, step_))
    return result


# A common run of channels: start in the first route, start in the second
# route, length, step in the second route (1 or -1).
_Run = Tuple[int, int, int, int]

# A face where a stretch ends: the endpoint of the first route, the endpoint
# of the second route, the travel direction of the first route at the face.
_StretchFace = Tuple[EndpointKey, EndpointKey, Tuple[int, int]]


def _add_stretch_orders(
    first: PlannedRoute,
    second: PlannedRoute,
    first_points: List[_Point],
    second_points: List[_Point],
    run: _Run,
    result: Dict[StructureChannelId, List[ForcedOrder]],
    port_orders: List[ForcedPortOrder],
) -> None:
    nesting = _nesting(first, second, first_points, second_points, run)
    if nesting is None:
        return
    inner, side, faces = nesting
    for first_key_, second_key_, direction_ in faces:
        inner_key_, outer_key_ = (
            (first_key_, second_key_)
            if inner is first
            else (second_key_, first_key_)
        )
        port_orders.append(
            ForcedPortOrder(
                inner=inner_key_,
                outer=outer_key_,
                # The right side of the travel direction at the face.
                inner_is_right=-direction_[1] * side > 0,
            )
        )
    first_start, second_start, length, step = run
    for offset_ in range(length):
        first_position_ = first_start + offset_
        second_position_ = second_start + step * offset_
        channel_ = first.channels[first_position_]
        direction_ = _direction(
            first_points[first_position_ + 1], first_points[first_position_ + 2]
        )
        if direction_ == (0, 0):
            continue
        # The right side of the travel direction, in screen coordinates.
        normal_x_, normal_y_ = -direction_[1], direction_[0]
        first_key_ = (first.edge.edge_id, first_position_)
        second_key_ = (second.edge.edge_id, second_position_)
        inner_key_, outer_key_ = (
            (first_key_, second_key_)
            if inner is first
            else (second_key_, first_key_)
        )
        result.setdefault(channel_, []).append(
            ForcedOrder(
                inner=inner_key_,
                outer=outer_key_,
                inner_is_later=(
                    normal_y_ if channel_.is_horizontal else normal_x_
                )
                * side
                > 0,
            )
        )


def _trimmed_run(
    first: PlannedRoute,
    first_points: List[_Point],
    second_points: List[_Point],
    run: _Run,
) -> Optional[_Run]:
    """
    Return the run without the end channels where the segments only touch.

    The routes run side by side only where their segments overlap. Return
    None if fewer than two channels remain, unless the one channel left lies
    under the columns.
    """

    first_start, second_start, length, step = run

    def overlap(offset: int) -> float:
        first_position_ = first_start + offset
        second_position_ = second_start + step * offset
        axis_ = 0 if first.channels[first_position_].is_horizontal else 1
        first_span_ = sorted(
            (
                first_points[first_position_ + 1][axis_],
                first_points[first_position_ + 2][axis_],
            )
        )
        second_span_ = sorted(
            (
                second_points[second_position_ + 1][axis_],
                second_points[second_position_ + 2][axis_],
            )
        )
        return min(first_span_[1], second_span_[1]) - max(
            first_span_[0], second_span_[0]
        )

    while length > 0 and overlap(0) <= 0:
        first_start += 1
        second_start += step
        length -= 1
    while length > 0 and overlap(length - 1) <= 0:
        length -= 1
    if length == 1 and (
        first.channels[first_start].kind is ChannelKind.BOTTOM_CORRIDOR
    ):
        # One channel does not tell by itself whether the routes go the
        # same way or toward each other: the travel directions do.
        same_way = _direction(
            first_points[first_start + 1], first_points[first_start + 2]
        ) == _direction(
            second_points[second_start + 1], second_points[second_start + 2]
        )
        return first_start, second_start, 1, 1 if same_way else -1
    if length < 2:
        return None
    return first_start, second_start, length, step


def _nesting(
    first: PlannedRoute,
    second: PlannedRoute,
    first_points: List[_Point],
    second_points: List[_Point],
    run: _Run,
) -> Optional[Tuple[PlannedRoute, int, List[_StretchFace]]]:
    """
    Return the inner route, its side, and the faces where the stretch ends.

    The side is 1 for the right of the travel direction of the first route,
    -1 for the left. Return None if the routes are not nested.

    Each end of the stretch sets a condition: a route lies on one side of
    the other. Where the routes turn off to different sides, each lies on
    the side it turns to. Where they turn off to the same side, the route
    that turns off earlier lies on that side. The routes are nested if the
    conditions of both ends agree.
    """

    first_start, second_start, length, step = run
    first_end = first_start + length - 1
    second_end = second_start + step * (length - 1)
    # Each end that sets a condition: (a route or None if the end sets no
    # order, the side of the other route where this route lies).
    conditions: List[Tuple[Optional[PlannedRoute], int]] = []
    faces: List[_StretchFace] = []
    for at_finish_ in (False, True):
        first_position_ = first_end if at_finish_ else first_start
        second_position_ = second_end if at_finish_ else second_start
        second_looks_up_ = at_finish_ == (step == 1)
        # The travel direction of the first route in this channel.
        direction_ = _direction(
            first_points[first_position_ + 1], first_points[first_position_ + 2]
        )
        if direction_ == (0, 0):
            return None
        first_end_ = _route_end(first_points, first_position_, at_finish_)
        second_end_ = _route_end(
            second_points, second_position_, second_looks_up_
        )
        if _same_face(
            first,
            first_position_,
            at_finish_,
            second,
            second_position_,
            second_looks_up_,
        ):
            face_start_, face_end_ = (
                (first_end_[0], first_end_[1])
                if at_finish_
                else (first_end_[1], first_end_[0])
            )
            faces.append(
                (
                    (first.edge.edge_id, _TARGET if at_finish_ else _SOURCE),
                    (
                        second.edge.edge_id,
                        _TARGET if second_looks_up_ else _SOURCE,
                    ),
                    _direction(face_start_, face_end_),
                )
            )
            continue
        first_turn_ = _side(direction_, first_end_[0], first_end_[1])
        second_turn_ = _side(direction_, second_end_[0], second_end_[1])
        if first_turn_ != 0 and second_turn_ == -first_turn_:
            # The routes turn off to different sides. In this order they
            # do not cross at this end, wherever each of them turns.
            conditions.append((first, first_turn_))
            continue
        first_along_ = _dot(first_end_[0], direction_)
        second_along_ = _dot(second_end_[0], direction_)
        if first_along_ == second_along_:
            conditions.append((None, 0))
            continue
        # At the finish, the earlier turn is closer to the start.
        first_is_earlier_ = (first_along_ < second_along_) == at_finish_
        earlier_ = first_end_ if first_is_earlier_ else second_end_
        conditions.append(
            (
                first if first_is_earlier_ else second,
                _side(direction_, earlier_[0], earlier_[1]),
            )
        )
    if len(conditions) == 0 or any(
        route_ is None or side_ == 0 for route_, side_ in conditions
    ):
        return None
    # The side where the first route lies, from each condition.
    first_sides = {
        side_ if route_ is first else -side_ for route_, side_ in conditions
    }
    if len(first_sides) != 1:
        return None
    first_side = first_sides.pop()
    # The inner route is the one that turns off earlier, if an end tells.
    inner = first
    for route_, _ in conditions:
        if route_ is not None and route_ is not first:
            inner = route_
            break
    return inner, first_side if inner is first else -first_side, faces


def _route_end(
    points: List[_Point], position: int, looks_up: bool
) -> Tuple[_Point, _Point]:
    """
    Return the point where a route leaves a stretch and the next point.

    looks_up: the route leaves toward its later channels.

    A through pass is a segment of zero length: the route goes on straight
    past it, so it leaves the stretch where it really turns.
    """

    step = 1 if looks_up else -1
    index = position + 2 if looks_up else position + 1
    while (
        0 <= index + 3 * step < len(points)
        and points[index + step] == points[index]
    ):
        index += 2 * step
    return points[index], points[index + step]


def _same_face(
    first: PlannedRoute,
    first_position: int,
    first_looks_up: bool,
    second: PlannedRoute,
    second_position: int,
    second_looks_up: bool,
) -> bool:
    def face(
        plan: PlannedRoute, position: int, looks_up: bool
    ) -> Optional[Tuple[str, Face]]:
        if looks_up and position == len(plan.channels) - 1:
            return plan.edge.target_id, plan.target_face
        if not looks_up and position == 0:
            return plan.edge.source_id, plan.source_face
        return None

    first_face = face(first, first_position, first_looks_up)
    return first_face is not None and first_face == face(
        second, second_position, second_looks_up
    )


def _direction(start: _Point, end: _Point) -> Tuple[int, int]:
    return (
        (end[0] > start[0]) - (end[0] < start[0]),
        (end[1] > start[1]) - (end[1] < start[1]),
    )


def _dot(point: _Point, direction: Tuple[int, int]) -> float:
    return point[0] * direction[0] + point[1] * direction[1]


def _side(direction: Tuple[int, int], end: _Point, after: _Point) -> int:
    """
    Return the side of a turn relative to the travel direction.

    1 is the right side, -1 the left side, in screen coordinates.
    """

    turn_x = after[0] - end[0]
    turn_y = after[1] - end[1]
    cross = direction[0] * turn_y - direction[1] * turn_x
    return (cross > 0) - (cross < 0)


def _center_x(rect: Rect) -> float:
    return rect.x + rect.width / 2
