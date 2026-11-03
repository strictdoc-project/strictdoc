import os
from dataclasses import dataclass
from typing import List, Optional, Tuple

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.core.project_config import (
    ProjectConfig,
    ProjectConfigDefault,
    ProjectFeature,
)
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer

# NESTOR is hidden because the feature is still very immature. MATHJAX,
# MERMAID, and SOURCE_FILE_LANGUAGE_PARSERS are deprecated: they are always
# enabled and no longer need to be listed in project_features.
_HIDDEN_OR_DEPRECATED_PROJECT_FEATURES = {
    ProjectFeature.NESTOR.value,
    ProjectFeature.MATHJAX.value,
    ProjectFeature.MERMAID.value,
    ProjectFeature.SOURCE_FILE_LANGUAGE_PARSERS.value,
}


def _visible_project_features() -> List[str]:
    return [
        feature_.value
        for feature_ in ProjectFeature
        if feature_ != ProjectFeature.ALL_FEATURES
        and feature_.value not in _HIDDEN_OR_DEPRECATED_PROJECT_FEATURES
    ]


@dataclass
class ProjectConfigurationViewObject:
    project_config: ProjectConfig
    link_renderer: LinkRenderer

    def __post_init__(self) -> None:
        self.strictdoc_version = __version__

    def get_document_level(self) -> int:
        return 0

    def default_lazy_document_loading_threshold(self) -> int:
        return ProjectConfigDefault.DEFAULT_LAZY_DOCUMENT_LOADING_THRESHOLD

    def display_or_none(self, value: Optional[str]) -> str:
        return value if value is not None and value != "" else "None"

    def project_features_display(self) -> Markup:
        active_features = [
            str(feature_)
            for feature_ in self.project_config.project_features
            if feature_ not in _HIDDEN_OR_DEPRECATED_PROJECT_FEATURES
        ]
        if "ALL_FEATURES" in active_features:
            remaining_features = [
                feature_
                for feature_ in active_features
                if feature_ != "ALL_FEATURES"
            ]
            remaining_text = (
                ", ".join(remaining_features) if remaining_features else "None"
            )
            return Markup(f"<b>ALL_FEATURES:</b><br/> {remaining_text}")
        return Markup(", ".join(active_features) if active_features else "None")

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
