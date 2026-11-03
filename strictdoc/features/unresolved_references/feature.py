from strictdoc.core.feature import Feature, FeatureContext
from strictdoc.features.unresolved_references.screen import (
    render_unresolved_references_screen,
)


class UnresolvedReferencesFeature(Feature):
    ALWAYS_EXPORT: bool = True
    HANDLE: str = "UNRESOLVED_REFERENCES_SCREEN"

    @staticmethod
    def supports_export() -> bool:
        return True

    def export(self, context: FeatureContext) -> None:
        render_unresolved_references_screen(context)

    @staticmethod
    def supports_server() -> bool:
        return True

    def screen_filename(self) -> str:
        return "unresolved_references.html"

    def render_screen(self, context: FeatureContext) -> None:
        render_unresolved_references_screen(context)

    def screen_icon(self) -> str:
        return "features/unresolved_references/icon.svg"
