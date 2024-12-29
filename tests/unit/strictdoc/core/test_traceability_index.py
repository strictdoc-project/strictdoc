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
        map_grammars_by_filenames={},
    )
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=document_builder.project_config
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
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role=None,
    )
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
        source_requirement_id="REQ-004",
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
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=document_builder.project_config
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
    document_builder_1 = DocumentBuilder("DOC-1")
    requirement1 = document_builder_1.add_requirement("REQ-001")
    document_1 = document_builder_1.build()

    document_builder_2 = DocumentBuilder("DOC-2")
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
        map_grammars_by_filenames={},
    )
    traceability_index: TraceabilityIndex = (
        TraceabilityIndexBuilder.create_from_document_tree(
            document_tree, project_config=document_builder_1.project_config
        )
    )
    traceability_index.update_requirement_parent_uid(
        requirement2, "REQ-001", None
    )

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


def test__adding_parent_link__04__two_requirements_remove_parent_link():
    document_builder = DocumentBuilder()
    requirement1 = document_builder.add_requirement("REQ-001")
    requirement2 = document_builder.add_requirement("REQ-002")
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
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
    traceability_index: TraceabilityIndex = (
        TraceabilityIndexBuilder.create_from_document_tree(
            document_tree, project_config=document_builder.project_config
        )
    )
    traceability_index.remove_requirement_parent_uid(
        requirement2, "REQ-001", role=None
    )

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
        map_grammars_by_filenames={},
    )
    traceability_index: TraceabilityIndex = (
        TraceabilityIndexBuilder.create_from_document_tree(
            document_tree, project_config=document_builder.project_config
        )
    )
    assert (
        traceability_index.get_node_by_mid(MID(document_1.reserved_mid))
        == document_1
    )
