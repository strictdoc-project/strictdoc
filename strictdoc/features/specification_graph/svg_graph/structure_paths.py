"""
Stage 7 of the graph generator for the structure mode: the edge polylines.

The stage converts the ports and the lanes of each route into coordinates.
The stage does not search for routes.
"""

from typing import Dict, Tuple

from strictdoc.features.specification_graph.svg_graph.gate_ports import (
    Face,
    Port,
)
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    Point,
)
from strictdoc.features.specification_graph.svg_graph.structure_geometry import (
    StructureGeometry,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    StructureChannelId,
)
from strictdoc.features.specification_graph.svg_graph.structure_routing import (
    StructureRoute,
    StructureRouting,
)


def compute_structure_edge_paths(
    routing: StructureRouting, geometry: StructureGeometry
) -> Dict[str, Tuple[Point, ...]]:
    return {
        edge_id_: _route_path(route_, geometry)
        for edge_id_, route_ in routing.routes.items()
    }


def _route_path(
    route: StructureRoute, geometry: StructureGeometry
) -> Tuple[Point, ...]:
    start = _port_point(route.source_port, geometry)
    end = _port_point(route.target_port, geometry)
    if len(route.lanes) == 0:
        return (start, end)
    points = [start]
    x = start.x
    y = start.y
    for channel_, lane_ in zip(route.channels, route.lanes):
        coordinate_ = _lane_coordinate(channel_, lane_, geometry)
        if channel_.is_horizontal:
            y = coordinate_
        else:
            x = coordinate_
        points.append(Point(x, y))
    points.append(Point(end.x, y))
    points.append(end)
    return tuple(points)


def _lane_coordinate(
    channel: StructureChannelId, lane: int, geometry: StructureGeometry
) -> float:
    """
    Return the y of a horizontal lane or the x of a vertical lane.

    The lanes of a channel are centered in the channel.
    """

    rect = geometry.channel_rect(channel)
    lane_count = geometry.lane_counts[channel]
    lane_pitch = geometry.config.lane_pitch
    if channel.is_horizontal:
        start, size = rect.y, rect.height
    else:
        start, size = rect.x, rect.width
    return (
        start + (size - (lane_count - 1) * lane_pitch) / 2 + lane * lane_pitch
    )


def _port_point(port: Port, geometry: StructureGeometry) -> Point:
    config = geometry.config
    rect = geometry.node_rects[port.node_id]
    x = rect.x + rect.width / 2
    if port.slot != 0:
        available_half_width = rect.width / 2 - config.port_margin
        pitch = min(config.port_pitch, available_half_width / port.list_size)
        x += port.slot * pitch
    return Point(
        x=x, y=rect.y if port.face is Face.TOP else rect.y + rect.height
    )
