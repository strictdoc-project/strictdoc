"""
@relation(SDOC-SRS-36, scope=file)
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from markupsafe import Markup
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_for_filename
from pygments.lexers.ada import AdaLexer
from pygments.lexers.c_cpp import CLexer, CppLexer
from pygments.lexers.configs import TOMLLexer
from pygments.lexers.data import YamlLexer
from pygments.lexers.javascript import JavascriptLexer
from pygments.lexers.markup import RstLexer, TexLexer
from pygments.lexers.python import PythonLexer
from pygments.lexers.special import TextLexer
from pygments.lexers.templates import HtmlDjangoLexer
from pygments.util import ClassNotFound

from strictdoc import __version__
from strictdoc.backend.sdoc.models.document_view import NullViewElement
from strictdoc.backend.sdoc_source_code.models.language_item_marker import (
    ForwardLanguageItemMarker,
    LanguageItemMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    ForwardRangeMarker,
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.file_system.source_tree import SourceFile
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.features.source_file_view.view_data import (
    FieldData,
    FieldDataRenderer,
    NodeData,
    NodeLinkData,
    SourceFileDataIndex,
    SourceFileDataLinkRenderer,
    SourceFileViewDataCollector,
)
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.file_system import file_open_read_utf8


@dataclass
class SourceMarkerTuple:
    ng_range_line_begin: int
    ng_range_line_end: int
    source_line: Markup
    markers: List[
        Union[LanguageItemMarker, ForwardRangeMarker, LineMarker, RangeMarker]
    ]

    def is_end(self) -> bool:
        return any(map(lambda m_: m_.is_end(), self.markers))

    def is_line_marker(self) -> bool:
        return any(map(lambda m_: isinstance(m_, LineMarker), self.markers))

    def is_range_marker(self) -> bool:
        return any(map(lambda m_: m_.is_range_marker(), self.markers))


SourceLineEntry = Union[
    Markup,
    SourceMarkerTuple,
]


@dataclass
class SourceLine:
    """
    One line of the source file page, ready for main.jinja to print.

    create_source_lines() decides in Python where the ranges open and close,
    so main.jinja only prints the records. The decisions are easier to read,
    test, and debug in Python than in Jinja.
    """

    # The line number, counted from 1.
    number: int
    # The line highlighted by Pygments.
    content: Markup
    # True for an empty line without markers. main.jinja prints a placeholder.
    is_empty: bool
    # The markers whose range header main.jinja prints above the line.
    range_opener: Optional[SourceMarkerTuple]
    # The markers whose range closer main.jinja prints below the line.
    range_closer: Optional[SourceMarkerTuple]


def create_source_lines(entries: List[SourceLineEntry]) -> List[SourceLine]:
    """
    Create one SourceLine per entry and decide where the ranges open and close.

    A range opens above a line with markers, unless the markers only end
    ranges. A range that covers one line has its begin and end markers on the
    same line, so this line opens the range too.

    A range closes below one of these lines:
    - A line with a marker that ends a range.
    - The last line of a line marker: the first line without markers whose
      number is the end of the latest line marker.
    """
    source_lines: List[SourceLine] = []
    # The latest line marker whose range has not closed yet.
    open_line_marker: Optional[SourceMarkerTuple] = None
    for number, entry in enumerate(entries, start=1):
        if isinstance(entry, SourceMarkerTuple):
            opens_range = (
                not entry.is_end()
                or entry.ng_range_line_begin == entry.ng_range_line_end
            )
            closes_range = entry.is_range_marker() and entry.is_end()
            if entry.is_line_marker():
                open_line_marker = entry
            source_lines.append(
                SourceLine(
                    number=number,
                    content=entry.source_line,
                    is_empty=False,
                    range_opener=entry if opens_range else None,
                    range_closer=entry if closes_range else None,
                )
            )
            continue

        range_closer: Optional[SourceMarkerTuple] = None
        if (
            open_line_marker is not None
            and open_line_marker.ng_range_line_end == number
        ):
            range_closer = open_line_marker
            open_line_marker = None
        source_lines.append(
            SourceLine(
                number=number,
                content=entry,
                is_empty=entry == "",
                range_opener=None,
                range_closer=range_closer,
            )
        )
    return source_lines


def highlight_source_file_lines(
    source_file: SourceFile,
    source_file_lines: List[str],
    coverage_info: SourceFileTraceabilityInfo,
) -> Tuple[
    List[SourceLineEntry],
    Markup,
]:
    assert isinstance(source_file, SourceFile)
    assert isinstance(source_file_lines, list)
    assert isinstance(coverage_info, SourceFileTraceabilityInfo)

    if source_file.is_python_file():
        lexer = PythonLexer()
    elif source_file.is_c_file():
        lexer = CLexer()
    elif source_file.is_cpp_file():
        lexer = CppLexer()
    elif source_file.is_ada_file():
        lexer = AdaLexer()
    elif source_file.is_tex_file():
        lexer = TexLexer()
    elif source_file.is_toml_file():
        lexer = TOMLLexer()
    elif source_file.is_jinja_file():
        lexer = HtmlDjangoLexer()
    elif source_file.is_javascript_file():
        lexer = JavascriptLexer()
    elif source_file.is_yaml_file():
        lexer = YamlLexer()
    elif source_file.is_rst_file():
        lexer = RstLexer()
    elif source_file.is_st_file():
        # Structured Text syntax doesn't seem to be supported by Pygments.
        lexer = TextLexer()
    else:
        try:
            lexer = get_lexer_for_filename(source_file.file_name)
        except ClassNotFound:
            lexer = TextLexer()

    # HACK:
    # Otherwise, Pygments will skip the first line as if it does not exist.
    # This behavior surprisingly has an effect on the first line if its empty.
    hack_first_line: bool = False
    if source_file_lines[0] == "\n":
        source_file_lines[0] = " \n"
        hack_first_line = True

    # HACK:
    # Pygments does not process lines if they are empty and are at the end
    # of a file. Adding a marker to the end so that Pygments do not cut the
    # corners.
    source_file_content = "".join(source_file_lines)
    source_file_content_with_marker = source_file_content + "\n###"

    html_formatter = HtmlFormatter()
    pygmented_source_file_content = highlight(
        source_file_content_with_marker, lexer, html_formatter
    )

    # HACK: split content into lines by cutting off the header and footer
    # parts generated by Pygments:
    # <div class="highlight"><pre> and </pre></div>
    # TODO: Implement proper splitting.
    start_pattern = '<div class="highlight"><pre>'
    end_pattern = "</pre></div>\n"
    assert pygmented_source_file_content.startswith(start_pattern)
    assert pygmented_source_file_content.endswith(end_pattern), (
        f"{pygmented_source_file_content}"
    )

    slice_start = len(start_pattern)
    slice_end = len(pygmented_source_file_content) - len(end_pattern)
    pygmented_source_file_content = pygmented_source_file_content[
        slice_start:slice_end
    ]
    # cast() is required for mypy: split() returns List[str], and
    # because List is invariant, mypy rejects assigning it directly to
    # a List[Union[str, SourceMarkerTuple]] variable even with the
    # annotation in place. cast() is a no-op at runtime, unlike
    # wrapping in list(), which would silently allocate a second,
    # unnecessary copy of the list just to satisfy the type checker.
    pygmented_source_file_lines: List[Union[str, SourceMarkerTuple]] = cast(
        List[Union[str, SourceMarkerTuple]],
        pygmented_source_file_content.split("\n"),
    )
    if hack_first_line:
        pygmented_source_file_lines[0] = "<span></span>"

    if pygmented_source_file_lines[-1] == "":
        pygmented_source_file_lines.pop()
    assert "###" in pygmented_source_file_lines[-1], (  # type: ignore[operator]
        "Expected marker to be in place."
    )
    # Pop ###, pop "\n"
    pygmented_source_file_lines.pop()
    if pygmented_source_file_lines[-1] == "":
        pygmented_source_file_lines.pop()

    assert len(pygmented_source_file_lines) == len(source_file_lines), (
        f"Something went wrong when running Pygments against "
        f"the source file: "
        f"{len(pygmented_source_file_lines)} == {len(source_file_lines)}, "
        f"{pygmented_source_file_lines} == {source_file_lines}."
    )

    for marker in coverage_info.markers:
        marker_line = (
            marker.ng_range_line_begin
            if marker.is_begin()
            else marker.ng_range_line_end
        )
        assert isinstance(marker_line, int)
        source_marker_tuple: SourceMarkerTuple
        if isinstance(
            pygmented_source_file_lines[marker_line - 1], SourceMarkerTuple
        ):
            source_marker_tuple = assert_cast(
                pygmented_source_file_lines[marker_line - 1],
                SourceMarkerTuple,
            )
        else:
            pygmented_source_file_line = assert_cast(
                pygmented_source_file_lines[marker_line - 1], str
            )
            assert marker.ng_range_line_begin is not None
            assert marker.ng_range_line_end is not None
            source_marker_tuple = SourceMarkerTuple(
                ng_range_line_begin=marker.ng_range_line_begin,
                ng_range_line_end=marker.ng_range_line_end,
                source_line=Markup(pygmented_source_file_line),
                markers=[],
            )
            pygmented_source_file_lines[marker_line - 1] = source_marker_tuple

        if isinstance(
            marker,
            (
                ForwardRangeMarker,
                ForwardLanguageItemMarker,
                LanguageItemMarker,
                RangeMarker,
                LineMarker,
            ),
        ):
            source_marker_tuple.markers.append(marker)
            continue

        raise NotImplementedError(marker)  # pragma: no cover

    pygments_styles = (
        f"/* Lexer: {lexer.name} */\n"
        + html_formatter.get_style_defs(".highlight")
    )

    return [_mark_safe(line) for line in pygmented_source_file_lines], Markup(
        pygments_styles
    )


def _mark_safe(
    line: Union[str, SourceMarkerTuple],
) -> Union[Markup, SourceMarkerTuple]:
    return line if isinstance(line, SourceMarkerTuple) else Markup(line)


class SourceFileViewObject:
    """
    The view object of a source file page. It holds the data of the page and
    renders the page from this data.

    create() collects the data in the main process: the markers of the
    source file and the data of the document nodes that the page shows (see
    view_data.py). The view object holds no reference to the traceability
    index or to SDocNode objects. As a result, it is small when pickled, and
    render_screen() can run in the main process or in a worker process.

    render_screen() reads and highlights the source file and renders the
    templates. The objects that only rendering needs are created there and
    are not pickled.
    """

    def __init__(
        self,
        *,
        project_config: ProjectConfig,
        source_file: SourceFile,
        trace_info: SourceFileTraceabilityInfo,
        node_uids: List[str],
        nodes: Dict[str, NodeData],
    ) -> None:
        self.project_config: ProjectConfig = project_config
        self.source_file: SourceFile = source_file
        self.trace_info: SourceFileTraceabilityInfo = trace_info
        # The nodes of the "Nodes" tab of aside.jinja.
        self.node_uids: List[str] = node_uids
        # All nodes that the page shows, by UID.
        self.nodes: Dict[str, NodeData] = nodes

        self.link_renderer: SourceFileDataLinkRenderer = (
            SourceFileDataLinkRenderer(
                root_path=source_file.path_depth_prefix,
                static_path=project_config.dir_for_sdoc_assets,
            )
        )
        self.traceability_index: SourceFileDataIndex = SourceFileDataIndex()
        self.current_view: NullViewElement = NullViewElement()
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version: str = __version__

        # The render state. render_screen() sets it for the time of
        # rendering and resets it afterwards.
        self.source_lines: List[SourceLine] = []
        # The lines that the "Ranges" tab of aside.jinja lists: the lines with
        # markers that begin a range.
        self.range_begin_lines: List[SourceMarkerTuple] = []
        self.pygments_styles: Markup = Markup("")
        self._jinja_environment: Optional[JinjaEnvironment] = None
        self._field_renderer: Optional[FieldDataRenderer] = None

    @staticmethod
    def create(
        *,
        source_file: SourceFile,
        data_collector: SourceFileViewDataCollector,
    ) -> "SourceFileViewObject":
        """
        Use cases: static export and server, in the main process or in the
        server process. The static export uses one data collector for all
        pages, the server one per page.
        """
        trace_info = data_collector.traceability_index.get_coverage_info(
            source_file.in_doctree_source_file_rel_path_posix
        )
        node_uids = data_collector.get_source_file_node_uids(source_file)
        return SourceFileViewObject(
            project_config=data_collector.project_config,
            source_file=source_file,
            trace_info=trace_info,
            node_uids=node_uids,
            nodes=data_collector.collect_nodes(
                source_file=source_file,
                trace_info=trace_info,
                node_uids=node_uids,
            ),
        )

    @staticmethod
    def _reset_render_state(state: Dict[str, Any]) -> None:
        state["source_lines"] = []
        state["range_begin_lines"] = []
        state["pygments_styles"] = Markup("")
        state["_jinja_environment"] = None
        state["_field_renderer"] = None

    def __getstate__(self) -> Dict[str, Any]:
        """
        Pickle only the data, never the render state.
        """
        state = self.__dict__.copy()
        SourceFileViewObject._reset_render_state(state)
        return state

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        """
        Use cases: static export, in a worker process or in the main process,
        and server, in the server process.
        """
        with file_open_read_utf8(self.source_file.full_path) as opened_file:
            source_file_lines = opened_file.readlines()

        entries: List[SourceLineEntry] = []
        pygments_styles: Markup = Markup("")
        if len(source_file_lines) > 0:
            entries, pygments_styles = highlight_source_file_lines(
                self.source_file, source_file_lines, self.trace_info
            )

        self.source_lines = create_source_lines(entries)
        self.range_begin_lines = [
            entry_
            for entry_ in entries
            if isinstance(entry_, SourceMarkerTuple) and not entry_.is_end()
        ]
        self.pygments_styles = pygments_styles
        self._jinja_environment = jinja_environment
        self._field_renderer = FieldDataRenderer(
            project_config=self.project_config,
            jinja_environment=jinja_environment,
            link_renderer=self.link_renderer,
        )
        try:
            return jinja_environment.render_template_as_markup(
                "features/source_file_view/index.jinja", view_object=self
            )
        finally:
            # The export keeps all view objects until the last page is
            # written. Without the reset, each view object would keep the
            # highlighted lines of its file until then.
            SourceFileViewObject._reset_render_state(self.__dict__)

    def _get_jinja_environment(self) -> JinjaEnvironment:
        assert self._jinja_environment is not None, (
            "render_screen() sets the Jinja environment."
        )
        return self._jinja_environment

    def _get_field_renderer(self) -> FieldDataRenderer:
        assert self._field_renderer is not None, (
            "render_screen() sets the field renderer."
        )
        return self._field_renderer

    def get_document_level(self) -> int:
        return self.source_file.level

    def get_source_file_node_uids(self) -> List[str]:
        return self.node_uids

    def render_detailed_node_for_banner(self, node_uid: str) -> Markup:
        return self._get_jinja_environment().render_template_as_markup(
            "components/node_content/index_extends_readonly.jinja",
            node=self.nodes[node_uid],
            view_object=self,
            requirement_style="table",
        )

    def render_node_title_for_banner_header(
        self, marker: Any, node_uid: str
    ) -> Markup:
        return self._get_jinja_environment().render_template_as_markup(
            "features/source_file_view/node_title_for_banner_header.jinja",
            node=self.nodes[node_uid],
            view_object=self,
            role=marker.role,
            is_forward_from_requirements_to_code=marker.is_forward(),
        )

    def render_aside_requirement(
        self,
        node_uid: str,
        range_begin: Optional[int] = None,
        range_end: Optional[int] = None,
    ) -> Markup:
        return self._get_jinja_environment().render_template_as_markup(
            "features/source_file_view/requirement.jinja",
            requirement=self.nodes[node_uid],
            view_object=self,
            requirement_style="table",
            range_begin=range_begin,
            range_end=range_end,
        )

    def render_node_statement(self, node: NodeData) -> Markup:
        return self._get_field_renderer().render(
            assert_cast(node.content_field, FieldData)
        )

    def render_truncated_node_statement(self, node: NodeData) -> Markup:
        # MarkupRenderer renders the full statement here too.
        return self.render_node_statement(node)

    def render_node_rationale(self, node: NodeData) -> Markup:
        return self._get_field_renderer().render(
            assert_cast(node.rationale_field, FieldData)
        )

    def render_node_field(self, node_field: FieldData) -> Markup:
        assert isinstance(node_field, FieldData), node_field
        return self._get_field_renderer().render(node_field)

    def render_url(self, url: str) -> str:
        return self.link_renderer.render_url(url)

    def render_marker_range_link(self, marker: RangeMarker) -> str:
        return self.link_renderer.render_marker_range_link(
            self.source_file.in_doctree_source_file_rel_path_posix,
            self.source_file,
            marker,
        )

    def render_node_link(self, node: NodeLinkData) -> str:
        assert isinstance(node, NodeLinkData), node
        return self.link_renderer.render_requirement_link_from_source_file(
            node, self.source_file
        )

    def render_static_url(self, url: str) -> str:
        return self.link_renderer.render_static_url(url)

    def render_local_anchor(self, node: NodeLinkData) -> str:
        return self.link_renderer.render_local_anchor(node)

    def render_issues(
        self,
        node: Any,  # noqa: ARG002
        field: Optional[str] = None,  # noqa: ARG002
    ) -> str:
        """
        FIXME: It is not great that this method is called from here.
        """
        return ""

    def get_source_file_path(self) -> str:
        return self.source_file.in_doctree_source_file_rel_path_posix

    def get_file_stats_lines_total(self) -> str:
        return str(self.trace_info.file_stats.lines_total)

    def get_file_stats_lines_total_non_empty(self) -> str:
        return str(self.trace_info.file_stats.lines_non_empty)

    def get_file_stats_non_empty_lines_covered(self) -> str:
        covered = self.trace_info.ng_lines_covered
        total_non_empty = self.trace_info.file_stats.lines_non_empty
        percentage = (
            (covered / total_non_empty * 100) if total_non_empty > 0 else 0
        )
        return f"{covered} / {total_non_empty} ({percentage:.1f}%)"

    def get_file_stats_functions_total(self) -> str:
        return str(len(self.trace_info.functions))

    def get_file_stats_functions_covered(self) -> str:
        covered = self.trace_info.covered_functions
        total = len(self.trace_info.functions)
        percentage = (covered / total * 100) if total > 0 else 0
        return f"{covered} / {total} ({percentage:.1f}%)"

    def get_html2pdf_classes(self, node: Any) -> str:  # noqa: ARG002
        """
        This view object class is coupled with the HTML2PDF-related template
        logic.

        The Source File View is not printed with HTML2PDF, so we keep its classes
        to noop.
        """
        return ""
