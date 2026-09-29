"""
Example graphs for the specification graph gallery.

Each case is an input of the graph generator. The gallery script renders the
cases for visual control. The unit tests use the same cases as test inputs.
"""

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

from strictdoc.features.specification_graph.svg_graph.model import (
    Graph,
    GraphEdge,
    GraphNode,
    LayoutMode,
)


@dataclass(frozen=True)
class GalleryCase:
    title: str
    description: str
    graph: Graph
    # Number of the open question in spec.md that the case helps to decide.
    open_question: Optional[int] = None


def _levels_case(
    title: str,
    description: str,
    node_ids: Sequence[str],
    edges: Sequence[Tuple[str, str]],
    open_question: Optional[int] = None,
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
        open_question=open_question,
    )


LEVELS_CASES: Tuple[GalleryCase, ...] = (
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
            "and C compete for the column of P. Q1 takes the column of Q. "
            "The case shows which branches stay straight."
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
        open_question=24,
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
            "Eight standalone nodes stand in a grid above the connected "
            "graph. The grid has the three columns of the connected graph."
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

GALLERY_CASES: Tuple[GalleryCase, ...] = LEVELS_CASES
