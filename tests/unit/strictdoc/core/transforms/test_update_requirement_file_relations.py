"""
@relation(SDOC-SRS-55, scope=file)
"""

from strictdoc.backend.sdoc.models.reference import (
    FileEntry,
    FileEntryFormat,
    FileReference,
)
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.core.transforms.update_requirement import (
    CreateOrUpdateNodeCommand,
    UpdateNodeInfo,
)
from strictdoc.export.html.form_objects.requirement_form_object import (
    RequirementFormObject,
    RequirementReferenceFormField,
)
from strictdoc.helpers.mid import MID
from tests.unit.helpers.document_builder import DocumentBuilder


def _build(file_entry_kwargs=None):
    document_builder = DocumentBuilder()
    requirement = document_builder.add_requirement("REQ-001")
    if file_entry_kwargs is not None:
        file_entry = FileEntry(
            parent=None,
            g_file_format=FileEntryFormat.SOURCECODE,
            **file_entry_kwargs,
        )
        file_reference = FileReference(
            parent=requirement, g_file_entry=file_entry
        )
        file_entry.parent = file_reference
        requirement.relations.append(file_reference)
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
    traceability_index.document_tree = document_tree
    return document, requirement, traceability_index


def _save(requirement, form_object, traceability_index):
    return CreateOrUpdateNodeCommand(
        form_object=form_object,
        node_info=UpdateNodeInfo(requirement),
        traceability_index=traceability_index,
        project_config=ProjectConfig.default_config(),
    ).perform()


def test_01_saving_node_preserves_file_relation_attributes():
    document, requirement, traceability_index = _build(
        {"g_file_path": "src/file.c", "g_line_range": "2, 5"}
    )
    form_object = RequirementFormObject.create_from_requirement(
        requirement=requirement,
        revision=0,
        context_document_mid=document.reserved_mid,
    )
    assert form_object.reference_fields[0].field_line_range == "2, 5"

    result = _save(requirement, form_object, traceability_index)

    assert len(requirement.relations) == 1
    file_reference = requirement.relations[0]
    assert isinstance(file_reference, FileReference)
    assert file_reference.g_file_entry.g_file_path == "src/file.c"
    assert file_reference.g_file_entry.g_line_range == "2, 5"
    assert file_reference.g_file_entry.line_range == (2, 5)
    assert file_reference.g_file_entry.g_file_format == "Sourcecode"
    assert result.file_relations_changed is False


def test_02_saving_node_preserves_file_relation_function():
    document, requirement, traceability_index = _build(
        {"g_file_path": "src/file.c", "g_line_range": None, "function": "foo"}
    )
    form_object = RequirementFormObject.create_from_requirement(
        requirement=requirement,
        revision=0,
        context_document_mid=document.reserved_mid,
    )
    _save(requirement, form_object, traceability_index)

    file_entry = requirement.relations[0].g_file_entry
    assert file_entry.function() == "foo"
    assert file_entry.g_line_range is None


def test_03_create_update_and_remove_file_relation():
    document, requirement, traceability_index = _build()

    form_object = RequirementFormObject.create_from_requirement(
        requirement=requirement,
        revision=0,
        context_document_mid=document.reserved_mid,
    )
    form_object.reference_fields.append(
        RequirementReferenceFormField(
            field_mid=MID.create(),
            field_type=RequirementReferenceFormField.FieldType.FILE,
            field_value="src/file.c",
            field_role=None,
            field_line_range="1, 3",
        )
    )
    result = _save(requirement, form_object, traceability_index)
    assert result.file_relations_changed is True
    file_entry = requirement.relations[0].g_file_entry
    assert file_entry.g_file_path == "src/file.c"
    assert file_entry.line_range == (1, 3)
    # New relations do not get an explicit FORMAT.
    assert file_entry.g_file_format is None

    # Update: change the line range only.
    form_object = RequirementFormObject.create_from_requirement(
        requirement=requirement,
        revision=1,
        context_document_mid=document.reserved_mid,
    )
    form_object.reference_fields[0].field_line_range = "4, 8"
    result = _save(requirement, form_object, traceability_index)
    assert result.file_relations_changed is True
    assert requirement.relations[0].g_file_entry.line_range == (4, 8)

    # Remove.
    form_object = RequirementFormObject.create_from_requirement(
        requirement=requirement,
        revision=2,
        context_document_mid=document.reserved_mid,
    )
    form_object.reference_fields.clear()
    result = _save(requirement, form_object, traceability_index)
    assert result.file_relations_changed is True
    assert requirement.relations == []
