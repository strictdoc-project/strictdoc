import os
from dataclasses import dataclass
from typing import List, Tuple, Union

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.core.feature import Feature
from strictdoc.core.project_config import (
    DEPRECATED_FEATURES,
    ProjectConfig,
    ProjectConfigDefault,
    ProjectFeature,
)
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer

# NESTOR is hidden because the feature is still very immature. The deprecated
# features are always enabled and no longer need to be listed in
# project_features.
_HIDDEN_OR_DEPRECATED_PROJECT_FEATURES: List[str] = [
    ProjectFeature.NESTOR,
    *DEPRECATED_FEATURES,
]


def _feature_handle(feature: Union[str, Feature]) -> str:
    if isinstance(feature, Feature):
        return feature.HANDLE
    if isinstance(feature, ProjectFeature):
        return feature.value
    return feature


@dataclass
class ProjectConfigurationViewObject:
    project_config: ProjectConfig
    link_renderer: LinkRenderer
    jinja_environment: JinjaEnvironment

    def __post_init__(self) -> None:
        self.strictdoc_version = __version__

    def get_document_level(self) -> int:
        return 0

    def default_lazy_document_loading_threshold(self) -> int:
        return ProjectConfigDefault.DEFAULT_LAZY_DOCUMENT_LOADING_THRESHOLD

    def project_features_display(self) -> Markup:
        active_features = [
            _feature_handle(feature_)
            for feature_ in self.project_config.project_features
            if _feature_handle(feature_)
            not in _HIDDEN_OR_DEPRECATED_PROJECT_FEATURES
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

    def render_screen(self) -> Markup:
        return self.jinja_environment.render_template_as_markup(
            "features/project_configuration/index.jinja", view_object=self
        )

    def render_path(self, path: str, testid: str) -> Markup:
        external_path, internal_path = self.split_path_for_display(path)
        return self.jinja_environment.render_template_as_markup(
            "features/project_configuration/path.jinja",
            external_path=external_path,
            internal_path=internal_path,
            testid=testid,
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
        # Only an absolute path can disclose the user's directory layout.
        if not os.path.isabs(path):
            return "", path

        project_root_path = self.project_config.get_project_root_path()
        external_prefix = os.path.dirname(project_root_path)
        if external_prefix and path.startswith(external_prefix):
            return external_prefix, path[len(external_prefix) :]

        fallback_prefix = os.path.dirname(path)
        if fallback_prefix and fallback_prefix != path:
            return fallback_prefix, path[len(fallback_prefix) :]
        return "", path
