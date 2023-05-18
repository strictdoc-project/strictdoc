from strictdoc import __version__
from strictdoc.cli.cli_arg_parser import ExportCommandConfig
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


class SourceFileCoverageHTMLGenerator:
    env = HTMLTemplates.jinja_environment

    @staticmethod
    def export(
        *,
        config: ExportCommandConfig,
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
    ):
        output = ""

        template = SourceFileCoverageHTMLGenerator.env.get_template(
            "screens/source_file_coverage/index.jinja"
        )
        link_renderer = LinkRenderer(
            root_path="", static_path=config.dir_for_sdoc_assets
        )
        output += template.render(
            config=config,
            project_config=project_config,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
            strictdoc_version=__version__,
        )

        return output
