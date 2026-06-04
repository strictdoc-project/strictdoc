"""
@relation(SDOC-SRS-55, scope=file)
"""

from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.html.form_objects.requirement_form_object import (
    RequirementFormObject,
)
from tests.unit.helpers.document_builder import DocumentBuilder

# A Markdown pipe table. It is valid Markdown but not valid RST: the separator
# row "|---|...|" is not a valid line-block continuation of the header row,
# which docutils reports as "Line block ends without a blank line".
MARKDOWN_TABLE = (
    "|   | Action | Verify |\n"
    "|---|--------|--------|\n"
    "| 1 | Do the thing | |\n"
    "| 2 | Do another thing | |\n"
)


def _build_index_with_single_requirement():
    document_builder = DocumentBuilder()
    requirement = document_builder.add_requirement("REQ-001")
    document = document_builder.build()

    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    traceability_index: TraceabilityIndex = (
        TraceabilityIndexBuilder.create_from_document_tree(
            document_tree, project_config=document_builder.project_config
        )
    )
    traceability_index.document_tree = document_tree
    return traceability_index, document, requirement


def _make_form_object_with_statement(requirement, document, statement_value):
    form_object: RequirementFormObject = (
        RequirementFormObject.create_from_requirement(
            requirement=requirement,
            revision=0,
            context_document_mid=document.reserved_mid,
        )
    )
    for field in form_object.fields["STATEMENT"]:
        field.field_value = statement_value
    return form_object


def test_markdown_document_validates_field_as_markdown():
    """
    In a Markdown document, a field containing a Markdown table validates
    without errors.
    """
    traceability_index, document, requirement = (
        _build_index_with_single_requirement()
    )
    document.config.markup = SDocMarkup.MARKDOWN

    form_object = _make_form_object_with_statement(
        requirement, document, MARKDOWN_TABLE
    )
    form_object.validate(
        traceability_index=traceability_index,
        context_document=document,
        config=ProjectConfig.default_config(),
        existing_revision=0,
    )

    assert not form_object.any_errors()
    assert form_object.get_errors("STATEMENT") == []


def test_rst_document_validates_field_as_rst():
    """
    In an RST document, a field is validated as RST. The pipe table is not
    valid RST, so validation reports an error against the field.
    """
    traceability_index, document, requirement = (
        _build_index_with_single_requirement()
    )
    document.config.markup = SDocMarkup.RST

    form_object = _make_form_object_with_statement(
        requirement, document, MARKDOWN_TABLE
    )
    form_object.validate(
        traceability_index=traceability_index,
        context_document=document,
        config=ProjectConfig.default_config(),
        existing_revision=0,
    )

    assert form_object.any_errors()
    assert len(form_object.get_errors("STATEMENT")) > 0
