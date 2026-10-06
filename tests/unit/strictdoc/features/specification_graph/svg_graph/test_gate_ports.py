from typing import Tuple

from strictdoc.features.specification_graph.svg_graph.gate_ports import (
    EndpointKey,
    Face,
    ForcedPortOrder,
    GateEndpoint,
    number_gate_ports,
)


def _endpoint(edge_id: str, position: float) -> GateEndpoint:
    """
    Create a source endpoint on the bottom face of node N, right side.
    """

    return GateEndpoint(
        endpoint_key=(edge_id, 0),
        node_id="N",
        face=Face.BOTTOM,
        side=1,
        half=1,
        sort_key=((position, 0.0), 0),
    )


def test_forced_port_orders_hold_together() -> None:
    """
    All forced port orders of one face hold at once, even where a swap for
    one pair breaks the order of a pair swapped before it.

    The ports start as P1, P2, P3 from the center. The first order puts P1
    right of P2, the second one puts P2 right of P3. The swap for the
    second pair moves P2 right of P1 again, so a single pass over the
    orders leaves the first one broken.

    Code: gate_ports.number_gate_ports.
    Fails if:
    - forced port orders are applied in one pass.
    """

    first: EndpointKey = ("P1", 0)
    second: EndpointKey = ("P2", 0)
    third: EndpointKey = ("P3", 0)
    ports = number_gate_ports(
        [_endpoint("P1", 1), _endpoint("P2", 2), _endpoint("P3", 3)],
        [
            ForcedPortOrder(inner=first, outer=second, inner_is_right=True),
            ForcedPortOrder(inner=second, outer=third, inner_is_right=True),
        ],
    )

    assert ports[third].slot < ports[second].slot < ports[first].slot


def test_port_order_is_mirrored_for_a_downward_relation() -> None:
    """
    Within a group, the ports follow the positions where the relations go:
    in the same order where the relation passes the port upward, in the
    mirrored order where it passes downward.

    Two endpoints on the right side of the bottom face of N go to the
    positions 1 and 2. Passed upward, the port next to the center goes to
    position 1. Passed downward, it goes to position 2.

    Code: gate_ports._order_key.
    Fails if:
    - the port order is not mirrored for a downward relation.
    """

    def slots(flows_down: bool) -> Tuple[int, int]:
        endpoints = [
            GateEndpoint(
                endpoint_key=(edge_id_, 0),
                node_id="N",
                face=Face.BOTTOM,
                side=1,
                half=1,
                sort_key=((position_, 0.0), index_),
                flows_down=flows_down,
            )
            for index_, (edge_id_, position_) in enumerate(
                (("P1", 1.0), ("P2", 2.0))
            )
        ]
        ports = number_gate_ports(endpoints)
        return ports[("P1", 0)].slot, ports[("P2", 0)].slot

    assert slots(flows_down=False) == (1, 2)
    assert slots(flows_down=True) == (2, 1)
