from strictdoc.features.project_statistics.metric import Metric, MetricSection
from strictdoc.helpers.deprecation_engine import DEPRECATION_ENGINE

DEPRECATION_ENGINE.add_message(
    "strictdoc.core.statistics.metric",
    (
        "WARNING: Importing project statistics metrics from "
        "'strictdoc.core.statistics.metric' is deprecated. Use "
        "'strictdoc.features.project_statistics.metric' instead."
    ),
)

__all__ = ("Metric", "MetricSection")
