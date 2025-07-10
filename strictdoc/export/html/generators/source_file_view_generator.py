"""
@relation(SDOC-SRS-36, scope=file)
"""

# mypy: disable-error-code="no-untyped-call,no-untyped-def,operator"
import os
from pathlib import Path
from typing import List, Tuple, Union

from markupsafe import Markup
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_for_filename
from pygments.lexers.c_cpp import CLexer, CppLexer
from pygments.lexers.configs import TOMLLexer
from pygments.lexers.data import YamlLexer
from pygments.lexers.javascript import JavascriptLexer
from pygments.lexers.markup import RstLexer, TexLexer
from pygments.lexers.python import PythonLexer
from pygments.lexers.special import TextLexer
from pygments.lexers.templates import HtmlDjangoLexer
from pygments.util import ClassNotFound

from strictdoc.backend.sdoc_source_code.models.function_range_marker import (
    ForwardFunctionRangeMarker,
    FunctionRangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.line_marker import LineMarker
from strictdoc.backend.sdoc_source_code.models.range_marker import (
    ForwardRangeMarker,
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.source_tree import SourceFile
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.generators.view_objects.source_file_view_object import (
    SourceFileViewObject,
    SourceLineEntry,
    SourceMarkerTuple,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.timing import measure_performance


class SourceFileViewHTMLGenerator:
    @staticmethod
    def export_to_file(
        *,
        project_config: ProjectConfig,
        source_file: SourceFile,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ) -> None:
        if os.path.isfile(source_file.output_file_full_path) and (
            get_file_modification_time(source_file.full_path)
            < get_file_modification_time(source_file.output_file_full_path)
            and not traceability_index.file_dependency_manager.must_generate(
                source_file.full_path
            )
        ):
            with measure_performance(
                f"Skip: {source_file.in_doctree_source_file_rel_path}"
            ):
                return

        with measure_performance(
            f"File: {source_file.in_doctree_source_file_rel_path}"
        ):
            document_content = SourceFileViewHTMLGenerator.export(
                project_config=project_config,
                source_file=source_file,
                traceability_index=traceability_index,
                html_templates=html_templates,
            )
            Path(source_file.output_dir_full_path).mkdir(
                parents=True, exist_ok=True
            )
            with open(
                source_file.output_file_full_path, "w", encoding="utf-8"
            ) as file:
                file.write(document_content)

    @staticmethod
    def export(
        *,
        project_config: ProjectConfig,
        source_file: SourceFile,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ):
        with open(source_file.full_path, encoding="utf-8") as opened_file:
            source_file_lines = opened_file.readlines()

        pygmented_source_file_lines: List[SourceLineEntry] = []
        pygments_styles: Markup = Markup("")

        trace_info: SourceFileTraceabilityInfo = (
            traceability_index.get_coverage_info(
                source_file.in_doctree_source_file_rel_path_posix
            )
        )

        if len(source_file_lines) > 0:
            (
                pygmented_source_file_lines,
                pygments_styles,
            ) = SourceFileViewHTMLGenerator.get_pygmented_source_lines(
                source_file, source_file_lines, trace_info
            )
        link_renderer = LinkRenderer(
            root_path=source_file.path_depth_prefix,
            static_path=project_config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            "RST",
            traceability_index,
            link_renderer,
            html_templates,
            project_config,
            None,
        )
        view_object = SourceFileViewObject(
            traceability_index=traceability_index,
            trace_info=trace_info,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            source_file=source_file,
            pygments_styles=pygments_styles,
            pygmented_source_file_lines=pygmented_source_file_lines,
            jinja_environment=html_templates.jinja_environment(),
        )
        return view_object.render_screen()

    @staticmethod
    def get_pygmented_source_lines(
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
        pygmented_source_file_lines: List[Union[str, SourceMarkerTuple]] = list(
            pygmented_source_file_content.split("\n")
        )
        if hack_first_line:
            pygmented_source_file_lines[0] = "<span></span>"

        if pygmented_source_file_lines[-1] == "":
            pygmented_source_file_lines.pop()
        assert "###" in pygmented_source_file_lines[-1], (
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
                pygmented_source_file_lines[marker_line - 1] = (
                    source_marker_tuple
                )

            if isinstance(
                marker,
                (
                    ForwardRangeMarker,
                    ForwardFunctionRangeMarker,
                    FunctionRangeMarker,
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

        return [
            SourceFileViewHTMLGenerator.mark_safe(line)
            for line in pygmented_source_file_lines
        ], Markup(pygments_styles)

    @staticmethod
    def mark_safe(
        line: Union[str, SourceMarkerTuple],
    ) -> Union[Markup, SourceMarkerTuple]:
        return line if isinstance(line, SourceMarkerTuple) else Markup(line)
