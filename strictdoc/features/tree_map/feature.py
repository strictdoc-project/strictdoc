from strictdoc.core.feature import Feature, FeatureContext

# The methods below import the screen code on first use, so that a project
# without this feature does not load it.


class TreeMapFeature(Feature):
    HANDLE = "TREE_MAP_SCREEN"

    @staticmethod
    def supports_export() -> bool:
        return True

    def export(self, context: FeatureContext) -> None:
        from strictdoc.features.tree_map.screen import (  # noqa: PLC0415
            render_tree_map_screen,
        )

        render_tree_map_screen(
            project_config=context.project_config,
            traceability_index=context.traceability_index,
            html_templates=context.html_templates,
        )

    @staticmethod
    def supports_server() -> bool:
        return True

    def screen_filename(self) -> str:
        return "tree_map.html"

    def render_screen(self, context: FeatureContext) -> None:
        from strictdoc.features.tree_map.screen import (  # noqa: PLC0415
            render_tree_map_screen,
        )

        render_tree_map_screen(
            project_config=context.project_config,
            traceability_index=context.traceability_index,
            html_templates=context.html_templates,
        )

    def screen_icon(self) -> str:
        return "features/tree_map/ico16_tree_map.svg"
