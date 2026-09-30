"""
Geometry checks shared by the tests of the layout modes.
"""

from itertools import combinations
from typing import Callable, Dict, List, Mapping, Tuple

from strictdoc.features.specification_graph.svg_graph.levels_geometry import (
    Point,
    Rect,
)

_Segment = Tuple[Point, Point]


def geometry_problems(
    edge_paths: Mapping[str, Tuple[Point, ...]],
    width: float,
    height: float,
    obstacles_for_edge: Callable[[str], Mapping[str, Rect]],
) -> List[str]:
    """
    Check the result invariants from spec.md, section "Инварианты результата".

    Two relations may cross only perpendicularly inside the segments of both
    relations. A relation must not pass through its obstacles: the nodes and
    the containers that do not hold its endpoints.
    """

    problems: List[str] = []
    segments_by_edge: Dict[str, List[_Segment]] = {
        edge_id_: [
            (start_, end_)
            for start_, end_ in zip(path_, path_[1:])
            if start_ != end_
        ]
        for edge_id_, path_ in edge_paths.items()
    }
    for edge_id_, segments_ in segments_by_edge.items():
        obstacles_ = obstacles_for_edge(edge_id_)
        for start_, end_ in segments_:
            if start_.x != end_.x and start_.y != end_.y:
                problems.append(f"{edge_id_}: diagonal segment")
            for point_ in (start_, end_):
                if not (0 <= point_.x <= width and 0 <= point_.y <= height):
                    problems.append(f"{edge_id_}: point outside the SVG")
            for node_id_, rect_ in obstacles_.items():
                if (
                    max(start_.x, end_.x) > rect_.x
                    and min(start_.x, end_.x) < rect_.x + rect_.width
                    and max(start_.y, end_.y) > rect_.y
                    and min(start_.y, end_.y) < rect_.y + rect_.height
                ):
                    problems.append(f"{edge_id_}: passes through {node_id_}")

    for (first_id_, first_), (second_id_, second_) in combinations(
        segments_by_edge.items(), 2
    ):
        for first_segment_ in first_:
            for second_segment_ in second_:
                if _collinear_contact(first_segment_, second_segment_):
                    problems.append(
                        f"{first_id_} and {second_id_}: shared or touching "
                        "segment"
                    )
        for bend_owner_, bends_, other_id_, other_segments_ in (
            (first_id_, edge_paths[first_id_][1:-1], second_id_, second_),
            (second_id_, edge_paths[second_id_][1:-1], first_id_, first_),
        ):
            for bend_ in bends_:
                if any(
                    _point_on_segment(bend_, segment_)
                    for segment_ in other_segments_
                ):
                    problems.append(
                        f"{bend_owner_}: bend on {other_id_} at "
                        f"({bend_.x}, {bend_.y})"
                    )
    return problems


def crossing_count(first: Tuple[Point, ...], second: Tuple[Point, ...]) -> int:
    """
    Count the perpendicular crossings of two polylines.
    """

    count = 0
    for first_start_, first_end_ in zip(first, first[1:]):
        for second_start_, second_end_ in zip(second, second[1:]):
            for horizontal_, vertical_ in (
                ((first_start_, first_end_), (second_start_, second_end_)),
                ((second_start_, second_end_), (first_start_, first_end_)),
            ):
                if not (
                    horizontal_[0].y == horizontal_[1].y
                    and vertical_[0].x == vertical_[1].x
                ):
                    continue
                if min(horizontal_[0].x, horizontal_[1].x) < vertical_[
                    0
                ].x < max(horizontal_[0].x, horizontal_[1].x) and min(
                    vertical_[0].y, vertical_[1].y
                ) < horizontal_[0].y < max(vertical_[0].y, vertical_[1].y):
                    count += 1
    return count


def _collinear_contact(first: _Segment, second: _Segment) -> bool:
    for axis_, other_axis_ in (("y", "x"), ("x", "y")):
        values_ = {getattr(point_, axis_) for point_ in (*first, *second)}
        if len(values_) != 1:
            continue
        low_ = max(
            min(getattr(point_, other_axis_) for point_ in first),
            min(getattr(point_, other_axis_) for point_ in second),
        )
        high_ = min(
            max(getattr(point_, other_axis_) for point_ in first),
            max(getattr(point_, other_axis_) for point_ in second),
        )
        if low_ <= high_:
            return True
    return False


def _point_on_segment(point: Point, segment: _Segment) -> bool:
    start, end = segment
    if start.x == end.x == point.x:
        return min(start.y, end.y) <= point.y <= max(start.y, end.y)
    if start.y == end.y == point.y:
        return min(start.x, end.x) <= point.x <= max(start.x, end.x)
    return False
