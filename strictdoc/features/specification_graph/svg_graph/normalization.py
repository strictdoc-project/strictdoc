"""
Stage 1 of the graph generator: validation and normalization.

The stage validates the input model, removes duplicate edges and self-loops,
finds cycles, and marks the edges that participate in the level
calculation. The stage uses no pixel geometry.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Mapping, Optional, Set, Tuple

from strictdoc.features.specification_graph.svg_graph.model import (
    BUILTIN_RELATION_STYLES,
    Graph,
    GraphEdge,
    GraphGroup,
    GraphNode,
    LayoutMode,
    RelationStyle,
)


class GraphModelError(ValueError):
    pass


class DiagnosticKind(Enum):
    DUPLICATE_EDGE = "duplicate_edge"
    SELF_LOOP = "self_loop"
    CYCLE = "cycle"


@dataclass(frozen=True)
class Diagnostic:
    kind: DiagnosticKind
    message: str
    node_ids: Tuple[str, ...]


@dataclass(frozen=True)
class GraphCycle:
    cycle_id: str
    node_ids: Tuple[str, ...]


@dataclass(frozen=True)
class NormalizedEdge:
    edge_id: str
    source_id: str
    target_id: str
    relation_type: str
    # Structure mode: one endpoint contains the other.
    is_ancestor_link: bool
    cycle_id: Optional[str]
    # The edge participates in the level calculation. From each cycle, the
    # edges that would close the cycle do not participate.
    is_level_edge: bool


@dataclass(frozen=True)
class NormalizedGraph:
    mode: LayoutMode
    # All nodes in input order: pre-order traversal of the structure.
    nodes: Tuple[GraphNode, ...]
    parent_ids: Mapping[str, Optional[str]]
    edges: Tuple[NormalizedEdge, ...]
    groups: Tuple[GraphGroup, ...]
    cycles: Tuple[GraphCycle, ...]
    diagnostics: Tuple[Diagnostic, ...]
    # Styles of the built-in types and of the input types.
    relation_types: Mapping[str, RelationStyle]


def normalize_graph(graph: Graph) -> NormalizedGraph:
    nodes, parent_ids = _collect_nodes(graph)
    _validate_groups(graph, nodes)

    node_index: Dict[str, int] = {
        node_.node_id: index_ for index_, node_ in enumerate(nodes)
    }
    diagnostics: List[Diagnostic] = []
    edges = _deduplicate_edges(graph.edges, node_index, diagnostics)

    components = _strongly_connected_components(nodes, edges)
    cycles = _cycles_from_components(components, node_index)
    cycle_id_by_node: Dict[str, str] = {
        node_id_: cycle_.cycle_id
        for cycle_ in cycles
        for node_id_ in cycle_.node_ids
    }
    for cycle_ in cycles:
        diagnostics.append(
            Diagnostic(
                kind=DiagnosticKind.CYCLE,
                message=(
                    f"Relations form a cycle {cycle_.cycle_id}: "
                    f"{', '.join(cycle_.node_ids)}."
                ),
                node_ids=cycle_.node_ids,
            )
        )

    level_edge_flags = _level_edge_flags(edges, cycle_id_by_node)

    normalized_edges: List[NormalizedEdge] = []
    for index_, edge_ in enumerate(edges):
        source_cycle_id_ = cycle_id_by_node.get(edge_.source_id)
        is_cyclic_ = (
            source_cycle_id_ is not None
            and source_cycle_id_ == cycle_id_by_node.get(edge_.target_id)
        )
        normalized_edges.append(
            NormalizedEdge(
                edge_id=f"edge-{index_ + 1}",
                source_id=edge_.source_id,
                target_id=edge_.target_id,
                relation_type=edge_.relation_type,
                is_ancestor_link=(
                    graph.mode is LayoutMode.STRUCTURE
                    and _is_ancestor_link(
                        edge_.source_id, edge_.target_id, parent_ids
                    )
                ),
                cycle_id=source_cycle_id_ if is_cyclic_ else None,
                is_level_edge=level_edge_flags[index_],
            )
        )

    return NormalizedGraph(
        mode=graph.mode,
        nodes=tuple(nodes),
        parent_ids=parent_ids,
        edges=tuple(normalized_edges),
        groups=graph.groups,
        cycles=cycles,
        diagnostics=tuple(diagnostics),
        relation_types={**BUILTIN_RELATION_STYLES, **graph.relation_types},
    )


def _collect_nodes(
    graph: Graph,
) -> Tuple[List[GraphNode], Dict[str, Optional[str]]]:
    nodes: List[GraphNode] = []
    parent_ids: Dict[str, Optional[str]] = {}
    pending: List[Tuple[GraphNode, Optional[str]]] = [
        (node_, None) for node_ in reversed(graph.root)
    ]
    while len(pending) > 0:
        node, parent_id = pending.pop()
        if node.node_id in parent_ids:
            raise GraphModelError(f"Duplicate node ID: {node.node_id}.")
        if len(node.children) > 0 and graph.mode is not LayoutMode.STRUCTURE:
            raise GraphModelError(
                f"Node {node.node_id} has children, "
                f"but only the structure mode supports children."
            )
        if (
            node.group_id is not None
            and graph.mode is not LayoutMode.LEVELS_WITH_GROUPS
        ):
            raise GraphModelError(
                f"Node {node.node_id} has a group, "
                f"but only the levels with groups mode supports groups."
            )
        nodes.append(node)
        parent_ids[node.node_id] = parent_id
        pending.extend(
            (child_, node.node_id) for child_ in reversed(node.children)
        )
    return nodes, parent_ids


def _validate_groups(graph: Graph, nodes: List[GraphNode]) -> None:
    if (
        len(graph.groups) > 0
        and graph.mode is not LayoutMode.LEVELS_WITH_GROUPS
    ):
        raise GraphModelError(
            "Only the levels with groups mode supports groups."
        )
    group_ids: Set[str] = set()
    for group_ in graph.groups:
        if group_.group_id in group_ids:
            raise GraphModelError(f"Duplicate group ID: {group_.group_id}.")
        group_ids.add(group_.group_id)
    for node_ in nodes:
        if node_.group_id is not None and node_.group_id not in group_ids:
            raise GraphModelError(
                f"Node {node_.node_id} refers to an unknown group: "
                f"{node_.group_id}."
            )


def _deduplicate_edges(
    edges: Tuple[GraphEdge, ...],
    node_index: Dict[str, int],
    diagnostics: List[Diagnostic],
) -> List[GraphEdge]:
    result: List[GraphEdge] = []
    seen: Set[GraphEdge] = set()
    for edge_ in edges:
        for endpoint_id_ in (edge_.source_id, edge_.target_id):
            if endpoint_id_ not in node_index:
                raise GraphModelError(
                    f"Edge {edge_.source_id} -> {edge_.target_id} refers to "
                    f"an unknown node: {endpoint_id_}."
                )
        if edge_.source_id == edge_.target_id:
            diagnostics.append(
                Diagnostic(
                    kind=DiagnosticKind.SELF_LOOP,
                    message=(
                        f"Node {edge_.source_id} has a relation "
                        f"to itself: {edge_.relation_type}."
                    ),
                    node_ids=(edge_.source_id,),
                )
            )
            continue
        if edge_ in seen:
            diagnostics.append(
                Diagnostic(
                    kind=DiagnosticKind.DUPLICATE_EDGE,
                    message=(
                        f"Duplicate relation {edge_.source_id} -> "
                        f"{edge_.target_id}: {edge_.relation_type}."
                    ),
                    node_ids=(edge_.source_id, edge_.target_id),
                )
            )
            continue
        seen.add(edge_)
        result.append(edge_)
    return result


def _strongly_connected_components(
    nodes: List[GraphNode], edges: List[GraphEdge]
) -> List[List[str]]:
    """
    Tarjan's algorithm, iterative to support deep graphs.
    """
    successors: Dict[str, List[str]] = {node_.node_id: [] for node_ in nodes}
    for edge_ in edges:
        successors[edge_.source_id].append(edge_.target_id)

    visit_index: Dict[str, int] = {}
    low_link: Dict[str, int] = {}
    stack: List[str] = []
    on_stack: Set[str] = set()
    components: List[List[str]] = []

    for start_node_ in nodes:
        if start_node_.node_id in visit_index:
            continue
        work: List[Tuple[str, int]] = [(start_node_.node_id, 0)]
        while len(work) > 0:
            node_id, successor_position = work.pop()
            if successor_position == 0:
                visit_index[node_id] = len(visit_index)
                low_link[node_id] = visit_index[node_id]
                stack.append(node_id)
                on_stack.add(node_id)
            node_successors = successors[node_id]
            if successor_position < len(node_successors):
                work.append((node_id, successor_position + 1))
                successor_id = node_successors[successor_position]
                if successor_id not in visit_index:
                    work.append((successor_id, 0))
                elif successor_id in on_stack:
                    low_link[node_id] = min(
                        low_link[node_id], visit_index[successor_id]
                    )
                continue
            if low_link[node_id] == visit_index[node_id]:
                component: List[str] = []
                while True:
                    member_id = stack.pop()
                    on_stack.discard(member_id)
                    component.append(member_id)
                    if member_id == node_id:
                        break
                components.append(component)
            if len(work) > 0:
                caller_id = work[-1][0]
                low_link[caller_id] = min(
                    low_link[caller_id], low_link[node_id]
                )
    return components


def _cycles_from_components(
    components: List[List[str]], node_index: Dict[str, int]
) -> Tuple[GraphCycle, ...]:
    cyclic_components = sorted(
        (
            sorted(component_, key=lambda node_id_: node_index[node_id_])
            for component_ in components
            if len(component_) > 1
        ),
        key=lambda component_: node_index[component_[0]],
    )
    return tuple(
        GraphCycle(cycle_id=f"cycle-{index_ + 1}", node_ids=tuple(component_))
        for index_, component_ in enumerate(cyclic_components)
    )


def _level_edge_flags(
    edges: List[GraphEdge], cycle_id_by_node: Dict[str, str]
) -> List[bool]:
    """
    Select the edges that take part in the level calculation.

    An edge between different cycles cannot close a cycle. Inside a cycle,
    the edges are accepted in input order. An edge is rejected if its target
    already reaches its source through the accepted edges.
    """
    accepted_successors: Dict[str, List[str]] = {}
    flags: List[bool] = []
    for edge_ in edges:
        cycle_id_ = cycle_id_by_node.get(edge_.source_id)
        if cycle_id_ is None or cycle_id_ != cycle_id_by_node.get(
            edge_.target_id
        ):
            flags.append(True)
            continue
        closes_cycle_ = _reaches(
            edge_.target_id, edge_.source_id, accepted_successors
        )
        if not closes_cycle_:
            accepted_successors.setdefault(edge_.source_id, []).append(
                edge_.target_id
            )
        flags.append(not closes_cycle_)
    return flags


def _reaches(
    start_id: str, goal_id: str, successors: Dict[str, List[str]]
) -> bool:
    pending: List[str] = [start_id]
    seen: Set[str] = set()
    while len(pending) > 0:
        node_id = pending.pop()
        if node_id == goal_id:
            return True
        if node_id in seen:
            continue
        seen.add(node_id)
        pending.extend(successors.get(node_id, ()))
    return False


def _is_ancestor_link(
    source_id: str, target_id: str, parent_ids: Mapping[str, Optional[str]]
) -> bool:
    return _is_ancestor(source_id, target_id, parent_ids) or _is_ancestor(
        target_id, source_id, parent_ids
    )


def _is_ancestor(
    ancestor_id: str, node_id: str, parent_ids: Mapping[str, Optional[str]]
) -> bool:
    current_id = parent_ids[node_id]
    while current_id is not None:
        if current_id == ancestor_id:
            return True
        current_id = parent_ids[current_id]
    return False
