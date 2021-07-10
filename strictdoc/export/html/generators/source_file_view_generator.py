from jinja2 import Environment, PackageLoader
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.c_cpp import CppLexer, CLexer
from pygments.lexers.python import PythonLexer

from strictdoc.core.finders.source_files_finder import SourceFile
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.helpers.string import multireplace


class SourceFileViewHTMLGenerator:
    env = Environment(
        loader=PackageLoader("strictdoc", "export/html/templates")
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(
        source_file: SourceFile,
        document_tree,
        traceability_index: TraceabilityIndex,
        link_renderer,
    ):
        output = ""

        template = SourceFileViewHTMLGenerator.env.get_template(
            "source_file_view/source_file_view.jinja.html"
        )

        with open(source_file.full_path) as f:
            source_file_lines = f.readlines()

        markup_renderer = MarkupRenderer()

        lexer = None
        if source_file.is_python_file():
            lexer = PythonLexer()
        elif source_file.is_c_file():
            lexer = CLexer()
        elif source_file.is_cpp_file():
            lexer = CppLexer()
        else:
            assert NotImplementedError

        html_formatter = HtmlFormatter()
        pygmented_source_file_content = highlight(
            "".join(source_file_lines), lexer, html_formatter
        )

        # Ugly hack to split content into lines: Cutting off:
        # <div class="highlight"><pre> and </pre></div>
        # TODO: Implement proper splitting.
        assert pygmented_source_file_content.startswith(
            '<div class="highlight"><pre>'
        )
        assert pygmented_source_file_content.endswith(
            "</pre></div>\n"
        ), f"{pygmented_source_file_content}"
        pygmented_source_file_content = pygmented_source_file_content[
            28 : len(pygmented_source_file_content) - 13
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
            replacements = {}
            for req in pragma.reqs:
                replacements[req] = f'<span class="TODO-CSS">{req}</span>'
            replacement_line = multireplace(source_line, replacements)
            pygmented_source_file_lines[pragma_line - 1] = replacement_line

        pygments_styles = html_formatter.get_style_defs(".highlight")
        output += template.render(
            source_file=source_file,
            source_file_lines=source_file_lines,
            pygments_styles=pygments_styles,
            source_file_content=pygmented_source_file_lines,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
            renderer=markup_renderer,
            document_type=DocumentType.document(),
        )
        return output
