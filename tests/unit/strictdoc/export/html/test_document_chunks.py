import pytest

from strictdoc.export.html.generators.view_objects.document_chunks import (
    slice_chunks,
)


def test_empty_input_produces_no_chunks():
    assert slice_chunks([], 100) == []


def test_250_mids_with_chunk_size_100_produce_three_chunks():
    node_mids = [f"MID_{i_}" for i_ in range(250)]

    chunks = slice_chunks(node_mids, 100)

    assert len(chunks) == 3
    assert [chunk_.size for chunk_ in chunks] == [100, 100, 50]
    assert [chunk_.index for chunk_ in chunks] == [0, 1, 2]
    for chunk_ in chunks:
        assert chunk_.first_node_mid == node_mids[chunk_.index * 100]


def test_exactly_chunk_size_mids_produce_one_chunk():
    node_mids = [f"MID_{i_}" for i_ in range(100)]

    chunks = slice_chunks(node_mids, 100)

    assert len(chunks) == 1
    assert chunks[0].index == 0
    assert chunks[0].first_node_mid == "MID_0"
    assert chunks[0].size == 100


def test_zero_chunk_size_raises_assertion_error():
    with pytest.raises(AssertionError):
        slice_chunks(["MID_0"], 0)


def test_negative_chunk_size_raises_assertion_error():
    with pytest.raises(AssertionError):
        slice_chunks(["MID_0"], -1)
