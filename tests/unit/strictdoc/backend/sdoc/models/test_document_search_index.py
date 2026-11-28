"""
@relation(SDOC-SRS-155, scope=file)
"""

import copyreg
import pickle
from pathlib import Path
from typing import Any, List

import pytest

from strictdoc.backend.sdoc.models.document import SDocDocumentSearchIndex
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.pickle import pickle_load


def create_search_index() -> SDocDocumentSearchIndex:
    return SDocDocumentSearchIndex(
        document_index={"re": ("MID_1", "MID_2"), "req": ("MID_1",)},
        map_nodes_by_mid={
            "MID_1": {"MID": "MID_1", "TITLE": "Requirement"},
            "MID_2": {"MID": "MID_2", "TITLE": "Rest"},
        },
    )


def test_01_pickle_round_trip_keeps_the_data() -> None:
    search_index = create_search_index()

    search_index_copy = pickle.loads(pickle.dumps(search_index))

    assert search_index_copy.document_index == search_index.document_index
    assert search_index_copy.map_nodes_by_mid == search_index.map_nodes_by_mid


def test_02_unpickled_data_is_decoded_once_on_first_access(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    search_index_copy = pickle.loads(pickle.dumps(create_search_index()))

    decoded: List[bytes] = []
    loads = pickle.loads

    def loads_(data: bytes) -> Any:
        decoded.append(data)
        return loads(data)

    monkeypatch.setattr(pickle, "loads", loads_)

    assert len(decoded) == 0
    assert search_index_copy.document_index["req"] == ("MID_1",)
    assert search_index_copy.map_nodes_by_mid["MID_2"]["TITLE"] == "Rest"
    assert search_index_copy.document_index["re"] == ("MID_1", "MID_2")
    assert len(decoded) == 1


def test_03_data_is_pickled_once(monkeypatch: pytest.MonkeyPatch) -> None:
    search_index = create_search_index()

    pickled: List[Any] = []
    dumps = pickle.dumps

    def dumps_(obj: Any, *args: Any, **kwargs: Any) -> bytes:
        pickled.append(obj)
        return dumps(obj, *args, **kwargs)

    monkeypatch.setattr(pickle, "dumps", dumps_)

    # The calls through dumps() bypass the counter. Only the nested pickle of
    # the data goes through dumps_().
    first = dumps(search_index)
    second = dumps(search_index)

    assert len(pickled) == 1
    assert first == second


def test_04_document_from_the_cache_has_the_search_index(
    tmp_path: Path,
) -> None:
    project_config = ProjectConfig.default_config()
    project_config.output_dir = str(tmp_path / "output")
    project_config.dir_for_sdoc_cache = str(tmp_path / "cache")
    input_file = tmp_path / "input.sdoc"
    input_file.write_text(
        """
[DOCUMENT]
TITLE: Document

[REQUIREMENT]
UID: REQ-1
TITLE: Search index
STATEMENT: Statement
""".lstrip()
    )
    # The first read parses the file and saves the document to the cache.
    search_index = (
        SDReader().read_from_file(str(input_file), project_config).search_index
    )

    document = SDReader.read_from_cache(str(input_file), project_config)

    assert document is not None
    assert "search" in search_index.document_index
    assert document.search_index.document_index == search_index.document_index
    assert (
        document.search_index.map_nodes_by_mid == search_index.map_nodes_by_mid
    )


def test_05_cache_entry_of_an_earlier_build_is_a_cache_miss() -> None:
    class EarlierSearchIndex:
        """
        Pickles like the search index of an earlier StrictDoc build, which
        was a dataclass with the fields as its state.
        """

        def __reduce__(self) -> Any:
            return (
                copyreg._reconstructor,  # type: ignore[attr-defined]
                (SDocDocumentSearchIndex, object, None),
                {"document_index": {}, "map_nodes_by_mid": {}},
            )

    assert pickle_load(pickle.dumps(EarlierSearchIndex())) is None
