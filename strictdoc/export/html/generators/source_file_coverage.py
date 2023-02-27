from strictdoc import __version__
from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


class SourceFileCoverageHTMLGenerator:
    env = HTMLTemplates.jinja_environment

    @staticmethod
    def export(
        config: ExportCommandConfig,
        traceability_index: TraceabilityIndex,
    ):
        output = ""

        template = SourceFileCoverageHTMLGenerator.env.get_template(
            "source_file_coverage/source_file_coverage.jinja.html"
        )
        link_renderer = LinkRenderer(root_path="")
        output += template.render(
            config=config,
            traceability_index=traceability_index,
            static_path="_static",
            link_renderer=link_renderer,
            strictdoc_version=__version__,
        )

        return output
