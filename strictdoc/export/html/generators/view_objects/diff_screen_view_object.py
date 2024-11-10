# mypy: disable-error-code="no-any-return,no-untyped-call,no-untyped-def"
from dataclasses import dataclass
from datetime import datetime

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


@dataclass
class DiffScreenViewObject:
    def __init__(
        self,
        *,
        project_config: ProjectConfig,
        results: bool,
        left_revision: str,
        left_revision_urlencoded: str,
        right_revision: str,
        right_revision_urlencoded: str,
        error_message: str,
        tab: str,
    ):
        self.project_config: ProjectConfig = project_config
        self.results: bool = results
        self.left_revision: str = left_revision
        self.left_revision_urlencoded: str = left_revision_urlencoded
        self.right_revision: str = right_revision
        self.right_revision_urlencoded: str = right_revision_urlencoded
        self.error_message: str = error_message
        self.tab: str = tab

        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        self.link_renderer: LinkRenderer = link_renderer
        self.standalone: bool = False
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "screens/git/index.jinja", view_object=self
        )

    def render_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_url(url))

    def render_static_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_static_url(url))

    def render_static_url_with_prefix(self, url: str) -> str:
        return self.link_renderer.render_static_url_with_prefix(url)

    def date_today(self) -> str:
        return datetime.today().strftime("%Y-%m-%d")
