from dataclasses import dataclass
from typing import List, Tuple

from strictdoc.features.specification_graph.svg_graph.gate_ports import Face
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedEdge,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    ChannelKind,
    StructureChannelId,
)
from strictdoc.features.specification_graph.svg_graph.structure_stretches import (
    _nesting,
)


@dataclass(frozen=True)
class _Route:
    index: int
    edge: NormalizedEdge
    source_face: Face
    target_face: Face
    channels: Tuple[StructureChannelId, ...]
    levels: Tuple[float, ...]


def _edge(edge_id: str, source_id: str, target_id: str) -> NormalizedEdge:
    return NormalizedEdge(
        edge_id=edge_id,
        source_id=source_id,
        target_id=target_id,
        relation_type="parent",
        is_ancestor_link=False,
        cycle_id=None,
        is_level_edge=True,
    )


def test_pair_between_shared_faces_keeps_the_order_of_traffic() -> None:
    """
    A pair whose stretch ends on shared faces at both ends keeps the order
    of right-hand traffic on the whole stretch.

    A -> B and B -> A leave and enter the bottom face of A and the top face
    of B, through the same three channels. No end of the stretch sets an
    order, so the first route lies on its right side.

    Code: structure_stretches._nesting.
    Fails if:
    - a pair between shared faces gets no order.
    """

    lower_channel = StructureChannelId(ChannelKind.COLUMN, "Doc", 0, 0)
    vertical = StructureChannelId(ChannelKind.VERTICAL, "Doc", 1)
    upper_channel = StructureChannelId(ChannelKind.COLUMN, "Doc", 1, 0)
    forward = _Route(
        index=0,
        edge=_edge("edge-1", "A", "B"),
        source_face=Face.BOTTOM,
        target_face=Face.TOP,
        channels=(lower_channel, vertical, upper_channel),
        levels=(10, 50, 30),
    )
    backward = _Route(
        index=1,
        edge=_edge("edge-2", "B", "A"),
        source_face=Face.TOP,
        target_face=Face.BOTTOM,
        channels=(upper_channel, vertical, lower_channel),
        levels=(30, 50, 10),
    )
    # The port of the source, one point per channel, then the target.
    forward_points: List[Tuple[float, float]] = [
        (0, 0),
        (0, 10),
        (50, 10),
        (50, 30),
        (100, 30),
        (100, 40),
    ]
    backward_points = list(reversed(forward_points))

    nesting = _nesting(
        forward, backward, forward_points, backward_points, (0, 2, 3, -1)
    )

    assert nesting is not None
    inner, side, faces = nesting
    assert inner is forward
    assert side == 1
    assert len(faces) == 2


def test_heights_under_the_columns_set_the_order_of_a_stretch() -> None:
    """
    Different heights of the two segments under the columns set the order
    of the whole stretch, against the order that the ends ask for.

    N -> X and N -> Y leave the bottom face of N and share three channels:
    the space under the columns, a vertical channel, and a column channel.
    At the end, N -> X turns up and N -> Y turns down, so the ends ask for
    N -> X above. Under the columns N -> Y lies at 50 and N -> X at 80:
    there N -> Y is above, and the heights cannot change. The stretch keeps
    N -> X below, on the right side of its travel to the right.

    Code: structure_stretches._fixed_side.
    Fails if:
    - the ends decide against the heights under the columns.
    """

    corridor = StructureChannelId(ChannelKind.BOTTOM_CORRIDOR, "Doc")
    vertical = StructureChannelId(ChannelKind.VERTICAL, "Doc", 1)
    column_channel = StructureChannelId(ChannelKind.COLUMN, "Doc", 1, 0)
    channels = (corridor, vertical, column_channel)
    lower = _Route(
        index=0,
        edge=_edge("edge-1", "N", "X"),
        source_face=Face.BOTTOM,
        target_face=Face.BOTTOM,
        channels=channels,
        levels=(80, 100, 20),
    )
    upper = _Route(
        index=1,
        edge=_edge("edge-2", "N", "Y"),
        source_face=Face.BOTTOM,
        target_face=Face.TOP,
        channels=channels,
        levels=(50, 110, 30),
    )
    # The port of the source, one point per channel, then the target.
    lower_points: List[Tuple[float, float]] = [
        (0, 0),
        (0, 80),
        (100, 80),
        (100, 20),
        (150, 20),
        (150, 10),
    ]
    upper_points: List[Tuple[float, float]] = [
        (10, 0),
        (10, 50),
        (110, 50),
        (110, 30),
        (160, 30),
        (160, 40),
    ]

    nesting = _nesting(lower, upper, lower_points, upper_points, (0, 0, 3, 1))

    assert nesting is not None
    inner, side, _ = nesting
    assert (side if inner is lower else -side) == 1
