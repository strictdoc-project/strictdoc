import pytest

from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.export.html.document_type import DocumentType
from tests.unit.helpers.view_object_builder import (
    create_document_screen_view_object as create_view_object,
)


def test_threshold_zero_disables_chunked_rendering():
    view_object = create_view_object(node_count=30, threshold=0)

    assert view_object.is_chunked_rendering() is False


def test_static_export_also_activates_chunked_rendering():
    # Static HTML export has no FastAPI server to fetch a chunk fragment
    # from, but it still activates chunked rendering: DocumentHTMLGenerator
    # delivers each chunk as a generated .js file instead (see
    # static_chunk_relative_path()/static_chunk_key() below).
    view_object = create_view_object(
        node_count=30, threshold=10, is_running_on_server=False
    )

    assert view_object.is_chunked_rendering() is True


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


def test_move_node_tree_title_uses_content_for_a_titleless_node():
    view_object = create_view_object(node_count=1, threshold=0)
    node = view_object.document.section_contents[0]
    assert isinstance(node, SDocNode)
    node.set_field_value(field_name="TITLE", form_field_index=0, value=None)
    node.set_field_value(
        field_name="STATEMENT",
        form_field_index=0,
        value="  First line\n  second line  ",
    )

    assert (
        view_object.get_move_node_tree_title(node) == "First line second line"
    )


def test_move_node_tree_title_truncates_content_preview():
    view_object = create_view_object(node_count=1, threshold=0)
    node = view_object.document.section_contents[0]
    assert isinstance(node, SDocNode)
    node.set_field_value(field_name="TITLE", form_field_index=0, value=None)
    node.set_field_value(
        field_name="STATEMENT",
        form_field_index=0,
        value="A" * 100,
    )

    title = view_object.get_move_node_tree_title(node)

    assert title == "A" * 79 + "…"
    assert len(title) == 80


@pytest.mark.parametrize(
    "image_markup",
    (
        ".. image:: assets/diagrams/system-context.png",
        "![System context](assets/diagrams/system-context.png)",
        '<img src="assets/diagrams/system-context.png">',
    ),
)
def test_move_node_tree_title_uses_filename_for_an_image_only_field(
    image_markup: str,
):
    view_object = create_view_object(node_count=1, threshold=0)
    node = view_object.document.section_contents[0]
    assert isinstance(node, SDocNode)
    node.set_field_value(field_name="TITLE", form_field_index=0, value=None)
    node.set_field_value(
        field_name="STATEMENT",
        form_field_index=0,
        value=image_markup,
    )

    assert view_object.get_move_node_tree_title(node) == "system-context.png"


def test_move_node_tree_title_uses_uid_when_no_content_field_has_a_value():
    view_object = create_view_object(node_count=1, threshold=0)
    node = view_object.document.section_contents[0]
    assert isinstance(node, SDocNode)
    node.set_field_value(field_name="TITLE", form_field_index=0, value=None)
    node.set_field_value(field_name="STATEMENT", form_field_index=0, value=None)

    assert view_object.get_move_node_tree_title(node) == "REQ-000"


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


def test_static_chunk_naming_helpers_are_keyed_by_document_and_index():
    view_object = create_view_object(
        node_count=30, threshold=10, is_running_on_server=False
    )
    chunks = view_object.document_content_chunks()

    assert [
        view_object.static_chunk_relative_path(chunk_) for chunk_ in chunks
    ] == ["input-chunk-0.js", "input-chunk-1.js", "input-chunk-2.js"]
    assert [view_object.static_chunk_key(chunk_) for chunk_ in chunks] == [
        "input-chunk-0",
        "input-chunk-1",
        "input-chunk-2",
    ]


def test_chunk_content_iterator_yields_nothing_for_unknown_cursor():
    view_object = create_view_object(node_count=30, threshold=10)

    chunk_nodes = list(
        view_object.document_chunk_content_iterator("DOES_NOT_EXIST", 10)
    )

    assert chunk_nodes == []
