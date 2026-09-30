from typing import List, Optional, Tuple

import pytest

from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CASES,
    GalleryCase,
)
from strictdoc.features.specification_graph.svg_graph.model import (
    Graph,
    GraphEdge,
    GraphNode,
    LayoutMode,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    normalize_graph,
)
from strictdoc.features.specification_graph.svg_graph.structure_layout import (
    StructureLayout,
    compute_structure_layout,
)


def _case(title: str) -> GalleryCase:
    return next(case_ for case_ in GALLERY_CASES if case_.title == title)


def _layout(case: GalleryCase) -> StructureLayout:
    return compute_structure_layout(normalize_graph(case.graph))


def _column_ids(
    layout: StructureLayout, container_id: Optional[str]
) -> List[Tuple[str, ...]]:
    """
    Return the node IDs of each column. None selects the root row.
    """

    return [column_.node_ids for column_ in layout.columns[container_id]]


def test_simple_nodes_form_columns_and_composites_break_them() -> None:
    """
    Consecutive simple nodes form one column. A composite takes its own.

    Code: structure_layout._columns.
    Fails if:
    - a composite node does not break the column of simple nodes.
    """

    layout = _layout(_case("Document tree from the sketch"))

    assert _column_ids(layout, "Section 1") == [
        ("N1",),
        ("Section 4",),
        ("N2", "N3"),
        ("Section 2",),
        ("N4", "N5", "N6", "N7", "N8"),
    ]
    assert [
        column_.is_composite for column_ in layout.columns["Section 1"]
    ] == [False, True, False, True, False]


def test_root_children_without_outside_relations_form_the_block() -> None:
    """
    Root children that relate only to themselves stand in the block.

    Code: structure_layout.split_root_children.
    Fails if:
    - a relation inside one root child counts as a relation to the outside.
    """

    layout = _layout(_case("Root with connected and unconnected documents"))

    assert _column_ids(layout, None) == [("A",), ("B",), ("C",)]
    assert layout.root_block_ids == ("D", "E", "F", "G")


def test_root_rule_applies_to_simple_root_nodes() -> None:
    """
    The root rule applies to simple root nodes as well.

    Code: structure_layout.split_root_children.
    Fails if:
    - a simple root node without relations stays in the row.
    """

    graph = Graph(
        mode=LayoutMode.STRUCTURE,
        root=(
            GraphNode(node_id="Lonely", title="Lonely"),
            GraphNode(
                node_id="Doc",
                title="Doc",
                children=(GraphNode(node_id="R1", title="R1"),),
            ),
            GraphNode(node_id="Linked", title="Linked"),
        ),
        edges=(
            GraphEdge(source_id="R1", target_id="Linked", relation_type="p"),
        ),
    )

    layout = compute_structure_layout(normalize_graph(graph))

    assert [column_.node_ids for column_ in layout.columns[None]] == [
        ("Doc",),
        ("Linked",),
    ]
    assert layout.root_block_ids == ("Lonely",)


def test_other_modes_are_rejected() -> None:
    """
    The structure layout rejects other layout modes.

    Code: structure_layout.compute_structure_layout.
    Fails if:
    - any mode is accepted.
    """

    graph = Graph(
        mode=LayoutMode.LEVELS, root=(GraphNode(node_id="A", title="A"),)
    )

    with pytest.raises(ValueError, match="does not support the mode"):
        compute_structure_layout(normalize_graph(graph))
