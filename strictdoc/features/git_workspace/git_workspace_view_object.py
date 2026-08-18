from typing import Optional

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.git_workspace.git_status_service import (
    GitWorkspaceStatus,
)


class GitWorkspaceViewObject:
    def __init__(
        self,
        *,
        project_config: ProjectConfig,
        status: GitWorkspaceStatus,
        target_branch: str,
        message: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        self.project_config: ProjectConfig = project_config
        self.status: GitWorkspaceStatus = status
        self.target_branch: str = target_branch
        self.message: Optional[str] = message
        self.error_message: Optional[str] = error_message

        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        self.link_renderer: LinkRenderer = link_renderer
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

    def get_document_level(self) -> int:
        return 0

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "features/git_workspace/index.jinja", view_object=self
        )

    def render_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_url(url))

    def render_static_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_static_url(url))

    def render_static_url_with_prefix(self, url: str) -> str:
        return self.link_renderer.render_static_url_with_prefix(url)
