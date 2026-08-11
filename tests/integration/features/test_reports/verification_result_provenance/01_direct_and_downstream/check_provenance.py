import os
from typing import Optional

from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.constants import GraphEdgeLabel
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.helpers.parallelizer import Parallelizer


def get_only_child_node_with_edge(
    traceability_index: TraceabilityIndex,
    parent_node: SDocNode,
    edge_label: GraphEdgeLabel,
) -> SDocNode:
    matching_child_nodes = [
        child_node_
        for child_node_, child_edge_label_ in (
            traceability_index.get_child_relations_with_roles(parent_node)
        )
        if child_edge_label_ == edge_label
    ]
    assert len(matching_child_nodes) == 1, matching_child_nodes
    return matching_child_nodes[0]


def get_child_relation_uids(
    traceability_index: TraceabilityIndex,
    parent_node: SDocNode,
) -> set[tuple[str, Optional[str]]]:
    child_relations = traceability_index.get_child_relations_with_roles(
        parent_node
    )
    return {
        (child_node_.reserved_uid, child_edge_label_)
        for child_node_, child_edge_label_ in child_relations
    }


def get_child_relation_types(
    traceability_index: TraceabilityIndex,
    parent_node: SDocNode,
) -> list[tuple[str, Optional[str]]]:
    return [
        (child_node_.node_type, child_edge_label_)
        for child_node_, child_edge_label_ in (
            traceability_index.get_child_relations_with_roles(parent_node)
        )
    ]


def get_verification_result_provenance_signature(
    traceability_index: TraceabilityIndex,
    requirement: SDocNode,
) -> list[tuple[SDocNode, Optional[SDocNode], SDocNode]]:
    return [
        (
            provenance_.verified_requirement,
            provenance_.test_case,
            provenance_.test_result,
        )
        for provenance_ in (
            traceability_index.get_verification_result_provenance(requirement)
        )
    ]


def main() -> None:
    project_root: str = os.getcwd()
    project_config: ProjectConfig = (
        ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=project_root
        )
    )
    project_config.input_paths = [project_root]
    project_config.source_root_path = project_root
    project_config.validate_and_finalize()
    parallelizer: Parallelizer = Parallelizer.create(parallelize=False)
    try:
        traceability_index: TraceabilityIndex = TraceabilityIndexBuilder.create(
            project_config=project_config,
            parallelizer=parallelizer,
        )
    finally:
        parallelizer.shutdown()

    grandparent_requirement = traceability_index.get_node_by_uid(
        "REQ-GRANDPARENT"
    )
    parent_requirement = traceability_index.get_node_by_uid("REQ-PARENT")
    direct_requirement = traceability_index.get_node_by_uid("REQ-DIRECT")
    mediated_requirement = traceability_index.get_node_by_uid("REQ-MEDIATED")
    assert isinstance(grandparent_requirement, SDocNode)
    assert isinstance(parent_requirement, SDocNode)
    assert isinstance(direct_requirement, SDocNode)
    assert isinstance(mediated_requirement, SDocNode)

    assert get_child_relation_uids(
        traceability_index, grandparent_requirement
    ) == {("REQ-PARENT", None)}
    assert get_child_relation_uids(traceability_index, parent_requirement) == {
        ("REQ-DIRECT", None),
        ("REQ-MEDIATED", None),
    }

    assert get_child_relation_types(traceability_index, direct_requirement) == [
        ("TEST_RESULT", GraphEdgeLabel.IS_SATISFIED_BY)
    ]
    direct_result = get_only_child_node_with_edge(
        traceability_index,
        direct_requirement,
        GraphEdgeLabel.IS_SATISFIED_BY,
    )
    assert direct_result.node_type == "TEST_RESULT"
    assert direct_result.reserved_status == "FAILED"

    assert get_child_relation_types(
        traceability_index, mediated_requirement
    ) == [("TEST_CASE", GraphEdgeLabel.IS_VERIFIED_BY)]
    test_case = get_only_child_node_with_edge(
        traceability_index,
        mediated_requirement,
        GraphEdgeLabel.IS_VERIFIED_BY,
    )
    assert test_case.node_type == "TEST_CASE"

    assert get_child_relation_types(traceability_index, test_case) == [
        ("TEST_RESULT", GraphEdgeLabel.HAS_RESULT)
    ]
    mediated_result = get_only_child_node_with_edge(
        traceability_index,
        test_case,
        GraphEdgeLabel.HAS_RESULT,
    )
    assert mediated_result.node_type == "TEST_RESULT"
    assert mediated_result.reserved_status == "FAILED"

    assert get_verification_result_provenance_signature(
        traceability_index,
        parent_requirement,
    ) == [
        (direct_requirement, None, direct_result),
        (mediated_requirement, test_case, mediated_result),
    ]
    assert get_verification_result_provenance_signature(
        traceability_index,
        grandparent_requirement,
    ) == [
        (direct_requirement, None, direct_result),
        (mediated_requirement, test_case, mediated_result),
    ]
    assert get_verification_result_provenance_signature(
        traceability_index,
        direct_requirement,
    ) == [(direct_requirement, None, direct_result)]
    assert get_verification_result_provenance_signature(
        traceability_index,
        mediated_requirement,
    ) == [(mediated_requirement, test_case, mediated_result)]

    assert direct_result is not mediated_result
    assert grandparent_requirement.reserved_status is None
    assert parent_requirement.reserved_status is None
    assert direct_requirement.reserved_status is None
    assert mediated_requirement.reserved_status is None


if __name__ == "__main__":
    main()
