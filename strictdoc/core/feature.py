"""
The Feature abstraction: facade for cross-cutting export/server
capabilities that are not document-content conversion (see Format for
that).

@relation(SDOC-SRS-119, scope=file)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from strictdoc.core.project_config import ProjectConfig
    from strictdoc.core.traceability_index import TraceabilityIndex
    from strictdoc.export.html.html_templates import HTMLTemplates


@dataclass
class FeatureContext:
    """
    Shared, per-call state that Feature.export()/render_screen()
    implementations pull from. Deliberately separate from Format's
    ExportContext: it carries only what a Feature actually needs
    (project_config/traceability_index/html_templates), not
    Format-specific fields like parallelizer or the HTML2PDF-only
    bundle_* fields.
    """

    project_config: "ProjectConfig"
    traceability_index: "TraceabilityIndex"
    html_templates: "HTMLTemplates"


class Feature(ABC):
    HANDLE: str
    """
    Reuses the existing ProjectFeature enum value string verbatim (e.g.
    "PROJECT_STATISTICS_SCREEN"), so string-based project_features=[...]
    entries keep resolving to this Feature unchanged.
    """

    @staticmethod
    @abstractmethod
    def supports_export() -> bool:
        raise NotImplementedError

    def export(self, context: FeatureContext) -> None:
        """Only called if supports_export() is True."""
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support export."
        )

    @staticmethod
    @abstractmethod
    def supports_server() -> bool:
        raise NotImplementedError

    def screen_filename(self) -> str:
        """
        Only called if supports_server() is True. The
        document_relative_path.relative_path value (e.g.
        "project_statistics.html") this Feature's screen owns, used as the
        dispatch key inside main_router.py's generate_document(). Not a
        FastAPI route: every HTML screen is served through one shared,
        cached, lock-protected route, and this filename is only the
        dispatch key into that shared machinery.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support a server screen."
        )

    def render_screen(self, context: FeatureContext) -> None:
        """
        Only called if supports_server() is True. Must write the screen's
        HTML file to context.project_config.export_output_html_root, the
        same contract every generate_document() branch already follows.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support a server screen."
        )

    def screen_icon(self) -> str:
        """
        Jinja template path for the left-sidebar nav icon, rendered via
        `{% include feature.screen_icon() %}`, e.g.
        "features/project_statistics/ico16_stat.svg".

        Resolved against the Jinja template search path, which is the
        static HTML_TEMPLATE_DIRS list in strictdoc/core/environment.py --
        the same mechanism every other feature's own .jinja templates
        already rely on. A built-in Feature's icon lives under its own
        feature's existing "features/<feature>/*.jinja" namespace inside
        its "<feature>/templates" entry (e.g.
        strictdoc/features/project_statistics/templates/features/
        project_statistics/ico16_stat.svg, alongside that feature's own
        main.jinja/index.jinja) -- no separate registration needed.

        TODO: a second method returning raw markup directly (for Features
        that can't register an entry in HTML_TEMPLATE_DIRS, e.g. a custom
        Feature defined outside strictdoc's own package) is a likely
        future addition, not implemented yet.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not provide a nav icon."
        )
