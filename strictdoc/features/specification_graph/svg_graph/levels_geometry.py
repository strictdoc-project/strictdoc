"""
Stages 5, 6, and 7 of the graph generator for the levels mode.

Stage 5 computes the channel sizes from the lane counts. Stage 6 computes the
node coordinates. Stage 7 converts the routes into polylines. Stage 7 does
not search for routes: it only converts lanes and ports into coordinates.
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Mapping, Optional, Tuple

from strictdoc.features.specification_graph.svg_graph.gate_ports import (
    Face,
    Port,
)
from strictdoc.features.specification_graph.svg_graph.levels_routing import (
    ChannelId,
    EdgeRoute,
    LevelsRouting,
    Orientation,
)
from strictdoc.features.specification_graph.svg_graph.levels_structure import (
    LevelsStructure,
)


@dataclass(frozen=True)
class GeometryConfig:
    """
    Size parameters of the levels mode geometry, in pixels.

    The layout parameters define the space. The arrowhead size follows from
    them: the layout does not depend on the arrowhead style.

    The vertical sizes are set in lane pitches, so they are multiples of the
    lane pitch by construction. Then every horizontal segment lies on one
    grid: two segments of one relation lie at the same height or at least
    one lane pitch apart, and a step between them is never smaller than one
    lane pitch.
    """

    # Channels.
    # Distance between neighbor lanes in a channel. The unit of the vertical
    # sizes.
    lane_pitch: float = 8
    # Distance from the outermost lane of a horizontal channel to the node
    # face. The last segment of a relation, which ends with the arrowhead,
    # is at least this long.
    lane_clearance_pitches: int = 2
    # Size of a channel with few lanes or no lanes.
    min_channel_pitches: int = 3

    # Nodes.
    # Minimum node width. A column with crowded gates gets wider nodes.
    node_width: float = 160
    # Three lines of the title.
    node_height_pitches: int = 7

    # Ports.
    # Preferred distance between neighbor ports on a face.
    port_pitch: float = 12
    # A crowded port list shrinks its pitch down to this value. The gate
    # center shifts and the column widens before the pitch goes lower.
    min_port_pitch: float = 8
    # Minimum distance from the outermost port to the node corner.
    port_margin: float = 8

    # Containers (structure mode).
    # Height of the header strip: two lines of the title and the padding.
    container_header_pitches: int = 5

    # SVG.
    # Empty border around the graph.
    margin_pitches: int = 2

    # Arrowhead reserves. The arrowhead size is computed from them.
    # Straight part of the last segment before the arrowhead.
    arrow_straight: float = 10
    # Free space between two neighbor arrowheads at the minimum port pitch.
    arrow_gap: float = 2

    @property
    def lane_clearance(self) -> float:
        return self.lane_clearance_pitches * self.lane_pitch

    @property
    def min_channel_size(self) -> float:
        return self.min_channel_pitches * self.lane_pitch

    @property
    def node_height(self) -> float:
        return self.node_height_pitches * self.lane_pitch

    @property
    def container_header_height(self) -> float:
        return self.container_header_pitches * self.lane_pitch

    @property
    def margin(self) -> float:
        return self.margin_pitches * self.lane_pitch

    @property
    def arrow_length(self) -> float:
        return self.lane_clearance - self.arrow_straight

    @property
    def arrow_width(self) -> float:
        return self.min_port_pitch - self.arrow_gap


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class LevelsGeometry:
    # The parameters that produced this geometry. The serializer draws the
    # arrowheads with them, so the drawing always matches the layout.
    config: GeometryConfig
    width: float
    height: float
    node_rects: Mapping[str, Rect]
    edge_paths: Mapping[str, Tuple[Point, ...]]
    channel_rects: Mapping[ChannelId, Rect]


def compute_levels_geometry(
    structure: LevelsStructure,
    routing: LevelsRouting,
    config: Optional[GeometryConfig] = None,
) -> LevelsGeometry:
    if config is None:
        config = GeometryConfig()

    horizontal_sizes = [
        horizontal_channel_size(
            routing.lane_counts.get(
                ChannelId(Orientation.HORIZONTAL, index_), 0
            ),
            config,
        )
        for index_ in range(-1, structure.row_count)
    ]
    vertical_sizes = [
        vertical_channel_size(
            routing.lane_counts.get(ChannelId(Orientation.VERTICAL, index_), 0),
            config,
        )
        for index_ in range(-1, structure.column_count)
    ]

    # Channel with index i starts at offset i + 1 in the size lists.
    row_tops: List[float] = []
    offset = config.margin + horizontal_sizes[0]
    for row_ in range(structure.row_count):
        row_tops.append(offset)
        offset += config.node_height + horizontal_sizes[row_ + 1]
    height = offset + config.margin

    list_sizes_by_gate = _list_sizes_by_gate(structure, routing)
    column_widths = _column_widths(structure, list_sizes_by_gate, config)
    column_lefts: List[float] = []
    offset = config.margin + vertical_sizes[0]
    for column_ in range(structure.column_count):
        column_lefts.append(offset)
        offset += column_widths[column_] + vertical_sizes[column_ + 1]
    width = offset + config.margin

    channel_rects: Dict[ChannelId, Rect] = {}
    for index_ in range(-1, structure.row_count):
        top_ = (
            config.margin
            if index_ == -1
            else row_tops[index_] + config.node_height
        )
        channel_rects[ChannelId(Orientation.HORIZONTAL, index_)] = Rect(
            x=config.margin,
            y=top_,
            width=width - 2 * config.margin,
            height=horizontal_sizes[index_ + 1],
        )
    for index_ in range(-1, structure.column_count):
        left_ = (
            config.margin
            if index_ == -1
            else column_lefts[index_] + column_widths[index_]
        )
        channel_rects[ChannelId(Orientation.VERTICAL, index_)] = Rect(
            x=left_,
            y=config.margin,
            width=vertical_sizes[index_ + 1],
            height=height - 2 * config.margin,
        )

    node_rects: Dict[str, Rect] = {
        node_id_: Rect(
            x=column_lefts[position_.column],
            y=row_tops[position_.row],
            width=column_widths[position_.column],
            height=config.node_height,
        )
        for node_id_, position_ in structure.positions.items()
    }

    gate_layouts = {
        gate_: _gate_layout(list_sizes_, column_widths[gate_[0]], config)
        for gate_, list_sizes_ in list_sizes_by_gate.items()
    }

    def port_point(port: Port) -> Point:
        rect = node_rects[port.node_id]
        gate_layout = gate_layouts[_gate_of(port, structure)]
        x = rect.x + rect.width / 2 + gate_layout.center_offset
        if port.slot != 0:
            side = -1 if port.slot < 0 else 1
            pitch = min(
                config.port_pitch,
                gate_layout.side_widths[side] / port.list_size,
            )
            x += port.slot * pitch
        return Point(
            x=x, y=rect.y if port.face is Face.TOP else rect.y + rect.height
        )

    edge_paths: Dict[str, Tuple[Point, ...]] = {
        edge_id_: _route_path(
            route_, channel_rects, routing, config, port_point
        )
        for edge_id_, route_ in routing.routes.items()
    }
    return LevelsGeometry(
        config=config,
        width=width,
        height=height,
        node_rects=node_rects,
        edge_paths=edge_paths,
        channel_rects=channel_rects,
    )


def horizontal_channel_size(lane_count: int, config: GeometryConfig) -> float:
    """
    Return the size of a horizontal channel.

    The lane clearance keeps room for the arrowhead between the outermost
    lane and the node face on both sides.
    """

    if lane_count == 0:
        return config.min_channel_size
    return max(
        config.min_channel_size,
        (lane_count - 1) * config.lane_pitch + 2 * config.lane_clearance,
    )


def vertical_channel_size(lane_count: int, config: GeometryConfig) -> float:
    """
    Return the size of a vertical channel.

    The lanes run along the side faces of the nodes, where no arrowhead
    ends, so one lane pitch separates the outermost lane from a node.
    """

    return max(config.min_channel_size, (lane_count + 1) * config.lane_pitch)


def _lane_offset(
    channel: ChannelId,
    lane: int,
    channel_rects: Dict[ChannelId, Rect],
    routing: LevelsRouting,
    config: GeometryConfig,
) -> float:
    """
    Return the x of a vertical lane or the y of a horizontal lane.

    The lanes of a channel are centered in the channel.
    """

    rect = channel_rects[channel]
    lane_count = routing.lane_counts[channel]
    if channel.orientation is Orientation.HORIZONTAL:
        start, size = rect.y, rect.height
    else:
        start, size = rect.x, rect.width
    return (
        start
        + (size - (lane_count - 1) * config.lane_pitch) / 2
        + lane * config.lane_pitch
    )


# A gate: the column and the horizontal channel. See the ports rules in
# spec.md, section "Маршруты".
_Gate = Tuple[int, int]


@dataclass(frozen=True)
class _GateLayout:
    # Shift of the gate center from the node center. Both faces of a gate use
    # the same shift, so a straight edge stays straight.
    center_offset: float
    # Width available for the ports on each side of the center: -1 for the
    # left side, 1 for the right side.
    side_widths: Mapping[int, float]


def _gate_of(port: Port, structure: LevelsStructure) -> _Gate:
    position = structure.positions[port.node_id]
    channel = position.row - 1 if port.face is Face.TOP else position.row
    return position.column, channel


def _list_sizes_by_gate(
    structure: LevelsStructure, routing: LevelsRouting
) -> Dict[_Gate, Dict[int, int]]:
    """
    Return the longest port list on each side of each gate.
    """

    result: Dict[_Gate, Dict[int, int]] = {}
    for route_ in routing.routes.values():
        for port_ in (route_.source_port, route_.target_port):
            sizes_ = result.setdefault(
                _gate_of(port_, structure), {-1: 0, 1: 0}
            )
            if port_.slot != 0:
                side_ = -1 if port_.slot < 0 else 1
                sizes_[side_] = max(sizes_[side_], port_.list_size)
    return result


def _column_widths(
    structure: LevelsStructure,
    list_sizes_by_gate: Dict[_Gate, Dict[int, int]],
    config: GeometryConfig,
) -> List[float]:
    """
    Return the node width of each column.

    A gate needs room for the longest list on each side at the minimum port
    pitch. If the minimum node width is not enough even with a shifted gate
    center, all nodes of the column get wider.
    """

    widths = [config.node_width] * structure.column_count
    for (column_, _), sizes_ in list_sizes_by_gate.items():
        needed_ = (
            sizes_[-1] + sizes_[1]
        ) * config.min_port_pitch + 2 * config.port_margin
        widths[column_] = max(widths[column_], needed_)
    return widths


def _gate_layout(
    list_sizes: Dict[int, int], node_width: float, config: GeometryConfig
) -> _GateLayout:
    """
    Place the center of a gate.

    The center stays in the middle of the face while both sides fit at the
    minimum port pitch. If one side does not fit, the center moves toward
    the other side by the missing width. The column width guarantees that
    the other side still fits.
    """

    half_width = node_width / 2 - config.port_margin
    left_needed = list_sizes[-1] * config.min_port_pitch
    right_needed = list_sizes[1] * config.min_port_pitch
    center_offset = 0.0
    if left_needed > half_width:
        center_offset = left_needed - half_width
    elif right_needed > half_width:
        center_offset = half_width - right_needed
    return _GateLayout(
        center_offset=center_offset,
        side_widths={
            -1: half_width + center_offset,
            1: half_width - center_offset,
        },
    )


def _route_path(
    route: EdgeRoute,
    channel_rects: Dict[ChannelId, Rect],
    routing: LevelsRouting,
    config: GeometryConfig,
    port_point: Callable[[Port], Point],
) -> Tuple[Point, ...]:
    start = port_point(route.source_port)
    end = port_point(route.target_port)
    lane_offsets = [
        _lane_offset(lane_.channel, lane_.lane, channel_rects, routing, config)
        for lane_ in route.lanes
    ]
    if len(lane_offsets) == 0:
        return (start, end)
    if len(lane_offsets) == 1:
        lane_y = lane_offsets[0]
        return (
            start,
            Point(start.x, lane_y),
            Point(end.x, lane_y),
            end,
        )
    first_y, vertical_x, second_y = lane_offsets
    return (
        start,
        Point(start.x, first_y),
        Point(vertical_x, first_y),
        Point(vertical_x, second_y),
        Point(end.x, second_y),
        end,
    )
