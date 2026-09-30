from typing import Dict, Tuple

import pytest

from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CASES,
)
from strictdoc.features.specification_graph.svg_graph.levels_structure import (
    LevelsStructure,
    compute_levels_structure,
)
from strictdoc.features.specification_graph.svg_graph.model import (
    Graph,
    GraphNode,
    LayoutMode,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    normalize_graph,
)


def _structure_of_case(title: str) -> LevelsStructure:
    case = next(case_ for case_ in GALLERY_CASES if case_.title == title)
    return compute_levels_structure(normalize_graph(case.graph))


def _positions(structure: LevelsStructure) -> Dict[str, Tuple[int, int]]:
    return {
        node_id_: (position_.row, position_.column)
        for node_id_, position_ in structure.positions.items()
    }


def test_simple_chain_is_one_column() -> None:
    """
    A chain stands in one column, one node per level.

    Code: levels_structure._IslandLayout._propagate_levels.
    Fails if:
    - a node stands on the level of its parent.
    """

    structure = _structure_of_case("Simple chain")

    assert _positions(structure) == {"A": (0, 0), "B": (1, 0), "C": (2, 0)}
    assert structure.skip_edge_ids == frozenset()


def test_deepest_parent_wins_and_other_relation_skips_levels() -> None:
    """
    A node stands below its deepest parent.

    The relation to the other parent skips levels.

    Code: levels_structure._IslandLayout._propagate_levels,
    levels_structure.compute_levels_structure.
    Fails if:
    - a node stands below its shallowest parent.
    """

    structure = _structure_of_case("Basic highway conflict")

    assert _positions(structure) == {
        "A": (0, 0),
        "B": (1, 0),
        "C": (2, 0),
        "D": (3, 0),
    }
    # Edge 3 is D -> A.
    assert structure.skip_edge_ids == frozenset({"edge-3"})


def test_root_moves_down_to_the_level_of_its_sibling() -> None:
    """
    A root moves down to stand one level above its child.

    Code: levels_structure._IslandLayout._compute_levels.
    Fails if:
    - root correction is off.
    - the corrected root takes the column of the middle child instead of the
      column right of it.
    """

    structure = _structure_of_case(
        "Real project case: root corrected to sit level with its sibling"
    )

    assert _positions(structure) == {
        "Zephyr": (0, 0),
        "L1": (1, 0),
        "DO-178C": (1, 1),
        "L2": (2, 0),
    }
    assert structure.corrected_root_ids == frozenset({"DO-178C"})
    assert structure.skip_edge_ids == frozenset()


def test_root_correction_picks_the_nearest_child() -> None:
    """
    Root correction uses the nearest child, not the farthest.

    Code: levels_structure._IslandLayout._compute_levels.
    Fails if:
    - root correction picks the farthest child.
    - root correction is off.
    - a node stands below its shallowest parent.
    """

    structure = _structure_of_case(
        "Root correction picks the nearest child, not the farthest"
    )

    assert _positions(structure) == {
        "NEAR-ANCHOR-ROOT": (0, 0),
        "NEAR-ANCHOR": (1, 0),
        "ROOT": (1, 1),
        "NEAR": (2, 0),
        "FAR-ANCHOR-ROOT": (0, 2),
        "FAR-ANCHOR-1": (1, 2),
        "FAR-ANCHOR-2": (2, 2),
        "FAR": (3, 2),
    }
    # Edge 7 is FAR -> ROOT.
    assert structure.skip_edge_ids == frozenset({"edge-7"})


def test_corrected_root_with_two_children_stands_between_them() -> None:
    """
    A corrected root with two children stands between them.

    Code: levels_structure._IslandLayout._place_corrected_roots.
    Fails if:
    - the corrected root takes the column of the middle child.
    - root correction is off.
    """

    structure = _structure_of_case(
        "Corrected root with two non-skip children: sits between them"
    )

    positions = _positions(structure)
    assert positions["GUEST"] == (1, 1)
    assert positions["L"] == (2, 0)
    assert positions["R"] == (2, 2)


def test_corrected_root_with_three_children_stands_right_of_middle() -> None:
    """
    A corrected root with three children stands right of the middle child.

    Code: levels_structure._IslandLayout._place_corrected_roots.
    Fails if:
    - the corrected root takes the column of the middle child.
    - root correction is off.
    """

    structure = _structure_of_case(
        "Corrected root with THREE non-skip children (odd count)"
    )

    positions = _positions(structure)
    assert positions["GUEST"] == (1, 2)
    assert positions["L"] == (2, 0)
    assert positions["M"] == (2, 1)
    assert positions["R"] == (2, 3)


def test_contenders_for_one_column_keep_the_input_order() -> None:
    """
    Nodes that lose a column contest stand right of the winner in input order.

    Code: levels_structure._IslandLayout._assign_level_columns.
    Fails if:
    - a losing node stands right of the winner instead of right of the last
      contender.
    """

    structure = _structure_of_case("Three chains compete for one parent column")

    assert _positions(structure) == {
        "P": (0, 0),
        "Q": (0, 3),
        "A": (1, 0),
        "B": (1, 1),
        "C": (1, 2),
        "A1": (2, 0),
        "B1": (2, 1),
        "C1": (2, 2),
        "Q1": (1, 3),
        "Q2": (2, 3),
    }


def test_islands_stand_side_by_side_below_standalone_nodes() -> None:
    """
    Islands stand side by side below the standalone nodes.

    Code: levels_structure.compute_levels_structure.
    Fails if:
    - the islands overlap in the same columns.
    """

    structure = _structure_of_case(
        "Disconnected components form separate islands"
    )

    assert _positions(structure) == {
        "A1": (1, 0),
        "B1": (1, 1),
        "A2": (2, 0),
        "B2": (2, 1),
        "Standalone": (0, 0),
    }
    assert structure.standalone_row_count == 1
    assert structure.standalone_node_ids == ("Standalone",)


def test_standalone_grid_takes_the_connected_graph_width() -> None:
    """
    The standalone grid takes the width of the connected graph.

    Code: levels_structure.compute_levels_structure.
    Fails if:
    - the standalone grid is always square.
    - the islands overlap in the same columns.
    """

    structure = _structure_of_case(
        "Standalone nodes wrap to the connected graph width"
    )

    positions = _positions(structure)
    # Ten nodes in three columns take four rows. A square grid would take
    # four columns.
    assert structure.standalone_row_count == 4
    assert positions["Standalone 1"] == (0, 0)
    assert positions["Standalone 3"] == (0, 2)
    assert positions["Standalone 4"] == (1, 0)
    assert positions["Standalone 10"] == (3, 0)
    assert positions["Root A"] == (4, 0)
    assert positions["Child C"] == (5, 2)


def test_standalone_grid_is_close_to_square_without_connected_graph() -> None:
    """
    Without a connected graph, the standalone grid is close to square.

    Code: levels_structure._square_grid_width.
    Fails if:
    - the standalone grid is one row.
    """

    graph = Graph(
        mode=LayoutMode.LEVELS,
        root=tuple(
            GraphNode(node_id=f"S{index_}", title=f"S{index_}")
            for index_ in range(5)
        ),
    )

    structure = compute_levels_structure(normalize_graph(graph))

    assert structure.column_count == 3
    assert structure.row_count == 2
    assert _positions(structure)["S4"] == (1, 1)


def test_edge_that_closes_a_cycle_is_a_skip_edge() -> None:
    """
    The downward edge that closes a cycle is a skip edge.

    Code: levels_structure.compute_levels_structure.
    Fails if:
    - only upward edges across levels are skip edges.
    - the edge that closes the cycle takes part in the levels.
    """

    structure = _structure_of_case(
        "Three-document cycle with an incoming branch"
    )

    assert _positions(structure) == {
        "C": (0, 0),
        "B": (1, 0),
        "A": (2, 0),
        "D": (3, 0),
    }
    # Edge 3 is C -> A: it closes the cycle and points down.
    assert structure.skip_edge_ids == frozenset({"edge-3"})


def test_other_modes_are_rejected() -> None:
    """
    The levels structure rejects other layout modes.

    Code: levels_structure.compute_levels_structure.
    Fails if:
    - any mode is accepted.
    """

    graph = Graph(
        mode=LayoutMode.STRUCTURE,
        root=(GraphNode(node_id="A", title="A"),),
    )

    with pytest.raises(ValueError, match="does not support the mode"):
        compute_levels_structure(normalize_graph(graph))
