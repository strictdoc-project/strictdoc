import os
from dataclasses import dataclass
from typing import Optional, Tuple

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.core.project_config import ProjectConfig, ProjectConfigDefault
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.server.project_settings import ProjectSettingsManager


@dataclass
class ProjectConfigurationViewObject:
    project_config: ProjectConfig
    link_renderer: LinkRenderer

    def __post_init__(self) -> None:
        self.is_running_on_server = self.project_config.is_running_on_server
        self.strictdoc_version = __version__

    def get_document_level(self) -> int:
        return 0

    def default_lazy_document_loading_threshold(self) -> int:
        return ProjectConfigDefault.DEFAULT_LAZY_DOCUMENT_LOADING_THRESHOLD

    def project_settings_unavailable_message(self) -> Optional[str]:
        inspection = ProjectSettingsManager(self.project_config).inspect()
        if any(state_.editable for state_ in inspection.settings):
            return None
        if inspection.message is not None:
            return inspection.message
        return next(
            (
                state_.message
                for state_ in inspection.settings
                if state_.message is not None
            ),
            "StrictDoc cannot edit this setting.",
        )

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "features/project_configuration/index.jinja", view_object=self
        )

    def render_static_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_static_url(url))

    def render_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_url(url))

    def active_configuration_path(self) -> str:
        if self.project_config.config_path is not None:
            return self.project_config.config_path
        project_root_path = self.project_config.get_project_root_path()
        if not os.path.isdir(project_root_path):
            project_root_path = os.path.dirname(project_root_path)
        return os.path.join(
            project_root_path,
            "strictdoc_config.py",
        )

    def split_path_for_display(self, path: str) -> Tuple[str, str]:
        project_root_path = self.project_config.get_project_root_path()
        external_prefix = os.path.dirname(project_root_path)
        if external_prefix and path.startswith(external_prefix):
            return external_prefix, path[len(external_prefix) :]

        fallback_prefix = os.path.dirname(path)
        if fallback_prefix and fallback_prefix != path:
            return fallback_prefix, path[len(fallback_prefix) :]
        return "", path
