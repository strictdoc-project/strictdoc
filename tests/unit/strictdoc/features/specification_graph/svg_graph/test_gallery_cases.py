"""
Stage invariants on every gallery case.
"""

from typing import Dict, List, Set

import pytest

from developer.examples.specification_graph.gallery_cases import (
    GALLERY_CASES,
    GalleryCase,
)
from strictdoc.features.specification_graph.svg_graph.normalization import (
    NormalizedGraph,
    normalize_graph,
)


@pytest.mark.parametrize(
    "case", GALLERY_CASES, ids=[case_.title for case_ in GALLERY_CASES]
)
def test_normalization_invariants(case: GalleryCase) -> None:
    normalized_graph = normalize_graph(case.graph)

    edge_ids = [edge_.edge_id for edge_ in normalized_graph.edges]
    assert len(edge_ids) == len(set(edge_ids))

    _assert_level_edges_are_acyclic(normalized_graph)

    cycle_members: Dict[str, Set[str]] = {
        cycle_.cycle_id: set(cycle_.node_ids)
        for cycle_ in normalized_graph.cycles
    }
    for edge_ in normalized_graph.edges:
        if edge_.cycle_id is not None:
            assert edge_.source_id in cycle_members[edge_.cycle_id]
            assert edge_.target_id in cycle_members[edge_.cycle_id]

    assert normalize_graph(case.graph) == normalized_graph


def _assert_level_edges_are_acyclic(normalized_graph: NormalizedGraph) -> None:
    successors: Dict[str, List[str]] = {
        node_.node_id: [] for node_ in normalized_graph.nodes
    }
    incoming_count: Dict[str, int] = {
        node_.node_id: 0 for node_ in normalized_graph.nodes
    }
    for edge_ in normalized_graph.edges:
        if edge_.is_level_edge:
            successors[edge_.source_id].append(edge_.target_id)
            incoming_count[edge_.target_id] += 1

    ready = [
        node_id_ for node_id_, count_ in incoming_count.items() if count_ == 0
    ]
    visited_count = 0
    while len(ready) > 0:
        node_id = ready.pop()
        visited_count += 1
        for successor_id_ in successors[node_id]:
            incoming_count[successor_id_] -= 1
            if incoming_count[successor_id_] == 0:
                ready.append(successor_id_)
    assert visited_count == len(normalized_graph.nodes)
