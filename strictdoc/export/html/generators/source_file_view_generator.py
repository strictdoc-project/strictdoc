from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.python import PythonLexer

from strictdoc.core.finders.source_files_finder import SourceFile
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType


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
        markup_renderer,
        link_renderer,
    ):
        output = ""

        template = SourceFileViewHTMLGenerator.env.get_template(
            "source_file_view/source_file_view.jinja.html"
        )

        with open(source_file.in_cwd_source_file_rel_path) as f:
            source_file_lines = f.readlines()

        html_formatter = HtmlFormatter()
        pygmented_source_file_content = highlight(
            "".join(source_file_lines), PythonLexer(), html_formatter
        )

        pygments_styles = html_formatter.get_style_defs(".highlight")
        output += template.render(
            source_file=source_file,
            source_file_lines=source_file_lines,
            pygments_styles=pygments_styles,
            source_file_content=pygmented_source_file_content,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
            renderer=markup_renderer,
            document_type=DocumentType.document(),
        )

        return output
