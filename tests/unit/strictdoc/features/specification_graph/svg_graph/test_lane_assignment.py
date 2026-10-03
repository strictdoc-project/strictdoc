from typing import Tuple

from strictdoc.features.specification_graph.svg_graph.lane_assignment import (
    CrossMember,
    LaneConflictPriority,
    LaneSegment,
    assign_lanes,
)


def _segment(
    edge_id: str,
    low: float,
    high: float,
    members: Tuple[Tuple[float, bool, bool], ...],
    order: int,
) -> LaneSegment:
    """
    Create a segment of the first half of a channel.

    Each member is (position, extends toward the high side, is the entry).
    The order sets the order in which the pairs of segments are visited.
    """

    return LaneSegment(
        key=(edge_id, 0),
        edge_id=edge_id,
        low=(low, 0),
        high=(high, 0),
        half=0,
        members=tuple(
            CrossMember(
                position=(position_, 0),
                to_high_side=to_high_side_,
                is_entry=is_entry_,
            )
            for position_, to_high_side_, is_entry_ in members
        ),
        order_key=((order, 0), order),
    )


def test_coincident_ends_win_over_a_crossing() -> None:
    """
    Two ends at the same position that extend to different sides decide
    the order, even against an end that asks for the other order.

    At 0, the end of A goes up and the end of B goes down. If A lay below
    B, the two ends would lie on top of each other. The end of A at 10
    goes down inside B and asks A to lie below B: that order only avoids a
    crossing, so it gives way.

    Code: lane_assignment._coincident_order.
    Fails if:
    - ends at the same position set no order.
    """

    first = _segment("A", 0, 10, ((0, False, True), (10, True, False)), 0)
    second = _segment("B", 0, 20, ((0, True, True), (20, False, False)), 1)

    lanes, _ = assign_lanes([first, second], LaneConflictPriority.EXIT)

    assert lanes[first.key] < lanes[second.key]


def test_weaker_order_gives_way_in_a_cycle() -> None:
    """
    If the orders of three segments form a cycle, the weakest order is
    dropped.

    A lies above B: their ends coincide at 0. B lies above C: both ends of
    C go down inside B. A and C have an unavoidable crossing, and the exit
    priority puts C above A. The three orders form a cycle; the order from
    the unavoidable crossing is the weakest, so it is dropped. C comes
    first in the segment order, so neither the order of the visit nor a
    random break of the cycle gives the right result.

    Code: lane_assignment.assign_lanes.
    Fails if:
    - the orders are not taken by strength.
    - an order that closes a cycle is not dropped.
    """

    first = _segment("A", 0, 50, ((0, False, True), (50, True, False)), 1)
    second = _segment("B", 0, 100, ((0, True, True), (100, True, False)), 2)
    third = _segment("C", 20, 80, ((20, True, True), (80, True, False)), 0)

    lanes, _ = assign_lanes(
        [first, second, third], LaneConflictPriority.EXIT
    )

    assert lanes[first.key] < lanes[second.key] < lanes[third.key]
