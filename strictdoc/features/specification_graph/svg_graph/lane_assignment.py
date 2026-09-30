"""
Lane assignment in one channel, shared by the layout modes.

spec.md, section "Полосы в канале", defines the rules. A segment is the part
of a route inside one channel. A constraint graph orders the overlapping
segments of one half of the channel.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Set, Tuple


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
class LaneConflictPair:
    """
    Two segments with an unavoidable crossing in one channel.
    """

    outer_edge_id: str
    inner_edge_id: str


def assign_lanes(
    segments: List[LaneSegment], priority: LaneConflictPriority
) -> Tuple[Dict[SegmentKey, int], List[LaneConflictPair]]:
    """
    Assign lanes in one channel.

    Within a half, a constraint graph orders the overlapping segments. The
    longest path from the first lane gives each segment its lane, so segments
    without overlap can share a lane.
    """

    result: Dict[SegmentKey, int] = {}
    conflicts: List[LaneConflictPair] = []
    lane_offset = 0
    for half_ in (0, 1):
        half_segments_ = sorted(
            (segment_ for segment_ in segments if segment_.half == half_),
            key=lambda segment_: segment_.order_key,
        )
        before_: Dict[SegmentKey, Set[SegmentKey]] = {
            segment_.key: set() for segment_ in half_segments_
        }
        for first_index_, first_ in enumerate(half_segments_):
            for second_ in half_segments_[first_index_ + 1 :]:
                order_ = _pair_order(first_, second_, priority, conflicts)
                if order_ == 1:
                    before_[second_.key].add(first_.key)
                elif order_ == -1:
                    before_[first_.key].add(second_.key)
        half_lanes_ = _longest_path_lanes(half_segments_, before_)
        for key_, lane_ in half_lanes_.items():
            result[key_] = lane_offset + lane_
        if len(half_lanes_) > 0:
            lane_offset += max(half_lanes_.values()) + 1
    return result, conflicts


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
