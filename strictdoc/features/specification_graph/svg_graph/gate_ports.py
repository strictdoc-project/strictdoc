"""
Port slots of a gate, shared by the layout modes.

spec.md, section "Порты", defines the rule. A gate is the pair of faces that
open into one horizontal channel in one column.
"""

from dataclasses import dataclass, replace
from enum import Enum
from typing import Dict, List, Sequence, Tuple


class Face(Enum):
    TOP = "top"
    BOTTOM = "bottom"


@dataclass(frozen=True)
class Port:
    node_id: str
    face: Face
    # Position on the face relative to the center: 0 is the center, negative
    # values are left of the center.
    slot: int
    # Number of slots in the list that numbered this port. The port pitch
    # depends on it: a long list gets a smaller pitch. 0 for the center slot.
    list_size: int = 0


# Key of an endpoint: the edge ID and 0 for the source or 1 for the target.
EndpointKey = Tuple[str, int]


@dataclass(frozen=True)
class GateEndpoint:
    endpoint_key: EndpointKey
    node_id: str
    face: Face
    # -1: the horizontal segment extends left of the port. 1: right of the
    # port. 0: the edge is straight and has no horizontal segment.
    side: int
    # Half of the channel that holds the horizontal segment: 0 for the top
    # half (the segment goes left), 1 for the bottom half (goes right).
    half: int
    # Position where the horizontal segment goes, then an index for ties.
    sort_key: Tuple[Tuple[float, float], int]
    # The relation passes the port downward: a source on a bottom face or a
    # target on a top face.
    flows_down: bool = False


@dataclass(frozen=True)
class ForcedPortOrder:
    """
    The port order of a nested pair on a face where its stretch ends.

    spec.md, section "Общий участок".
    """

    inner: EndpointKey
    outer: EndpointKey
    # The port of the inner route stands right of the port of the outer one.
    inner_is_right: bool


def number_gate_ports(
    endpoints: List[GateEndpoint],
    forced: Sequence[ForcedPortOrder] = (),
) -> Dict[EndpointKey, Port]:
    """
    Assign a slot to each port of one gate.

    The upper face of a gate is the bottom face of the upper node. The lower
    face is the top face of the lower node.

    Each face of a gate has a left group, the center slot, and a right group.
    A straight edge takes the center slot. A gate has at most one straight
    edge. Within a group, the slots follow the positions where the edges go:
    in the same order where the relation passes the port upward, in the
    mirrored order where it passes downward. This order lets the lanes nest
    without a crossing.

    Each face numbers its group on its own, so both faces keep one rhythm:
    ports with equal slots stand on one vertical. This is safe when the two
    verticals cannot meet. The vertical of an upper port runs from the top of
    the channel down to its lane. The vertical of a lower port runs from the
    bottom of the channel up to its lane. The half of the channel of each
    lane is known before the lanes are assigned (right-hand traffic):

    - upper segment in the top half, lower segment in the bottom half: the
      verticals never meet
    - upper segment in the bottom half, lower segment in the top half: the
      verticals always overlap
    - both segments in one half: the lanes decide, so the pair counts as
      unsafe.

    If a group of a gate has at least one unsafe pair of an upper and a lower
    port, the two faces number this group with one shared list of two
    blocks: the ports of the upper face near the center, the ports of the
    lower face after them. Each face keeps its ports together as one bundle
    and skips the slots of the other block (fictitious slots). For upward
    edges, the right group is safe and the left group is unsafe.

    Upper block near the center: for upward edges the unavoidable crossings
    of the two blocks then happen near the source ports, away from the
    arrowheads.

    A forced port order of a nested pair on a shared stretch puts the two
    ports in the order of the stretch: the pair exchanges its slots if
    needed.
    """

    ports: Dict[EndpointKey, Port] = {}
    for endpoint_ in endpoints:
        if endpoint_.side == 0:
            ports[endpoint_.endpoint_key] = Port(
                endpoint_.node_id, endpoint_.face, 0
            )
    for side_ in (-1, 1):
        group_ = sorted(
            (endpoint_ for endpoint_ in endpoints if endpoint_.side == side_),
            key=_order_key,
        )
        upper_ = [
            endpoint_ for endpoint_ in group_ if endpoint_.face is Face.BOTTOM
        ]
        lower_ = [
            endpoint_ for endpoint_ in group_ if endpoint_.face is Face.TOP
        ]
        if side_ == -1:
            # The lists run from the center outward. On the left side, the
            # port next to the center goes to the rightmost position.
            upper_.reverse()
            lower_.reverse()
        if _group_is_unsafe(upper_, lower_):
            numbered_lists_ = [upper_ + lower_]
        else:
            numbered_lists_ = [upper_, lower_]
        for list_ in numbered_lists_:
            for index_, endpoint_ in enumerate(list_):
                # Index 0 is the slot next to the center on both sides.
                slot_ = -(index_ + 1) if side_ == -1 else index_ + 1
                ports[endpoint_.endpoint_key] = Port(
                    endpoint_.node_id,
                    endpoint_.face,
                    slot_,
                    list_size=len(list_),
                )
    # A swap for one pair can break the order of a pair swapped before it,
    # so the pairs are applied again until no port moves. Each pass that
    # moves a port fixes at least one pair; contradicting orders stop after
    # as many passes as there are pairs.
    for _ in range(len(forced) + 1):
        moved_ = False
        for order_ in forced:
            if order_.inner not in ports or order_.outer not in ports:
                continue
            inner_ = ports[order_.inner]
            outer_ = ports[order_.outer]
            if (inner_.slot > outer_.slot) != order_.inner_is_right:
                ports[order_.inner] = replace(inner_, slot=outer_.slot)
                ports[order_.outer] = replace(outer_, slot=inner_.slot)
                moved_ = True
        if not moved_:
            break
    return ports


def _order_key(endpoint: GateEndpoint) -> Tuple[Tuple[float, float], int]:
    """
    Return the key of the port order within a group.

    A relation that passes the port downward mirrors the order.
    """

    (position, secondary), index = endpoint.sort_key
    if endpoint.flows_down:
        return (-position, -secondary), index
    return (position, secondary), index


def _group_is_unsafe(
    upper: List[GateEndpoint], lower: List[GateEndpoint]
) -> bool:
    """
    Return True if an upper port and a lower port of a group can meet.

    A pair is safe only if the upper segment lies in the top half and the
    lower segment lies in the bottom half.
    """

    if len(upper) == 0 or len(lower) == 0:
        return False
    return any(endpoint_.half != 0 for endpoint_ in upper) or any(
        endpoint_.half != 1 for endpoint_ in lower
    )
