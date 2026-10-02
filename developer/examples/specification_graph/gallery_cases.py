"""
Example graphs for the specification graph gallery.

Each case is an input of the graph generator. The gallery script renders the
cases for visual control. The unit tests use the same cases as test inputs.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple, Union

from strictdoc.features.specification_graph.svg_graph.levels_routing import (
    LaneConflictPriority,
    RoutingOptions,
    SkipChannelChoice,
)
from strictdoc.features.specification_graph.svg_graph.model import (
    Graph,
    GraphEdge,
    GraphNode,
    LayoutMode,
    RelationStyle,
)


@dataclass(frozen=True)
class RejectedAlternative:
    """
    A routing choice that spec.md rejects.

    The gallery renders the case a second time with these options, next to
    the generator result, and marks the picture as rejected.
    """

    # The option value that produces the rejected route, as Python code.
    option_code: str
    options: RoutingOptions
    description: str


@dataclass(frozen=True)
class GalleryCase:
    title: str
    description: str
    graph: Graph
    rejected_alternative: Optional[RejectedAlternative] = None


def _levels_case(
    title: str,
    description: str,
    node_ids: Sequence[str],
    edges: Sequence[Tuple[str, str]],
    rejected_alternative: Optional[RejectedAlternative] = None,
) -> GalleryCase:
    """
    Create a levels mode case.

    Each edge is a (child, parent) pair.
    """

    return GalleryCase(
        title=title,
        description=description,
        graph=Graph(
            mode=LayoutMode.LEVELS,
            root=tuple(
                GraphNode(node_id=node_id_, title=node_id_)
                for node_id_ in node_ids
            ),
            edges=tuple(
                GraphEdge(
                    source_id=child_id_,
                    target_id=parent_id_,
                    relation_type="parent",
                )
                for child_id_, parent_id_ in edges
            ),
        ),
        rejected_alternative=rejected_alternative,
    )


def _chain_nodes(names: Sequence[str], length: int) -> List[str]:
    return [f"{name_}{index_}" for index_ in range(length) for name_ in names]


def _chain_edges(names: Sequence[str], length: int) -> List[Tuple[str, str]]:
    return [
        (f"{name_}{index_ + 1}", f"{name_}{index_}")
        for name_ in names
        for index_ in range(length - 1)
    ]


def _extreme_gate_case(
    goes_right: bool, sent_count: int, received_count: int
) -> GalleryCase:
    """
    Create a case with many ports in the gate between U and L.

    U stands above L. L -> U is straight. L sends relations to the nodes
    U2, U3, ... beside U. U receives relations from the nodes L2, L3, ...
    beside L. Each Lk -> Uk is straight and fixes the columns.
    """

    side_count = max(sent_count, received_count)
    upper_side = [f"U{index_ + 2}" for index_ in range(side_count)]
    lower_side = [f"L{index_ + 2}" for index_ in range(side_count)]
    if goes_right:
        node_ids = ["U", *upper_side, "L", *lower_side]
    else:
        node_ids = [*upper_side, "U", *lower_side, "L"]
    edges = [
        ("L", "U"),
        *(("L", target_id_) for target_id_ in upper_side[:sent_count]),
        *((source_id_, "U") for source_id_ in lower_side[:received_count]),
        *zip(lower_side, upper_side),
    ]
    side = "right" if goes_right else "left"
    if goes_right:
        rule = (
            "The group is safe: the segments into U run left in the top "
            "half, the segments out of L run right in the bottom half. Both "
            "faces keep one rhythm, with equal slots on one vertical."
        )
    else:
        rule = (
            "The group is unsafe: the segments into U run right in the "
            "bottom half, the segments out of L run left in the top half. "
            "The faces share one slot list, so each port skips the slots of "
            "the other face."
        )
    return _levels_case(
        f"Extreme gate, {side}: L sends {sent_count}, "
        f"U receives {received_count}",
        (
            f"L -> U is straight. L sends {sent_count} relations to the "
            f"{side}. U receives {received_count} relations from the {side}. "
            f"All of them use the {side} group of the gate between U and L. "
            + rule
        ),
        node_ids,
        edges,
    )


EXTREME_GATE_CASES: Tuple[GalleryCase, ...] = tuple(
    _extreme_gate_case(goes_right_, sent_count_, received_count_)
    for goes_right_ in (True, False)
    for sent_count_, received_count_ in ((12, 12), (12, 13), (12, 4))
)


LEVELS_CASES: Tuple[GalleryCase, ...] = (
    _levels_case(
        "Nested relations in one channel",
        (
            "X -> D and Y -> C both go right in the channel below A, B, C, "
            "D. The segment of Y -> C lies inside the segment of X -> D, so "
            "X -> D must cross one vertical of Y -> C. Entry priority: X -> D "
            "stays above Y -> C and crosses the vertical into C."
        ),
        ["A", "B", "C", "D", "X", "Y"],
        [("X", "A"), ("X", "D"), ("Y", "B"), ("Y", "C"), ("Y", "D")],
        rejected_alternative=RejectedAlternative(
            option_code=(
                "RoutingOptions("
                "lane_conflict_priority=LaneConflictPriority.EXIT)"
            ),
            options=RoutingOptions(
                lane_conflict_priority=LaneConflictPriority.EXIT
            ),
            description=(
                "Exit priority: X -> D stays below Y -> C and crosses the "
                "vertical out of Y."
            ),
        ),
    ),
    _levels_case(
        "Relations across levels from far columns",
        (
            "M3 -> P1 and Q3 -> P1 skip one level. Both relations climb in "
            "the vertical channel next to P1, the column of the target."
        ),
        _chain_nodes(["P", "M", "Q"], 4),
        [*_chain_edges(["P", "M", "Q"], 4), ("M3", "P1"), ("Q3", "P1")],
        rejected_alternative=RejectedAlternative(
            option_code=(
                "RoutingOptions("
                "skip_channel_choice=SkipChannelChoice.NEAR_SOURCE)"
            ),
            options=RoutingOptions(
                skip_channel_choice=SkipChannelChoice.NEAR_SOURCE
            ),
            description=(
                "Near source: each relation climbs in the vertical channel "
                "next to its source, so the two relations use two channels."
            ),
        ),
    ),
    _levels_case(
        "Opposite ports in one gate",
        (
            "The bottom face of U and the top face of L open into one "
            "channel in one column. U receives B -> U from the left. L sends "
            "L -> A to the left. All ports of the two faces take different "
            "positions. The two relations go in opposite directions and "
            "cross once: no lane order avoids this crossing."
        ),
        ["A", "U", "B", "L"],
        [("B", "A"), ("L", "U"), ("L", "A"), ("B", "U")],
    ),
    _levels_case(
        "Many ports in one gate",
        (
            "L sends relations to U and to U2-U5. U receives relations from "
            "L and from L2-L5. The gate between U and L has nine ports. The "
            "port pitch shrinks so that all ports stay on the faces."
        ),
        ["U", "U2", "U3", "U4", "U5", "L", "L2", "L3", "L4", "L5"],
        [
            ("L", "U"),
            ("L", "U2"),
            ("L", "U3"),
            ("L", "U4"),
            ("L", "U5"),
            ("L2", "U"),
            ("L3", "U"),
            ("L4", "U"),
            ("L5", "U"),
            ("L2", "U2"),
            ("L3", "U3"),
            ("L4", "U4"),
            ("L5", "U5"),
        ],
    ),
    _levels_case(
        "Simple chain",
        "A <- B <- C. One node per level, one column.",
        ["A", "B", "C"],
        [("B", "A"), ("C", "B")],
    ),
    _levels_case(
        "Basic highway conflict",
        (
            "D relates to A directly and to C through B. The deepest parent "
            "wins: D stays below C. The relation D -> A crosses levels and "
            "is dashed."
        ),
        ["A", "B", "C", "D"],
        [("B", "A"), ("C", "B"), ("D", "A"), ("D", "C")],
    ),
    _levels_case(
        "Isolated document + hierarchy",
        (
            "E has no relations. E stands in the block of standalone nodes "
            "above the connected graph."
        ),
        ["E", "A", "B", "C", "D"],
        [("B", "A"), ("C", "B"), ("D", "A"), ("D", "C")],
    ),
    _levels_case(
        "Real project case: root corrected to sit level with its sibling",
        (
            "Zephyr and DO-178C are roots. L1 relates to Zephyr. L2 relates "
            "to L1 and to DO-178C. DO-178C moves down to the level of L1. "
            "Both relations of L2 are solid."
        ),
        ["L1", "L2", "DO-178C", "Zephyr"],
        [("L1", "Zephyr"), ("L2", "L1"), ("L2", "DO-178C")],
    ),
    _levels_case(
        "Root correction picks the nearest child, not the farthest",
        (
            "ROOT has two children. NEAR has its own chain of two levels. "
            "FAR has its own chain of three levels. ROOT moves one level "
            "above NEAR. The relation FAR -> ROOT crosses levels and is "
            "dashed. The FAR branch stays one straight column."
        ),
        [
            "ROOT",
            "NEAR-ANCHOR-ROOT",
            "NEAR-ANCHOR",
            "NEAR",
            "FAR-ANCHOR-ROOT",
            "FAR-ANCHOR-1",
            "FAR-ANCHOR-2",
            "FAR",
        ],
        [
            ("NEAR-ANCHOR", "NEAR-ANCHOR-ROOT"),
            ("NEAR", "NEAR-ANCHOR"),
            ("NEAR", "ROOT"),
            ("FAR-ANCHOR-1", "FAR-ANCHOR-ROOT"),
            ("FAR-ANCHOR-2", "FAR-ANCHOR-1"),
            ("FAR", "FAR-ANCHOR-2"),
            ("FAR", "ROOT"),
        ],
    ),
    _levels_case(
        "Corrected root with two non-skip children: sits between them",
        (
            "GUEST has two children, L and R, on the same level. GUEST "
            "stands between them. The relations of GUEST do not cross."
        ),
        [
            "GUEST",
            "L-ANCHOR-ROOT",
            "L-ANCHOR",
            "L",
            "R-ANCHOR-ROOT",
            "R-ANCHOR",
            "R",
        ],
        [
            ("L-ANCHOR", "L-ANCHOR-ROOT"),
            ("L", "L-ANCHOR"),
            ("L", "GUEST"),
            ("R-ANCHOR", "R-ANCHOR-ROOT"),
            ("R", "R-ANCHOR"),
            ("R", "GUEST"),
        ],
    ),
    _levels_case(
        "Corrected root with THREE non-skip children (odd count)",
        (
            "GUEST has three children, L, M, and R, on the same level. GUEST "
            "stands right of M. The relation to L crosses the column of M."
        ),
        [
            "GUEST",
            "L-ANCHOR-ROOT",
            "L-ANCHOR",
            "L",
            "M-ANCHOR-ROOT",
            "M-ANCHOR",
            "M",
            "R-ANCHOR-ROOT",
            "R-ANCHOR",
            "R",
        ],
        [
            ("L-ANCHOR", "L-ANCHOR-ROOT"),
            ("L", "L-ANCHOR"),
            ("L", "GUEST"),
            ("M-ANCHOR", "M-ANCHOR-ROOT"),
            ("M", "M-ANCHOR"),
            ("M", "GUEST"),
            ("R-ANCHOR", "R-ANCHOR-ROOT"),
            ("R", "R-ANCHOR"),
            ("R", "GUEST"),
        ],
    ),
    _levels_case(
        "Three chains compete for one parent column",
        (
            "P has three children, A, B, and C. Each child has its own "
            "child. Q stands right of P and has a chain of two nodes. A, B, "
            "and C compete for the column of P. A wins. B and C stand right "
            "of A in input order. Q moves right. All branches stay straight."
        ),
        ["P", "Q", "A", "B", "C", "A1", "B1", "C1", "Q1", "Q2"],
        [
            ("A", "P"),
            ("B", "P"),
            ("C", "P"),
            ("A1", "A"),
            ("B1", "B"),
            ("C1", "C"),
            ("Q1", "Q"),
            ("Q2", "Q1"),
        ],
    ),
    _levels_case(
        "Disconnected components form separate islands",
        (
            "The input order interleaves two independent chains. Each chain "
            "is an island in its own column. The standalone node stands "
            "above the islands."
        ),
        ["A1", "B1", "A2", "B2", "Standalone"],
        [("A2", "A1"), ("B2", "B1")],
    ),
    _levels_case(
        "Standalone nodes wrap to the connected graph width",
        (
            "Ten standalone nodes stand in a grid above the connected "
            "graph. The grid has the three columns of the connected graph, "
            "not the four columns of a square grid."
        ),
        [
            "Standalone 1",
            "Standalone 2",
            "Standalone 3",
            "Standalone 4",
            "Standalone 5",
            "Standalone 6",
            "Standalone 7",
            "Standalone 8",
            "Standalone 9",
            "Standalone 10",
            "Root A",
            "Root B",
            "Root C",
            "Child A",
            "Child B",
            "Child C",
        ],
        [("Child A", "Root A"), ("Child B", "Root B"), ("Child C", "Root C")],
    ),
    _levels_case(
        "Complete 3 by 3 relation grid",
        "Each of the three lower nodes relates to each of the three upper "
        "nodes.",
        ["A", "B", "C", "D", "E", "F"],
        [
            ("D", "A"),
            ("D", "B"),
            ("D", "C"),
            ("E", "A"),
            ("E", "B"),
            ("E", "C"),
            ("F", "A"),
            ("F", "B"),
            ("F", "C"),
        ],
    ),
    _levels_case(
        "Direction-aware track order",
        (
            "Four children keep their vertical relations to their parents. "
            "Two extra relations go right to R. Two extra relations go left "
            "to L."
        ),
        ["L", "M1", "M2", "R", "C1", "C2", "C3", "C4"],
        [
            ("C1", "L"),
            ("C1", "R"),
            ("C2", "M1"),
            ("C2", "R"),
            ("C3", "M2"),
            ("C3", "L"),
            ("C4", "R"),
            ("C4", "L"),
        ],
    ),
    _levels_case(
        "Busy channel expands to fit its lanes",
        (
            "Eight nodes create competing routes across three levels. The "
            "channel between the first two levels widens. Each relation "
            "keeps one horizontal lane."
        ),
        ["N0", "N1", "N2", "N3", "N4", "N5", "N6", "N7"],
        [
            ("N7", "N0"),
            ("N5", "N3"),
            ("N4", "N3"),
            ("N4", "N2"),
            ("N6", "N1"),
            ("N4", "N1"),
            ("N7", "N5"),
            ("N6", "N0"),
        ],
    ),
    _levels_case(
        "Extreme number of relations from N8",
        "N8 relates to every other connected node.",
        ["N0", "N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8"],
        [
            ("N7", "N0"),
            ("N5", "N3"),
            ("N4", "N3"),
            ("N4", "N2"),
            ("N6", "N1"),
            ("N4", "N1"),
            ("N7", "N5"),
            ("N6", "N0"),
            ("N8", "N7"),
            ("N8", "N0"),
            ("N8", "N4"),
            ("N8", "N6"),
            ("N8", "N1"),
            ("N8", "N2"),
            ("N8", "N3"),
            ("N8", "N5"),
        ],
    ),
    _levels_case(
        "Two cycles have separate diagnostics",
        (
            "A and B form the first cycle. C, D, and E form the second "
            "cycle. F relates to C and is not part of a cycle. Each cycle "
            "has its own ID."
        ),
        ["A", "B", "C", "D", "E", "F"],
        [
            ("A", "B"),
            ("B", "A"),
            ("C", "D"),
            ("D", "E"),
            ("E", "C"),
            ("F", "C"),
        ],
    ),
    _levels_case(
        "Three-document cycle with an incoming branch",
        (
            "A, B, and C form one cycle. D relates to A and is not part of "
            "the cycle. The relation C -> A closes the cycle and does not "
            "take part in the level calculation."
        ),
        ["A", "B", "C", "D"],
        [("A", "B"), ("B", "C"), ("C", "A"), ("D", "A")],
    ),
    _levels_case(
        "Opposite cycle relations use separate routes",
        (
            "A relates to B. B relates to A. The two relations use separate "
            "lanes."
        ),
        ["A", "B"],
        [("A", "B"), ("B", "A")],
    ),
)

# A structure node: a string is a simple node, a pair is a composite node
# with its children.
StructureSpec = Union[str, Tuple[str, Sequence["StructureSpec"]]]


def _structure_node(spec: StructureSpec, titles: Dict[str, str]) -> GraphNode:
    if isinstance(spec, str):
        return GraphNode(node_id=spec, title=titles.get(spec, spec))
    node_id, children = spec
    return GraphNode(
        node_id=node_id,
        title=titles.get(node_id, node_id),
        children=tuple(_structure_node(child_, titles) for child_ in children),
    )


def _structure_case(
    title: str,
    description: str,
    root: Sequence[StructureSpec],
    edges: Sequence[Tuple[str, str]] = (),
    titles: Optional[Dict[str, str]] = None,
) -> GalleryCase:
    """
    Create a structure mode case.

    Each edge is a (source, target) pair.
    """

    titles_ = {} if titles is None else titles
    return GalleryCase(
        title=title,
        description=description,
        graph=Graph(
            mode=LayoutMode.STRUCTURE,
            root=tuple(_structure_node(spec_, titles_) for spec_ in root),
            edges=tuple(
                GraphEdge(
                    source_id=source_id_,
                    target_id=target_id_,
                    relation_type="parent",
                )
                for source_id_, target_id_ in edges
            ),
        ),
    )


STRUCTURE_CASES: Tuple[GalleryCase, ...] = (
    _structure_case(
        "Fewest bends before the shortest length",
        (
            "A2 -> B2 connects the bottom nodes of two short columns. The "
            "route over the bottom corridor has two bends and passes under "
            "S only, so it lies just below S. The tall section T does not "
            "push it down."
        ),
        [
            (
                "Doc",
                [
                    "A1",
                    "A2",
                    ("S", ["S1"]),
                    "B1",
                    "B2",
                    ("T", ["T1", "T2", "T3", "T4", "T5", "T6"]),
                ],
            )
        ],
        [("A2", "B2")],
    ),
    _structure_case(
        "Fewest bends under a tall section",
        (
            "A2 -> B2 connects the bottom nodes of two short columns. The "
            "section S between them is tall, so the route under S goes far "
            "down. The route over the top corridor is shorter but has six "
            "bends. The route under S has two bends and wins."
        ),
        [
            (
                "Doc",
                [
                    "A1",
                    "A2",
                    ("S", ["S1", "S2", "S3", "S4"]),
                    "B1",
                    "B2",
                ],
            )
        ],
        [("A2", "B2")],
    ),
    _structure_case(
        "Bottom corridor follows the columns",
        (
            "A segment in the bottom corridor lies just below the columns it "
            "passes over. A2 -> B1 passes under A and S only, so the tall "
            "section T does not push it down. A2 -> C1 passes under T."
        ),
        [
            (
                "Doc",
                [
                    "A1",
                    "A2",
                    ("S", ["S1", "S2"]),
                    "B1",
                    ("T", ["T1", "T2", "T3", "T4"]),
                    "C1",
                ],
            )
        ],
        [("A2", "B1"), ("A2", "C1")],
    ),
    _structure_case(
        "Through pass under a short section",
        (
            "A3 -> B3 goes along the gap under A3, crosses the vertical "
            "channels and the pocket under the short section S straight, "
            "and reaches B3 at the same height. A4 -> B4 takes the same way "
            "one lane lower."
        ),
        [
            (
                "Doc",
                [
                    "A1",
                    "A2",
                    "A3",
                    "A4",
                    ("S", ["S1"]),
                    "B1",
                    "B2",
                    "B3",
                    "B4",
                    ("T", ["T1", "T2", "T3", "T4", "T5", "T6"]),
                ],
            )
        ],
        [("A3", "B3"), ("A4", "B4")],
    ),
    _structure_case(
        "Vertical lane at the height of a column gap",
        (
            "B1 -> A4 goes over the top corridor, down the vertical channel "
            "between A and S, and into the gap between A3 and A4. A3 -> B3 "
            "passes through at the height of the gaps. It crosses the "
            "vertical channel that B1 -> A4 goes down, so one crossing is "
            "unavoidable. The gap between B3 and B4 has one lane, so "
            "A3 -> B3 makes a step before B3."
        ),
        [
            (
                "Doc",
                [
                    "A1",
                    "A2",
                    "A3",
                    "A4",
                    ("S", ["S1"]),
                    "B1",
                    "B2",
                    "B3",
                    "B4",
                ],
            )
        ],
        [("A3", "B3"), ("B1", "A4")],
    ),
    _structure_case(
        "Lane order in the bottom corridor",
        (
            "C2 -> A2 goes left and passes under the tall section T. "
            "B2 -> C2 goes right and passes under short columns only. The "
            "segments overlap. Right-hand traffic puts the segment that goes "
            "left above, so B2 -> C2 lies below C2 -> A2."
        ),
        [
            (
                "Doc",
                [
                    "A1",
                    "A2",
                    ("T", ["T1", "T2", "T3", "T4"]),
                    "B1",
                    "B2",
                    ("U", ["U1"]),
                    "C1",
                    "C2",
                ],
            )
        ],
        [("C2", "A2"), ("B2", "C2")],
    ),
    _structure_case(
        "Relations that turn together",
        (
            "A2 -> B1 and A3 -> B1 both climb in the vertical channel left of "
            "the section S and turn right into the top corridor. The lanes "
            "nest, so the two relations do not cross."
        ),
        [("Doc", ["A1", "A2", "A3", ("S", ["S1"]), "B1", "B2"])],
        [("A2", "B1"), ("A3", "B1")],
    ),
    _structure_case(
        "Relations inside one container",
        (
            "All relations connect simple nodes of the document. A3 -> A2 "
            "is straight between neighbors in one column. A1 -> C1 and "
            "C2 -> A2 pass the section S through the corridors or the "
            "vertical channels. Each route takes the fewest bends, then the "
            "shortest length. S2 -> S1 stays inside the section."
        ),
        [
            (
                "Doc",
                [
                    "A1",
                    "A2",
                    "A3",
                    ("S", ["S1", "S2"]),
                    "C1",
                    "C2",
                    "C3",
                ],
            )
        ],
        [
            ("A3", "A2"),
            ("A1", "C1"),
            ("C2", "A2"),
            ("C3", "A3"),
            ("S2", "S1"),
            ("C1", "C3"),
        ],
    ),
    _structure_case(
        "Relations inside one container, more ports",
        (
            'The case "Relations inside one container" with a section and '
            "a column on each side. A2 and C2 also connect to the nodes on "
            "the left and on the right, so their faces carry more ports. "
            "C2 -> A2 stays nested inside A1 -> C1. L1 -> R1 goes over all "
            "columns."
        ),
        [
            (
                "Doc",
                [
                    "L1",
                    "L2",
                    "L3",
                    ("U", ["U1"]),
                    "A1",
                    "A2",
                    "A3",
                    ("S", ["S1", "S2"]),
                    "C1",
                    "C2",
                    "C3",
                    ("W", ["W1"]),
                    "R1",
                    "R2",
                    "R3",
                ],
            )
        ],
        [
            ("A3", "A2"),
            ("A1", "C1"),
            ("C2", "A2"),
            ("C3", "A3"),
            ("S2", "S1"),
            ("C1", "C3"),
            ("A2", "L2"),
            ("L2", "A2"),
            ("C2", "R2"),
            ("R2", "C2"),
            ("L2", "C2"),
            ("A2", "R2"),
            ("L1", "R1"),
        ],
    ),
    _structure_case(
        "Steps beside a pocket",
        (
            "The case with more ports, with four nodes in the columns C and "
            "R, and C3 -> R3, R3 -> C3. Both lines pass under W straight. "
            "The column C has more lanes above C3 than the column R above "
            "R3, so the gaps under C3 and R3 end at different heights. Each "
            "line makes a step in a vertical channel: up on the right lane, "
            "down on the left lane."
        ),
        [
            (
                "Doc",
                [
                    "L1",
                    "L2",
                    "L3",
                    ("U", ["U1"]),
                    "A1",
                    "A2",
                    "A3",
                    ("S", ["S1", "S2"]),
                    "C1",
                    "C2",
                    "C3",
                    "C4",
                    ("W", ["W1"]),
                    "R1",
                    "R2",
                    "R3",
                    "R4",
                ],
            )
        ],
        [
            ("A3", "A2"),
            ("A1", "C1"),
            ("C2", "A2"),
            ("C3", "A3"),
            ("S2", "S1"),
            ("C1", "C3"),
            ("A2", "L2"),
            ("L2", "A2"),
            ("C2", "R2"),
            ("R2", "C2"),
            ("L2", "C2"),
            ("A2", "R2"),
            ("L1", "R1"),
            ("C3", "R3"),
            ("R3", "C3"),
        ],
    ),
    _structure_case(
        "Document tree from the sketch",
        (
            "Section 1 holds simple nodes, Section 4, and Section 2 with "
            "Section 3 inside. Consecutive simple nodes form one column. "
            "Each section takes a column of its own. T1, T2, and T3 relate "
            "to nodes inside Section 1, so all four root children stand in "
            "the row."
        ),
        [
            "T1",
            "T2",
            "T3",
            (
                "Section 1",
                [
                    "N1",
                    ("Section 4", ["S4-1", "S4-2", "S4-3", "S4-4"]),
                    "N2",
                    "N3",
                    (
                        "Section 2",
                        [
                            "S2-1",
                            ("Section 3", ["S3-1", "S3-2", "S3-3", "S3-4"]),
                        ],
                    ),
                    "N4",
                    "N5",
                    "N6",
                    "N7",
                    "N8",
                ],
            ),
        ],
        [("N1", "T1"), ("S3-1", "T2"), ("N4", "T3"), ("S4-2", "N1")],
    ),
    _structure_case(
        "Columns of different height",
        (
            "Column 1 has one node, column 2 has five nodes, column 3 is a "
            "section of medium height. The columns align at the top. The "
            "bottom corridor lies below the tallest column. The space below "
            "a short column is not a channel."
        ),
        [
            (
                "Document",
                [
                    ("Short", ["A1"]),
                    ("Tall", ["B1", "B2", "B3", "B4", "B5"]),
                    ("Medium", ["C1", "C2"]),
                ],
            )
        ],
    ),
    _structure_case(
        "Root with connected and unconnected documents",
        (
            "Documents A, B, and C relate to each other and stand in the "
            "row. Documents D, E, F, and G have no relation to another "
            "document. They stand in the block above the row. Each document "
            "takes the highest free place, so G stands below D. The block is "
            "not wider than the row."
        ),
        [
            ("A", ["A1", "A2"]),
            ("D", ["D1"]),
            ("B", ["B1", "B2", "B3"]),
            ("E", ["E1", "E2", "E3", "E4"]),
            ("C", ["C1"]),
            ("F", ["F1", "F2"]),
            ("G", ["G1"]),
        ],
        [("B1", "A1"), ("C1", "B2"), ("D1", "D"), ("E2", "E1")],
    ),
    _structure_case(
        "Root without relations",
        (
            "No document relates to another document. All documents stand "
            "in the block. The block is close to a square by area."
        ),
        [
            ("Doc 1", ["D1-1", "D1-2"]),
            ("Doc 2", ["D2-1"]),
            ("Doc 3", ["D3-1", "D3-2", "D3-3"]),
            ("Doc 4", ["D4-1"]),
            ("Doc 5", ["D5-1", "D5-2"]),
            ("Doc 6", ["D6-1"]),
        ],
    ),
    _structure_case(
        "Deep nesting",
        (
            "Four levels of sections. Each container gets its size from "
            "its columns, from the inside out."
        ),
        [
            (
                "Document",
                [
                    "Intro",
                    (
                        "Level 1",
                        [
                            (
                                "Level 2",
                                [
                                    ("Level 3", ["Deep 1", "Deep 2"]),
                                    "Beside 3",
                                ],
                            ),
                            "Beside 2",
                        ],
                    ),
                    "Outro",
                ],
            )
        ],
    ),
    _structure_case(
        "Long container titles",
        (
            "A container title takes at most two lines at the top left of "
            "the header. The rest is cut. The full title is in the tooltip."
        ),
        [("Doc", [("Sec", ["Req 1", "Req 2"]), "Req 3"])],
        titles={
            "Doc": (
                "A document with a very long title that does not fit into "
                "two lines of the container header at all, so the header "
                "cuts it and the tooltip shows the full text"
            ),
            "Sec": "A section title of medium length for a narrow box",
        },
    ),
)


SERIALIZATION_CASES: Tuple[GalleryCase, ...] = (
    GalleryCase(
        title="Titles, relation types, and diagnostics",
        description=(
            "A long title wraps and stops after three lines. The full title "
            "is in the tooltip. B -> A has the input type verifies with its "
            "own style. C -> A has the input type unknown without a style: "
            "it gets the default style. C relates to itself, and B -> A is "
            "given twice: the generator drops both and marks the nodes with "
            "a warning sign."
        ),
        graph=Graph(
            mode=LayoutMode.LEVELS,
            root=(
                GraphNode(
                    node_id="A",
                    title=(
                        "A requirement with a very long title that does not "
                        "fit into three lines of the node box"
                    ),
                    link="https://example.com/A",
                    details=(("UID", "REQ-A"), ("Document", "Spec")),
                ),
                GraphNode(node_id="B", title="B: short title"),
                GraphNode(node_id="C", title="C"),
            ),
            edges=(
                GraphEdge(
                    source_id="B", target_id="A", relation_type="verifies"
                ),
                GraphEdge(
                    source_id="B", target_id="A", relation_type="verifies"
                ),
                GraphEdge(
                    source_id="C", target_id="A", relation_type="unknown"
                ),
                GraphEdge(source_id="C", target_id="C", relation_type="parent"),
            ),
            relation_types={
                "verifies": RelationStyle(label="Verifies", color="#1f6fd1"),
            },
        ),
    ),
)


@dataclass(frozen=True)
class GalleryChapter:
    title: str
    cases: Tuple[GalleryCase, ...]


_ALL_CASES: Tuple[GalleryCase, ...] = (
    SERIALIZATION_CASES + STRUCTURE_CASES + LEVELS_CASES + EXTREME_GATE_CASES
)


def _chapter(title: str, *case_titles: str) -> GalleryChapter:
    by_title = {case_.title: case_ for case_ in _ALL_CASES}
    return GalleryChapter(
        title=title,
        cases=tuple(by_title[case_title_] for case_title_ in case_titles),
    )


GALLERY_CHAPTERS: Tuple[GalleryChapter, ...] = (
    _chapter("Serialization", "Titles, relation types, and diagnostics"),
    _chapter(
        "Structure: layout",
        "Document tree from the sketch",
        "Columns of different height",
        "Root with connected and unconnected documents",
        "Root without relations",
        "Deep nesting",
        "Long container titles",
    ),
    _chapter(
        "Structure: routes in one container",
        "Fewest bends before the shortest length",
        "Fewest bends under a tall section",
        "Relations that turn together",
        "Relations inside one container",
        "Relations inside one container, more ports",
    ),
    _chapter(
        "Structure: space under the columns",
        "Bottom corridor follows the columns",
        "Through pass under a short section",
        "Vertical lane at the height of a column gap",
        "Lane order in the bottom corridor",
        "Steps beside a pocket",
    ),
    _chapter(
        "Levels: layout",
        "Simple chain",
        "Isolated document + hierarchy",
        "Real project case: root corrected to sit level with its sibling",
        "Root correction picks the nearest child, not the farthest",
        "Corrected root with two non-skip children: sits between them",
        "Corrected root with THREE non-skip children (odd count)",
        "Three chains compete for one parent column",
        "Disconnected components form separate islands",
        "Standalone nodes wrap to the connected graph width",
    ),
    _chapter(
        "Levels: routes and lanes",
        "Nested relations in one channel",
        "Relations across levels from far columns",
        "Basic highway conflict",
        "Complete 3 by 3 relation grid",
        "Direction-aware track order",
        "Busy channel expands to fit its lanes",
        "Extreme number of relations from N8",
    ),
    _chapter(
        "Levels: ports and gates",
        "Opposite ports in one gate",
        "Many ports in one gate",
        *(case_.title for case_ in EXTREME_GATE_CASES),
    ),
    _chapter(
        "Levels: cycles",
        "Two cycles have separate diagnostics",
        "Three-document cycle with an incoming branch",
        "Opposite cycle relations use separate routes",
    ),
)

GALLERY_CASES: Tuple[GalleryCase, ...] = tuple(
    case_ for chapter_ in GALLERY_CHAPTERS for case_ in chapter_.cases
)

# Each case belongs to exactly one chapter.
assert sorted(case_.title for case_ in GALLERY_CASES) == sorted(
    case_.title for case_ in _ALL_CASES
)
