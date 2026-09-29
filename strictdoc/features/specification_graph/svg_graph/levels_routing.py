"""
Stages 3 and 4 of the graph generator for the levels mode.

Stage 3 selects the channels of each route. Stage 4 orders the ports on the
node faces and assigns a lane to each route segment. Both stages use no pixel
geometry. spec.md, section "Маршруты", defines the rules.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Mapping, Optional, Set, Tuple

from strictdoc.features.specification_graph.svg_graph.levels_structure import (
    LevelsStructure,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedGraph,
)


class LaneConflictPriority(Enum):
    """
    Which crossing to avoid when a segment lies inside another one.

    ENTRY keeps the entry verticals uncrossed. EXIT keeps the exit verticals
    uncrossed. See open question 22 in spec.md.
    """

    ENTRY = "entry"
    EXIT = "exit"


class SkipChannelChoice(Enum):
    """
    Which vertical channel an edge across levels uses.

    See open question 25 in spec.md.
    """

    NEAR_SOURCE = "near_source"
    NEAR_TARGET = "near_target"


@dataclass(frozen=True)
class RoutingOptions:
    lane_conflict_priority: LaneConflictPriority = LaneConflictPriority.ENTRY
    skip_channel_choice: SkipChannelChoice = SkipChannelChoice.NEAR_SOURCE


class Face(Enum):
    TOP = "top"
    BOTTOM = "bottom"


class Orientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass(frozen=True)
class ChannelId:
    """
    A routing channel.

    Horizontal channel H(r) lies below row r. H(-1) lies above the first row.
    Vertical channel V(c) lies right of column c. V(-1) lies left of the
    first column.
    """

    orientation: Orientation
    index: int


@dataclass(frozen=True)
class Port:
    node_id: str
    face: Face
    # Position on the face relative to the center: 0 is the center, negative
    # values are left of the center.
    slot: int


@dataclass(frozen=True)
class LaneRef:
    channel: ChannelId
    # Lanes count from the top of a horizontal channel and from the left of a
    # vertical channel.
    lane: int


@dataclass(frozen=True)
class EdgeRoute:
    edge_id: str
    source_port: Port
    target_port: Port
    # Lanes in route order. A straight edge has no lanes. An edge between
    # adjacent levels has one horizontal lane. An edge across levels has a
    # horizontal, a vertical, and a horizontal lane.
    lanes: Tuple[LaneRef, ...]


@dataclass(frozen=True)
class LaneConflict:
    """
    Two segments with an unavoidable crossing.

    The inner segment lies inside the outer segment and runs in the same
    direction. The priority option decides which vertical of the inner
    segment the outer segment crosses.
    """

    channel: ChannelId
    outer_edge_id: str
    inner_edge_id: str


@dataclass(frozen=True)
class LevelsRouting:
    options: RoutingOptions
    routes: Mapping[str, EdgeRoute]
    lane_counts: Mapping[ChannelId, int]
    conflicts: Tuple[LaneConflict, ...]


def compute_levels_routing(
    normalized_graph: NormalizedGraph,
    structure: LevelsStructure,
    options: Optional[RoutingOptions] = None,
) -> LevelsRouting:
    if options is None:
        options = RoutingOptions()
    plans = [
        _plan_edge(
            index_,
            edge_.edge_id,
            edge_.source_id,
            edge_.target_id,
            structure,
            options,
        )
        for index_, edge_ in enumerate(normalized_graph.edges)
    ]

    conflicts: List[LaneConflict] = []
    vertical_lanes = _assign_vertical_lanes(plans, options, conflicts)
    ports = _assign_ports(plans, vertical_lanes)
    horizontal_lanes = _assign_horizontal_lanes(
        plans, ports, vertical_lanes, options, conflicts
    )

    routes: Dict[str, EdgeRoute] = {}
    lane_counts: Dict[ChannelId, int] = {}
    for lane_ref_ in [
        *vertical_lanes.values(),
        *horizontal_lanes.values(),
    ]:
        lane_counts[lane_ref_.channel] = max(
            lane_counts.get(lane_ref_.channel, 0), lane_ref_.lane + 1
        )
    for plan_ in plans:
        lanes_: List[LaneRef] = []
        first_lane_ = horizontal_lanes.get((plan_.edge_id, 0))
        if first_lane_ is not None:
            lanes_.append(first_lane_)
        if plan_.vertical_channel is not None:
            lanes_.append(vertical_lanes[plan_.edge_id])
            lanes_.append(horizontal_lanes[(plan_.edge_id, 1)])
        routes[plan_.edge_id] = EdgeRoute(
            edge_id=plan_.edge_id,
            source_port=ports[(plan_.edge_id, _SOURCE)],
            target_port=ports[(plan_.edge_id, _TARGET)],
            lanes=tuple(lanes_),
        )
    return LevelsRouting(
        options=options,
        routes=routes,
        lane_counts=lane_counts,
        conflicts=tuple(conflicts),
    )


# Keys of the two endpoints of an edge.
_SOURCE = 0
_TARGET = 1

# Logical position along a channel. A node in column c has the position
# (2c + 1, port slot). A lane of vertical channel V(k) has the position
# (2k + 2, lane). Tuples compare in this order from left to right.
_Position = Tuple[int, int]


@dataclass(frozen=True)
class _EdgePlan:
    index: int
    edge_id: str
    source_id: str
    target_id: str
    goes_up: bool
    source_row: int
    target_row: int
    source_column: int
    target_column: int
    # Horizontal channel next to the source and next to the target. The
    # channels are equal for adjacent levels.
    source_channel: int
    target_channel: int
    vertical_channel: Optional[int]

    @property
    def source_face(self) -> Face:
        return Face.TOP if self.goes_up else Face.BOTTOM

    @property
    def target_face(self) -> Face:
        return Face.BOTTOM if self.goes_up else Face.TOP


def _plan_edge(
    index: int,
    edge_id: str,
    source_id: str,
    target_id: str,
    structure: LevelsStructure,
    options: RoutingOptions,
) -> _EdgePlan:
    source_position = structure.positions[source_id]
    target_position = structure.positions[target_id]
    source_row = source_position.row
    target_row = target_position.row
    if source_row == target_row:
        raise ValueError(
            f"Edge {edge_id} connects nodes on the same row: {source_row}."
        )
    goes_up = source_row > target_row
    if goes_up:
        source_channel = source_row - 1
        target_channel = target_row
    else:
        source_channel = source_row
        target_channel = target_row - 1

    vertical_channel: Optional[int] = None
    if abs(source_row - target_row) > 1:
        vertical_channel = _choose_vertical_channel(
            source_position.column, target_position.column, options
        )
    return _EdgePlan(
        index=index,
        edge_id=edge_id,
        source_id=source_id,
        target_id=target_id,
        goes_up=goes_up,
        source_row=source_row,
        target_row=target_row,
        source_column=source_position.column,
        target_column=target_position.column,
        source_channel=source_channel,
        target_channel=target_channel,
        vertical_channel=vertical_channel,
    )


def _choose_vertical_channel(
    source_column: int, target_column: int, options: RoutingOptions
) -> int:
    if source_column == target_column:
        # The channel left of the column. An upward line left of a node
        # passes the node clockwise.
        return source_column - 1
    if options.skip_channel_choice is SkipChannelChoice.NEAR_SOURCE:
        if target_column > source_column:
            return source_column
        return source_column - 1
    if target_column > source_column:
        return target_column - 1
    return target_column


@dataclass(frozen=True)
class _CrossMember:
    """
    A perpendicular part of a route that touches a segment.

    For a horizontal segment, the members are its entry and exit verticals.
    For a vertical segment, the members are its entry and exit horizontals.
    """

    position: _Position
    # The member extends from the segment lane toward the high side of the
    # channel: the bottom of a horizontal channel or the right of a vertical
    # channel.
    to_high_side: bool
    is_entry: bool


@dataclass(frozen=True)
class _Segment:
    key: Tuple[str, int]
    edge_id: str
    low: _Position
    high: _Position
    # Half 0 comes first: the top half of a horizontal channel or the left
    # half of a vertical channel.
    half: int
    members: Tuple[_CrossMember, _CrossMember]
    order_key: Tuple[_Position, int]


def _assign_vertical_lanes(
    plans: List[_EdgePlan],
    options: RoutingOptions,
    conflicts: List[LaneConflict],
) -> Dict[str, LaneRef]:
    segments_by_channel: Dict[int, List[_Segment]] = {}
    for plan_ in plans:
        if plan_.vertical_channel is None:
            continue
        channel_ = plan_.vertical_channel
        entry_ = (plan_.source_channel, 0)
        exit_ = (plan_.target_channel, 0)
        segments_by_channel.setdefault(channel_, []).append(
            _Segment(
                key=(plan_.edge_id, 0),
                edge_id=plan_.edge_id,
                low=min(entry_, exit_),
                high=max(entry_, exit_),
                # Right-hand traffic: up in the right half, down in the left
                # half.
                half=1 if plan_.goes_up else 0,
                members=(
                    _CrossMember(
                        position=entry_,
                        to_high_side=plan_.source_column > channel_,
                        is_entry=True,
                    ),
                    _CrossMember(
                        position=exit_,
                        to_high_side=plan_.target_column > channel_,
                        is_entry=False,
                    ),
                ),
                order_key=(entry_, plan_.index),
            )
        )

    result: Dict[str, LaneRef] = {}
    for channel_index_, segments_ in sorted(segments_by_channel.items()):
        channel_id_ = ChannelId(Orientation.VERTICAL, channel_index_)
        lanes_ = _assign_lanes(segments_, options, channel_id_, conflicts)
        for segment_ in segments_:
            result[segment_.edge_id] = LaneRef(
                channel_id_, lanes_[segment_.key]
            )
    return result


def _assign_ports(
    plans: List[_EdgePlan], vertical_lanes: Dict[str, LaneRef]
) -> Dict[Tuple[str, int], Port]:
    """
    Order the ports in each gate.

    A gate is the pair of faces that open into one horizontal channel in one
    column: the bottom face of the upper node and the top face of the lower
    node. All ports of a gate take different slots, so no two verticals in
    the channel share an x position.

    A straight edge takes the center slot. A gate has at most one straight
    edge. The edges to the left take the slots left of the center, the edges
    to the right take the slots right of the center. Within a side, the slots
    follow the positions where the edges go.
    """

    straight_edge_ids: Set[str] = set()
    straight_gates: Set[Tuple[int, int]] = set()
    for plan_ in plans:
        gate_ = (plan_.source_column, plan_.source_channel)
        if (
            plan_.vertical_channel is None
            and plan_.source_column == plan_.target_column
            and gate_ not in straight_gates
        ):
            straight_gates.add(gate_)
            straight_edge_ids.add(plan_.edge_id)

    # Gate -> list of (side, sort key, endpoint key, node ID, face).
    endpoints_by_gate: Dict[
        Tuple[int, int],
        List[Tuple[int, Tuple[_Position, int], Tuple[str, int], str, Face]],
    ] = {}
    for plan_ in plans:
        for (
            endpoint_,
            node_id_,
            face_,
            own_column_,
            other_column_,
            channel_,
        ) in (
            (
                _SOURCE,
                plan_.source_id,
                plan_.source_face,
                plan_.source_column,
                plan_.target_column,
                plan_.source_channel,
            ),
            (
                _TARGET,
                plan_.target_id,
                plan_.target_face,
                plan_.target_column,
                plan_.source_column,
                plan_.target_channel,
            ),
        ):
            if plan_.vertical_channel is not None:
                lane_ = vertical_lanes[plan_.edge_id].lane
                other_position_ = (2 * plan_.vertical_channel + 2, lane_)
            else:
                other_position_ = (2 * other_column_ + 1, 0)
            own_position_ = (2 * own_column_ + 1, 0)
            if plan_.edge_id in straight_edge_ids:
                side_ = 0
            elif other_position_ < own_position_:
                side_ = -1
            else:
                side_ = 1
            endpoints_by_gate.setdefault((own_column_, channel_), []).append(
                (
                    side_,
                    (other_position_, plan_.index),
                    (plan_.edge_id, endpoint_),
                    node_id_,
                    face_,
                )
            )

    ports: Dict[Tuple[str, int], Port] = {}
    for endpoints_ in endpoints_by_gate.values():
        left_ = sorted(
            (endpoint_ for endpoint_ in endpoints_ if endpoint_[0] == -1),
            key=lambda endpoint_: endpoint_[1],
        )
        right_ = sorted(
            (endpoint_ for endpoint_ in endpoints_ if endpoint_[0] == 1),
            key=lambda endpoint_: endpoint_[1],
        )
        for index_, (_, _, endpoint_key_, node_id_, face_) in enumerate(left_):
            ports[endpoint_key_] = Port(node_id_, face_, index_ - len(left_))
        for index_, (_, _, endpoint_key_, node_id_, face_) in enumerate(right_):
            ports[endpoint_key_] = Port(node_id_, face_, index_ + 1)
        for side_, _, endpoint_key_, node_id_, face_ in endpoints_:
            if side_ == 0:
                ports[endpoint_key_] = Port(node_id_, face_, 0)
    return ports


def _assign_horizontal_lanes(
    plans: List[_EdgePlan],
    ports: Dict[Tuple[str, int], Port],
    vertical_lanes: Dict[str, LaneRef],
    options: RoutingOptions,
    conflicts: List[LaneConflict],
) -> Dict[Tuple[str, int], LaneRef]:
    segments_by_channel: Dict[int, List[_Segment]] = {}
    for plan_ in plans:
        source_port_ = ports[(plan_.edge_id, _SOURCE)]
        target_port_ = ports[(plan_.edge_id, _TARGET)]
        source_position_ = (2 * plan_.source_column + 1, source_port_.slot)
        target_position_ = (2 * plan_.target_column + 1, target_port_.slot)
        # For an upward edge, the entry vertical comes from below and the
        # exit vertical goes up.
        entry_to_bottom_ = plan_.goes_up
        pieces_: List[Tuple[int, int, _Position, _Position]] = []
        if plan_.vertical_channel is None:
            if source_position_ == target_position_:
                # The ports stand on one vertical: the edge is straight.
                continue
            pieces_.append(
                (0, plan_.source_channel, source_position_, target_position_)
            )
        else:
            vertical_position_ = (
                2 * plan_.vertical_channel + 2,
                vertical_lanes[plan_.edge_id].lane,
            )
            pieces_.append(
                (0, plan_.source_channel, source_position_, vertical_position_)
            )
            pieces_.append(
                (1, plan_.target_channel, vertical_position_, target_position_)
            )
        for piece_index_, channel_, entry_, exit_ in pieces_:
            goes_left_ = exit_ < entry_
            segments_by_channel.setdefault(channel_, []).append(
                _Segment(
                    key=(plan_.edge_id, piece_index_),
                    edge_id=plan_.edge_id,
                    low=min(entry_, exit_),
                    high=max(entry_, exit_),
                    # Right-hand traffic: left in the top half, right in the
                    # bottom half.
                    half=0 if goes_left_ else 1,
                    members=(
                        _CrossMember(
                            position=entry_,
                            to_high_side=entry_to_bottom_,
                            is_entry=True,
                        ),
                        _CrossMember(
                            position=exit_,
                            to_high_side=not entry_to_bottom_,
                            is_entry=False,
                        ),
                    ),
                    order_key=(entry_, plan_.index),
                )
            )

    result: Dict[Tuple[str, int], LaneRef] = {}
    for channel_index_, segments_ in sorted(segments_by_channel.items()):
        channel_id_ = ChannelId(Orientation.HORIZONTAL, channel_index_)
        lanes_ = _assign_lanes(segments_, options, channel_id_, conflicts)
        for segment_ in segments_:
            result[segment_.key] = LaneRef(channel_id_, lanes_[segment_.key])
    return result


def _assign_lanes(
    segments: List[_Segment],
    options: RoutingOptions,
    channel: ChannelId,
    conflicts: List[LaneConflict],
) -> Dict[Tuple[str, int], int]:
    """
    Assign lanes in one channel.

    Within a half, a constraint graph orders the overlapping segments. The
    longest path from the first lane gives each segment its lane, so segments
    without overlap can share a lane.
    """

    result: Dict[Tuple[str, int], int] = {}
    lane_offset = 0
    for half_ in (0, 1):
        half_segments_ = sorted(
            (segment_ for segment_ in segments if segment_.half == half_),
            key=lambda segment_: segment_.order_key,
        )
        before_: Dict[Tuple[str, int], Set[Tuple[str, int]]] = {
            segment_.key: set() for segment_ in half_segments_
        }
        for first_index_, first_ in enumerate(half_segments_):
            for second_ in half_segments_[first_index_ + 1 :]:
                order_ = _pair_order(
                    first_, second_, options, channel, conflicts
                )
                if order_ == 1:
                    before_[second_.key].add(first_.key)
                elif order_ == -1:
                    before_[first_.key].add(second_.key)
        half_lanes_ = _longest_path_lanes(half_segments_, before_)
        for key_, lane_ in half_lanes_.items():
            result[key_] = lane_offset + lane_
        if len(half_lanes_) > 0:
            lane_offset += max(half_lanes_.values()) + 1
    return result


def _pair_order(
    first: _Segment,
    second: _Segment,
    options: RoutingOptions,
    channel: ChannelId,
    conflicts: List[LaneConflict],
) -> int:
    """
    Return 1 if the first segment takes a lower lane, -1 for the opposite.

    Return 0 if the segments do not overlap.
    """

    if not _overlap(first, second):
        return 0
    # (order, is_entry, is the second segment the inner one).
    votes: List[Tuple[int, bool, bool]] = []
    for member_ in second.members:
        if first.low < member_.position < first.high:
            # The member of the second segment extends toward the high side.
            # The first segment must stay on the low side of it.
            votes.append(
                (1 if member_.to_high_side else -1, member_.is_entry, True)
            )
    for member_ in first.members:
        if second.low < member_.position < second.high:
            votes.append(
                (-1 if member_.to_high_side else 1, member_.is_entry, False)
            )
    if len(votes) == 0:
        return 0
    orders = {vote_[0] for vote_ in votes}
    if len(orders) == 1:
        return votes[0][0]

    prefer_entry = options.lane_conflict_priority is LaneConflictPriority.ENTRY
    preferred = [vote_ for vote_ in votes if vote_[1] == prefer_entry]
    chosen = preferred[0] if len(preferred) > 0 else votes[0]
    outer, inner = (first, second) if chosen[2] else (second, first)
    conflicts.append(
        LaneConflict(
            channel=channel,
            outer_edge_id=outer.edge_id,
            inner_edge_id=inner.edge_id,
        )
    )
    return chosen[0]


def _longest_path_lanes(
    segments: List[_Segment],
    before: Dict[Tuple[str, int], Set[Tuple[str, int]]],
) -> Dict[Tuple[str, int], int]:
    """
    Give each segment the lane after all segments that must come before it.

    If the constraints form a cycle, the first remaining segment in order
    ignores its unresolved constraints. A segment never shares a lane with an
    overlapping segment.
    """

    segment_by_key = {segment_.key: segment_ for segment_ in segments}
    remaining = [segment_.key for segment_ in segments]
    lanes: Dict[Tuple[str, int], int] = {}
    while len(remaining) > 0:
        ready = [
            key_
            for key_ in remaining
            if all(before_key_ in lanes for before_key_ in before[key_])
        ]
        if len(ready) == 0:
            ready = [remaining[0]]
        for key_ in ready:
            lane_ = max(
                (
                    lanes[before_key_] + 1
                    for before_key_ in before[key_]
                    if before_key_ in lanes
                ),
                default=0,
            )
            segment_ = segment_by_key[key_]
            while any(
                lanes[placed_key_] == lane_
                and _overlap(segment_, segment_by_key[placed_key_])
                for placed_key_ in lanes
            ):
                lane_ += 1
            lanes[key_] = lane_
        remaining = [key_ for key_ in remaining if key_ not in lanes]
    return lanes


def _overlap(first: _Segment, second: _Segment) -> bool:
    return not (first.high < second.low or second.high < first.low)
