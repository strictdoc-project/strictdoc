from typing import Sequence, Tuple

import pytest

from strictdoc.features.specification_graph.svg_graph.model import (
    Graph,
    GraphEdge,
    GraphGroup,
    GraphNode,
    LayoutMode,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    DiagnosticKind,
    GraphModelError,
    NormalizedGraph,
    normalize_graph,
)


def _levels_graph(
    node_ids: Sequence[str], edges: Sequence[Tuple[str, str]]
) -> Graph:
    return Graph(
        mode=LayoutMode.LEVELS,
        root=tuple(
            GraphNode(node_id=node_id_, title=node_id_) for node_id_ in node_ids
        ),
        edges=tuple(
            GraphEdge(
                source_id=source_id_,
                target_id=target_id_,
                relation_type="parent",
            )
            for source_id_, target_id_ in edges
        ),
    )


def _edge_pairs(graph: NormalizedGraph) -> Tuple[Tuple[str, str], ...]:
    return tuple((edge_.source_id, edge_.target_id) for edge_ in graph.edges)


def test_nodes_follow_pre_order_of_the_structure() -> None:
    """
    Nodes and their parents follow the pre-order of the input structure.

    Code: normalization._collect_nodes.
    Fails if:
    - the traversal pushes the children in input order, so the last child comes
      out first.
    """

    graph = Graph(
        mode=LayoutMode.STRUCTURE,
        root=(
            GraphNode(
                node_id="DOC",
                title="DOC",
                children=(
                    GraphNode(
                        node_id="SECTION",
                        title="SECTION",
                        children=(GraphNode(node_id="REQ-1", title="REQ-1"),),
                    ),
                    GraphNode(node_id="REQ-2", title="REQ-2"),
                ),
            ),
            GraphNode(node_id="OTHER", title="OTHER"),
        ),
    )

    normalized_graph = normalize_graph(graph)

    assert tuple(node_.node_id for node_ in normalized_graph.nodes) == (
        "DOC",
        "SECTION",
        "REQ-1",
        "REQ-2",
        "OTHER",
    )
    assert dict(normalized_graph.parent_ids) == {
        "DOC": None,
        "SECTION": "DOC",
        "REQ-1": "SECTION",
        "REQ-2": "DOC",
        "OTHER": None,
    }


def test_duplicate_node_id_is_an_error() -> None:
    """
    A duplicate node ID rejects the input.

    Code: normalization._collect_nodes.
    Fails if:
    - the duplicate node ID check is missing.
    """

    with pytest.raises(GraphModelError, match="Duplicate node ID: A"):
        normalize_graph(_levels_graph(["A", "B", "A"], []))


def test_edge_to_unknown_node_is_an_error() -> None:
    """
    An edge to an unknown node rejects the input.

    Code: normalization._deduplicate_edges.
    Fails if:
    - the unknown endpoint check is missing.
    """

    with pytest.raises(GraphModelError, match="unknown node: X"):
        normalize_graph(_levels_graph(["A"], [("A", "X")]))


def test_children_outside_structure_mode_are_an_error() -> None:
    """
    Children outside the structure mode reject the input.

    Code: normalization._collect_nodes.
    Fails if:
    - children are accepted in any mode.
    """

    graph = Graph(
        mode=LayoutMode.LEVELS,
        root=(
            GraphNode(
                node_id="A",
                title="A",
                children=(GraphNode(node_id="B", title="B"),),
            ),
        ),
    )

    with pytest.raises(GraphModelError, match="Node A has children"):
        normalize_graph(graph)


def test_group_outside_groups_mode_is_an_error() -> None:
    """
    A node group outside the levels with groups mode rejects the input.

    Code: normalization._collect_nodes.
    Fails if:
    - a node group is accepted in any mode.
    """

    graph = Graph(
        mode=LayoutMode.LEVELS,
        root=(GraphNode(node_id="A", title="A", group_id="G"),),
    )

    with pytest.raises(GraphModelError, match="Node A has a group"):
        normalize_graph(graph)


def test_unknown_group_is_an_error() -> None:
    """
    A reference to an unknown group rejects the input.

    Code: normalization._validate_groups.
    Fails if:
    - the unknown group check is missing.
    """

    graph = Graph(
        mode=LayoutMode.LEVELS_WITH_GROUPS,
        root=(GraphNode(node_id="A", title="A", group_id="G"),),
        groups=(GraphGroup(group_id="OTHER", title="Other"),),
    )

    with pytest.raises(GraphModelError, match="unknown group: G"):
        normalize_graph(graph)


def test_exact_duplicate_edges_are_drawn_once_and_reported() -> None:
    """
    An exact duplicate edge is dropped and reported.

    An edge with the same ends and another type stays.

    Code: normalization._deduplicate_edges.
    Fails if:
    - exact duplicates are kept.
    """

    graph = Graph(
        mode=LayoutMode.LEVELS,
        root=(
            GraphNode(node_id="C", title="C"),
            GraphNode(node_id="P", title="P"),
        ),
        edges=(
            GraphEdge(source_id="C", target_id="P", relation_type="parent"),
            GraphEdge(source_id="C", target_id="P", relation_type="parent"),
            GraphEdge(source_id="C", target_id="P", relation_type="verifies"),
        ),
    )

    normalized_graph = normalize_graph(graph)

    assert tuple(edge_.relation_type for edge_ in normalized_graph.edges) == (
        "parent",
        "verifies",
    )
    assert tuple(
        diagnostic_.kind for diagnostic_ in normalized_graph.diagnostics
    ) == (DiagnosticKind.DUPLICATE_EDGE,)


def test_self_loop_is_not_drawn_and_marks_the_node() -> None:
    """
    A self-loop is dropped and reported on its node.

    Code: normalization._deduplicate_edges.
    Fails if:
    - self-loops are kept.
    """

    normalized_graph = normalize_graph(
        _levels_graph(["A", "B"], [("A", "A"), ("A", "B")])
    )

    assert _edge_pairs(normalized_graph) == (("A", "B"),)
    assert len(normalized_graph.diagnostics) == 1
    diagnostic = normalized_graph.diagnostics[0]
    assert diagnostic.kind is DiagnosticKind.SELF_LOOP
    assert diagnostic.node_ids == ("A",)


def test_edge_ids_are_stable_and_follow_input_order() -> None:
    """
    Edge IDs are edge-1, edge-2, ... in input order.

    Code: normalization.normalize_graph.
    Fails if:
    - the numbering starts at 0.
    """

    normalized_graph = normalize_graph(
        _levels_graph(["A", "B", "C"], [("B", "A"), ("C", "B")])
    )

    assert tuple(edge_.edge_id for edge_ in normalized_graph.edges) == (
        "edge-1",
        "edge-2",
    )


def test_two_cycles_have_separate_diagnostics() -> None:
    """
    Each cycle has its own ID, numbered by the first node of the cycle.

    Gallery case: "Two cycles have separate diagnostics".

    Code: normalization._cycles_from_components.
    Fails if:
    - the cycles are numbered in another order.
    """

    normalized_graph = normalize_graph(
        _levels_graph(
            ["A", "B", "C", "D", "E", "F"],
            [
                ("A", "B"),
                ("B", "A"),
                ("C", "D"),
                ("D", "E"),
                ("E", "C"),
                ("F", "C"),
            ],
        )
    )

    assert tuple(
        (cycle_.cycle_id, cycle_.node_ids) for cycle_ in normalized_graph.cycles
    ) == (
        ("cycle-1", ("A", "B")),
        ("cycle-2", ("C", "D", "E")),
    )
    assert tuple(
        (edge_.source_id, edge_.target_id, edge_.cycle_id)
        for edge_ in normalized_graph.edges
    ) == (
        ("A", "B", "cycle-1"),
        ("B", "A", "cycle-1"),
        ("C", "D", "cycle-2"),
        ("D", "E", "cycle-2"),
        ("E", "C", "cycle-2"),
        ("F", "C", None),
    )
    assert tuple(
        diagnostic_.kind for diagnostic_ in normalized_graph.diagnostics
    ) == (DiagnosticKind.CYCLE, DiagnosticKind.CYCLE)


def test_edge_that_closes_a_cycle_does_not_take_part_in_levels() -> None:
    """
    The edge that closes a cycle does not take part in the levels.

    The edges are accepted in input order.

    Gallery case: "Three-document cycle with an incoming branch".

    Code: normalization._level_edge_flags.
    Fails if:
    - the edge that closes a cycle takes part in the levels.
    """

    normalized_graph = normalize_graph(
        _levels_graph(
            ["A", "B", "C", "D"],
            [("A", "B"), ("B", "C"), ("C", "A"), ("D", "A")],
        )
    )

    assert tuple(
        (edge_.source_id, edge_.target_id, edge_.is_level_edge)
        for edge_ in normalized_graph.edges
    ) == (
        ("A", "B", True),
        ("B", "C", True),
        ("C", "A", False),
        ("D", "A", True),
    )
    assert normalized_graph.cycles[0].node_ids == ("A", "B", "C")


def test_level_edges_are_acyclic_for_nested_cycles() -> None:
    """
    The level edges stay acyclic when cycles share nodes.

    Code: normalization._level_edge_flags, normalization._reaches.
    Fails if:
    - the edge that closes a cycle takes part in the levels.
    """

    normalized_graph = normalize_graph(
        _levels_graph(
            ["A", "B", "C"],
            [("A", "B"), ("B", "A"), ("B", "C"), ("C", "A"), ("A", "C")],
        )
    )

    assert tuple(
        (edge_.source_id, edge_.target_id)
        for edge_ in normalized_graph.edges
        if edge_.is_level_edge
    ) == (("A", "B"), ("B", "C"), ("A", "C"))


def test_ancestor_links_are_detected_in_both_directions() -> None:
    """
    A link between a node and its ancestor is detected in both directions.

    Code: normalization._is_ancestor_link.
    Fails if:
    - only the link from the ancestor to its descendant is detected.
    """

    graph = Graph(
        mode=LayoutMode.STRUCTURE,
        root=(
            GraphNode(
                node_id="DOC",
                title="DOC",
                children=(
                    GraphNode(
                        node_id="SECTION",
                        title="SECTION",
                        children=(GraphNode(node_id="REQ-1", title="REQ-1"),),
                    ),
                    GraphNode(node_id="REQ-2", title="REQ-2"),
                ),
            ),
        ),
        edges=(
            GraphEdge(source_id="REQ-1", target_id="DOC", relation_type="p"),
            GraphEdge(
                source_id="SECTION", target_id="REQ-1", relation_type="p"
            ),
            GraphEdge(source_id="REQ-1", target_id="REQ-2", relation_type="p"),
        ),
    )

    normalized_graph = normalize_graph(graph)

    assert tuple(
        edge_.is_ancestor_link for edge_ in normalized_graph.edges
    ) == (True, True, False)


def test_deep_chain_does_not_hit_the_recursion_limit() -> None:
    """
    A cycle of 1500 nodes does not hit the Python recursion limit.

    Code: normalization._strongly_connected_components,
    normalization._level_edge_flags.
    Fails if:
    - the cycle search is recursive.
    - the edge that closes the cycle takes part in the levels.
    """

    node_ids = [f"N{index_}" for index_ in range(1500)]
    edges = [
        (node_ids[index_ + 1], node_ids[index_])
        for index_ in range(len(node_ids) - 1)
    ]
    edges.append((node_ids[0], node_ids[-1]))

    normalized_graph = normalize_graph(_levels_graph(node_ids, edges))

    assert len(normalized_graph.cycles) == 1
    assert len(normalized_graph.cycles[0].node_ids) == 1500
    assert (
        sum(1 for edge_ in normalized_graph.edges if not edge_.is_level_edge)
        == 1
    )
