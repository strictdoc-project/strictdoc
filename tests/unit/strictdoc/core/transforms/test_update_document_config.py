from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.core.transforms.update_document_config import (
    UpdateDocumentConfigTransform,
)
from strictdoc.export.html.form_objects.document_config_form_object import (
    DocumentConfigFormObject,
    DocumentMetadataFormField,
)
from tests.unit.helpers.document_builder import DocumentBuilder


def _build_traceability_index(document, project_config):
    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    return TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=project_config
    )


def _perform_metadata_update(document, traceability_index, metadata_value):
    form_object = DocumentConfigFormObject(
        document_mid=str(document.reserved_mid),
        document_title=document.title,
        document_uid=document.config.uid,
        document_version=None,
        document_classification=None,
        document_requirement_prefix=None,
        document_custom_metadata_fields=[
            DocumentMetadataFormField(
                field_mid="metadata_owner",
                field_name="OWNER",
                field_value=metadata_value,
            ),
        ],
    )
    UpdateDocumentConfigTransform(
        form_object=form_object,
        document=document,
        traceability_index=traceability_index,
    ).perform()


def test_metadata_link_resolves_to_owning_document_after_save():
    """
    Regression test: saving a document METADATA field containing
    [LINK: UID] through the web-form transform must wire the
    DocumentCustomMetadataKeyValuePair.parent chain correctly, so that
    InlineLink.parent_node() (used by the incoming-links UI panel and
    validations) does not crash with an AssertionError.
    """
    document_builder = DocumentBuilder("DOC-1")
    document_builder.add_requirement("REQ-001")
    document = document_builder.build()
    # DocumentBuilder is a lightweight test helper: unlike real grammar
    # parsing, it does not wire DocumentConfig.parent back to the document.
    document.config.parent = document

    traceability_index = _build_traceability_index(
        document, document_builder.project_config
    )

    _perform_metadata_update(document, traceability_index, "[LINK: REQ-001]")

    entry = document.config.custom_metadata.entries[0]
    assert entry.key == "OWNER"
    assert entry.get_owning_node() is document

    inline_link = entry.parts[0]
    assert inline_link.parent_node() is document

    target_node = traceability_index.get_node_by_uid("REQ-001")
    incoming_links = traceability_index.get_incoming_links(target_node)
    assert incoming_links is not None
    assert inline_link in incoming_links


def test_metadata_link_is_replaced_on_subsequent_save():
    document_builder = DocumentBuilder("DOC-1")
    document_builder.add_requirement("REQ-001")
    document_builder.add_requirement("REQ-002")
    document = document_builder.build()
    document.config.parent = document

    traceability_index = _build_traceability_index(
        document, document_builder.project_config
    )

    _perform_metadata_update(document, traceability_index, "[LINK: REQ-001]")

    req_001 = traceability_index.get_node_by_uid("REQ-001")
    assert traceability_index.get_incoming_links(req_001) is not None

    _perform_metadata_update(document, traceability_index, "[LINK: REQ-002]")

    assert traceability_index.get_incoming_links(req_001) is None

    req_002 = traceability_index.get_node_by_uid("REQ-002")
    incoming_links = traceability_index.get_incoming_links(req_002)
    assert incoming_links is not None
    assert incoming_links[0].link == "REQ-002"
