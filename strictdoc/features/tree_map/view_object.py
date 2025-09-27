"""
@relation(SDOC-SRS-157, scope=file)
"""

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.tree_map.plotly_js import PLOTLY_JS_EXTENSION


class TreeMapViewObject:
    def __init__(
        self,
        *,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
        body: str,
    ) -> None:
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.body: Markup = Markup(body)
        self.link_renderer: LinkRenderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        self.standalone: bool = False
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

        self.plotly_js_extension: Markup = PLOTLY_JS_EXTENSION

    def get_document_level(self) -> int:
        return 0

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "screens/tree_map/index.jinja", view_object=self
        )

    def render_static_url(self, url: str) -> str:
        return self.link_renderer.render_static_url(url)

    def render_url(self, url: str) -> str:
        # FIXME: Switch to Markup(...).
        return self.link_renderer.render_url(url)
