import pytest

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.helpers.mid import MID
from tests.unit.helpers.test_document_builder import DocumentBuilder


def test_valid_01_one_document_with_1req():
    document_builder = DocumentBuilder()
    requirement = document_builder.add_requirement("REQ-001")
    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
    )
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree
    )
    parent_requirements = traceability_index.get_parent_requirements(
        requirement
    )
    assert parent_requirements == []


def test_valid_02_one_document_with_1req():
    document_builder = DocumentBuilder()
    requirement1 = document_builder.add_requirement("REQ-001")
    requirement2 = document_builder.add_requirement("REQ-002")
    requirement3 = document_builder.add_requirement("REQ-003")
    requirement4 = document_builder.add_requirement("REQ-004")
    document_builder.add_requirement_parent("REQ-002", "REQ-001")
    document_builder.add_requirement_parent("REQ-003", "REQ-001")
    document_builder.add_requirement_parent("REQ-003", "REQ-002")
    document_builder.add_requirement_parent("REQ-004", "REQ-003")

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
    )
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree
    )
    requirement1_parents = traceability_index.get_parent_requirements(
        requirement1
    )
    assert requirement1_parents == []

    requirement2_parents = traceability_index.get_parent_requirements(
        requirement2
    )
    assert requirement2_parents == [requirement1]

    requirement3_parents = traceability_index.get_parent_requirements(
        requirement3
    )
    assert requirement3_parents == [requirement1, requirement2]

    requirement4_parents = traceability_index.get_parent_requirements(
        requirement4
    )
    assert requirement4_parents == [requirement3]


def test_invalid_02_4_reqs_cycled():
    document_builder = DocumentBuilder()
    _ = document_builder.add_requirement("REQ-001")
    _ = document_builder.add_requirement("REQ-002")
    _ = document_builder.add_requirement("REQ-003")
    _ = document_builder.add_requirement("REQ-004")
    document_builder.add_requirement_parent("REQ-004", "REQ-003")
    document_builder.add_requirement_parent("REQ-003", "REQ-002")
    document_builder.add_requirement_parent("REQ-002", "REQ-001")
    document_builder.add_requirement_parent("REQ-001", "REQ-004")

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
    )
    with pytest.raises(DocumentTreeError):
        _ = TraceabilityIndexBuilder.create_from_document_tree(document_tree)


def test_invalid_03_3_reqs_cycled():
    document_builder = DocumentBuilder()
    _ = document_builder.add_requirement("REQ-001")
    _ = document_builder.add_requirement("REQ-002")
    _ = document_builder.add_requirement("REQ-003")
    document_builder.add_requirement_parent("REQ-003", "REQ-001")
    document_builder.add_requirement_parent("REQ-003", "REQ-002")
    document_builder.add_requirement_parent("REQ-002", "REQ-003")

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
    )
    with pytest.raises(DocumentTreeError):
        _ = TraceabilityIndexBuilder.create_from_document_tree(document_tree)


def test_invalid_04_5_reqs_cycled():
    document_builder = DocumentBuilder()
    _ = document_builder.add_requirement("REQ-001")
    _ = document_builder.add_requirement("REQ-002")
    _ = document_builder.add_requirement("REQ-003")
    _ = document_builder.add_requirement("REQ-004")
    _ = document_builder.add_requirement("REQ-005")
    document_builder.add_requirement_parent("REQ-002", "REQ-001")
    document_builder.add_requirement_parent("REQ-003", "REQ-002")
    document_builder.add_requirement_parent("REQ-004", "REQ-003")
    document_builder.add_requirement_parent("REQ-005", "REQ-004")
    document_builder.add_requirement_parent("REQ-003", "REQ-005")

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
    )
    with pytest.raises(DocumentTreeError):
        _ = TraceabilityIndexBuilder.create_from_document_tree(document_tree)


def test_invalid_05_4_reqs_good_then_3_cycled():
    document_builder = DocumentBuilder()
    _ = document_builder.add_requirement("REQ-001")
    _ = document_builder.add_requirement("REQ-002")
    _ = document_builder.add_requirement("REQ-003")
    _ = document_builder.add_requirement("REQ-004")

    document_builder.add_requirement_parent("REQ-004", "REQ-003")
    document_builder.add_requirement_parent("REQ-003", "REQ-002")
    document_builder.add_requirement_parent("REQ-002", "REQ-001")

    _ = document_builder.add_requirement("REQ-005")
    _ = document_builder.add_requirement("REQ-006")
    _ = document_builder.add_requirement("REQ-007")

    document_builder.add_requirement_parent("REQ-006", "REQ-005")
    document_builder.add_requirement_parent("REQ-007", "REQ-006")
    document_builder.add_requirement_parent("REQ-005", "REQ-007")

    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
    )
    with pytest.raises(DocumentTreeError):
        _ = TraceabilityIndexBuilder.create_from_document_tree(document_tree)


def test__adding_parent_link__01__two_requirements_in_one_document():
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
    )
    traceability_index: TraceabilityIndex = (
        TraceabilityIndexBuilder.create_from_document_tree(document_tree)
    )
    traceability_index.update_requirement_parent_uid(requirement2, "REQ-001")

    # REQ2 has REQ1 as its parent.
    req2_parent_requirements = traceability_index.get_parent_requirements(
        requirement2
    )
    assert req2_parent_requirements == [requirement1]

    # REQ1 has REQ2 as its child.
    req1_child_requirements = traceability_index.get_children_requirements(
        requirement1
    )
    assert req1_child_requirements == [requirement2]


def test__adding_parent_link__02__two_requirements_in_two_documents():
    document_builder_1 = DocumentBuilder()
    requirement1 = document_builder_1.add_requirement("REQ-001")
    document_1 = document_builder_1.build()

    document_builder_2 = DocumentBuilder()
    requirement2 = document_builder_2.add_requirement("REQ-002")
    document_2 = document_builder_2.build()

    file_tree = []
    document_list = [document_1, document_2]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
    )
    traceability_index: TraceabilityIndex = (
        TraceabilityIndexBuilder.create_from_document_tree(document_tree)
    )
    traceability_index.update_requirement_parent_uid(requirement2, "REQ-001")

    # REQ2 has REQ1 as its parent.
    req2_parent_requirements = traceability_index.get_parent_requirements(
        requirement2
    )
    assert req2_parent_requirements == [requirement1]

    # REQ1 has REQ2 as its child.
    req1_child_requirements = traceability_index.get_children_requirements(
        requirement1
    )
    assert req1_child_requirements == [requirement2]

    # Document 1 has Document 2 as a child document.
    document1_child_documents = traceability_index.get_document_children(
        document_1
    )
    assert next(iter(document1_child_documents)) == document_2

    # Document 2 has Document 1 as a parent document.
    document2_child_documents = traceability_index.get_document_parents(
        document_2
    )
    assert next(iter(document2_child_documents)) == document_1


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
    )
    traceability_index: TraceabilityIndex = (
        TraceabilityIndexBuilder.create_from_document_tree(document_tree)
    )
    traceability_index.update_requirement_parent_uid(requirement2, "REQ-001")
    with pytest.raises(DocumentTreeError) as exc_info:
        traceability_index.update_requirement_parent_uid(
            requirement1, "REQ-002"
        )
    assert (
        "a cycle detected: "
        "requirements in the document tree must not reference each"
    ) in exc_info.value.args[0]


def test__adding_parent_link__04__two_requirements_remove_parent_link():
    document_builder = DocumentBuilder()
    requirement1 = document_builder.add_requirement("REQ-001")
    requirement2 = document_builder.add_requirement("REQ-002")
    document_builder.add_requirement_parent(
        req_id="REQ-002", parent_req_id="REQ-001"
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
    )
    traceability_index: TraceabilityIndex = (
        TraceabilityIndexBuilder.create_from_document_tree(document_tree)
    )
    traceability_index.remove_requirement_parent_uid(requirement2, "REQ-001")

    req2_parent_requirements = traceability_index.get_parent_requirements(
        requirement2
    )
    assert req2_parent_requirements == []

    req1_child_requirements = traceability_index.get_children_requirements(
        requirement1
    )
    assert req1_child_requirements == []


def test_get_node_by_mid():
    document_builder = DocumentBuilder()
    document_1 = document_builder.build()

    file_tree = []
    document_list = [document_1]
    map_docs_by_paths = {}
    document_tree = DocumentTree(
        file_tree=file_tree,
        document_list=document_list,
        map_docs_by_paths=map_docs_by_paths,
        map_docs_by_rel_paths={},
    )
    traceability_index: TraceabilityIndex = (
        TraceabilityIndexBuilder.create_from_document_tree(document_tree)
    )
    assert (
        traceability_index.get_node_by_mid(MID(document_1.mid.value))
        == document_1
    )
