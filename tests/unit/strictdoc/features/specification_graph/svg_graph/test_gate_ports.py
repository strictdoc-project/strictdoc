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
