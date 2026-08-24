from strictdoc.core.feature import Feature, FeatureContext
from strictdoc.features.tree_map_html.screen import render_tree_map_html_screen


class TreeMapHTMLFeature(Feature):
    HANDLE = "TREE_MAP_HTML_SCREEN"

    @staticmethod
    def supports_export() -> bool:
        return True

    def export(self, context: FeatureContext) -> None:
        render_tree_map_html_screen(
            project_config=context.project_config,
            traceability_index=context.traceability_index,
            html_templates=context.html_templates,
        )

    @staticmethod
    def supports_server() -> bool:
        return True

    def screen_filename(self) -> str:
        return "tree_map_html.html"

    def render_screen(self, context: FeatureContext) -> None:
        render_tree_map_html_screen(
            project_config=context.project_config,
            traceability_index=context.traceability_index,
            html_templates=context.html_templates,
        )

    def screen_icon(self) -> str:
        return "icons/ico16_requirement.svg"
