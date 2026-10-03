"""
Lane assignment in one channel, shared by the layout modes.

spec.md, section "Полосы в канале", defines the rules. A segment is the part
of a route inside one channel. A constraint graph orders the overlapping
segments of one half of the channel.
"""

from dataclasses import dataclass, replace
from enum import Enum
from typing import Dict, FrozenSet, List, Sequence, Set, Tuple


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


@dataclass(frozen=True)
class LaneSegment:
    key: SegmentKey
    edge_id: str
    low: LanePosition
    high: LanePosition
    # Half 0 comes first: the top half of a horizontal channel or the left
    # half of a vertical channel.
    half: int
    # A segment that leaves the channel through its end, for example through
    # the side face of a container, has fewer members.
    members: Tuple[CrossMember, ...]
    order_key: Tuple[LanePosition, int]


@dataclass(frozen=True)
class ForcedOrder:
    """
    The order of two segments of a nested pair on a shared stretch.

    spec.md, section "Общий участок". The inner segment moves to the half of
    the outer segment if the halves differ.
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

    Within a half, a constraint graph orders the overlapping segments. The
    longest path from the first lane gives each segment its lane, so segments
    without overlap can share a lane. A forced order of a nested pair on a
    shared stretch replaces the constraints of that pair.
    """

    result: Dict[SegmentKey, int] = {}
    conflicts: List[LaneConflictPair] = []
    lane_offset = 0
    segments = _yield_to_nesting(
        _apply_forced_halves(segments, forced, priority)
    )
    # (earlier, later) -> the earlier segment takes the smaller lane.
    forced_pairs: Set[Tuple[SegmentKey, SegmentKey]] = {
        (order_.outer, order_.inner)
        if order_.inner_is_later
        else (order_.inner, order_.outer)
        for order_ in forced
    }
    for half_ in (0, 1):
        half_segments_ = sorted(
            (segment_ for segment_ in segments if segment_.half == half_),
            key=lambda segment_: segment_.order_key,
        )
        before_: Dict[SegmentKey, Set[SegmentKey]] = {
            segment_.key: set() for segment_ in half_segments_
        }
        # Pairs whose order costs no crossing: the votes contradict, so one
        # crossing happens in either order, or there are no votes.
        free_: Set[FrozenSet[SegmentKey]] = set()
        # (strength, earlier, later): the earlier segment takes the smaller
        # lane. A smaller strength is a stronger reason.
        orders_: List[Tuple[int, SegmentKey, SegmentKey]] = []
        for first_index_, first_ in enumerate(half_segments_):
            for second_ in half_segments_[first_index_ + 1 :]:
                coincident_ = _coincident_order(first_, second_)
                if coincident_ != 0:
                    order_, strength_ = coincident_, _COINCIDENT
                elif (first_.key, second_.key) in forced_pairs:
                    order_, strength_ = 1, _FORCED
                elif (second_.key, first_.key) in forced_pairs:
                    order_, strength_ = -1, _FORCED
                else:
                    conflict_count_ = len(conflicts)
                    order_ = _pair_order(first_, second_, priority, conflicts)
                    strength_ = _CROSSING
                    if order_ == 0 or len(conflicts) > conflict_count_:
                        free_.add(frozenset((first_.key, second_.key)))
                        strength_ = _CONFLICT
                if order_ == 1:
                    orders_.append((strength_, first_.key, second_.key))
                elif order_ == -1:
                    orders_.append((strength_, second_.key, first_.key))
        # A weaker order that contradicts the stronger ones already taken
        # is dropped. A stable sort keeps the segment order within one
        # strength.
        for _, earlier_, later_ in sorted(orders_, key=lambda o_: o_[0]):
            if not _comes_before(before_, later_, earlier_):
                before_[later_].add(earlier_)
        _keep_ribbons(half_segments_, before_, free_, forced_pairs)
        half_lanes_ = _longest_path_lanes(half_segments_, before_)
        for key_, lane_ in half_lanes_.items():
            result[key_] = lane_offset + lane_
        if len(half_lanes_) > 0:
            lane_offset += max(half_lanes_.values()) + 1
    return result, conflicts


def _keep_ribbons(
    segments: List[LaneSegment],
    before: Dict[SegmentKey, Set[SegmentKey]],
    free: Set[FrozenSet[SegmentKey]],
    ribbon_pairs: Set[Tuple[SegmentKey, SegmentKey]],
) -> None:
    """
    Move a foreign segment out of a ribbon if this costs no crossing.

    This function is the only place of this rule. spec.md, section
    "Ленты". A ribbon pair is a forced pair of a shared stretch: the
    earlier segment, then the later one. A foreign segment that overlaps
    both goes to one side of the pair. A free order (no votes, or
    contradicting votes) can change without a new crossing. A fixed order
    decides the side. If both orders are free, the foreign segment goes to
    the side of the smaller lanes. If both orders are fixed and put the
    segment between, it stays between.
    """

    by_key = {segment_.key: segment_ for segment_ in segments}

    def relation(first: SegmentKey, second: SegmentKey) -> int:
        if first in before[second]:
            return 1
        if second in before[first]:
            return -1
        return 0

    def place(
        foreign: SegmentKey, earlier: SegmentKey, later: SegmentKey, first: bool
    ) -> None:
        for member_ in (earlier, later):
            before[foreign].discard(member_)
            before[member_].discard(foreign)
            if first:
                before[member_].add(foreign)
            else:
                before[foreign].add(member_)

    for earlier_, later_ in sorted(ribbon_pairs):
        if earlier_ not in by_key or later_ not in by_key:
            continue
        for foreign_, segment_ in by_key.items():
            if foreign_ in (earlier_, later_):
                continue
            if not (
                _overlap(segment_, by_key[earlier_])
                and _overlap(segment_, by_key[later_])
            ):
                continue
            with_earlier_ = relation(earlier_, foreign_)
            with_later_ = relation(foreign_, later_)
            earlier_is_fixed_ = frozenset((earlier_, foreign_)) not in free
            later_is_fixed_ = frozenset((foreign_, later_)) not in free
            if earlier_is_fixed_ and with_earlier_ == 1:
                if later_is_fixed_ and with_later_ == 1:
                    # Both orders are fixed: the segment stays between.
                    continue
                place(foreign_, earlier_, later_, first=False)
            elif earlier_is_fixed_ and with_earlier_ == -1:
                place(foreign_, earlier_, later_, first=True)
            elif later_is_fixed_ and with_later_ == -1:
                place(foreign_, earlier_, later_, first=False)
            else:
                place(foreign_, earlier_, later_, first=True)


def _apply_forced_halves(
    segments: List[LaneSegment],
    forced: Sequence[ForcedOrder],
    priority: LaneConflictPriority,
) -> List[LaneSegment]:
    """
    Move the inner segment of each forced pair into the half of the outer.

    The segments of the inner half that must lie on the same side of the
    outer segment by their own ends move with it. Otherwise the half of the
    inner segment would keep them on the other side of the outer segment,
    and they would cross it.
    """

    segment_by_key = {segment_.key: segment_ for segment_ in segments}
    target_half: Dict[SegmentKey, int] = {}
    for order_ in forced:
        if order_.inner not in segment_by_key or (
            order_.outer not in segment_by_key
        ):
            continue
        inner_half_ = segment_by_key[order_.inner].half
        outer_ = segment_by_key[order_.outer]
        target_half[order_.inner] = outer_.half
        if inner_half_ == outer_.half:
            continue
        # 1: the segment comes before the outer one, as an earlier lane.
        inner_side_ = -1 if order_.inner_is_later else 1
        for segment_ in segments:
            if (
                segment_.half == inner_half_
                and segment_.key != order_.inner
                and _ends_order(segment_, outer_, priority) == inner_side_
            ):
                target_half[segment_.key] = outer_.half
    return [
        replace(segment_, half=target_half[segment_.key])
        if segment_.key in target_half
        else segment_
        for segment_ in segments
    ]


def _yield_to_nesting(segments: List[LaneSegment]) -> List[LaneSegment]:
    """
    Move a nested segment into the half of the segment around it.

    spec.md, section "Общий участок": this is a shared stretch of one
    channel. A segment is nested in an overlapping segment of the other
    half if both of its members lie inside the outer segment and extend to
    the same side. If the halves require the order that makes both members
    cross the outer segment, the inner segment moves to the half of the
    outer one. There, the constraint graph puts it on the side of its
    members, and the two segments do not cross.
    """

    moved: Set[SegmentKey] = set()
    for inner_ in segments:
        if len(inner_.members) != 2:
            continue
        sides_ = {member_.to_high_side for member_ in inner_.members}
        if len(sides_) != 1:
            continue
        # The members extend toward the high side: the inner segment must
        # lie on the high side of the outer one, in the later half.
        must_be_later_ = sides_.pop()
        for outer_ in segments:
            if (
                outer_.half != inner_.half
                and (outer_.half < inner_.half) != must_be_later_
                and all(
                    outer_.low < member_.position < outer_.high
                    for member_ in inner_.members
                )
            ):
                moved.add(inner_.key)
                break
    return [
        replace(segment_, half=1 - segment_.half)
        if segment_.key in moved
        else segment_
        for segment_ in segments
    ]


# The strength of a reason for the order of two segments, the strongest
# first: two ends at the same position (the other order lays them on top of
# each other), a nested pair on a shared stretch, the ends (the other order
# adds a crossing), the priority of an unavoidable crossing.
_COINCIDENT = 0
_FORCED = 1
_CROSSING = 2
_CONFLICT = 3


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
    segment, -1 for the second. Return 0 if no ends coincide this way.
    """

    if not _overlap(first, second):
        return 0
    for first_member_ in first.members:
        for second_member_ in second.members:
            if (
                first_member_.position == second_member_.position
                and first_member_.to_high_side != second_member_.to_high_side
            ):
                return -1 if first_member_.to_high_side else 1
    return 0


def _ends_order(
    first: LaneSegment, second: LaneSegment, priority: LaneConflictPriority
) -> int:
    """
    Return the order that the ends of two segments require.

    Return 1 if the first segment must take a lower lane, -1 for the
    opposite, and 0 if the ends require no order or contradict each other.
    """

    coincident = _coincident_order(first, second)
    if coincident != 0:
        return coincident
    conflicts: List[LaneConflictPair] = []
    order = _pair_order(first, second, priority, conflicts)
    return 0 if len(conflicts) > 0 else order


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
