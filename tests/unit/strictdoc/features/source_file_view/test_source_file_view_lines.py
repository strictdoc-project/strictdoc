"""
@relation(SDOC-SRS-36, scope=file)
"""

from pathlib import Path
from typing import List, Optional

from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityReader,
)
from strictdoc.core.file_system.source_tree import SourceFile
from strictdoc.features.source_file_view.generator import (
    SourceFileViewHTMLGenerator,
)
from strictdoc.features.source_file_view.view_object import (
    SourceLine,
    SourceMarkerTuple,
    create_source_lines,
)


def create_lines(tmp_path: Path, source_input: str) -> List[SourceLine]:
    """
    Read the markers of the source input and create the lines of its page,
    the same way as SourceFileViewHTMLGenerator.export().
    """
    path_to_file = tmp_path / "file.txt"
    path_to_file.write_text(source_input)
    source_file = SourceFile(
        level=0,
        full_path=str(path_to_file),
        in_doctree_source_file_rel_path="file.txt",
        output_dir_full_path=str(tmp_path / "output"),
        output_file_full_path=str(tmp_path / "output" / "file.txt.html"),
    )
    trace_info = SourceFileTraceabilityReader().read(source_input)
    entries, _ = SourceFileViewHTMLGenerator.get_pygmented_source_lines(
        source_file, source_input.splitlines(keepends=True), trace_info
    )
    return create_source_lines(entries)


def get_range(
    marker_tuple: Optional[SourceMarkerTuple],
) -> Optional[List[int]]:
    if marker_tuple is None:
        return None
    return [
        marker_tuple.markers[0].ng_range_line_begin,
        marker_tuple.markers[0].ng_range_line_end,
    ]


def test_01_range_marker_opens_and_closes_range(tmp_path: Path) -> None:
    lines = create_lines(
        tmp_path,
        """\
# @relation(REQ-1, scope=range_start)
CONTENT
# @relation(REQ-1, scope=range_end)
""",
    )

    assert [line_.number for line_ in lines] == [1, 2, 3]
    assert [get_range(line_.range_opener) for line_ in lines] == [
        [1, 3],
        None,
        None,
    ]
    assert [get_range(line_.range_closer) for line_ in lines] == [
        None,
        None,
        [1, 3],
    ]


def test_02_line_marker_closes_range_below_next_line(tmp_path: Path) -> None:
    lines = create_lines(
        tmp_path,
        """\
CONTENT 1
# @relation(REQ-1, scope=line)
CONTENT 2
CONTENT 3
""",
    )

    assert [get_range(line_.range_opener) for line_ in lines] == [
        None,
        [2, 3],
        None,
        None,
    ]
    assert [get_range(line_.range_closer) for line_ in lines] == [
        None,
        None,
        [2, 3],
        None,
    ]


def test_03_line_marker_followed_by_range_marker(tmp_path: Path) -> None:
    lines = create_lines(
        tmp_path,
        """\
# @relation(REQ-1, scope=line)
# @relation(REQ-2, scope=range_start)
CONTENT
# @relation(REQ-2, scope=range_end)
""",
    )

    assert [get_range(line_.range_opener) for line_ in lines] == [
        [1, 2],
        [2, 4],
        None,
        None,
    ]
    # The range of the line marker ends on line 2. Line 2 has markers, so it
    # closes no line marker range, and the range of line 1 gets no closer.
    # The page template behaved the same way before create_source_lines().
    assert [get_range(line_.range_closer) for line_ in lines] == [
        None,
        None,
        None,
        [2, 4],
    ]


def test_04_file_marker_opens_range_without_closer(tmp_path: Path) -> None:
    lines = create_lines(
        tmp_path,
        """\
# @relation(REQ-1, scope=file)
CONTENT
""",
    )

    assert [get_range(line_.range_opener) for line_ in lines] == [
        [1, 2],
        None,
    ]
    assert [line_.range_closer for line_ in lines] == [None, None]


def test_05_empty_lines(tmp_path: Path) -> None:
    lines = create_lines(
        tmp_path,
        """\
CONTENT 1

CONTENT 2
""",
    )

    assert [line_.is_empty for line_ in lines] == [False, True, False]
    assert "CONTENT 2" in lines[2].content
