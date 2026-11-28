"""
The public Python API of StrictDoc.

A project config (strictdoc_config.py), a custom statistics generator, or a
plugin imports this module. Every export loads the project config, so this
module imports the Excel export and the project statistics only on first
access, through __getattr__() below. The Excel export imports xlsxwriter.
"""

from typing import TYPE_CHECKING, Any

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.grammar_element import GrammarElement
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.constants import GraphLinkType
from strictdoc.core.document_iterator import SDocDocumentIterator
from strictdoc.core.graph.abstract_bucket import ALL_EDGES
from strictdoc.core.plugin import StrictDocPlugin
from strictdoc.core.project_config import (
    ProjectConfig,
    ProjectConfigLoader,
    ProjectFeature,
    SourceNodesEntry,
)
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.git_client import GitClient
from strictdoc.helpers.mid import MID
from strictdoc.helpers.parallelizer import Parallelizer

if TYPE_CHECKING:
    from strictdoc.backend.excel.export.excel_generator import ExcelGenerator
    from strictdoc.features.project_statistics.metric import (
        Metric,
        MetricSection,
    )
    from strictdoc.features.project_statistics.view_object import (
        ProjectStatisticsViewObject,
    )

__all__ = [
    "ALL_EDGES",
    "MID",
    "DocumentTreeError",
    "ExcelGenerator",
    "GitClient",
    "GrammarElement",
    "GraphLinkType",
    "HTMLTemplates",
    "LinkRenderer",
    "Metric",
    "MetricSection",
    "GraphLinkType",
    "HTMLTemplates",
    "LinkRenderer",
    "Metric",
    "MetricSection",
    "Parallelizer",
    "ProjectConfig",
    "ProjectConfigLoader",
    "ProjectFeature",
    "ProjectStatisticsViewObject",
    "SDocDocument",
    "SDocDocumentIterator",
    "SDocNode",
    "SourceFileTraceabilityInfo",
    "SDocDocument",
    "SDocDocumentIterator",
    "SDocNode",
    "SourceFileTraceabilityInfo",
    "SourceNodesEntry",
    "StrictDocPlugin",
    "TraceabilityIndex",
    "TraceabilityIndexBuilder",
    "assert_cast",
]


def __getattr__(name: str) -> Any:
    """
    Import the names that are not imported above on first access (PEP 562).

    The imports are written out, not built with importlib, so that PyInstaller
    finds these modules (see tasks.py).
    """
    value: Any
    if name == "ExcelGenerator":
        from strictdoc.backend.excel.export.excel_generator import (  # noqa: PLC0415
            ExcelGenerator,
        )

        value = ExcelGenerator
    elif name in ("Metric", "MetricSection"):
        from strictdoc.features.project_statistics import (  # noqa: PLC0415
            metric,
        )

        value = getattr(metric, name)
    elif name == "ProjectStatisticsViewObject":
        from strictdoc.features.project_statistics.view_object import (  # noqa: PLC0415
            ProjectStatisticsViewObject,
        )

        value = ProjectStatisticsViewObject
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    globals()[name] = value
    return value
