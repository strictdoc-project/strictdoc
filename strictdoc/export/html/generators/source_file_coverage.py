from jinja2 import Environment, PackageLoader, StrictUndefined

from strictdoc.core.traceability_index import TraceabilityIndex


class SourceFileCoverageHTMLGenerator:
    env = Environment(
        loader=PackageLoader("strictdoc", "export/html/templates"),
        undefined=StrictUndefined,
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

        output += template.render(
            document_tree=document_tree,
            traceability_index=traceability_index,
            static_path="_static",
        )

        return output
