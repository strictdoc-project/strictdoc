"""
Stages 3 and 4 of the graph generator for the levels mode.

Stage 3 selects the channels of each route. Stage 4 orders the ports on the
node faces and assigns a lane to each route segment. Both stages use no pixel
geometry. spec.md, section "Маршруты", defines the rules.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Mapping, Optional, Set, Tuple

from strictdoc.features.specification_graph.svg_graph.gate_ports import (
    Face,
    GateEndpoint,
    Port,
    number_gate_ports,
)
from strictdoc.features.specification_graph.svg_graph.lane_assignment import (
    CrossMember,
    LaneConflictPriority,
    LaneSegment,
    assign_lanes,
)
from strictdoc.features.specification_graph.svg_graph.levels_structure import (
    LevelsStructure,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedGraph,
)


class SkipChannelChoice(Enum):
    """
    Which vertical channel an edge across levels uses.

    NEAR_SOURCE climbs in the channel next to the source column. NEAR_TARGET
    climbs in the channel next to the target column.
    """

    NEAR_SOURCE = "near_source"
    NEAR_TARGET = "near_target"


class OverUnderTie(Enum):
    """
    The structure mode: which path wins when the path over the columns and
    the path under them have equal bends and close lengths.

    FEWER_CROSSINGS takes the path that crosses fewer paths of the other
    relations, and the path under the columns if both cross equally many.
    UNDER always takes the path under the columns.
    """

    FEWER_CROSSINGS = "fewer_crossings"
    UNDER = "under"


@dataclass(frozen=True)
class RoutingOptions:
    """
    Routing choices with more than one valid answer.

    The defaults are the decisions recorded in spec.md, section "Маршруты".
    To change a decision, change the default here and update spec.md.
    """

    lane_conflict_priority: LaneConflictPriority = LaneConflictPriority.EXIT
    skip_channel_choice: SkipChannelChoice = SkipChannelChoice.NEAR_TARGET
    over_under_tie: OverUnderTie = OverUnderTie.FEWER_CROSSINGS


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


def _assign_vertical_lanes(
    plans: List[_EdgePlan],
    options: RoutingOptions,
    conflicts: List[LaneConflict],
) -> Dict[str, LaneRef]:
    segments_by_channel: Dict[int, List[LaneSegment]] = {}
    for plan_ in plans:
        if plan_.vertical_channel is None:
            continue
        channel_ = plan_.vertical_channel
        entry_ = (plan_.source_channel, 0)
        exit_ = (plan_.target_channel, 0)
        segments_by_channel.setdefault(channel_, []).append(
            LaneSegment(
                key=(plan_.edge_id, 0),
                edge_id=plan_.edge_id,
                low=min(entry_, exit_),
                high=max(entry_, exit_),
                # Right-hand traffic: up in the right half, down in the left
                # half.
                half=1 if plan_.goes_up else 0,
                members=(
                    CrossMember(
                        position=entry_,
                        to_high_side=plan_.source_column > channel_,
                        is_entry=True,
                    ),
                    CrossMember(
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
    Assign a slot to each port.

    The levels mode collects the endpoints of each gate. The gate is the
    column and the horizontal channel. gate_ports.number_gate_ports numbers
    the ports of each gate.
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

    endpoints_by_gate: Dict[Tuple[int, int], List[GateEndpoint]] = {}
    for plan_ in plans:
        for (
            endpoint_role_,
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
            # The segment leaves a source port and arrives at a target port.
            if endpoint_role_ == _SOURCE:
                goes_left_ = other_position_ < own_position_
            else:
                goes_left_ = other_position_ > own_position_
            endpoints_by_gate.setdefault((own_column_, channel_), []).append(
                GateEndpoint(
                    endpoint_key=(plan_.edge_id, endpoint_role_),
                    node_id=node_id_,
                    face=face_,
                    side=side_,
                    half=0 if goes_left_ else 1,
                    sort_key=(other_position_, plan_.index),
                    flows_down=(
                        (endpoint_role_ == _SOURCE) == (face_ is Face.BOTTOM)
                    ),
                )
            )

    ports: Dict[Tuple[str, int], Port] = {}
    for endpoints_ in endpoints_by_gate.values():
        ports.update(number_gate_ports(endpoints_))
    return ports


def _assign_horizontal_lanes(
    plans: List[_EdgePlan],
    ports: Dict[Tuple[str, int], Port],
    vertical_lanes: Dict[str, LaneRef],
    options: RoutingOptions,
    conflicts: List[LaneConflict],
) -> Dict[Tuple[str, int], LaneRef]:
    segments_by_channel: Dict[int, List[LaneSegment]] = {}
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
                LaneSegment(
                    key=(plan_.edge_id, piece_index_),
                    edge_id=plan_.edge_id,
                    low=min(entry_, exit_),
                    high=max(entry_, exit_),
                    # Right-hand traffic: left in the top half, right in the
                    # bottom half. This is the weakest reason of the order:
                    # it orders two overlapping segments only if their ends
                    # do not. Each segment here ends at its own port, so
                    # the ends order every pair: an end inside the other
                    # segment (lane_assignment._pair_order) or two ends at
                    # one point (lane_assignment._coincident_order). The
                    # rule stays for ends that do not order a pair.
                    half=0 if goes_left_ else 1,
                    members=(
                        CrossMember(
                            position=entry_,
                            to_high_side=entry_to_bottom_,
                            is_entry=True,
                        ),
                        CrossMember(
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
    segments: List[LaneSegment],
    options: RoutingOptions,
    channel: ChannelId,
    conflicts: List[LaneConflict],
) -> Dict[Tuple[str, int], int]:
    lanes, conflict_pairs = assign_lanes(
        segments, options.lane_conflict_priority
    )
    conflicts.extend(
        LaneConflict(
            channel=channel,
            outer_edge_id=pair_.outer_edge_id,
            inner_edge_id=pair_.inner_edge_id,
        )
        for pair_ in conflict_pairs
    )
    return lanes
