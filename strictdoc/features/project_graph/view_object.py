import json
from typing import Any, Dict

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


class ProjectGraphViewObject:
    def __init__(
        self,
        *,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
        graph_data: Dict[str, Any],
    ) -> None:
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.link_renderer: LinkRenderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

        # Escape "</" so the JSON payload cannot prematurely close the
        # surrounding <script> tag it gets embedded into.
        self.graph_data_json: Markup = Markup(
            json.dumps(graph_data).replace("</", "<\\/")
        )

    def get_document_level(self) -> int:
        return 0

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "features/project_graph/index.jinja", view_object=self
        )

    def render_static_url(self, url: str) -> str:
        return self.link_renderer.render_static_url(url)

    def render_url(self, url: str) -> str:
        # FIXME: Switch to Markup(...).
        return self.link_renderer.render_url(url)
