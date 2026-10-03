"""
Lane assignment in one channel, shared by the layout modes.

spec.md, section "Полосы в канале", defines the rules. A segment is the part
of a route inside one channel. A constraint graph orders the overlapping
segments of the channel.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Sequence, Set, Tuple


class LaneConflictPriority(Enum):
    """
    Which crossing to avoid when a segment lies inside another one.

    ENTRY keeps the entry verticals uncrossed: the outer segment crosses the
    vertical of the inner segment near the target. EXIT keeps the exit
    verticals uncrossed: the outer segment crosses the vertical of the inner
    segment near the source.
    """

    ENTRY = "entry"
    EXIT = "exit"


# Position along a channel. Positions compare as tuples.
LanePosition = Tuple[float, float]

# Key of a segment: the edge ID and the index of the segment in the route.
SegmentKey = Tuple[str, int]


@dataclass(frozen=True)
class CrossMember:
    """
    A perpendicular part of a route that touches a segment.

    For a horizontal segment, the members are its entry and exit verticals.
    For a vertical segment, the members are its entry and exit horizontals.
    """

    position: LanePosition
    # The member extends from the segment lane toward the high side of the
    # channel: the bottom of a horizontal channel or the right of a vertical
    # channel.
    to_high_side: bool
    is_entry: bool
    # The position is known exactly. A position that stands for a lane not
    # known yet, for example the center of a channel, is not exact: two
    # such positions can be equal while the lanes differ.
    is_exact: bool = True


@dataclass(frozen=True)
class LaneSegment:
    key: SegmentKey
    edge_id: str
    low: LanePosition
    high: LanePosition
    # The direction of travel. 0: left in a horizontal channel, down in a
    # vertical channel. Right-hand traffic puts a segment of direction 0
    # above (left of) an overlapping segment of direction 1 if nothing else
    # orders them.
    half: int
    # A segment that leaves the channel through its end, for example through
    # the side face of a container, has fewer members.
    members: Tuple[CrossMember, ...]
    order_key: Tuple[LanePosition, int]
    # Under the columns: the highest y the segment may take, the base
    # height. A segment that passes only under short columns has its base
    # height in a pocket. None in other channels.
    base_level: Optional[float] = None


@dataclass(frozen=True)
class ForcedOrder:
    """
    The order of two segments of a nested pair on a shared stretch.

    spec.md, section "Общий участок". This order wins over the ends of the
    two segments and over the direction of travel.
    """

    inner: SegmentKey
    outer: SegmentKey
    # The inner segment takes a larger lane than the outer one.
    inner_is_later: bool


@dataclass(frozen=True)
class LaneConflictPair:
    """
    Two segments with an unavoidable crossing in one channel.
    """

    outer_edge_id: str
    inner_edge_id: str


def assign_lanes(
    segments: List[LaneSegment],
    priority: LaneConflictPriority,
    forced: Sequence[ForcedOrder] = (),
) -> Tuple[Dict[SegmentKey, int], List[LaneConflictPair]]:
    """
    Assign lanes in one channel.

    A constraint graph orders the overlapping segments. Each order between
    two segments has a reason, and the reasons have strengths; a weaker
    order that contradicts the stronger ones is dropped. The direction of
    travel is the weakest reason: it orders only two overlapping segments
    of different directions whose ends set no order. The longest path from
    the first lane gives each segment its lane, so any segments without
    overlap can share a lane, whatever their directions.
    """

    conflicts: List[LaneConflictPair] = []
    # (earlier, later) -> the earlier segment takes the smaller lane.
    forced_pairs: Set[Tuple[SegmentKey, SegmentKey]] = {
        (order_.outer, order_.inner)
        if order_.inner_is_later
        else (order_.inner, order_.outer)
        for order_ in forced
    }
    segments = sorted(segments, key=lambda segment_: segment_.order_key)
    before: Dict[SegmentKey, Set[SegmentKey]] = {
        segment_.key: set() for segment_ in segments
    }
    # (strength, earlier, later): the earlier segment takes the smaller
    # lane. A smaller strength is a stronger reason.
    orders: List[Tuple[int, SegmentKey, SegmentKey]] = []
    for first_index_, first_ in enumerate(segments):
        for second_ in segments[first_index_ + 1 :]:
            coincident_ = _coincident_order(first_, second_)
            if coincident_ != 0:
                order_, strength_ = coincident_, _COINCIDENT
            elif (first_.key, second_.key) in forced_pairs:
                order_, strength_ = 1, _FORCED
            elif (second_.key, first_.key) in forced_pairs:
                order_, strength_ = -1, _FORCED
            elif _base_order(first_, second_) != 0:
                order_, strength_ = _base_order(first_, second_), _BASE
            else:
                conflict_count_ = len(conflicts)
                order_ = _pair_order(first_, second_, priority, conflicts)
                strength_ = _CROSSING
                if len(conflicts) > conflict_count_:
                    strength_ = _CONFLICT
            if order_ == 1:
                orders.append((strength_, first_.key, second_.key))
            elif order_ == -1:
                orders.append((strength_, second_.key, first_.key))
    # A stable sort keeps the segment order within one strength.
    for _, earlier_, later_ in sorted(orders, key=lambda order_: order_[0]):
        if not _comes_before(before, later_, earlier_):
            before[later_].add(earlier_)
    _order_free_pairs_by_direction(segments, before)
    return _longest_path_lanes(segments, before), conflicts


def _order_free_pairs_by_direction(
    segments: List[LaneSegment], before: Dict[SegmentKey, Set[SegmentKey]]
) -> None:
    """
    Order by the direction of travel the overlapping segments of different
    directions that are still free.

    Right-hand traffic: the segment of the first half comes first, that is
    the segment that goes left lies above, and the segment that goes up
    lies right. An order that contradicts the orders already set is
    skipped: the ends and the other reasons win.
    """

    for first_index_, first_ in enumerate(segments):
        for second_ in segments[first_index_ + 1 :]:
            if first_.half == second_.half or not _overlap(first_, second_):
                continue
            earlier_, later_ = (
                (first_, second_)
                if first_.half < second_.half
                else (second_, first_)
            )
            if _comes_before(
                before, later_.key, earlier_.key
            ) or _comes_before(before, earlier_.key, later_.key):
                continue
            before[later_.key].add(earlier_.key)


# The strength of a reason for the order of two segments, the strongest
# first: two ends at the same exact position (the other order lays them on
# top of each other), a nested pair on a shared stretch, the base heights
# under the columns (see _base_order), the ends (the other order adds a
# crossing), the priority of an unavoidable crossing.
_COINCIDENT = 0
_FORCED = 1
_BASE = 2
_CROSSING = 3
_CONFLICT = 4


def _base_order(first: LaneSegment, second: LaneSegment) -> int:
    """
    Return the order of two overlapping segments under the columns by their
    base heights.

    The segment with the higher base height lies higher: return 1 if this
    is the first segment, -1 for the second, 0 if the base heights are
    equal or unknown. A pocket is empty space: every segment that fits into
    it takes it and shortens its way.

    The rule holds for segments whose two ends both go up, and for them it
    never adds a crossing. If one segment lies inside the other along the
    channel, the only order without a crossing puts the inner one higher,
    and its base height is not lower, because it passes under a part of the
    same columns. If the segments are shifted, one crossing is unavoidable
    in either order; this order moves it into the pocket, where there is
    room, even where the priority of the unavoidable crossing would choose
    the other order.

    A segment with an end that continues a lane straight, or with an end
    that goes down in a vertical channel, is not ordered this way: there
    the argument above does not hold.
    """

    if (
        first.base_level is None
        or second.base_level is None
        or first.base_level == second.base_level
        or not _ends_go_up(first)
        or not _ends_go_up(second)
        or not _overlap(first, second)
    ):
        return 0
    return 1 if first.base_level < second.base_level else -1


def _ends_go_up(segment: LaneSegment) -> bool:
    """
    Return True if both ends of a horizontal segment go up.
    """

    return len(segment.members) == 2 and not any(
        member_.to_high_side for member_ in segment.members
    )


def _comes_before(
    before: Dict[SegmentKey, Set[SegmentKey]],
    first: SegmentKey,
    second: SegmentKey,
) -> bool:
    """
    Return True if the orders already set put the first segment before the
    second one.
    """

    stack = [second]
    seen: Set[SegmentKey] = set()
    while len(stack) > 0:
        key_ = stack.pop()
        if key_ == first:
            return True
        if key_ not in seen:
            seen.add(key_)
            stack.extend(before[key_])
    return False


def _coincident_order(first: LaneSegment, second: LaneSegment) -> int:
    """
    Return the order of two segments with ends at the same position.

    If the ends extend to different sides, the segment whose end extends
    toward the low side takes the lower lane: return 1 if this is the first
    segment, -1 for the second, 0 if no ends coincide this way. The other
    order lays the two ends on top of each other.

    Only exact positions coincide. A position that stands for a lane not
    known yet can be equal to another one while the lanes differ.
    """

    if not _overlap(first, second):
        return 0
    for first_member_ in first.members:
        for second_member_ in second.members:
            if (
                first_member_.is_exact
                and second_member_.is_exact
                and first_member_.position == second_member_.position
                and first_member_.to_high_side != second_member_.to_high_side
            ):
                return -1 if first_member_.to_high_side else 1
    return 0


def _pair_order(
    first: LaneSegment,
    second: LaneSegment,
    priority: LaneConflictPriority,
    conflicts: List[LaneConflictPair],
) -> int:
    """
    Return 1 if the first segment takes a lower lane, -1 for the opposite.

    Return 0 if the segments do not overlap.
    """

    if not _overlap(first, second):
        return 0
    # (order, is_entry, is the second segment the inner one).
    votes: List[Tuple[int, bool, bool]] = []
    for member_ in second.members:
        if first.low < member_.position < first.high:
            # The member of the second segment extends toward the high side.
            # The first segment must stay on the low side of it.
            votes.append(
                (1 if member_.to_high_side else -1, member_.is_entry, True)
            )
    for member_ in first.members:
        if second.low < member_.position < second.high:
            votes.append(
                (-1 if member_.to_high_side else 1, member_.is_entry, False)
            )
    if len(votes) == 0:
        return 0
    orders = {vote_[0] for vote_ in votes}
    if len(orders) == 1:
        return votes[0][0]

    prefer_entry = priority is LaneConflictPriority.ENTRY
    preferred = [vote_ for vote_ in votes if vote_[1] == prefer_entry]
    chosen = preferred[0] if len(preferred) > 0 else votes[0]
    outer, inner = (first, second) if chosen[2] else (second, first)
    conflicts.append(
        LaneConflictPair(
            outer_edge_id=outer.edge_id, inner_edge_id=inner.edge_id
        )
    )
    return chosen[0]


def _longest_path_lanes(
    segments: List[LaneSegment],
    before: Dict[SegmentKey, Set[SegmentKey]],
) -> Dict[SegmentKey, int]:
    """
    Give each segment the lane after all segments that must come before it.

    If the constraints form a cycle, the first remaining segment in order
    ignores its unresolved constraints. A segment never shares a lane with an
    overlapping segment.
    """

    segment_by_key = {segment_.key: segment_ for segment_ in segments}
    remaining = [segment_.key for segment_ in segments]
    lanes: Dict[SegmentKey, int] = {}
    while len(remaining) > 0:
        ready = [
            key_
            for key_ in remaining
            if all(before_key_ in lanes for before_key_ in before[key_])
        ]
        if len(ready) == 0:
            ready = [remaining[0]]
        for key_ in ready:
            lane_ = max(
                (
                    lanes[before_key_] + 1
                    for before_key_ in before[key_]
                    if before_key_ in lanes
                ),
                default=0,
            )
            segment_ = segment_by_key[key_]
            while any(
                lanes[placed_key_] == lane_
                and _overlap(segment_, segment_by_key[placed_key_])
                for placed_key_ in lanes
            ):
                lane_ += 1
            lanes[key_] = lane_
        remaining = [key_ for key_ in remaining if key_ not in lanes]
    return lanes


def _overlap(first: LaneSegment, second: LaneSegment) -> bool:
    return not (first.high < second.low or second.high < first.low)
