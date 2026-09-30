"""
Stage 7 of the graph generator for the structure mode: the edge polylines.

The stage converts the ports and the lanes of each route into coordinates.
The stage does not search for routes.
"""

from typing import Dict, List, Tuple

from strictdoc.features.specification_graph.svg_graph.gate_ports import (
    Face,
    Port,
)
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    Point,
)
from strictdoc.features.specification_graph.svg_graph.structure_geometry import (
    StructureGeometry,
    centered_lane_offset,
    port_offset,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    ChannelKind,
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
    return _straighten(route_channel_points(route, geometry))


def route_channel_points(
    route: StructureRoute, geometry: StructureGeometry
) -> List[Point]:
    """
    Return the points of a route: the ports and one point per channel.

    Point i + 1 starts the segment in channel i. A through pass gives a
    vertical segment of zero length.
    """

    start = _port_point(route.source_port, geometry)
    end = _port_point(route.target_port, geometry)
    if len(route.lanes) == 0:
        return [start, end]
    points = [start]
    x = start.x
    y = start.y
    for position_, (channel_, lane_) in enumerate(
        zip(route.channels, route.lanes)
    ):
        if channel_.kind is ChannelKind.BOTTOM_CORRIDOR:
            _, _, y = geometry.bottom_segment_lines[(route.edge_id, position_)]
        elif channel_.is_horizontal:
            y = _lane_coordinate(channel_, lane_, geometry)
        else:
            x = _lane_coordinate(channel_, lane_, geometry)
        points.append(Point(x, y))
    points.append(Point(end.x, y))
    points.append(end)
    return points


def _straighten(points: List[Point]) -> Tuple[Point, ...]:
    """
    Remove the repeated points and the points inside straight runs.

    A through pass is a vertical segment of zero length, so its points
    repeat or lie on a straight line.
    """

    result: List[Point] = []
    for point_ in points:
        if len(result) > 0 and result[-1] == point_:
            continue
        if len(result) >= 2 and (
            result[-2].x == result[-1].x == point_.x
            or result[-2].y == result[-1].y == point_.y
        ):
            result[-1] = point_
            continue
        result.append(point_)
    return tuple(result)


def _lane_coordinate(
    channel: StructureChannelId, lane: int, geometry: StructureGeometry
) -> float:
    """
    Return the y of a horizontal lane or the x of a vertical lane.
    """

    rect = geometry.channel_rect(channel)
    if channel.is_horizontal:
        start, size = rect.y, rect.height
    else:
        start, size = rect.x, rect.width
    return start + centered_lane_offset(
        size, geometry.lane_counts[channel], lane, geometry.config
    )


def _port_point(port: Port, geometry: StructureGeometry) -> Point:
    rect = geometry.node_rects[port.node_id]
    return Point(
        x=rect.x
        + rect.width / 2
        + port_offset(port.slot, port.list_size, rect.width, geometry.config),
        y=rect.y if port.face is Face.TOP else rect.y + rect.height,
    )
