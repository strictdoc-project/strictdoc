# mypy: disable-error-code="no-untyped-call,no-untyped-def,operator"
import html
from typing import List

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

from strictdoc.backend.sdoc_source_code.models.range_marker import (
    ForwardRangeMarker,
    LineMarker,
    RangeMarker,
)
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.finders.source_files_finder import SourceFile
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.generators.view_objects.source_file_view_object import (
    SourceFileViewObject,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


class SourceFileViewHTMLGenerator:
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

        pygmented_source_file_lines: List[str] = []
        pygments_styles: str = ""

        if len(source_file_lines) > 0:
            coverage_info: SourceFileTraceabilityInfo = (
                traceability_index.get_coverage_info(
                    source_file.in_doctree_source_file_rel_path_posix
                )
            )
            (
                pygmented_source_file_lines,
                pygments_styles,
            ) = SourceFileViewHTMLGenerator.get_pygmented_source_lines(
                source_file, source_file_lines, coverage_info
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
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            source_file=source_file,
            pygments_styles=pygments_styles,
            pygmented_source_file_lines=pygmented_source_file_lines,
        )
        return view_object.render_screen(html_templates.jinja_environment())

    @staticmethod
    def get_pygmented_source_lines(
        source_file: SourceFile,
        source_file_lines: List[str],
        coverage_info: SourceFileTraceabilityInfo,
    ):
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
        assert pygmented_source_file_content.endswith(
            end_pattern
        ), f"{pygmented_source_file_content}"

        slice_start = len(start_pattern)
        slice_end = len(pygmented_source_file_content) - len(end_pattern)
        pygmented_source_file_content = pygmented_source_file_content[
            slice_start:slice_end
        ]
        pygmented_source_file_lines = pygmented_source_file_content.split("\n")
        if hack_first_line:
            pygmented_source_file_lines[0] = "<span></span>"

        if pygmented_source_file_lines[-1] == "":
            pygmented_source_file_lines.pop()
        assert (
            "###" in pygmented_source_file_lines[-1]
        ), "Expected marker to be in place."
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

        for pragma in coverage_info.pragmas:
            pragma_line = pragma.ng_source_line_begin
            if isinstance(pragma, ForwardRangeMarker):
                pygmented_source_file_lines[pragma_line - 1] = (
                    pygmented_source_file_lines[pragma_line - 1].rstrip("\n")
                    + " ",
                    "\n",
                    pragma,
                )
                continue

            source_line = source_file_lines[pragma_line - 1]

            assert len(pragma.reqs_objs) > 0
            before_line = source_line[
                : pragma.reqs_objs[0].ng_source_column - 1
            ].rstrip("/")
            closing_bracket_index = (
                source_line.index("]")
                if isinstance(pragma, RangeMarker)
                else source_line.index(")")
                if isinstance(pragma, LineMarker)
                else None
            )
            assert closing_bracket_index is not None
            after_line = source_line[closing_bracket_index:].rstrip()

            before_line = html.escape(before_line)
            after_line = html.escape(after_line)

            pygmented_source_file_lines[pragma_line - 1] = (
                before_line,
                after_line,
                pragma,
            )
        pygments_styles = (
            f"/* Lexer: {lexer.name} */\n"
            + html_formatter.get_style_defs(".highlight")
        )

        return pygmented_source_file_lines, pygments_styles
