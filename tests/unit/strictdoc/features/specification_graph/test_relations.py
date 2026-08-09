from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.features.specification_graph.relations import (
    get_document_relation_edges,
)
from tests.unit.helpers.document_builder import DocumentBuilder


def test_same_document_relation_is_not_an_edge():
    document_builder = DocumentBuilder()
    requirement1 = document_builder.add_requirement("REQ-001")
    document_builder.add_requirement("REQ-002")
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role=None,
    )
    document = document_builder.build()

    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=document_builder.project_config
    )

    assert get_document_relation_edges(traceability_index) == []
    assert requirement1.reserved_uid == "REQ-001"


def test_cross_document_relation_is_an_edge():
    document_builder_1 = DocumentBuilder("DOC-1")
    document_builder_1.add_requirement("REQ-001")
    document_1 = document_builder_1.build()

    document_builder_2 = DocumentBuilder("DOC-2")
    document_builder_2.add_requirement("REQ-002")
    document_2 = document_builder_2.build()

    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document_1, document_2],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    traceability_index: TraceabilityIndex = (
        TraceabilityIndexBuilder.create_from_document_tree(
            document_tree, project_config=document_builder_1.project_config
        )
    )
    requirement2 = next(
        node_
        for node_ in document_2.section_contents
        if node_.reserved_uid == "REQ-002"
    )
    traceability_index.update_requirement_parent_uid(
        requirement2, "REQ-001", None
    )

    edges = get_document_relation_edges(traceability_index)

    assert edges == [(document_2, document_1)]


def test_multiple_relations_between_same_documents_collapse_to_one_edge():
    document_builder_1 = DocumentBuilder("DOC-1")
    document_builder_1.add_requirement("REQ-001")
    document_1 = document_builder_1.build()

    document_builder_2 = DocumentBuilder("DOC-2")
    document_builder_2.add_requirement("REQ-002")
    document_builder_2.add_requirement("REQ-003")
    document_2 = document_builder_2.build()

    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document_1, document_2],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    traceability_index: TraceabilityIndex = (
        TraceabilityIndexBuilder.create_from_document_tree(
            document_tree, project_config=document_builder_1.project_config
        )
    )
    requirement2 = next(
        node_
        for node_ in document_2.section_contents
        if node_.reserved_uid == "REQ-002"
    )
    requirement3 = next(
        node_
        for node_ in document_2.section_contents
        if node_.reserved_uid == "REQ-003"
    )
    traceability_index.update_requirement_parent_uid(
        requirement2, "REQ-001", None
    )
    traceability_index.update_requirement_parent_uid(
        requirement3, "REQ-001", None
    )

    edges = get_document_relation_edges(traceability_index)

    assert edges == [(document_2, document_1)]


def test_relation_role_does_not_affect_edge_detection():
    document_builder_1 = DocumentBuilder("DOC-1")
    document_builder_1.add_requirement("REQ-001")
    document_1 = document_builder_1.build()

    document_builder_2 = DocumentBuilder("DOC-2")
    document_builder_2.add_requirement("REQ-002")
    document_builder_2.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role="Refines",
    )
    document_2 = document_builder_2.build()

    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document_1, document_2],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    traceability_index: TraceabilityIndex = (
        TraceabilityIndexBuilder.create_from_document_tree(
            document_tree, project_config=document_builder_1.project_config
        )
    )

    edges = get_document_relation_edges(traceability_index)

    assert edges == [(document_2, document_1)]


def test_isolated_document_has_no_edges():
    document_builder = DocumentBuilder()
    document_builder.add_requirement("REQ-001")
    document = document_builder.build()

    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=document_builder.project_config
    )

    assert get_document_relation_edges(traceability_index) == []
