"""
The ray map of the structure mode: base data about each relation.

spec.md, section "Карта лучей". The map does not route and does not change
the drawing. For each relation it gives the two ends of the line, the type
of their relative position, and a ray from each end to the point where the
line goes. A line does not depend on the direction of its relation, so its
ends are ordered by place: the first end lies left, or above in one column.
The map records which end is the source.
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Mapping, Optional, Tuple

from strictdoc.features.specification_graph.svg_graph.gate_ports import Face
from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    Rect,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedEdge,
    NormalizedGraph,
)
from strictdoc.features.specification_graph.svg_graph.structure_geometry import (
    StructureGeometry,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    StructureLayout,
)


class Height(Enum):
    # The second end lies below the first one, above it, or the two nodes
    # overlap in height.
    BELOW = "below"
    ABOVE = "above"
    LEVEL = "level"


@dataclass(frozen=True)
class PositionType:
    """
    The relative position of the two ends of a line.

    The axes, spec.md, section "Карта лучей":
    - side faces: the number of side faces of sections the line crosses on
      the way from the first end to the second one;
    - columns: the distance between the columns of the two ends in their
      common container: 0 for one column, 1 for neighbors;
    - height: where the second end lies relative to the first one;
    - blocked: whether a column between the two ends, in the common
      container, closes the straight line at the height of the first end
      and at the height of the second end.
    """

    side_faces: int
    columns: int
    height: Height
    blocked_at_first: bool
    blocked_at_second: bool


@dataclass(frozen=True)
class Ray:
    """
    A ray from one end of a line to the point where the line goes.

    The point is the center of the other end. If the other end lies inside
    a section next to the common container, the point lies on the side face
    of that section where the line enters it, at the height of the other
    end: the section is one target for the lines that go into it.
    """

    node_id: str
    point: Tuple[float, float]
    dx: float
    dy: float
    distance: float
    # The angle of the ray from the horizontal, in degrees: positive below
    # the horizontal, negative above.
    angle: float
    # The face the ray leaves: the top face if the point lies above the top
    # of the node, otherwise the bottom face.
    face: Face


@dataclass(frozen=True)
class RelationRays:
    edge_id: str
    first_end: str
    second_end: str
    source_is_first: bool
    position: PositionType
    first_ray: Ray
    second_ray: Ray


def compute_ray_map(
    normalized_graph: NormalizedGraph,
    layout: StructureLayout,
    geometry: StructureGeometry,
) -> Dict[str, RelationRays]:
    """
    Return the rays of each relation between two simple nodes in the row.

    The relations with a composite node and the relations of the root block
    are not in the map: the structure mode does not route them.
    """

    composite_ids = {
        node_.node_id
        for node_ in normalized_graph.nodes
        if len(node_.children) > 0
    }
    result: Dict[str, RelationRays] = {}
    for edge_ in normalized_graph.edges:
        if (
            edge_.source_id in composite_ids
            or edge_.target_id in composite_ids
            or edge_.source_id not in layout.places
            or edge_.target_id not in layout.places
        ):
            continue
        result[edge_.edge_id] = _relation_rays(
            edge_, normalized_graph, layout, geometry
        )
    return result


def _relation_rays(
    edge: NormalizedEdge,
    normalized_graph: NormalizedGraph,
    layout: StructureLayout,
    geometry: StructureGeometry,
) -> RelationRays:
    rects = geometry.node_rects
    source_first = _is_first(edge.source_id, edge.target_id, rects)
    first, second = (
        (edge.source_id, edge.target_id)
        if source_first
        else (edge.target_id, edge.source_id)
    )
    common = _common_container(first, second, normalized_graph)
    first_top = _top_ancestor(first, common, normalized_graph)
    second_top = _top_ancestor(second, common, normalized_graph)
    first_column = layout.places[first_top].column
    second_column = layout.places[second_top].column

    def point_of(end: str, end_top: str, other_top: str) -> Tuple[float, float]:
        x, y = _center(rects[end])
        if end_top == end:
            return x, y
        # The line enters the section through the face that looks toward
        # the other end.
        section = rects[end_top]
        if _center(rects[other_top])[0] < _center(section)[0]:
            return section.x, y
        return section.x + section.width, y

    first_point = point_of(second, second_top, first_top)
    second_point = point_of(first, first_top, second_top)
    blocked_at_first, blocked_at_second = (
        _is_blocked(
            _center(rects[end_])[1],
            first_column,
            second_column,
            common,
            layout,
            rects,
        )
        for end_ in (first, second)
    )
    return RelationRays(
        edge_id=edge.edge_id,
        first_end=first,
        second_end=second,
        source_is_first=source_first,
        position=PositionType(
            side_faces=_depth(first, common, normalized_graph)
            + _depth(second, common, normalized_graph),
            columns=abs(second_column - first_column),
            height=_height(rects[first], rects[second]),
            blocked_at_first=blocked_at_first,
            blocked_at_second=blocked_at_second,
        ),
        first_ray=_ray(first, first_point, rects[first]),
        second_ray=_ray(second, second_point, rects[second]),
    )


def _is_first(node_id: str, other_id: str, rects: Mapping[str, Rect]) -> bool:
    """
    Return True if the node is the first end: it lies left of the other
    end, or above it if the two have one x.
    """

    x, y = _center(rects[node_id])
    other_x, other_y = _center(rects[other_id])
    return (x, y) < (other_x, other_y)


def _container_chain(
    node_id: str, normalized_graph: NormalizedGraph
) -> List[Optional[str]]:
    chain: List[Optional[str]] = []
    parent_id = normalized_graph.parent_ids[node_id]
    while True:
        chain.append(parent_id)
        if parent_id is None:
            return chain
        parent_id = normalized_graph.parent_ids[parent_id]


def _common_container(
    first: str, second: str, normalized_graph: NormalizedGraph
) -> Optional[str]:
    second_chain = _container_chain(second, normalized_graph)
    return next(
        container_id_
        for container_id_ in _container_chain(first, normalized_graph)
        if container_id_ in second_chain
    )


def _top_ancestor(
    node_id: str, container_id: Optional[str], normalized_graph: NormalizedGraph
) -> str:
    """
    Return the child of the container that holds the node, or the node.
    """

    while normalized_graph.parent_ids[node_id] != container_id:
        parent_id = normalized_graph.parent_ids[node_id]
        assert parent_id is not None
        node_id = parent_id
    return node_id


def _depth(
    node_id: str, container_id: Optional[str], normalized_graph: NormalizedGraph
) -> int:
    """
    Return the number of sections between the node and the container.
    """

    return _container_chain(node_id, normalized_graph).index(container_id)


def _height(first: Rect, second: Rect) -> Height:
    if second.y >= first.y + first.height:
        return Height.BELOW
    if second.y + second.height <= first.y:
        return Height.ABOVE
    return Height.LEVEL


def _is_blocked(
    y: float,
    first_column: int,
    second_column: int,
    container_id: Optional[str],
    layout: StructureLayout,
    rects: Mapping[str, Rect],
) -> bool:
    """
    Return True if a column between the two columns reaches down to the
    height y: a straight line at that height would cross it.

    The columns stand at the top of the container, so a column reaches a
    height between its top and its bottom.
    """

    low, high = sorted((first_column, second_column))
    for column_ in layout.columns[container_id][low + 1 : high]:
        top_ = min(rects[node_id_].y for node_id_ in column_.node_ids)
        bottom_ = max(
            rects[node_id_].y + rects[node_id_].height
            for node_id_ in column_.node_ids
        )
        if top_ <= y <= bottom_:
            return True
    return False


def _ray(node_id: str, point: Tuple[float, float], rect: Rect) -> Ray:
    x, y = _center(rect)
    dx = point[0] - x
    dy = point[1] - y
    return Ray(
        node_id=node_id,
        point=point,
        dx=dx,
        dy=dy,
        distance=math.hypot(dx, dy),
        angle=math.degrees(math.atan2(dy, abs(dx)))
        if dx != 0 or dy != 0
        else 0.0,
        face=Face.TOP if point[1] < rect.y else Face.BOTTOM,
    )


def _center(rect: Rect) -> Tuple[float, float]:
    return rect.x + rect.width / 2, rect.y + rect.height / 2
