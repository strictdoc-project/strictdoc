from markupsafe import Markup

from strictdoc.core.project_config import ProjectConfig
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.project_configuration.view_object import (
    ProjectConfigurationViewObject,
)


class ProjectConfigurationHTMLGenerator:
    @staticmethod
    def export(
        project_config: ProjectConfig,
        html_templates: HTMLTemplates,
    ) -> Markup:
        link_renderer = LinkRenderer(
            root_path="",
            static_path=project_config.dir_for_sdoc_assets,
        )
        view_object = ProjectConfigurationViewObject(
            project_config=project_config,
            link_renderer=link_renderer,
        )
        return view_object.render_screen(html_templates.jinja_environment())
