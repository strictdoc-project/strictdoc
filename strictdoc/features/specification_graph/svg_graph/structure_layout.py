"""
Stage 2 of the graph generator for the structure mode: structure.

The stage places the children of each container in columns. The stage uses
no pixel geometry. spec.md, section "Режим «структура»", defines the rules.
"""

from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Set, Tuple

from strictdoc.features.specification_graph.svg_graph.model import (
    GraphNode,
    LayoutMode,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedGraph,
)


@dataclass(frozen=True)
class ContainerColumn:
    # Simple nodes from top to bottom, or one composite node.
    node_ids: Tuple[str, ...]
    is_composite: bool


@dataclass(frozen=True)
class StructureLayout:
    # Columns of each composite node, by node ID. The key None is the row of
    # the connected root children.
    columns: Mapping[Optional[str], Tuple[ContainerColumn, ...]]
    # Root children in the block above the row, in input order.
    root_block_ids: Tuple[str, ...]


def compute_structure_layout(
    normalized_graph: NormalizedGraph,
) -> StructureLayout:
    if normalized_graph.mode is not LayoutMode.STRUCTURE:
        raise ValueError(
            f"Structure layout does not support the mode: "
            f"{normalized_graph.mode.value}."
        )

    root_nodes = [
        node_
        for node_ in normalized_graph.nodes
        if normalized_graph.parent_ids[node_.node_id] is None
    ]
    row_nodes, block_nodes = split_root_children(normalized_graph, root_nodes)

    columns: Dict[Optional[str], Tuple[ContainerColumn, ...]] = {
        None: _columns(row_nodes)
    }
    for node_ in normalized_graph.nodes:
        if len(node_.children) > 0:
            columns[node_.node_id] = _columns(list(node_.children))
    return StructureLayout(
        columns=columns,
        root_block_ids=tuple(node_.node_id for node_ in block_nodes),
    )


def split_root_children(
    normalized_graph: NormalizedGraph, root_nodes: List[GraphNode]
) -> Tuple[List[GraphNode], List[GraphNode]]:
    """
    Split the root children into the row and the block.

    This function is the only place of the root rule. spec.md, section "Раскладка корня": a root child is connected if the
    child or any of its descendants has a relation to a node outside the
    child. Connected children form the row. The other children form the
    block above the row. Inner containers do not use this rule.
    """

    root_of: Dict[str, str] = {}
    for node_ in normalized_graph.nodes:
        parent_id_ = normalized_graph.parent_ids[node_.node_id]
        root_of[node_.node_id] = (
            node_.node_id if parent_id_ is None else root_of[parent_id_]
        )
    connected_root_ids: Set[str] = set()
    for edge_ in normalized_graph.edges:
        source_root_ = root_of[edge_.source_id]
        target_root_ = root_of[edge_.target_id]
        if source_root_ != target_root_:
            connected_root_ids.add(source_root_)
            connected_root_ids.add(target_root_)
    row_nodes = [
        node_ for node_ in root_nodes if node_.node_id in connected_root_ids
    ]
    block_nodes = [
        node_ for node_ in root_nodes if node_.node_id not in connected_root_ids
    ]
    return row_nodes, block_nodes


def _columns(children: List[GraphNode]) -> Tuple[ContainerColumn, ...]:
    """
    Apply the column rule to the children of one container.

    Consecutive simple nodes form one column from top to bottom. A composite
    node takes a column of its own.
    """

    columns: List[ContainerColumn] = []
    simple_run: List[str] = []
    for child_ in children:
        if len(child_.children) == 0:
            simple_run.append(child_.node_id)
            continue
        if len(simple_run) > 0:
            columns.append(
                ContainerColumn(node_ids=tuple(simple_run), is_composite=False)
            )
            simple_run = []
        columns.append(
            ContainerColumn(node_ids=(child_.node_id,), is_composite=True)
        )
    if len(simple_run) > 0:
        columns.append(
            ContainerColumn(node_ids=tuple(simple_run), is_composite=False)
        )
    return tuple(columns)
