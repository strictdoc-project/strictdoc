from datetime import datetime

from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.generators.view_objects.document_screen_view_object import (
    DocumentScreenViewObject,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.helpers.git_client import GitClient
from tests.unit.helpers.document_builder import DocumentBuilder


def create_view_object(
    *,
    node_count,
    threshold,
    is_running_on_server=True,
    document_type=DocumentType.DOCUMENT,
) -> DocumentScreenViewObject:
    document_builder = DocumentBuilder()
    for node_idx_ in range(node_count):
        document_builder.add_requirement(f"REQ-{node_idx_:03d}")
    document = document_builder.build()

    project_config = document_builder.project_config
    project_config.chunked_documents_threshold = threshold
    project_config.is_running_on_server = is_running_on_server

    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=project_config
    )

    link_renderer = LinkRenderer(root_path="", static_path="_static")
    html_templates = HTMLTemplates.create(
        project_config=project_config,
        enable_caching=False,
        strictdoc_last_update=datetime.today(),
    )
    markup_renderer = MarkupRenderer.create(
        "RST",
        traceability_index,
        link_renderer,
        html_templates,
        project_config,
        document,
    )
    return DocumentScreenViewObject(
        document_type=document_type,
        document=document,
        traceability_index=traceability_index,
        project_config=project_config,
        link_renderer=link_renderer,
        markup_renderer=markup_renderer,
        jinja_environment=html_templates.jinja_environment(),
        git_client=GitClient(),
    )


def test_threshold_zero_disables_chunked_rendering():
    view_object = create_view_object(node_count=30, threshold=0)

    assert view_object.is_chunked_rendering() is False


def test_not_running_on_server_disables_chunked_rendering():
    view_object = create_view_object(
        node_count=30, threshold=10, is_running_on_server=False
    )

    assert view_object.is_chunked_rendering() is False


def test_chunked_rendering_activates_above_threshold():
    view_object = create_view_object(node_count=30, threshold=10)

    assert view_object.is_chunked_rendering() is True


def test_threshold_greater_than_node_count_disables_chunked_rendering():
    view_object = create_view_object(node_count=30, threshold=50)

    assert view_object.is_chunked_rendering() is False


def test_node_count_exactly_at_threshold_disables_chunked_rendering():
    view_object = create_view_object(node_count=10, threshold=10)

    assert view_object.is_chunked_rendering() is False


def test_non_document_screen_disables_chunked_rendering():
    view_object = create_view_object(
        node_count=30, threshold=10, document_type=DocumentType.TABLE
    )

    assert view_object.is_chunked_rendering() is False


def test_document_content_chunks_cover_all_nodes_in_order():
    view_object = create_view_object(node_count=30, threshold=10)
    node_mids = [
        node_.reserved_mid
        for node_, _ in view_object.document_content_iterator()
    ]
    assert len(node_mids) == 30

    # The bare call defaults to the effective document chunk size, which
    # the threshold (10) caps below CHUNK_SIZE, producing chunks of 10.
    chunks = view_object.document_content_chunks()

    assert view_object.document_chunk_size() == 10
    assert [chunk_.index for chunk_ in chunks] == [0, 1, 2]
    assert [chunk_.size for chunk_ in chunks] == [10, 10, 10]
    assert [chunk_.first_node_mid for chunk_ in chunks] == [
        node_mids[0],
        node_mids[10],
        node_mids[20],
    ]

    # An explicit chunk size large enough to fit the whole document
    # produces a single chunk covering all nodes.
    chunks = view_object.document_content_chunks(chunk_size=100)

    assert len(chunks) == 1
    assert chunks[0].index == 0
    assert chunks[0].first_node_mid == node_mids[0]
    assert chunks[0].size == 30


def test_document_content_chunks_custom_size_produces_multiple_chunks():
    view_object = create_view_object(node_count=30, threshold=10)
    node_mids = [
        node_.reserved_mid
        for node_, _ in view_object.document_content_iterator()
    ]
    assert len(node_mids) == 30

    chunks = view_object.document_content_chunks(chunk_size=10)

    assert len(chunks) == 3
    assert [chunk_.index for chunk_ in chunks] == [0, 1, 2]
    assert [chunk_.size for chunk_ in chunks] == [10, 10, 10]
    assert [chunk_.first_node_mid for chunk_ in chunks] == [
        node_mids[0],
        node_mids[10],
        node_mids[20],
    ]


def test_chunk_content_iterator_yields_first_count_nodes():
    view_object = create_view_object(node_count=30, threshold=10)
    node_mids = [
        node_.reserved_mid
        for node_, _ in view_object.document_content_iterator()
    ]

    chunk_mids = [
        node_.reserved_mid
        for node_, _ in view_object.document_chunk_content_iterator(
            node_mids[0], 10
        )
    ]

    assert chunk_mids == node_mids[0:10]


def test_chunk_content_iterator_yields_nodes_from_middle_cursor():
    view_object = create_view_object(node_count=30, threshold=10)
    node_mids = [
        node_.reserved_mid
        for node_, _ in view_object.document_content_iterator()
    ]

    chunk_nodes = [
        node_
        for node_, _ in view_object.document_chunk_content_iterator(
            node_mids[10], 10
        )
    ]

    chunk_mids = [node_.reserved_mid for node_ in chunk_nodes]
    assert chunk_mids == node_mids[10:20]

    # Independent oracle: the DocumentBuilder assigns each requirement a
    # reserved UID of the form REQ-NNN in creation order, so the window
    # check does not rely solely on document_content_iterator().
    chunk_uids = [node_.reserved_uid for node_ in chunk_nodes]
    assert chunk_uids == [f"REQ-{node_idx_:03d}" for node_idx_ in range(10, 20)]


def test_chunk_content_iterator_yields_remainder_when_count_past_end():
    view_object = create_view_object(node_count=30, threshold=10)
    node_mids = [
        node_.reserved_mid
        for node_, _ in view_object.document_content_iterator()
    ]

    chunk_mids = [
        node_.reserved_mid
        for node_, _ in view_object.document_chunk_content_iterator(
            node_mids[24], 10
        )
    ]

    assert chunk_mids == node_mids[24:30]


def test_chunk_content_iterator_yields_nothing_for_unknown_cursor():
    view_object = create_view_object(node_count=30, threshold=10)

    chunk_nodes = list(
        view_object.document_chunk_content_iterator("DOES_NOT_EXIST", 10)
    )

    assert chunk_nodes == []
