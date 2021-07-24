from jinja2 import Environment, PackageLoader, StrictUndefined

from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


class SourceFileCoverageHTMLGenerator:
    env = Environment(
        loader=PackageLoader("strictdoc", "export/html/templates"),
        undefined=StrictUndefined,
    )
    env.globals.update(isinstance=isinstance)

    @staticmethod
    def export(
        config: ExportCommandConfig,
        document_tree,
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
    ):
        output = ""

        template = SourceFileCoverageHTMLGenerator.env.get_template(
            "source_file_coverage/source_file_coverage.jinja.html"
        )

        output += template.render(
            config=config,
            document_tree=document_tree,
            traceability_index=traceability_index,
            static_path="_static",
            link_renderer=link_renderer,
        )

        return output
