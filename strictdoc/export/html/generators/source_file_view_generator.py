from jinja2 import Environment, PackageLoader
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.python import PythonLexer

from strictdoc.core.finders.source_files_finder import SourceFile
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


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

        with open(source_file.in_cwd_source_file_rel_path) as f:
            source_file_lines = f.readlines()

        markup_renderer = MarkupRenderer()

        html_formatter = HtmlFormatter()
        pygmented_source_file_content = highlight(
            "".join(source_file_lines), PythonLexer(), html_formatter
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
