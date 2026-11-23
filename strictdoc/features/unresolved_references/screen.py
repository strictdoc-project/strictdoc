import os

from markupsafe import Markup

from strictdoc.core.feature import FeatureContext
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.unresolved_references.view_object import (
    UnresolvedReferencesViewObject,
)


def render_unresolved_references_screen(context: FeatureContext) -> None:
    view_object: UnresolvedReferencesViewObject = (
        UnresolvedReferencesViewObject(
            project_config=context.project_config,
            traceability_index=context.traceability_index,
            link_renderer=LinkRenderer(
                root_path="",
                static_path=context.project_config.dir_for_sdoc_assets,
            ),
        )
    )
    document_content: Markup = view_object.render_screen(
        context.html_templates.jinja_environment()
    )
    output_path: str = os.path.join(
        context.project_config.export_output_html_root,
        "unresolved_references.html",
    )
    with open(output_path, "w", encoding="utf8") as output_file:
        output_file.write(document_content)
