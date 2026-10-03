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
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Mapping, Optional, Set, Tuple

from strictdoc.features.specification_graph.svg_graph.gate_ports import (
    EndpointKey,
    Face,
    ForcedPortOrder,
    GateEndpoint,
    Port,
    number_gate_ports,
)
from strictdoc.features.specification_graph.svg_graph.lane_assignment import (
    CrossMember,
    ForcedOrder,
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
    centered_lane_offset,
    compute_structure_geometry,
    corridor_segment_y,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    ChannelKind,
    CorridorSegment,
    LaneEnd,
    PortEnd,
    SegmentEnd,
    StructureChannelId,
    StructureLayout,
)
from strictdoc.features.specification_graph.svg_graph.structure_stretches import (
    shared_stretch_orders,
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
    # Lane count of each channel with lanes at fixed positions. The bottom
    # corridor places its segments by the contour of the columns, see
    # bottom_segments.
    lane_counts: Mapping[StructureChannelId, int]
    bottom_segments: Tuple[CorridorSegment, ...]
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
    # The estimated level of each channel: the y of a horizontal segment or
    # the x of a vertical segment. A through pass is a vertical segment
    # between two horizontal segments of the same level.
    levels: Tuple[float, ...]
    # The two nodes stand next to each other in one column.
    is_straight_candidate: bool


@dataclass(order=True)
class _SearchItem:
    """
    An item of the path search queue, ordered by bends, length, nested
    channels, and tie.

    A done item is a complete path with the final segment to the target
    port. The search returns when it takes a done item, so the final segment
    counts in the order of the queue. is_through: the point came by a
    through pass and keeps its height. nested_channels: the channels of the
    path that belong to containers inside the common container.
    """

    bends: int
    length: float
    nested_channels: int
    tie: int
    is_done: bool = field(compare=False)
    channel: StructureChannelId = field(compare=False)
    point: Tuple[float, float] = field(compare=False)
    is_through: bool = field(compare=False)
    path: Tuple[StructureChannelId, ...] = field(compare=False)
    levels: Tuple[float, ...] = field(compare=False)


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
        # The forced orders of the nested pairs on shared stretches.
        self.forced_orders: Dict[StructureChannelId, List[ForcedOrder]] = {}
        self.forced_port_orders: List[ForcedPortOrder] = []
        self.composite_ids: Set[str] = {
            node_.node_id
            for node_ in normalized_graph.nodes
            if len(node_.children) > 0
        }
        self.side_face_links: Dict[
            StructureChannelId, List[StructureChannelId]
        ] = _side_face_links(layout)
        # Container -> (left, right, bottom) of each column in the estimate.
        self.column_spans: Dict[
            Optional[str], List[Tuple[float, float, float]]
        ] = _column_spans(layout, estimate)

    def route(self) -> StructureRouting:
        plans: List[_Plan] = []
        unrouted: List[str] = []
        for index_, edge_ in enumerate(self.normalized_graph.edges):
            plan_ = self._plan(index_, edge_)
            if plan_ is None:
                unrouted.append(edge_.edge_id)
            else:
                plans.append(plan_)

        straight_ids = self._straight_ids(plans)
        # The heights of the columns are exact from here on: the lane count
        # of each column channel follows from the routes alone.
        exact = compute_structure_geometry(
            self.normalized_graph,
            self.layout,
            self.config,
            lane_counts=self._column_lane_counts(plans, straight_ids),
        )
        plans = [self._exact_levels(plan_, exact, {}) for plan_ in plans]
        self.forced_orders, self.forced_port_orders = shared_stretch_orders(
            [
                plan_
                for plan_ in plans
                if plan_.edge.edge_id not in straight_ids
            ],
            exact,
        )

        # Containers inside out: a layer of containers of one depth at a
        # time. When a layer is done, its sizes and the heights of its pass
        # ports are final, and the next layer gets them exact.
        conflicts: List[StructureLaneConflict] = []
        column_counts = self._column_lane_counts(plans, straight_ids)
        vertical_lanes: Dict[Tuple[str, int], int] = {}
        ports: Dict[EndpointKey, Port] = {}
        horizontal_lanes: Dict[Tuple[str, int], int] = {}
        finished: Set[Optional[str]] = set()
        for layer_ in self._layers():
            layer_geometry_ = compute_structure_geometry(
                self.normalized_graph,
                self.layout,
                self.config,
                lane_counts={
                    **column_counts,
                    **_lane_counts(
                        plans,
                        straight_ids,
                        vertical_lanes,
                        horizontal_lanes,
                        finished,
                    ),
                },
                bottom_segments=_bottom_segments(
                    plans,
                    straight_ids,
                    vertical_lanes,
                    horizontal_lanes,
                    finished,
                    self.normalized_graph.parent_ids,
                ),
            )
            finished_levels_ = _finished_levels(
                plans, straight_ids, horizontal_lanes, finished, layer_geometry_
            )
            plans = [
                self._exact_levels(plan_, layer_geometry_, finished_levels_)
                for plan_ in plans
            ]
            vertical_lanes.update(
                self._assign_vertical_lanes(plans, conflicts, layer_)
            )
            ports.update(
                self._assign_ports(plans, vertical_lanes, straight_ids, layer_)
            )
            horizontal_lanes.update(
                self._assign_horizontal_lanes(
                    plans,
                    ports,
                    straight_ids,
                    vertical_lanes,
                    conflicts,
                    layer_,
                )
            )
            finished |= layer_

        routes: Dict[str, StructureRoute] = {}
        lane_counts: Dict[StructureChannelId, int] = {}
        bottom_segments: List[CorridorSegment] = []
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
            route_ = StructureRoute(
                edge_id=edge_id_,
                source_port=ports[(edge_id_, _SOURCE)],
                target_port=ports[(edge_id_, _TARGET)],
                channels=plan_.channels,
                lanes=lanes_,
            )
            routes[edge_id_] = route_
            bottom_segments.extend(
                _route_bottom_segments(route_, self.normalized_graph.parent_ids)
            )
            for channel_, lane_ in zip(plan_.channels, lanes_):
                if channel_.kind is not ChannelKind.BOTTOM_CORRIDOR:
                    lane_counts[channel_] = max(
                        lane_counts.get(channel_, 0), lane_ + 1
                    )
        return StructureRouting(
            routes=routes,
            lane_counts=lane_counts,
            bottom_segments=tuple(bottom_segments),
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
        chain = self._chain(source_id, target_id)

        if (
            source_place.container_id == target_place.container_id
            and source_place.column == target_place.column
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
                levels=(_center_y(self.channel_rects[channel]),),
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
                source_id, source_face_, target_id, target_face_, chain
            )
            if path_ is None:
                continue
            (bends_, length_), channels_, levels_ = path_
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
                        levels=levels_,
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
        chain: FrozenSet[Optional[str]],
    ) -> Optional[
        Tuple[
            Tuple[int, float],
            Tuple[StructureChannelId, ...],
            Tuple[float, ...],
        ]
    ]:
        """
        Find the path with the fewest bends, then the shortest length, then
        the fewest channels inside nested containers.

        The fewest bends win even over a much longer path, for example under
        a whole long column. This is a temporary decision, see spec.md,
        section "Путь по каналам".

        The path alternates horizontal and vertical channels. Each change of
        channel is a bend, except a through pass. Each port adds a bend where
        its vertical stub turns into the first or the last horizontal
        channel. The length includes the stubs from the node faces to the
        channels. Return the cost, the channels, and the level of each
        channel: the y of a horizontal segment or the x of a vertical one.

        A point in the bottom corridor that comes by a turn first takes the
        lowest height of the corridor. When the segment ends, its height
        follows from the columns it passes over, and the length gets the
        difference for both of its vertical ends. A point that comes by a
        through pass keeps its height.

        The last rule keeps a line in the channels of the common container:
        it enters a nested container as late as possible and leaves it as
        early as possible. A path in one direction is the reverse of the
        path in the other, so two opposite relations between the same places
        take the same channels.
        """

        common_id = next(
            container_id_
            for container_id_ in chain
            if container_id_ is None
            or self.normalized_graph.parent_ids[container_id_] not in chain
        )
        start = self._port_channel(source_id, source_face)
        end = self._port_channel(target_id, target_face)
        source_x = _center_x(self.estimate.node_rects[source_id])
        target_x = _center_x(self.estimate.node_rects[target_id])
        start_point = (source_x, self._channel_y(start))
        stubs_length = self._stub_length(
            source_id, source_face, start
        ) + self._stub_length(target_id, target_face, end)

        queue: List[_SearchItem] = []
        tie = 0

        def push(
            bends: int,
            length: float,
            is_done: bool,
            channel: StructureChannelId,
            point: Tuple[float, float],
            is_through: bool,
            path: Tuple[StructureChannelId, ...],
            levels: Tuple[float, ...],
        ) -> None:
            nonlocal tie
            heapq.heappush(
                queue,
                _SearchItem(
                    bends,
                    length,
                    sum(
                        1
                        for channel_ in path
                        if channel_.container_id != common_id
                    ),
                    tie,
                    is_done,
                    channel,
                    point,
                    is_through,
                    path,
                    levels,
                ),
            )
            tie += 1

        push(
            1,
            stubs_length,
            False,
            start,
            start_point,
            False,
            (start,),
            (start_point[1],),
        )
        visited: Set[Tuple[StructureChannelId, Tuple[float, float], bool]] = (
            set()
        )
        while len(queue) > 0:
            item = heapq.heappop(queue)
            if item.is_done:
                return (item.bends, item.length), item.path, item.levels
            state = (item.channel, item.point, item.is_through)
            if state in visited:
                continue
            visited.add(state)
            x, y = item.point
            # Where the segment in this channel starts for the columns under
            # it: a line from a child container starts at its side face.
            start_x = (
                self._face_x(item.path[-2], item.channel)
                if len(item.path) >= 2
                else x
            )
            if item.channel == end:
                segment_y_ = self._segment_y(
                    item.channel, start_x, target_x, y, item.is_through
                )
                if segment_y_ is not None:
                    push(
                        item.bends + 1,
                        item.length
                        + abs(x - target_x)
                        + (segment_y_ - y)
                        + (segment_y_ - self._channel_y(item.channel)),
                        True,
                        item.channel,
                        item.point,
                        item.is_through,
                        item.path,
                        item.levels[:-1] + (segment_y_,),
                    )
                continue
            for neighbor_ in self._neighbors(item.channel, chain):
                if neighbor_ in item.path:
                    continue
                turn_ = self._turn_point(item.channel, neighbor_)
                if not item.channel.is_horizontal:
                    push(
                        item.bends + 1,
                        item.length + abs(y - turn_[1]),
                        False,
                        neighbor_,
                        turn_,
                        False,
                        item.path + (neighbor_,),
                        item.levels + (turn_[1],),
                    )
                    continue
                # The segment in this horizontal channel ends at the
                # vertical channel: by a turn or by a through pass.
                segment_y_ = self._segment_y(
                    item.channel,
                    start_x,
                    self._face_x(neighbor_, item.channel, turn_[0]),
                    y,
                    item.is_through,
                )
                if segment_y_ is None:
                    continue
                length_ = item.length + abs(x - turn_[0]) + (segment_y_ - y)
                next_point_ = (turn_[0], segment_y_)
                closed_levels_ = item.levels[:-1] + (segment_y_, turn_[0])
                push(
                    item.bends + 1,
                    length_,
                    False,
                    neighbor_,
                    next_point_,
                    False,
                    item.path + (neighbor_,),
                    closed_levels_,
                )
                for through_ in self._through_passes(
                    item.channel,
                    x,
                    neighbor_,
                    segment_y_,
                    chain,
                    item.is_through,
                ):
                    if through_ not in item.path:
                        push(
                            item.bends,
                            length_,
                            False,
                            through_,
                            next_point_,
                            True,
                            item.path + (neighbor_, through_),
                            closed_levels_ + (segment_y_,),
                        )
        return None

    def _through_passes(
        self,
        channel: StructureChannelId,
        x: float,
        vertical: StructureChannelId,
        y: float,
        chain: FrozenSet[Optional[str]],
        is_through: bool,
    ) -> List[StructureChannelId]:
        """
        Return the channels that a horizontal line enters by a through pass.

        spec.md, section "Сквозной проход". The line goes along the channel
        from x at the height y and crosses the vertical channel straight.
        The other side of the vertical channel is a column. The line
        continues there at the same height:

        - a column of simple nodes: in a column channel whose lane lies at
          this height;
        - a column of a container on the chain: in a horizontal channel of
          the container at the facing side face whose lane lies at this
          height;
        - in both cases, in the space under the column (the bottom
          corridor), if the columns it passes over end at least the
          clearance above.

        A through pass keeps the height of a lane. A segment under the
        columns that came by a turn has no lane of its own, so it does not
        continue by a through pass, and the bottom corridor of a child
        container is not a target: it has no lane to keep.

        In the route, the through pass is a vertical segment of zero length,
        so the channels still alternate.
        """

        container_id = vertical.container_id
        columns = self.layout.columns[container_id]
        vertical_x = _center_x(self.channel_rects[vertical])
        column_index = vertical.index if x < vertical_x else vertical.index - 1
        if not 0 <= column_index < len(columns):
            return []
        column = columns[column_index]
        # The space under the column belongs to this container: the line can
        # always pass there, see _segment_y.
        candidates: List[StructureChannelId] = [
            StructureChannelId(ChannelKind.BOTTOM_CORRIDOR, container_id)
        ]
        if not column.is_composite:
            candidates.extend(
                StructureChannelId(
                    ChannelKind.COLUMN, container_id, column_index, gap_
                )
                for gap_ in range(len(column.node_ids) - 1)
            )
        elif column.node_ids[0] in chain:
            # The channels of the container at the facing side face that
            # have lanes.
            candidates.extend(
                horizontal_
                for horizontal_ in self.side_face_links.get(vertical, [])
                if horizontal_.container_id == column.node_ids[0]
                and horizontal_.kind is not ChannelKind.BOTTOM_CORRIDOR
            )
        if channel.kind is ChannelKind.BOTTOM_CORRIDOR:
            # A segment under the columns continues straight only with the
            # height of a lane it came with, and only into a lane.
            if not is_through:
                return []
            candidates = [
                candidate_
                for candidate_ in candidates
                if candidate_.kind is not ChannelKind.BOTTOM_CORRIDOR
            ]
        result = [
            candidate_
            for candidate_ in candidates
            if candidate_ != channel
            and (
                candidate_.kind is ChannelKind.BOTTOM_CORRIDOR
                or _center_y(self.channel_rects[candidate_]) == y
            )
        ]
        return result

    def _layers(self) -> List[FrozenSet[Optional[str]]]:
        """
        Return the containers by depth, the deepest layer first.
        """

        depths: Dict[Optional[str], int] = {None: 0}
        for node_ in self.normalized_graph.nodes:
            if node_.node_id in self.composite_ids:
                parent_id_ = self.normalized_graph.parent_ids[node_.node_id]
                depths[node_.node_id] = depths[parent_id_] + 1
        return [
            frozenset(
                container_id_
                for container_id_, depth_ in depths.items()
                if depth_ == depth
            )
            for depth in sorted(set(depths.values()), reverse=True)
        ]

    def _chain(
        self, source_id: str, target_id: str
    ) -> FrozenSet[Optional[str]]:
        """
        Return the containers of the chain of a relation.

        spec.md, section "Цепочка контейнеров": the containers of the source
        up to the common container, and down to the target.
        """

        def containers(node_id: str) -> List[Optional[str]]:
            result_: List[Optional[str]] = []
            parent_id_ = self.normalized_graph.parent_ids[node_id]
            while True:
                result_.append(parent_id_)
                if parent_id_ is None:
                    return result_
                parent_id_ = self.normalized_graph.parent_ids[parent_id_]

        source_containers = containers(source_id)
        target_containers = containers(target_id)
        common = next(
            container_id_
            for container_id_ in source_containers
            if container_id_ in target_containers
        )
        return frozenset(
            source_containers[: source_containers.index(common) + 1]
            + target_containers[: target_containers.index(common) + 1]
        )

    def _neighbors(
        self, channel: StructureChannelId, chain: FrozenSet[Optional[str]]
    ) -> List[StructureChannelId]:
        """
        Return the channels that touch a channel, within the chain.

        The channels of one container touch as in the layout. A crossing of
        a side face also joins a horizontal channel on one side of the face
        with a vertical channel on the other side, see _side_face_links.
        """

        return [
            neighbor_
            for neighbor_ in self.layout.neighbor_channels(channel)
            + self.side_face_links.get(channel, [])
            if neighbor_.container_id in chain
        ]

    def _face_x(
        self,
        vertical: StructureChannelId,
        horizontal: StructureChannelId,
        x: Optional[float] = None,
    ) -> float:
        """
        Return where a horizontal segment meets a vertical channel.

        If the vertical channel lies in a child container, the segment
        enters the child through its side face: the columns under the
        segment end at that face.
        """

        rect = self.channel_rects[vertical]
        if x is None:
            x = _center_x(rect)
        if vertical.container_id == horizontal.container_id:
            return x
        child_id = vertical.container_id
        if (
            child_id is None
            or self.normalized_graph.parent_ids[child_id]
            != horizontal.container_id
        ):
            return x
        frame = self.estimate.node_rects[child_id]
        return frame.x if vertical.index == 0 else frame.x + frame.width

    def _stub_length(
        self, node_id: str, face: Face, channel: StructureChannelId
    ) -> float:
        rect = self.estimate.node_rects[node_id]
        face_y = rect.y if face is Face.TOP else rect.y + rect.height
        return abs(face_y - self._channel_y(channel))

    def _turn_point(
        self, first: StructureChannelId, second: StructureChannelId
    ) -> Tuple[float, float]:
        horizontal, vertical = (
            (first, second) if first.is_horizontal else (second, first)
        )
        return (
            _center_x(self.channel_rects[vertical]),
            self._channel_y(horizontal),
        )

    def _channel_y(self, channel: StructureChannelId) -> float:
        """
        Return the height of a point in a horizontal channel.

        In the bottom corridor, the height is the lowest height a segment can
        take: the clearance below the shortest column.
        """

        if channel.kind is not ChannelKind.BOTTOM_CORRIDOR:
            return _center_y(self.channel_rects[channel])
        return (
            min(
                bottom_
                for _, _, bottom_ in self.column_spans[channel.container_id]
            )
            + self.config.lane_clearance
        )

    def _segment_y(
        self,
        channel: StructureChannelId,
        first_x: float,
        second_x: float,
        y: float,
        is_through: bool,
    ) -> Optional[float]:
        """
        Return the height of a segment in a horizontal channel.

        In the bottom corridor, a segment that came by a turn lies the
        clearance below the lowest column it passes over. A segment that
        came by a through pass keeps its height y. Return None if it would
        pass closer than the clearance to a column above it.
        """

        if channel.kind is not ChannelKind.BOTTOM_CORRIDOR:
            return _center_y(self.channel_rects[channel])
        lowest_y, through_y = corridor_segment_y(
            self.column_spans[channel.container_id],
            min(first_x, second_x),
            max(first_x, second_x),
            (y,) if is_through else (),
            self.config,
        )
        return through_y if is_through else lowest_y

    # Stage 4: lanes and ports.

    def _straight_ids(self, plans: List[_Plan]) -> Set[str]:
        """
        Return the straight edges. A gate has at most one straight edge.
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
        return straight_ids

    def _column_lane_counts(
        self, plans: List[_Plan], straight_ids: Set[str]
    ) -> Dict[StructureChannelId, int]:
        """
        Return the lane count of each column channel from the routes alone.

        This method is the only place of this rule. spec.md, section
        "Порядок расчёта". The count is known before the lanes, so the
        heights of the columns are exact when the lanes need them.

        A column channel has two halves by right-hand traffic: the segments
        that go left and the segments that go right. In one half, the
        segments to the left vertical channel overlap each other, and so do
        the segments to the right one. A segment to the left and a segment
        to the right do not overlap, because the ports of the left side of
        a face stand left of the ports of the right side. So they share
        lanes. A segment across the channel overlaps all segments of its
        half:

            lanes = sum over the two halves of
                    max(segments to the left, segments to the right)
                    + segments across

        A test checks that the lane assignment gives the same count.
        """

        # Channel -> half -> [to the left, to the right, across].
        counts: Dict[StructureChannelId, Dict[int, List[int]]] = {}
        for plan_ in plans:
            if plan_.edge.edge_id in straight_ids:
                continue
            channels_ = plan_.channels
            last_ = len(channels_) - 1
            for position_, channel_ in enumerate(channels_):
                if channel_.kind is not ChannelKind.COLUMN:
                    continue
                # The levels of the vertical channels are their x.
                if 0 < position_ < last_:
                    goes_left_ = (
                        plan_.levels[position_ + 1]
                        < plan_.levels[position_ - 1]
                    )
                    kind_ = 2
                elif position_ == 0 and last_ > 0:
                    to_left_ = plan_.levels[1] < _center_x(
                        self.estimate.node_rects[plan_.edge.source_id]
                    )
                    goes_left_ = to_left_
                    kind_ = 0 if to_left_ else 1
                elif position_ == last_ and last_ > 0:
                    from_left_ = plan_.levels[last_ - 1] < _center_x(
                        self.estimate.node_rects[plan_.edge.target_id]
                    )
                    goes_left_ = not from_left_
                    kind_ = 0 if from_left_ else 1
                else:
                    # From a port to a port of the same channel.
                    goes_left_ = False
                    kind_ = 2
                half_ = 0 if goes_left_ else 1
                counts.setdefault(channel_, {}).setdefault(half_, [0, 0, 0])[
                    kind_
                ] += 1
        return {
            channel_: sum(
                max(left_, right_) + across_
                for left_, right_, across_ in halves_.values()
            )
            for channel_, halves_ in counts.items()
        }

    def _exact_levels(
        self,
        plan: _Plan,
        exact: StructureGeometry,
        finished_levels: Mapping[Tuple[str, int], float],
    ) -> _Plan:
        """
        Return the plan with the levels of the exact column heights.

        A segment under the columns takes the level of a column channel that
        it continues across a vertical channel, if that level fits under the
        columns. The geometry follows the same rule, see
        CorridorSegment.through_lanes. A segment of a finished container
        keeps the exact height of its lane: the height of its pass port.
        """

        rects = {
            channel_.channel_id: channel_.rect for channel_ in exact.channels
        }
        spans = _column_spans(self.layout, exact)
        channels = plan.channels
        last = len(channels) - 1
        levels = list(plan.levels)
        for position_, channel_ in enumerate(channels):
            if not channel_.is_horizontal:
                continue
            finished_level_ = finished_levels.get(
                (plan.edge.edge_id, position_)
            )
            if finished_level_ is not None:
                levels[position_] = finished_level_
                continue
            if channel_.kind is not ChannelKind.BOTTOM_CORRIDOR:
                levels[position_] = _center_y(rects[channel_])
                continue
            ends_x_ = (
                _center_x(exact.node_rects[plan.edge.source_id])
                if position_ == 0
                else levels[position_ - 1],
                _center_x(exact.node_rects[plan.edge.target_id])
                if position_ == last
                else levels[position_ + 1],
            )
            lowest_y_, through_y_ = corridor_segment_y(
                spans[channel_.container_id],
                min(ends_x_),
                max(ends_x_),
                (
                    _center_y(rects[channels[other_]])
                    for other_ in (position_ - 2, position_ + 2)
                    if 0 <= other_ <= last
                    and _is_lane_of_container_or_child(
                        channels[other_],
                        channel_.container_id,
                        self.normalized_graph.parent_ids,
                    )
                ),
                self.config,
            )
            levels[position_] = lowest_y_ if through_y_ is None else through_y_
        return _Plan(
            index=plan.index,
            edge=plan.edge,
            source_face=plan.source_face,
            target_face=plan.target_face,
            channels=channels,
            levels=tuple(levels),
            is_straight_candidate=plan.is_straight_candidate,
        )

    def _assign_vertical_lanes(
        self,
        plans: List[_Plan],
        conflicts: List[StructureLaneConflict],
        layer: FrozenSet[Optional[str]],
    ) -> Dict[Tuple[str, int], int]:
        segments_by_channel: Dict[StructureChannelId, List[LaneSegment]] = {}
        for plan_ in plans:
            channels_ = plan_.channels
            for position_ in range(1, len(channels_), 2):
                channel_ = channels_[position_]
                if channel_.container_id not in layer:
                    continue
                vertical_x_ = plan_.levels[position_]
                entry_y_ = plan_.levels[position_ - 1]
                exit_y_ = plan_.levels[position_ + 1]
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
        # The lanes of a parent vertical channel are not known yet when a
        # child container is done: its center stands for them.
        return (
            _center_x(self.channel_rects[channel]),
            vertical_lanes.get((plan.edge.edge_id, position), 0),
        )

    def _assign_ports(
        self,
        plans: List[_Plan],
        vertical_lanes: Dict[Tuple[str, int], int],
        straight_ids: Set[str],
        layer: FrozenSet[Optional[str]],
    ) -> Dict[EndpointKey, Port]:
        """
        Collect the endpoints of each gate and number the ports.

        A gate is a horizontal channel and a column. A gate has at most one
        straight edge.
        """

        moved_keys = self._moved_horizontal_keys(plans)
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
                goes_left_ = self._goes_left(plan_, position_)
                gate_ = (
                    plan_.channels[position_],
                    self.layout.places[node_id_].column,
                )
                if gate_[0].container_id not in layer:
                    continue
                flows_down_ = (role_ == _SOURCE) == (face_ is Face.BOTTOM)
                if (plan_.edge.edge_id, position_) in moved_keys:
                    # A forced order moves the segment to the other half.
                    goes_left_ = not goes_left_
                endpoints_by_gate.setdefault(gate_, []).append(
                    GateEndpoint(
                        endpoint_key=(plan_.edge.edge_id, role_),
                        node_id=node_id_,
                        face=face_,
                        side=side_,
                        half=0 if goes_left_ else 1,
                        sort_key=(other_position_, plan_.index),
                        flows_down=flows_down_,
                    )
                )
        ports: Dict[EndpointKey, Port] = {}
        for endpoints_ in endpoints_by_gate.values():
            ports.update(number_gate_ports(endpoints_, self.forced_port_orders))
        return ports

    def _moved_horizontal_keys(
        self, plans: List[_Plan]
    ) -> Set[Tuple[str, int]]:
        """
        Return the horizontal segments that a forced order moves.

        A forced order moves the inner segment to the half of the outer one.
        """

        plans_by_edge = {plan_.edge.edge_id: plan_ for plan_ in plans}

        def goes_left(key: Tuple[str, int]) -> bool:
            return self._goes_left(plans_by_edge[key[0]], key[1])

        return {
            order_.inner
            for channel_, orders_ in self.forced_orders.items()
            if channel_.is_horizontal
            for order_ in orders_
            if goes_left(order_.inner) != goes_left(order_.outer)
        }

    def _goes_left(self, plan: _Plan, position: int) -> bool:
        """
        Return True if the horizontal segment at the position goes left.
        """

        last = len(plan.channels) - 1
        entry_x = (
            _center_x(self.estimate.node_rects[plan.edge.source_id])
            if position == 0
            else plan.levels[position - 1]
        )
        exit_x = (
            _center_x(self.estimate.node_rects[plan.edge.target_id])
            if position == last
            else plan.levels[position + 1]
        )
        return exit_x < entry_x

    def _assign_horizontal_lanes(
        self,
        plans: List[_Plan],
        ports: Dict[EndpointKey, Port],
        straight_ids: Set[str],
        vertical_lanes: Dict[Tuple[str, int], int],
        conflicts: List[StructureLaneConflict],
        layer: FrozenSet[Optional[str]],
    ) -> Dict[Tuple[str, int], int]:
        segments_by_channel: Dict[StructureChannelId, List[LaneSegment]] = {}
        for plan_ in plans:
            edge_id_ = plan_.edge.edge_id
            if edge_id_ in straight_ids:
                continue
            channels_ = plan_.channels
            last_ = len(channels_) - 1
            for position_ in range(0, len(channels_), 2):
                if channels_[position_].container_id not in layer:
                    continue
                channel_y_ = plan_.levels[position_]
                # A through pass has no perpendicular member: the segment
                # leaves the channel straight.
                members_: List[CrossMember] = []
                if position_ == 0:
                    entry_ = self._port_position(
                        ports[(edge_id_, _SOURCE)], plan_.edge.source_id
                    )
                    # The source stub reaches the node below or above the
                    # channel.
                    members_.append(
                        CrossMember(
                            position=entry_,
                            to_high_side=plan_.source_face is Face.TOP,
                            is_entry=True,
                        )
                    )
                else:
                    entry_ = self._vertical_lane_x(
                        plan_, position_ - 1, vertical_lanes
                    )
                    previous_y_ = plan_.levels[position_ - 2]
                    if previous_y_ != channel_y_:
                        members_.append(
                            CrossMember(
                                position=entry_,
                                to_high_side=previous_y_ > channel_y_,
                                is_entry=True,
                            )
                        )
                if position_ == last_:
                    exit_ = self._port_position(
                        ports[(edge_id_, _TARGET)], plan_.edge.target_id
                    )
                    members_.append(
                        CrossMember(
                            position=exit_,
                            to_high_side=plan_.target_face is Face.TOP,
                            is_entry=False,
                        )
                    )
                else:
                    exit_ = self._vertical_lane_x(
                        plan_, position_ + 1, vertical_lanes
                    )
                    next_y_ = plan_.levels[position_ + 2]
                    if next_y_ != channel_y_:
                        members_.append(
                            CrossMember(
                                position=exit_,
                                to_high_side=next_y_ > channel_y_,
                                is_entry=False,
                            )
                        )
                segments_by_channel.setdefault(channels_[position_], []).append(
                    LaneSegment(
                        key=(edge_id_, position_),
                        edge_id=edge_id_,
                        low=min(entry_, exit_),
                        high=max(entry_, exit_),
                        # Right-hand traffic: left in the top half, right in
                        # the bottom half.
                        half=0 if exit_ < entry_ else 1,
                        members=tuple(members_),
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
                segments_,
                self.options.lane_conflict_priority,
                self.forced_orders.get(channel_, []),
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


def _plan_lanes(
    plan: _Plan,
    vertical_lanes: Mapping[Tuple[str, int], int],
    horizontal_lanes: Mapping[Tuple[str, int], int],
) -> Tuple[int, ...]:
    """
    Return the lanes of a plan; a lane not assigned yet is 0.
    """

    return tuple(
        (vertical_lanes if position_ % 2 == 1 else horizontal_lanes).get(
            (plan.edge.edge_id, position_), 0
        )
        for position_ in range(len(plan.channels))
    )


def _lane_counts(
    plans: List[_Plan],
    straight_ids: Set[str],
    vertical_lanes: Mapping[Tuple[str, int], int],
    horizontal_lanes: Mapping[Tuple[str, int], int],
    containers: Set[Optional[str]],
) -> Dict[StructureChannelId, int]:
    """
    Return the lane counts of the channels of the containers.

    The bottom corridor places its segments by itself, so it has no count.
    """

    result: Dict[StructureChannelId, int] = {}
    for plan_ in plans:
        if plan_.edge.edge_id in straight_ids:
            continue
        lanes_ = _plan_lanes(plan_, vertical_lanes, horizontal_lanes)
        for channel_, lane_ in zip(plan_.channels, lanes_):
            if (
                channel_.container_id in containers
                and channel_.kind is not ChannelKind.BOTTOM_CORRIDOR
            ):
                result[channel_] = max(result.get(channel_, 0), lane_ + 1)
    return result


def _bottom_segments(
    plans: List[_Plan],
    straight_ids: Set[str],
    vertical_lanes: Mapping[Tuple[str, int], int],
    horizontal_lanes: Mapping[Tuple[str, int], int],
    containers: Set[Optional[str]],
    parent_ids: Mapping[str, Optional[str]],
) -> List[CorridorSegment]:
    """
    Return the segments in the bottom corridors of the containers.
    """

    result: List[CorridorSegment] = []
    for plan_ in plans:
        if plan_.edge.edge_id in straight_ids:
            continue
        route_ = StructureRoute(
            edge_id=plan_.edge.edge_id,
            source_port=Port(plan_.edge.source_id, plan_.source_face, 0),
            target_port=Port(plan_.edge.target_id, plan_.target_face, 0),
            channels=plan_.channels,
            lanes=_plan_lanes(plan_, vertical_lanes, horizontal_lanes),
        )
        result.extend(
            segment_
            for segment_ in _route_bottom_segments(route_, parent_ids)
            if segment_.container_id in containers
        )
    return result


def _route_bottom_segments(
    route: StructureRoute, parent_ids: Mapping[str, Optional[str]]
) -> List[CorridorSegment]:
    return [
        CorridorSegment(
            key=(route.edge_id, position_),
            container_id=channel_.container_id,
            lane=lane_,
            ends=(
                _segment_end(route, position_ - 1),
                _segment_end(route, position_ + 1),
            ),
            through_lanes=_through_lanes(route, position_, parent_ids),
        )
        for position_, (channel_, lane_) in enumerate(
            zip(route.channels, route.lanes)
        )
        if channel_.kind is ChannelKind.BOTTOM_CORRIDOR
    ]


def _finished_levels(
    plans: List[_Plan],
    straight_ids: Set[str],
    horizontal_lanes: Mapping[Tuple[str, int], int],
    containers: Set[Optional[str]],
    geometry: StructureGeometry,
) -> Dict[Tuple[str, int], float]:
    """
    Return the exact height of each horizontal segment of the containers.
    """

    result: Dict[Tuple[str, int], float] = {}
    for plan_ in plans:
        if plan_.edge.edge_id in straight_ids:
            continue
        for position_ in range(0, len(plan_.channels), 2):
            channel_ = plan_.channels[position_]
            key_ = (plan_.edge.edge_id, position_)
            if channel_.container_id not in containers:
                continue
            if channel_.kind is ChannelKind.BOTTOM_CORRIDOR:
                result[key_] = geometry.bottom_segment_lines[key_][2]
                continue
            rect_ = geometry.channel_rect(channel_)
            result[key_] = rect_.y + centered_lane_offset(
                rect_.height,
                geometry.lane_counts[channel_],
                horizontal_lanes[key_],
                geometry.config,
            )
    return result


def _segment_end(route: StructureRoute, position: int) -> SegmentEnd:
    """
    Return the end of a horizontal segment at a neighbor position.

    Outside the route, the end is a port. Inside, it is the lane of the
    vertical channel at that position.
    """

    if position < 0:
        port = route.source_port
    elif position >= len(route.channels):
        port = route.target_port
    else:
        return LaneEnd(
            channel=route.channels[position], lane=route.lanes[position]
        )
    return PortEnd(
        node_id=port.node_id, slot=port.slot, list_size=port.list_size
    )


def _side_face_links(
    layout: StructureLayout,
) -> Dict[StructureChannelId, List[StructureChannelId]]:
    """
    Link the channels of each container with its parent at the side faces.

    A crossing of a side face joins a horizontal channel on one side with a
    vertical channel on the other side, in both directions: a horizontal
    channel of the container at its outer vertical channel with the
    vertical channel of the parent next to the face, and the space under the
    columns of the parent with the outer vertical channel of the container.
    """

    result: Dict[StructureChannelId, List[StructureChannelId]] = {}
    for container_id_, columns_ in layout.columns.items():
        for column_index_, column_ in enumerate(columns_):
            if not column_.is_composite:
                continue
            child_id_ = column_.node_ids[0]
            child_columns_ = layout.columns[child_id_]
            for parent_index_, child_index_ in (
                (column_index_, 0),
                (column_index_ + 1, len(child_columns_)),
            ):
                parent_vertical_ = StructureChannelId(
                    ChannelKind.VERTICAL, container_id_, parent_index_
                )
                child_vertical_ = StructureChannelId(
                    ChannelKind.VERTICAL, child_id_, child_index_
                )
                for horizontal_ in layout.neighbor_channels(child_vertical_):
                    if not horizontal_.is_horizontal:
                        continue
                    result.setdefault(parent_vertical_, []).append(horizontal_)
                    result.setdefault(horizontal_, []).append(parent_vertical_)
                # A line under the columns of the parent crosses the face
                # straight and turns in the outer vertical channel of the
                # child. Only the space under the columns: its height can go
                # down below the top corridor of the child, a lane of a
                # column channel cannot.
                corridor_ = StructureChannelId(
                    ChannelKind.BOTTOM_CORRIDOR, container_id_
                )
                result.setdefault(child_vertical_, []).append(corridor_)
                result.setdefault(corridor_, []).append(child_vertical_)
    return result


def _through_lanes(
    route: StructureRoute,
    position: int,
    parent_ids: Mapping[str, Optional[str]],
) -> Tuple[LaneEnd, ...]:
    """
    Return the lanes that a segment under the columns can continue straight.

    The candidates are the column channels and top corridors on both sides
    of the segment, across a vertical channel, in the same container or in
    a child container. The entry comes first. A lane of the parent does not
    count: the parent is placed later, so its lane height is not known yet.
    """

    return tuple(
        LaneEnd(channel=route.channels[other_], lane=route.lanes[other_])
        for other_ in (position - 2, position + 2)
        if 0 <= other_ < len(route.channels)
        and _is_lane_of_container_or_child(
            route.channels[other_],
            route.channels[position].container_id,
            parent_ids,
        )
    )


def _is_lane_of_container_or_child(
    channel: StructureChannelId,
    container_id: Optional[str],
    parent_ids: Mapping[str, Optional[str]],
) -> bool:
    """
    Return True for a lane channel of the container or of its child.
    """

    if channel.kind not in (ChannelKind.COLUMN, ChannelKind.TOP_CORRIDOR):
        return False
    if channel.container_id == container_id:
        return True
    return (
        channel.container_id is not None
        and parent_ids[channel.container_id] == container_id
    )


def _column_spans(
    layout: StructureLayout, geometry: StructureGeometry
) -> Dict[Optional[str], List[Tuple[float, float, float]]]:
    """
    Return (left, right, bottom) of each column of each container.
    """

    return {
        container_id_: [
            _column_span([geometry.node_rects[id_] for id_ in column_.node_ids])
            for column_ in columns_
        ]
        for container_id_, columns_ in layout.columns.items()
    }


def _column_span(rects: List[Rect]) -> Tuple[float, float, float]:
    return (
        min(rect_.x for rect_ in rects),
        max(rect_.x + rect_.width for rect_ in rects),
        max(rect_.y + rect_.height for rect_ in rects),
    )


def _center_x(rect: Rect) -> float:
    return rect.x + rect.width / 2


def _center_y(rect: Rect) -> float:
    return rect.y + rect.height / 2
