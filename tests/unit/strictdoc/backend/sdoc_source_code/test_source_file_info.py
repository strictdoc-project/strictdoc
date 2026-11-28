"""
@relation(SDOC-SRS-142, scope=file)
"""

import pickle
from pathlib import Path

from strictdoc.backend.sdoc_source_code.caching_reader import (
    SourceFileTraceabilityCachingReader,
)
from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityReader,
)
from strictdoc.core.project_config import ProjectConfig

SOURCE_INPUT = """
# @relation(REQ-001, scope=range_start)
CONTENT 1
CONTENT 2
# @relation(REQ-001, scope=range_end)
""".lstrip()


def test_01_pickle_leaves_out_the_lines_and_keeps_the_markers() -> None:
    traceability_info = SourceFileTraceabilityReader().read(SOURCE_INPUT)

    traceability_info_copy = pickle.loads(pickle.dumps(traceability_info))

    assert not hasattr(traceability_info_copy, "g_parts")
    assert [marker_.reqs for marker_ in traceability_info_copy.markers] == [
        ["REQ-001"],
        ["REQ-001"],
    ]
    assert list(traceability_info_copy.ng_map_reqs_to_markers) == ["REQ-001"]
    assert (
        traceability_info_copy.file_stats.lines_total
        == traceability_info.file_stats.lines_total
    )
    # Pickling does not change the parsed object.
    assert len(traceability_info.g_parts) == 4


def test_02_cached_source_file_has_no_lines(tmp_path: Path) -> None:
    project_config = ProjectConfig.default_config()
    project_config.output_dir = str(tmp_path / "output")
    project_config.dir_for_sdoc_cache = str(tmp_path / "cache")
    input_file = tmp_path / "input.txt"
    input_file.write_text(SOURCE_INPUT)
    # The first read parses the file and saves it to the cache.
    SourceFileTraceabilityCachingReader.read_from_file(
        str(input_file), project_config
    )

    traceability_info = SourceFileTraceabilityCachingReader.read_from_file(
        str(input_file), project_config
    )

    assert traceability_info is not None
    assert not hasattr(traceability_info, "g_parts")
    assert len(traceability_info.markers) == 2
