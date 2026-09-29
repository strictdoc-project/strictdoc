"""
Stages 5, 6, and 7 of the graph generator for the levels mode.

Stage 5 computes the channel sizes from the lane counts. Stage 6 computes the
node coordinates. Stage 7 converts the routes into polylines. Stage 7 does
not search for routes: it only converts lanes and ports into coordinates.
"""

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Tuple

from strictdoc.features.specification_graph.svg_graph.levels_routing import (
    ChannelId,
    EdgeRoute,
    Face,
    LevelsRouting,
    Orientation,
    Port,
)
from strictdoc.features.specification_graph.svg_graph.levels_structure import (
    LevelsStructure,
)


@dataclass(frozen=True)
class GeometryConfig:
    node_width: float = 160
    node_height: float = 52
    port_pitch: float = 12
    lane_pitch: float = 8
    min_channel_size: float = 24
    margin: float = 16


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
        _channel_size(
            routing.lane_counts.get(
                ChannelId(Orientation.HORIZONTAL, index_), 0
            ),
            config,
        )
        for index_ in range(-1, structure.row_count)
    ]
    vertical_sizes = [
        _channel_size(
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

    column_lefts: List[float] = []
    offset = config.margin + vertical_sizes[0]
    for column_ in range(structure.column_count):
        column_lefts.append(offset)
        offset += config.node_width + vertical_sizes[column_ + 1]
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
            else column_lefts[index_] + config.node_width
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
            width=config.node_width,
            height=config.node_height,
        )
        for node_id_, position_ in structure.positions.items()
    }

    edge_paths: Dict[str, Tuple[Point, ...]] = {
        edge_id_: _route_path(
            route_, node_rects, channel_rects, routing, config
        )
        for edge_id_, route_ in routing.routes.items()
    }
    return LevelsGeometry(
        width=width,
        height=height,
        node_rects=node_rects,
        edge_paths=edge_paths,
        channel_rects=channel_rects,
    )


def _channel_size(lane_count: int, config: GeometryConfig) -> float:
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


def _port_point(
    port: Port, node_rects: Dict[str, Rect], config: GeometryConfig
) -> Point:
    rect = node_rects[port.node_id]
    return Point(
        x=rect.x + rect.width / 2 + port.slot * config.port_pitch,
        y=rect.y if port.face is Face.TOP else rect.y + rect.height,
    )


def _route_path(
    route: EdgeRoute,
    node_rects: Dict[str, Rect],
    channel_rects: Dict[ChannelId, Rect],
    routing: LevelsRouting,
    config: GeometryConfig,
) -> Tuple[Point, ...]:
    start = _port_point(route.source_port, node_rects, config)
    end = _port_point(route.target_port, node_rects, config)
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
