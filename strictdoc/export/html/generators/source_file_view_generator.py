import html

from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.c_cpp import CLexer, CppLexer
from pygments.lexers.markup import TexLexer
from pygments.lexers.python import PythonLexer
from pygments.lexers.templates import HtmlDjangoLexer

from strictdoc import __version__
from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.finders.source_files_finder import SourceFile
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


class SourceFileViewHTMLGenerator:
    env = HTMLTemplates.jinja_environment

    @staticmethod
    def export(
        *,
        config: ExportCommandConfig,
        project_config: ProjectConfig,
        source_file: SourceFile,
        traceability_index: TraceabilityIndex,
    ):
        output = ""

        document_type = DocumentType.document()
        template = SourceFileViewHTMLGenerator.env.get_template(
            "screens/source_file_view/index.jinja"
        )

        with open(source_file.full_path, encoding="utf-8") as opened_file:
            source_file_lines = opened_file.readlines()

        if source_file.is_python_file():
            lexer = PythonLexer()
        elif source_file.is_c_file():
            lexer = CLexer()
        elif source_file.is_cpp_file():
            lexer = CppLexer()
        elif source_file.is_tex_file():
            lexer = TexLexer()
        elif source_file.is_jinja_file():
            lexer = HtmlDjangoLexer()
        else:
            raise NotImplementedError(source_file)

        # HACK.
        # Otherwise, Pygments will skip the first line as if it does not exist.
        # This behavior surprisingly affects on the first line if its empty.
        hack_first_line: bool = False
        if source_file_lines[0] == "\n":
            source_file_lines[0] = " \n"
            hack_first_line = True

        source_file_content = "".join(source_file_lines)

        html_formatter = HtmlFormatter()
        pygmented_source_file_content = highlight(
            source_file_content, lexer, html_formatter
        )

        # Ugly hack to split content into lines: Cutting off:
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
        assert len(pygmented_source_file_lines) == len(source_file_lines), (
            f"Something went wrong when running Pygments against "
            f"the source file: "
            f"{len(pygmented_source_file_lines)} == {len(source_file_lines)}"
        )

        coverage_info = traceability_index.get_coverage_info(
            source_file.in_doctree_source_file_rel_path_posix
        )
        for pragma in coverage_info.pragmas:
            pragma_line = pragma.ng_source_line_begin
            source_line = source_file_lines[pragma_line - 1]
            assert len(pragma.reqs_objs) > 0
            before_line = source_line[
                : pragma.reqs_objs[0].ng_source_column - 1
            ].rstrip("/")
            closing_bracket_index = source_line.index("]")
            after_line = source_line[closing_bracket_index:].rstrip()

            before_line = html.escape(before_line)
            after_line = html.escape(after_line)

            pygmented_source_file_lines[pragma_line - 1] = (
                before_line,
                after_line,
                pragma,
            )
        pygments_styles = html_formatter.get_style_defs(".highlight")

        link_renderer = LinkRenderer(
            root_path=source_file.path_depth_prefix,
            static_path=config.dir_for_sdoc_assets,
        )
        markup_renderer = MarkupRenderer.create(
            "RST", traceability_index, link_renderer, None
        )
        output += template.render(
            config=config,
            project_config=project_config,
            source_file=source_file,
            source_file_lines=source_file_lines,
            pygments_styles=pygments_styles,
            source_file_content=pygmented_source_file_lines,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
            renderer=markup_renderer,
            document_type=document_type,
            strictdoc_version=__version__,
        )
        return output
