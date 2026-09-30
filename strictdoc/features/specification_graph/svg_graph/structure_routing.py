"""
Stages 3 and 4 of the graph generator for the structure mode.

Stage 3 selects the channels of each route. Stage 4 assigns the lanes of the
vertical channels, the port slots, and the lanes of the horizontal channels.
spec.md, section "Маршруты" of the structure mode, defines the rules.

This module routes the relations between simple nodes of one container.
The relations across containers and the relations with a composite node
are not routed yet.
"""

import heapq
from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Set, Tuple

from strictdoc.features.specification_graph.svg_graph.gate_ports import (
    EndpointKey,
    Face,
    GateEndpoint,
    Port,
    number_gate_ports,
)
from strictdoc.features.specification_graph.svg_graph.lane_assignment import (
    CrossMember,
    LaneSegment,
    assign_lanes,
)
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    GeometryConfig,
    Rect,
)
from strictdoc.features.specification_graph.svg_graph.levels_routing import (
    RoutingOptions,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedEdge,
    NormalizedGraph,
)
from strictdoc.features.specification_graph.svg_graph.structure_geometry import (
    StructureGeometry,
    compute_structure_geometry,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    StructureChannelId,
    StructureLayout,
)


@dataclass(frozen=True)
class StructureRoute:
    edge_id: str
    source_port: Port
    target_port: Port
    # Channels in route order. The channels alternate: horizontal, vertical,
    # horizontal, and so on. The first channel opens to the source port, the
    # last channel opens to the target port.
    channels: Tuple[StructureChannelId, ...]
    # Lane of the route in each channel. A straight edge has no lanes.
    lanes: Tuple[int, ...]


@dataclass(frozen=True)
class StructureLaneConflict:
    channel: StructureChannelId
    outer_edge_id: str
    inner_edge_id: str


@dataclass(frozen=True)
class StructureRouting:
    routes: Mapping[str, StructureRoute]
    lane_counts: Mapping[StructureChannelId, int]
    conflicts: Tuple[StructureLaneConflict, ...]
    # Relations this stage does not route yet: relations across containers
    # and relations with a composite node.
    unrouted_edge_ids: Tuple[str, ...]


def compute_structure_routing(
    normalized_graph: NormalizedGraph,
    layout: StructureLayout,
    config: Optional[GeometryConfig] = None,
    options: Optional[RoutingOptions] = None,
) -> StructureRouting:
    if config is None:
        config = GeometryConfig()
    if options is None:
        options = RoutingOptions()
    # Positions for the path costs and the lane order: the geometry with the
    # minimum channels. The exact channel sizes follow from the lanes.
    estimate = compute_structure_geometry(normalized_graph, layout, config)
    router = _Router(normalized_graph, layout, estimate, config, options)
    return router.route()


_SOURCE = 0
_TARGET = 1


@dataclass(frozen=True)
class _Plan:
    index: int
    edge: NormalizedEdge
    source_face: Face
    target_face: Face
    channels: Tuple[StructureChannelId, ...]
    # The two nodes stand next to each other in one column.
    is_straight_candidate: bool


class _Router:
    def __init__(
        self,
        normalized_graph: NormalizedGraph,
        layout: StructureLayout,
        estimate: StructureGeometry,
        config: GeometryConfig,
        options: RoutingOptions,
    ) -> None:
        self.normalized_graph: NormalizedGraph = normalized_graph
        self.layout: StructureLayout = layout
        self.estimate: StructureGeometry = estimate
        self.config: GeometryConfig = config
        self.options: RoutingOptions = options
        self.channel_rects: Dict[StructureChannelId, Rect] = {
            channel_.channel_id: channel_.rect for channel_ in estimate.channels
        }
        self.composite_ids: Set[str] = {
            node_.node_id
            for node_ in normalized_graph.nodes
            if len(node_.children) > 0
        }

    def route(self) -> StructureRouting:
        plans: List[_Plan] = []
        unrouted: List[str] = []
        for index_, edge_ in enumerate(self.normalized_graph.edges):
            plan_ = self._plan(index_, edge_)
            if plan_ is None:
                unrouted.append(edge_.edge_id)
            else:
                plans.append(plan_)

        conflicts: List[StructureLaneConflict] = []
        vertical_lanes = self._assign_vertical_lanes(plans, conflicts)
        ports, straight_ids = self._assign_ports(plans, vertical_lanes)
        horizontal_lanes = self._assign_horizontal_lanes(
            plans, ports, straight_ids, vertical_lanes, conflicts
        )

        routes: Dict[str, StructureRoute] = {}
        lane_counts: Dict[StructureChannelId, int] = {}
        for plan_ in plans:
            edge_id_ = plan_.edge.edge_id
            if edge_id_ in straight_ids:
                lanes_: Tuple[int, ...] = ()
            else:
                lanes_ = tuple(
                    (
                        vertical_lanes[(edge_id_, position_)]
                        if position_ % 2 == 1
                        else horizontal_lanes[(edge_id_, position_)]
                    )
                    for position_ in range(len(plan_.channels))
                )
                for channel_, lane_ in zip(plan_.channels, lanes_):
                    lane_counts[channel_] = max(
                        lane_counts.get(channel_, 0), lane_ + 1
                    )
            routes[edge_id_] = StructureRoute(
                edge_id=edge_id_,
                source_port=ports[(edge_id_, _SOURCE)],
                target_port=ports[(edge_id_, _TARGET)],
                channels=plan_.channels,
                lanes=lanes_,
            )
        return StructureRouting(
            routes=routes,
            lane_counts=lane_counts,
            conflicts=tuple(conflicts),
            unrouted_edge_ids=tuple(unrouted),
        )

    # Stage 3: the channels of each route.

    def _plan(self, index: int, edge: NormalizedEdge) -> Optional[_Plan]:
        source_id = edge.source_id
        target_id = edge.target_id
        if (
            source_id in self.composite_ids
            or target_id in self.composite_ids
            or source_id not in self.layout.places
            or target_id not in self.layout.places
        ):
            return None
        source_place = self.layout.places[source_id]
        target_place = self.layout.places[target_id]
        if source_place.container_id != target_place.container_id:
            return None

        if (
            source_place.column == target_place.column
            and abs(source_place.row - target_place.row) == 1
        ):
            # Neighbors in one column face each other across one channel.
            source_is_upper = source_place.row < target_place.row
            channel = (
                self.layout.channel_below(source_id)
                if source_is_upper
                else self.layout.channel_above(source_id)
            )
            return _Plan(
                index=index,
                edge=edge,
                source_face=Face.BOTTOM if source_is_upper else Face.TOP,
                target_face=Face.TOP if source_is_upper else Face.BOTTOM,
                channels=(channel,),
                is_straight_candidate=True,
            )

        best: Optional[Tuple[Tuple[int, float, int], _Plan]] = None
        for face_rank_, (source_face_, target_face_) in enumerate(
            (
                (Face.TOP, Face.TOP),
                (Face.TOP, Face.BOTTOM),
                (Face.BOTTOM, Face.TOP),
                (Face.BOTTOM, Face.BOTTOM),
            )
        ):
            path_ = self._best_path(
                source_id, source_face_, target_id, target_face_
            )
            if path_ is None:
                continue
            (bends_, length_), channels_ = path_
            cost_ = (bends_, length_, face_rank_)
            if best is None or cost_ < best[0]:
                best = (
                    cost_,
                    _Plan(
                        index=index,
                        edge=edge,
                        source_face=source_face_,
                        target_face=target_face_,
                        channels=channels_,
                        is_straight_candidate=False,
                    ),
                )
        assert best is not None
        return best[1]

    def _port_channel(self, node_id: str, face: Face) -> StructureChannelId:
        if face is Face.TOP:
            return self.layout.channel_above(node_id)
        return self.layout.channel_below(node_id)

    def _best_path(
        self,
        source_id: str,
        source_face: Face,
        target_id: str,
        target_face: Face,
    ) -> Optional[Tuple[Tuple[int, float], Tuple[StructureChannelId, ...]]]:
        """
        Find the path with the fewest bends, then the shortest length.

        The path alternates horizontal and vertical channels. Each change of
        channel is a bend. Each port adds a bend where its vertical stub
        turns into the first or the last horizontal channel. The length
        includes the stubs from the node faces to the channels.
        """

        start = self._port_channel(source_id, source_face)
        end = self._port_channel(target_id, target_face)
        source_x = _center_x(self.estimate.node_rects[source_id])
        target_x = _center_x(self.estimate.node_rects[target_id])
        start_point = (source_x, _center_y(self.channel_rects[start]))
        stubs_length = self._stub_length(
            source_id, source_face, start
        ) + self._stub_length(target_id, target_face, end)

        # Queue items: (bends, length, tie, is_done, channel, point, path).
        # A done item is a complete path with the final segment to the
        # target port. The search returns when it takes a done item, so the
        # final segment counts in the order of the queue.
        queue: List[
            Tuple[
                int,
                float,
                int,
                bool,
                StructureChannelId,
                Tuple[float, float],
                Tuple[StructureChannelId, ...],
            ]
        ] = [(1, stubs_length, 0, False, start, start_point, (start,))]
        tie = 1
        visited: Set[Tuple[StructureChannelId, Tuple[float, float]]] = set()
        while len(queue) > 0:
            bends, length, _, is_done, channel, point, path = heapq.heappop(
                queue
            )
            if is_done:
                return (bends, length), path
            if (channel, point) in visited:
                continue
            visited.add((channel, point))
            if channel == end:
                heapq.heappush(
                    queue,
                    (
                        bends + 1,
                        length + abs(point[0] - target_x),
                        tie,
                        True,
                        channel,
                        point,
                        path,
                    ),
                )
                tie += 1
                continue
            for neighbor_ in self.layout.neighbor_channels(channel):
                if neighbor_ in path:
                    continue
                turn_ = self._turn_point(channel, neighbor_)
                heapq.heappush(
                    queue,
                    (
                        bends + 1,
                        length
                        + abs(point[0] - turn_[0])
                        + abs(point[1] - turn_[1]),
                        tie,
                        False,
                        neighbor_,
                        turn_,
                        path + (neighbor_,),
                    ),
                )
                tie += 1
        return None

    def _stub_length(
        self, node_id: str, face: Face, channel: StructureChannelId
    ) -> float:
        rect = self.estimate.node_rects[node_id]
        face_y = rect.y if face is Face.TOP else rect.y + rect.height
        return abs(face_y - _center_y(self.channel_rects[channel]))

    def _turn_point(
        self, first: StructureChannelId, second: StructureChannelId
    ) -> Tuple[float, float]:
        horizontal, vertical = (
            (first, second) if first.is_horizontal else (second, first)
        )
        return (
            _center_x(self.channel_rects[vertical]),
            _center_y(self.channel_rects[horizontal]),
        )

    # Stage 4: lanes and ports.

    def _assign_vertical_lanes(
        self,
        plans: List[_Plan],
        conflicts: List[StructureLaneConflict],
    ) -> Dict[Tuple[str, int], int]:
        segments_by_channel: Dict[StructureChannelId, List[LaneSegment]] = {}
        for plan_ in plans:
            channels_ = plan_.channels
            for position_ in range(1, len(channels_), 2):
                channel_ = channels_[position_]
                vertical_x_ = _center_x(self.channel_rects[channel_])
                entry_y_ = _center_y(
                    self.channel_rects[channels_[position_ - 1]]
                )
                exit_y_ = _center_y(
                    self.channel_rects[channels_[position_ + 1]]
                )
                entry_far_x_ = self._horizontal_far_x(
                    plan_, position_ - 1, position_
                )
                exit_far_x_ = self._horizontal_far_x(
                    plan_, position_ + 1, position_
                )
                segments_by_channel.setdefault(channel_, []).append(
                    LaneSegment(
                        key=(plan_.edge.edge_id, position_),
                        edge_id=plan_.edge.edge_id,
                        low=(min(entry_y_, exit_y_), 0.0),
                        high=(max(entry_y_, exit_y_), 0.0),
                        # Right-hand traffic: up in the right half, down in
                        # the left half.
                        half=1 if exit_y_ < entry_y_ else 0,
                        members=(
                            CrossMember(
                                position=(entry_y_, 0.0),
                                to_high_side=entry_far_x_ > vertical_x_,
                                is_entry=True,
                            ),
                            CrossMember(
                                position=(exit_y_, 0.0),
                                to_high_side=exit_far_x_ > vertical_x_,
                                is_entry=False,
                            ),
                        ),
                        order_key=((entry_y_, 0.0), plan_.index),
                    )
                )
        return self._assign_channel_lanes(segments_by_channel, conflicts)

    def _horizontal_far_x(
        self, plan: _Plan, position: int, seen_from: int
    ) -> float:
        """
        Return the far end of a horizontal segment of a route.

        The far end is seen from the vertical segment at the position
        seen_from. It is the port or the vertical channel on the other side.
        """

        channels = plan.channels
        if position == 0:
            return _center_x(self.estimate.node_rects[plan.edge.source_id])
        if position == len(channels) - 1:
            return _center_x(self.estimate.node_rects[plan.edge.target_id])
        other = position + 1 if seen_from == position - 1 else position - 1
        return _center_x(self.channel_rects[channels[other]])

    def _vertical_lane_x(
        self,
        plan: _Plan,
        position: int,
        vertical_lanes: Dict[Tuple[str, int], int],
    ) -> Tuple[float, float]:
        channel = plan.channels[position]
        return (
            _center_x(self.channel_rects[channel]),
            vertical_lanes[(plan.edge.edge_id, position)],
        )

    def _assign_ports(
        self,
        plans: List[_Plan],
        vertical_lanes: Dict[Tuple[str, int], int],
    ) -> Tuple[Dict[EndpointKey, Port], Set[str]]:
        """
        Collect the endpoints of each gate and number the ports.

        A gate is a horizontal channel and a column. A gate has at most one
        straight edge.
        """

        straight_ids: Set[str] = set()
        straight_gates: Set[Tuple[StructureChannelId, int]] = set()
        for plan_ in plans:
            if not plan_.is_straight_candidate:
                continue
            gate_ = (
                plan_.channels[0],
                self.layout.places[plan_.edge.source_id].column,
            )
            if gate_ not in straight_gates:
                straight_gates.add(gate_)
                straight_ids.add(plan_.edge.edge_id)

        endpoints_by_gate: Dict[
            Tuple[StructureChannelId, int], List[GateEndpoint]
        ] = {}
        for plan_ in plans:
            last_ = len(plan_.channels) - 1
            for role_, node_id_, face_, position_, other_id_ in (
                (
                    _SOURCE,
                    plan_.edge.source_id,
                    plan_.source_face,
                    0,
                    plan_.edge.target_id,
                ),
                (
                    _TARGET,
                    plan_.edge.target_id,
                    plan_.target_face,
                    last_,
                    plan_.edge.source_id,
                ),
            ):
                own_x_ = _center_x(self.estimate.node_rects[node_id_])
                if len(plan_.channels) == 1:
                    other_position_ = (
                        _center_x(self.estimate.node_rects[other_id_]),
                        0.0,
                    )
                else:
                    neighbor_ = 1 if role_ == _SOURCE else last_ - 1
                    other_position_ = self._vertical_lane_x(
                        plan_, neighbor_, vertical_lanes
                    )
                own_position_ = (own_x_, 0.0)
                if plan_.edge.edge_id in straight_ids:
                    side_ = 0
                elif other_position_ < own_position_:
                    side_ = -1
                else:
                    side_ = 1
                if role_ == _SOURCE:
                    goes_left_ = other_position_ < own_position_
                else:
                    goes_left_ = other_position_ > own_position_
                gate_ = (
                    plan_.channels[position_],
                    self.layout.places[node_id_].column,
                )
                endpoints_by_gate.setdefault(gate_, []).append(
                    GateEndpoint(
                        endpoint_key=(plan_.edge.edge_id, role_),
                        node_id=node_id_,
                        face=face_,
                        side=side_,
                        half=0 if goes_left_ else 1,
                        sort_key=(other_position_, plan_.index),
                        flows_down=(
                            (role_ == _SOURCE) == (face_ is Face.BOTTOM)
                        ),
                    )
                )
        ports: Dict[EndpointKey, Port] = {}
        for endpoints_ in endpoints_by_gate.values():
            ports.update(number_gate_ports(endpoints_))
        return ports, straight_ids

    def _assign_horizontal_lanes(
        self,
        plans: List[_Plan],
        ports: Dict[EndpointKey, Port],
        straight_ids: Set[str],
        vertical_lanes: Dict[Tuple[str, int], int],
        conflicts: List[StructureLaneConflict],
    ) -> Dict[Tuple[str, int], int]:
        segments_by_channel: Dict[StructureChannelId, List[LaneSegment]] = {}
        for plan_ in plans:
            edge_id_ = plan_.edge.edge_id
            if edge_id_ in straight_ids:
                continue
            channels_ = plan_.channels
            last_ = len(channels_) - 1
            for position_ in range(0, len(channels_), 2):
                channel_y_ = _center_y(self.channel_rects[channels_[position_]])
                if position_ == 0:
                    entry_ = self._port_position(
                        ports[(edge_id_, _SOURCE)], plan_.edge.source_id
                    )
                    # The source stub reaches the node below or above the
                    # channel.
                    entry_to_bottom_ = plan_.source_face is Face.TOP
                else:
                    entry_ = self._vertical_lane_x(
                        plan_, position_ - 1, vertical_lanes
                    )
                    previous_y_ = _center_y(
                        self.channel_rects[channels_[position_ - 2]]
                    )
                    entry_to_bottom_ = previous_y_ > channel_y_
                if position_ == last_:
                    exit_ = self._port_position(
                        ports[(edge_id_, _TARGET)], plan_.edge.target_id
                    )
                    exit_to_bottom_ = plan_.target_face is Face.TOP
                else:
                    exit_ = self._vertical_lane_x(
                        plan_, position_ + 1, vertical_lanes
                    )
                    next_y_ = _center_y(
                        self.channel_rects[channels_[position_ + 2]]
                    )
                    exit_to_bottom_ = next_y_ > channel_y_
                segments_by_channel.setdefault(channels_[position_], []).append(
                    LaneSegment(
                        key=(edge_id_, position_),
                        edge_id=edge_id_,
                        low=min(entry_, exit_),
                        high=max(entry_, exit_),
                        # Right-hand traffic: left in the top half, right in
                        # the bottom half.
                        half=0 if exit_ < entry_ else 1,
                        members=(
                            CrossMember(
                                position=entry_,
                                to_high_side=entry_to_bottom_,
                                is_entry=True,
                            ),
                            CrossMember(
                                position=exit_,
                                to_high_side=exit_to_bottom_,
                                is_entry=False,
                            ),
                        ),
                        order_key=(entry_, plan_.index),
                    )
                )
        return self._assign_channel_lanes(segments_by_channel, conflicts)

    def _port_position(self, port: Port, node_id: str) -> Tuple[float, float]:
        return (_center_x(self.estimate.node_rects[node_id]), port.slot)

    def _assign_channel_lanes(
        self,
        segments_by_channel: Dict[StructureChannelId, List[LaneSegment]],
        conflicts: List[StructureLaneConflict],
    ) -> Dict[Tuple[str, int], int]:
        result: Dict[Tuple[str, int], int] = {}
        for channel_, segments_ in segments_by_channel.items():
            lanes_, pairs_ = assign_lanes(
                segments_, self.options.lane_conflict_priority
            )
            result.update(lanes_)
            conflicts.extend(
                StructureLaneConflict(
                    channel=channel_,
                    outer_edge_id=pair_.outer_edge_id,
                    inner_edge_id=pair_.inner_edge_id,
                )
                for pair_ in pairs_
            )
        return result


def _center_x(rect: Rect) -> float:
    return rect.x + rect.width / 2


def _center_y(rect: Rect) -> float:
    return rect.y + rect.height / 2
