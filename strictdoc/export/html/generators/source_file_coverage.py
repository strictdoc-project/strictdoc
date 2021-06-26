from jinja2 import Environment, PackageLoader
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.python import PythonLexer

from strictdoc.core.finders.source_files_finder import SourceFile
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer


class SourceFileCoverageHTMLGenerator:
    env = Environment(
        loader=PackageLoader("strictdoc", "export/html/templates")
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(
        document_tree,
        traceability_index: TraceabilityIndex,
    ):
        output = ""

        template = SourceFileCoverageHTMLGenerator.env.get_template(
            "source_file_coverage/source_file_coverage.jinja.html"
        )

        output += template.render(document_tree=document_tree)

        return output
