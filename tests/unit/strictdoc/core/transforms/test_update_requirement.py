from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementRelationChild,
    GrammarElementRelationParent,
)
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.core.transforms.update_requirement import (
    UpdateRequirementTransform,
)
from strictdoc.export.html.form_objects.requirement_form_object import (
    RequirementFormObject,
    RequirementReferenceFormField,
)
from strictdoc.helpers.mid import MID
from tests.unit.helpers.test_document_builder import DocumentBuilder


def test_01_single_document_add_first_parent_relation_with_no_role():
    document_builder = DocumentBuilder()
    requirement1 = document_builder.add_requirement("REQ-001")
    requirement2 = document_builder.add_requirement("REQ-002")
    assert len(requirement2.relations) == 0

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
        TraceabilityIndexBuilder.create_from_document_tree(document_tree)
    )
    traceability_index.document_tree = document_tree
    assert traceability_index.get_parent_requirements(requirement1) == []

    requirement2_parents = list(
        traceability_index.get_parent_relations_with_roles(requirement2)
    )
    assert requirement2_parents == []

    form_object: RequirementFormObject = (
        RequirementFormObject.create_from_requirement(
            requirement=requirement2,
            context_document_mid=document_1.reserved_mid,
        )
    )
    form_object.reference_fields.append(
        RequirementReferenceFormField(
            field_mid=MID.create(),
            field_type=RequirementReferenceFormField.FieldType.PARENT,
            field_value="REQ-001",
            field_role=None,
        )
    )
    update_command = UpdateRequirementTransform(
        form_object=form_object,
        requirement=requirement2,
        traceability_index=traceability_index,
    )
    update_command.perform()

    assert len(requirement2.relations) == 1
    requirement2_parents = list(
        traceability_index.get_parent_relations_with_roles(requirement2)
    )
    assert requirement2_parents == [
        (requirement1, None),
    ]


def test_02_single_document_add_second_parent_relation_with_role():
    document_builder = DocumentBuilder()
    requirement1 = document_builder.add_requirement("REQ-001")
    requirement2 = document_builder.add_requirement("REQ-002")
    document_builder.add_requirement_relation(
        relation_type="Parent",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role="Refines",
    )
    assert len(requirement2.relations) == 1

    document_1 = document_builder.build()
    document_1.grammar.elements[0].relations.append(
        GrammarElementRelationParent(
            document_1.grammar.elements[0], "Parent", "Refines"
        )
    )
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
        TraceabilityIndexBuilder.create_from_document_tree(document_tree)
    )
    traceability_index.document_tree = document_tree
    assert traceability_index.get_parent_requirements(requirement1) == []

    requirement2_parents = list(
        traceability_index.get_parent_relations_with_roles(requirement2)
    )
    assert requirement2_parents == [(requirement1, "Refines")]

    form_object: RequirementFormObject = (
        RequirementFormObject.create_from_requirement(
            requirement=requirement2,
            context_document_mid=document_1.reserved_mid,
        )
    )
    update_command = UpdateRequirementTransform(
        form_object=form_object,
        requirement=requirement2,
        traceability_index=traceability_index,
    )
    update_command.perform()
    assert len(requirement2.relations) == 1

    form_object.reference_fields.append(
        RequirementReferenceFormField(
            field_mid=MID.create(),
            field_type=RequirementReferenceFormField.FieldType.PARENT,
            field_value="REQ-001",
            field_role="Implements",
        )
    )
    update_command.perform()

    assert len(requirement2.relations) == 2
    requirement2_parents = list(
        traceability_index.get_parent_relations_with_roles(requirement2)
    )
    assert requirement2_parents == [
        (requirement1, "Refines"),
        (requirement1, "Implements"),
    ]


def test_20_single_document_add_second_child_relation_with_role():
    document_builder = DocumentBuilder()
    requirement1 = document_builder.add_requirement("REQ-001")
    requirement2 = document_builder.add_requirement("REQ-002")
    document_builder.add_requirement_relation(
        relation_type="Child",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role="IsRefinedBy",
    )

    assert len(requirement2.relations) == 1

    document_1 = document_builder.build()
    document_1.grammar.elements[0].relations.append(
        GrammarElementRelationChild(
            document_1.grammar.elements[0], "Child", "IsRefinedBy"
        )
    )

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
        TraceabilityIndexBuilder.create_from_document_tree(document_tree)
    )
    traceability_index.document_tree = document_tree
    requirement1_parents = list(
        traceability_index.get_parent_relations_with_roles(requirement1)
    )
    assert requirement1_parents == [(requirement2, "IsRefinedBy")]

    requirement2_children = list(
        traceability_index.get_child_relations_with_roles(requirement2)
    )
    assert requirement2_children == [(requirement1, "IsRefinedBy")]

    form_object: RequirementFormObject = (
        RequirementFormObject.create_from_requirement(
            requirement=requirement2,
            context_document_mid=document_1.reserved_mid,
        )
    )
    form_object.reference_fields.append(
        RequirementReferenceFormField(
            field_mid=MID.create(),
            field_type=RequirementReferenceFormField.FieldType.CHILD,
            field_value="REQ-001",
            field_role="IsImplementedBy",
        )
    )
    update_command = UpdateRequirementTransform(
        form_object=form_object,
        requirement=requirement2,
        traceability_index=traceability_index,
    )
    update_command.perform()

    requirement1_parents = list(
        traceability_index.get_parent_relations_with_roles(requirement1)
    )
    assert requirement1_parents == [
        (requirement2, "IsRefinedBy"),
        (requirement2, "IsImplementedBy"),
    ]

    requirement2_children = list(
        traceability_index.get_child_relations_with_roles(requirement2)
    )
    assert requirement2_children == [
        (requirement1, "IsRefinedBy"),
        (requirement1, "IsImplementedBy"),
    ]


def test_25_single_document_remove_child_relation():
    document_builder = DocumentBuilder()
    requirement1 = document_builder.add_requirement("REQ-001")
    requirement2 = document_builder.add_requirement("REQ-002")
    document_builder.add_requirement_relation(
        relation_type="Child",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role="IsRefinedBy",
    )

    assert len(requirement2.relations) == 1

    document_1 = document_builder.build()
    document_1.grammar.elements[0].relations.append(
        GrammarElementRelationChild(
            document_1.grammar.elements[0], "Child", "IsRefinedBy"
        )
    )

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
        TraceabilityIndexBuilder.create_from_document_tree(document_tree)
    )
    traceability_index.document_tree = document_tree
    requirement1_parents = list(
        traceability_index.get_parent_relations_with_roles(requirement1)
    )
    assert requirement1_parents == [(requirement2, "IsRefinedBy")]

    requirement2_children = list(
        traceability_index.get_child_relations_with_roles(requirement2)
    )
    assert requirement2_children == [(requirement1, "IsRefinedBy")]

    form_object: RequirementFormObject = (
        RequirementFormObject.create_from_requirement(
            requirement=requirement2,
            context_document_mid=document_1.reserved_mid,
        )
    )

    # Form object has no relations.
    form_object.reference_fields.clear()

    update_command = UpdateRequirementTransform(
        form_object=form_object,
        requirement=requirement2,
        traceability_index=traceability_index,
    )
    update_command.perform()

    requirement1_parents = list(
        traceability_index.get_parent_relations_with_roles(requirement1)
    )
    assert requirement1_parents == []

    requirement2_children = list(
        traceability_index.get_child_relations_with_roles(requirement2)
    )
    assert requirement2_children == []


def test_26_two_documents_remove_child_relation():
    # Document 1
    document_builder = DocumentBuilder()
    requirement1 = document_builder.add_requirement("REQ-001")
    document_1 = document_builder.build()

    # Document 2
    document_builder = DocumentBuilder()
    requirement2 = document_builder.add_requirement("REQ-002")
    document_builder.add_requirement_relation(
        relation_type="Child",
        source_requirement_id="REQ-002",
        target_requirement_id="REQ-001",
        role="IsRefinedBy",
    )
    assert len(requirement2.relations) == 1
    document_2 = document_builder.build()
    document_2.grammar.elements[0].relations.append(
        GrammarElementRelationChild(
            document_2.grammar.elements[0], "Child", "IsRefinedBy"
        )
    )
    assert requirement1.document != requirement2.document

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
        TraceabilityIndexBuilder.create_from_document_tree(document_tree)
    )
    traceability_index.document_tree = document_tree

    assert traceability_index.get_document_children(document_1) == set()
    assert traceability_index.get_document_parents(document_2) == set()
    assert traceability_index.get_document_parents(document_1) == {document_2}
    assert traceability_index.get_document_children(document_2) == {document_1}

    requirement2_children = list(
        traceability_index.get_child_relations_with_roles(requirement2)
    )
    assert requirement2_children == [(requirement1, "IsRefinedBy")]

    form_object: RequirementFormObject = (
        RequirementFormObject.create_from_requirement(
            requirement=requirement2,
            context_document_mid=document_2.reserved_mid,
        )
    )

    # Form object has no relations.
    form_object.reference_fields.clear()

    update_command = UpdateRequirementTransform(
        form_object=form_object,
        requirement=requirement2,
        traceability_index=traceability_index,
    )
    update_command.perform()

    requirement1_parents = list(
        traceability_index.get_parent_relations_with_roles(requirement1)
    )
    assert requirement1_parents == []

    requirement2_children = list(
        traceability_index.get_child_relations_with_roles(requirement2)
    )
    assert requirement2_children == []
    assert traceability_index.get_document_children(document_1) == set()
    assert traceability_index.get_document_children(document_2) == set()
    assert traceability_index.get_document_parents(document_1) == set()
    assert traceability_index.get_document_parents(document_2) == set()
