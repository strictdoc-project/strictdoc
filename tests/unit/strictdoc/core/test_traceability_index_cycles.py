import pytest

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from tests.unit.helpers.test_document_builder import DocumentBuilder


def test_invalid_01_2_reqs_cycled():
    document_builder = DocumentBuilder()
    document_builder.add_requirement("REQ-001")
    document_builder.add_requirement("REQ-002")
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-001",
        target_requirement_id="REQ-002",
        role=None,
    )

    document_1 = document_builder.build()
    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    with pytest.raises(DocumentTreeError):
        _ = TraceabilityIndexBuilder.create_from_document_tree(
            document_tree, project_config=document_builder.project_config
        )


def test_invalid_02_4_reqs_cycled():
    document_builder = DocumentBuilder()
    _ = document_builder.add_requirement("REQ-001")
    _ = document_builder.add_requirement("REQ-002")
    _ = document_builder.add_requirement("REQ-003")
    _ = document_builder.add_requirement("REQ-004")
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-004",
        target_requirement_id="REQ-003",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-003",
        target_requirement_id="REQ-002",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-001",
        target_requirement_id="REQ-004",
        role=None,
    )

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    with pytest.raises(DocumentTreeError):
        _ = TraceabilityIndexBuilder.create_from_document_tree(
            document_tree, project_config=document_builder.project_config
        )


def test_invalid_03_3_reqs_cycled():
    document_builder = DocumentBuilder()
    _ = document_builder.add_requirement("REQ-001")
    _ = document_builder.add_requirement("REQ-002")
    _ = document_builder.add_requirement("REQ-003")
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-003",
        target_requirement_id="REQ-001",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-003",
        target_requirement_id="REQ-002",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-003",
        role=None,
    )

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    with pytest.raises(DocumentTreeError):
        _ = TraceabilityIndexBuilder.create_from_document_tree(
            document_tree, project_config=document_builder.project_config
        )


def test_invalid_04_5_reqs_cycled():
    document_builder = DocumentBuilder()
    _ = document_builder.add_requirement("REQ-001")
    _ = document_builder.add_requirement("REQ-002")
    _ = document_builder.add_requirement("REQ-003")
    _ = document_builder.add_requirement("REQ-004")
    _ = document_builder.add_requirement("REQ-005")
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-003",
        target_requirement_id="REQ-002",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-004",
        target_requirement_id="REQ-003",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-005",
        target_requirement_id="REQ-004",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-003",
        target_requirement_id="REQ-005",
        role=None,
    )

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    with pytest.raises(DocumentTreeError) as exc_info:
        _ = TraceabilityIndexBuilder.create_from_document_tree(
            document_tree, project_config=document_builder.project_config
        )

    exception: DocumentTreeError = exc_info.value
    assert exception.problem_uid == "REQ-003"
    assert exception.cycled_uids == [
        "REQ-001",
        "REQ-002",
        "REQ-003",
        "REQ-004",
        "REQ-005",
    ]


def test_invalid_05_4_reqs_good_then_3_cycled():
    document_builder = DocumentBuilder()
    _ = document_builder.add_requirement("REQ-001")
    _ = document_builder.add_requirement("REQ-002")
    _ = document_builder.add_requirement("REQ-003")
    _ = document_builder.add_requirement("REQ-004")

    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-004",
        target_requirement_id="REQ-003",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-003",
        target_requirement_id="REQ-002",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role=None,
    )

    _ = document_builder.add_requirement("REQ-005")
    _ = document_builder.add_requirement("REQ-006")
    _ = document_builder.add_requirement("REQ-007")

    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-006",
        target_requirement_id="REQ-005",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-007",
        target_requirement_id="REQ-006",
        role=None,
    )
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-005",
        target_requirement_id="REQ-007",
        role=None,
    )

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    with pytest.raises(DocumentTreeError):
        _ = TraceabilityIndexBuilder.create_from_document_tree(
            document_tree, project_config=document_builder.project_config
        )


def test__adding_parent_link__03__two_requirements_disallow_cycle():
    document_builder = DocumentBuilder()
    requirement1 = document_builder.add_requirement("REQ-001")
    requirement2 = document_builder.add_requirement("REQ-002")
    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    traceability_index: TraceabilityIndex = (
        TraceabilityIndexBuilder.create_from_document_tree(
            document_tree, project_config=document_builder.project_config
        )
    )
    traceability_index.update_requirement_parent_uid(
        requirement2, "REQ-001", None
    )
    with pytest.raises(DocumentTreeError) as exc_info:
        traceability_index.update_requirement_parent_uid(
            requirement1, "REQ-002", role=None
        )

    exception: DocumentTreeError = exc_info.value
    assert exception.problem_uid == "REQ-001"
    assert exception.cycled_uids == ["REQ-001", "REQ-002"]
