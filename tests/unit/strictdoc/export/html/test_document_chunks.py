import pytest

from strictdoc.export.html.generators.view_objects.document_chunks import (
    slice_chunks,
)


def test_empty_input_produces_no_chunks():
    assert slice_chunks([], 100) == []


def test_250_mids_with_chunk_size_100_produce_three_chunks():
    node_entries = [(f"MID_{i_}", f"ANCHOR_{i_}") for i_ in range(250)]

    chunks = slice_chunks(node_entries, 100)

    assert len(chunks) == 3
    assert [chunk_.size for chunk_ in chunks] == [100, 100, 50]
    assert [chunk_.index for chunk_ in chunks] == [0, 1, 2]
    for chunk_ in chunks:
        entry_slice = node_entries[
            chunk_.index * 100 : (chunk_.index + 1) * 100
        ]
        assert chunk_.first_node_mid == entry_slice[0][0]
        assert list(chunk_.node_mids) == [entry[0] for entry in entry_slice]
        assert list(chunk_.anchors) == [entry[1] for entry in entry_slice]


def test_exactly_chunk_size_mids_produce_one_chunk():
    node_entries = [(f"MID_{i_}", f"ANCHOR_{i_}") for i_ in range(100)]

    chunks = slice_chunks(node_entries, 100)

    assert len(chunks) == 1
    assert chunks[0].index == 0
    assert chunks[0].first_node_mid == "MID_0"
    assert chunks[0].size == 100
    assert list(chunks[0].node_mids) == [entry[0] for entry in node_entries]
    assert list(chunks[0].anchors) == [entry[1] for entry in node_entries]


def test_zero_chunk_size_raises_assertion_error():
    with pytest.raises(AssertionError):
        slice_chunks([("MID_0", "ANCHOR_0")], 0)


def test_negative_chunk_size_raises_assertion_error():
    with pytest.raises(AssertionError):
        slice_chunks([("MID_0", "ANCHOR_0")], -1)
