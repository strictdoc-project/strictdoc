from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.c_cpp import CppLexer, CLexer
from pygments.lexers.markup import TexLexer
from pygments.lexers.python import PythonLexer

from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.finders.source_files_finder import SourceFile
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.export.html.html_templates import HTMLTemplates


class SourceFileViewHTMLGenerator:
    env = HTMLTemplates.jinja_environment

    @staticmethod
    def export(
        config: ExportCommandConfig,
        source_file: SourceFile,
        traceability_index: TraceabilityIndex,
        link_renderer,
    ):
        output = ""

        document_type = DocumentType.document()
        template = SourceFileViewHTMLGenerator.env.get_template(
            "source_file_view/source_file_view.jinja.html"
        )

        with open(source_file.full_path, encoding="utf-8") as opened_file:
            source_file_lines = opened_file.readlines()

        markup_renderer = MarkupRenderer.create(
            "RST", traceability_index, link_renderer, None
        )

        lexer = None
        if source_file.is_python_file():
            lexer = PythonLexer()
        elif source_file.is_c_file():
            lexer = CLexer()
        elif source_file.is_cpp_file():
            lexer = CppLexer()
        elif source_file.is_tex_file():
            lexer = TexLexer()
        else:
            raise NotImplementedError

        html_formatter = HtmlFormatter()
        pygmented_source_file_content = highlight(
            "".join(source_file_lines), lexer, html_formatter
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
        if pygmented_source_file_lines[-1] == "":
            pygmented_source_file_lines.pop()

        coverage_info = traceability_index.get_coverage_info(
            source_file.in_doctree_source_file_rel_path
        )

        for pragma in coverage_info.pragmas:
            pragma_line = pragma.ng_source_line_begin
            source_line = source_file_lines[pragma_line - 1]
            if len(pragma.reqs_objs):
                replacement_line = source_line[
                    : pragma.reqs_objs[0].ng_source_column - 1
                ]
                replacement_line = (
                    replacement_line.rstrip("/").rstrip("[").rstrip()
                )
            pygmented_source_file_lines[pragma_line - 1] = (
                replacement_line,
                "",
                pragma,
            )

        pygments_styles = html_formatter.get_style_defs(".highlight")

        root_path = source_file.path_depth_prefix
        static_path = f"{root_path}/_static"

        output += template.render(
            config=config,
            source_file=source_file,
            source_file_lines=source_file_lines,
            pygments_styles=pygments_styles,
            source_file_content=pygmented_source_file_lines,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
            renderer=markup_renderer,
            document_type=document_type,
            root_path=root_path,
            static_path=static_path,
        )
        return output
