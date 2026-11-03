from pathlib import Path
from typing import Tuple

import pytest
from markupsafe import Markup

from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.backend.sdoc_source_code.models.source_node import SourceNode
from strictdoc.backend.sdoc_source_code.reader import (
    SourceFileTraceabilityReader,
)
from strictdoc.backend.sdoc_source_code.reader_c import (
    SourceFileTraceabilityReader_C,
)
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.file_system.source_tree import SourceFile
from strictdoc.core.file_traceability_index import FileTraceabilityIndex
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.features.source_file_view.view_object import SourceFileViewObject
from strictdoc.helpers.exception import StrictDocException
from tests.unit.helpers.document_builder import DocumentBuilder


def test_get_req_uids_by_function_names_matches_gcovr_name():
    file_traceability_index = FileTraceabilityIndex()
    file_traceability_index.map_file_function_names_to_reqs_uids[
        "functions.cpp"
    ] = {
        "test::Adder::add(int const&, int const&)": [
            (
                "GCOV:functions.cpp:test::Adder::add(int const&, int const&)",
                None,
            )
        ]
    }

    assert file_traceability_index.get_req_uids_by_function_names(
        "functions.cpp",
        [
            "test::Adder::add",
            "test::Adder::add(const int& a, const int& b)",
            "test::Adder::add(int const&, int const&)",
        ],
    ) == [("GCOV:functions.cpp:test::Adder::add(int const&, int const&)", None)]


def test_get_function_matching_names_includes_gcovr_style_cpp_name():
    source_file_traceability_info = SourceFileTraceabilityReader_C().read(
        b"""\
namespace test {

int Adder::add(const int& a, const int& b) {
  return a + b;
}
}
""",
        file_path="functions.cpp",
    )

    assert FileTraceabilityIndex.get_function_matching_names(
        source_file_traceability_info.functions[0]
    ) == [
        "test::Adder::add",
        "test::Adder::add(const int& a, const int& b)",
        "test::Adder::add(int const&, int const&)",
    ]


def test_missing_source_requirement_range_is_reported_once(
    tmp_path: Path,
) -> None:
    index, file_index, trace_info = _create_source_index(
        tmp_path,
        "# @relation(REQ-MISSING, scope=range_start, role=Implementation)\n"
        "uncovered code\n"
        "# @relation(REQ-MISSING, scope=range_end)\n",
    )

    missing = index.get_missing_source_requirement_relations()
    assert len(missing) == 1
    assert missing[0].requirement_uid == "REQ-MISSING"
    assert missing[0].source_file.in_doctree_source_file_rel_path_posix == (
        "source.txt"
    )
    assert missing[0].marker.ng_source_line_begin == 1
    assert missing[0].marker.ng_range_line_end == 3
    assert missing[0].marker.role == "Implementation"
    assert len(file_index.get_missing_requirement_relations("source.txt")) == 1
    assert file_index.get_missing_requirement_relations("other.txt") == []
    missing.clear()
    assert len(index.get_missing_source_requirement_relations()) == 1
    assert index.get_source_file_reqs("source.txt") is None
    assert trace_info.ng_lines_covered == 0
    assert trace_info.get_coverage() == 0


def test_missing_source_requirement_preserves_valid_coverage(
    tmp_path: Path,
) -> None:
    index, _, trace_info = _create_source_index(
        tmp_path,
        "# @relation(REQ-001, REQ-MISSING, scope=range_start)\n"
        "covered code\n"
        "# @relation(REQ-001, REQ-MISSING, scope=range_end)\n",
    )

    assert len(index.get_missing_source_requirement_relations()) == 1
    requirements = index.get_source_file_reqs("source.txt")
    assert requirements is not None
    assert [requirement_.reserved_uid for requirement_ in requirements] == [
        "REQ-001"
    ]
    assert trace_info.ng_lines_covered == 3
    assert trace_info.get_coverage() == 100


def test_missing_source_requirement_keeps_separate_locations(
    tmp_path: Path,
) -> None:
    index, _, _ = _create_source_index(
        tmp_path,
        "# @relation(REQ-MISSING, scope=line)\n"
        "first line\n"
        "# @relation(REQ-MISSING, scope=line)\n"
        "second line\n",
    )

    missing = index.get_missing_source_requirement_relations("source.txt")
    assert [relation_.marker.ng_source_line_begin for relation_ in missing] == [
        1,
        3,
    ]


def test_missing_source_requirement_strict_mode_raises(tmp_path: Path) -> None:
    with pytest.raises(StrictDocException, match="does not exist: REQ-MISSING"):
        _create_source_index(
            tmp_path,
            "# @relation(REQ-MISSING, scope=line)\ncode\n",
            allow_missing=False,
        )


def test_missing_source_requirement_creates_no_source_node_edge(
    tmp_path: Path,
) -> None:
    index, file_index, trace_info = _create_source_index(
        tmp_path, "# @relation(REQ-MISSING, scope=file)\ncode\n"
    )
    requirement = index.get_node_by_uid("REQ-001")
    source_node = SourceNode(
        entity_name=None,
        comment_byte_range=None,
        markers=[trace_info.markers[0]],
    )

    file_index.connect_source_node_requirements(source_node, requirement, index)

    assert index.get_parent_requirements(requirement) == []


@pytest.mark.parametrize("location", ["title", "details", "aside"])
def test_missing_source_requirement_rendering_escapes_uid(
    tmp_path: Path, location: str
) -> None:
    index, _, trace_info = _create_source_index(
        tmp_path, "# @relation(REQ-001, scope=line)\ncode\n"
    )
    config = ProjectConfig.default_config()
    templates = HTMLTemplates.create(
        project_config=config,
        enable_caching=False,
        strictdoc_last_update=index.strictdoc_last_update,
    )
    link_renderer = LinkRenderer(root_path="", static_path="_static")
    renderer = MarkupRenderer.create(
        markup=SDocMarkup.TEXT,
        traceability_index=index,
        link_renderer=link_renderer,
        html_templates=templates,
        config=config,
        context_document=None,
    )
    assert trace_info.source_file is not None
    view = SourceFileViewObject(
        traceability_index=index,
        trace_info=trace_info,
        project_config=config,
        link_renderer=link_renderer,
        markup_renderer=renderer,
        text_renderer=renderer,
        source_file=trace_info.source_file,
        pygments_styles=Markup(""),
        pygmented_source_file_lines=[],
        jinja_environment=templates.jinja_environment(),
    )
    missing_uid = "<missing&requirement>"
    if location == "title":
        output = view.render_node_title_for_banner_header(
            trace_info.markers[0], missing_uid
        )
    elif location == "details":
        output = view.render_detailed_node_for_banner(missing_uid)
    else:
        output = view.render_aside_requirement(missing_uid)

    assert "Missing requirement:" in output
    assert "&lt;missing&amp;requirement&gt;" in output
    assert missing_uid not in output
    assert "href=" not in output


def _create_source_index(
    tmp_path: Path, source: str, *, allow_missing: bool = True
) -> Tuple[
    TraceabilityIndex, FileTraceabilityIndex, SourceFileTraceabilityInfo
]:
    document_builder = DocumentBuilder()
    document_builder.add_requirement("REQ-001")
    document_builder.project_config.relaxed_mode = allow_missing
    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document_builder.build()],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=document_builder.project_config
    )
    source_path = tmp_path / "source.txt"
    source_path.write_text(source, encoding="utf-8")
    source_file = SourceFile(
        level=0,
        full_path=str(source_path),
        in_doctree_source_file_rel_path="source.txt",
        output_dir_full_path=str(tmp_path),
        output_file_full_path=str(tmp_path / "source.txt.html"),
    )
    trace_info = SourceFileTraceabilityReader().read(source)
    file_index = index.get_file_traceability_index()
    file_index.create_traceability_info(source_file, trace_info)
    file_index.validate_and_resolve(index, document_builder.project_config)
    return index, file_index, trace_info
