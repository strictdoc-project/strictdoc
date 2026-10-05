from typing import Optional, Tuple

import pytest

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
    base_level: Optional[float] = None,
    is_exact: bool = True,
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
                is_exact=is_exact,
            )
            for position_, to_high_side_, is_entry_ in members
        ),
        order_key=((order, 0), order),
        base_level=base_level,
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


def test_segment_that_fits_a_pocket_lies_higher() -> None:
    """
    Under the columns, of two overlapping segments, the one with the
    higher base height lies higher.

    A fits a pocket: its base height is 10, the base height of B is 30.
    One crossing is unavoidable. The exit priority would put A below B;
    the base heights put A above, so the crossing moves into the pocket.
    The base heights decide even if an end of A goes down: that side is
    known only at the base height of A. Two ends at one point do not
    change the order either.

    Code: lane_assignment._base_order, lane_assignment.assign_lanes.
    Fails if:
    - the base heights do not order the segments under the columns.
    - two ends at one point win over the base heights.
    """

    first = _segment(
        "A", 0, 50, ((0, False, False), (50, False, True)), 0, base_level=10
    )
    second = _segment(
        "B", 20, 100, ((20, False, False), (100, False, True)), 1, 30
    )
    lanes, _ = assign_lanes([first, second], LaneConflictPriority.EXIT)
    assert lanes[first.key] < lanes[second.key]

    going_down = _segment(
        "A", 20, 50, ((20, True, False), (50, True, True)), 0, base_level=10
    )
    lanes, _ = assign_lanes([going_down, second], LaneConflictPriority.EXIT)
    assert lanes[going_down.key] < lanes[second.key]


def test_stand_in_positions_do_not_coincide() -> None:
    """
    Ends at equal positions that stand for lanes not known yet set no
    order.

    The test of coincident ends with stand-in positions: at 0, the end of A
    goes up and the end of B goes down, but the lanes behind these
    positions are not known, so the ends need not lie on top of each
    other. The end of A at 10 goes down inside B and decides: A lies below
    B.

    Code: lane_assignment._coincident_order.
    Fails if:
    - a position that stands for an unknown lane counts as exact.
    """

    first = _segment(
        "A", 0, 10, ((0, False, True), (10, True, False)), 0, is_exact=False
    )
    second = _segment(
        "B", 0, 20, ((0, True, True), (20, False, False)), 1, is_exact=False
    )

    lanes, _ = assign_lanes([first, second], LaneConflictPriority.EXIT)

    assert lanes[first.key] > lanes[second.key]


@pytest.mark.parametrize(
    "priority", [LaneConflictPriority.ENTRY, LaneConflictPriority.EXIT]
)
def test_unavoidable_crossing_takes_the_order_with_fewer_lanes(
    priority: LaneConflictPriority,
) -> None:
    """
    An unavoidable crossing takes the order that gives the channel fewer
    lanes, whatever the priority of the crossing.

    X crosses the channel from 0 to 100. L runs from a port at 40 to the
    left end at 10, and its two ends ask for opposite orders against X: one
    crossing is unavoidable in either order. R runs from 90 to a port at
    60, and both of its ends go up inside X: R lies above X. L and R do not
    overlap. With X above L, the three segments take three lanes. With L
    above X, L shares the lane of R, and the channel takes two lanes.

    Code: lane_assignment._fewer_lanes_reversed.
    Fails if:
    - the priority of an unavoidable crossing decides against the lane
      count.
    """

    across = _segment("X", 0, 100, ((0, False, True), (100, True, False)), 0)
    left = _segment("L", 10, 40, ((40, False, True), (10, True, False)), 1)
    right = _segment("R", 60, 90, ((90, False, True), (60, False, False)), 2)

    lanes, _ = assign_lanes([across, left, right], priority)

    assert lanes[left.key] == lanes[right.key]
    assert lanes[right.key] < lanes[across.key]
    assert max(lanes.values()) == 1
