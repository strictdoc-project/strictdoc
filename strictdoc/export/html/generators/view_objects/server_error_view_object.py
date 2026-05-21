from strictdoc import __version__
from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


class ServerErrorViewObject:
    def __init__(
        self,
        *,
        project_config: ProjectConfig,
        error_code: int,
        path_type: str = "document",
    ):
        self.project_config: ProjectConfig = project_config
        self.error_code: int = error_code
        self.path_type: str = path_type

        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        self.link_renderer: LinkRenderer = link_renderer

        self.standalone: bool = False
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

    def get_document_level(self) -> int:
        return 0

    def get_error_title(self) -> str:
        if self.error_code == 404:
            if self.path_type == "asset":
                return "404 — File Not Found"
            return "404 — Page Not Found"
        if self.error_code == 500:
            return "500 — Internal Server Error"
        return f"{self.error_code} — Error"

    def get_error_text(self) -> str:
        if self.error_code == 404:
            if self.path_type == "asset":
                return "The requested file doesn't exist or has been moved."
            return (
                "The page you're looking for doesn't exist or has been moved."
            )
        if self.error_code == 500:
            return "An unexpected error occurred. Please try again."
        return "Something went wrong."

    def render_screen(self, jinja_environment: JinjaEnvironment) -> str:
        return jinja_environment.render_template_as_markup(
            "error/index.jinja", view_object=self
        )

    def render_static_url(self, url: str) -> str:
        return self.link_renderer.render_static_url_with_prefix(url)

    def render_url(self, url: str) -> str:
        return self.link_renderer.render_url(url)

    def render_static_url_with_prefix(self, url: str) -> str:
        return self.link_renderer.render_static_url_with_prefix(url)
