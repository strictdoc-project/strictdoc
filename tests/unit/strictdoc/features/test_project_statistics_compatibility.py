import importlib
import sys
from types import ModuleType

from pytest import CaptureFixture

from strictdoc.features.project_statistics.generator import (
    ProgressStatisticsGenerator,
)
from strictdoc.features.project_statistics.metric import Metric, MetricSection
from strictdoc.features.project_statistics.models.project_tree_stats import (
    DocumentStats,
    DocumentTreeStats,
)
from strictdoc.features.project_statistics.view_object import (
    ProjectStatisticsViewObject,
)
from strictdoc.helpers.deprecation_engine import DEPRECATION_ENGINE


def import_deprecated_module(module_name: str) -> ModuleType:
    sys.modules.pop(module_name, None)
    DEPRECATION_ENGINE.deprecations.pop(module_name, None)
    return importlib.import_module(module_name)


def forget_deprecation(module_name: str) -> None:
    DEPRECATION_ENGINE.deprecations.pop(module_name, None)


def test_deprecated_metric_module(capsys: CaptureFixture[str]) -> None:
    module_name = "strictdoc.core.statistics.metric"
    module = import_deprecated_module(module_name)

    assert module.Metric is Metric
    assert module.MetricSection is MetricSection
    captured = capsys.readouterr()
    assert "'strictdoc.core.statistics.metric' is deprecated" in captured.out
    assert "'strictdoc.features.project_statistics.metric'" in captured.out
    forget_deprecation(module_name)


def test_deprecated_project_statistics_view_object_module(
    capsys: CaptureFixture[str],
) -> None:
    module_name = (
        "strictdoc.export.html.generators.view_objects."
        "project_statistics_view_object"
    )
    module = import_deprecated_module(module_name)

    assert module.ProjectStatisticsViewObject is ProjectStatisticsViewObject
    captured = capsys.readouterr()
    assert "project_statistics_view_object' is deprecated" in captured.out
    assert "'strictdoc.features.project_statistics.view_object'" in captured.out
    forget_deprecation(module_name)


def test_deprecated_project_tree_stats_module(
    capsys: CaptureFixture[str],
) -> None:
    module_name = (
        "strictdoc.export.html.generators.view_objects.project_tree_stats"
    )
    module = import_deprecated_module(module_name)

    assert module.DocumentStats is DocumentStats
    assert module.DocumentTreeStats is DocumentTreeStats
    captured = capsys.readouterr()
    assert "project_tree_stats' is deprecated" in captured.out
    assert (
        "'strictdoc.features.project_statistics.models.project_tree_stats'"
        in captured.out
    )
    forget_deprecation(module_name)


def test_deprecated_project_statistics_generator_module(
    capsys: CaptureFixture[str],
) -> None:
    module_name = "strictdoc.export.html.generators.project_statistics"
    module = import_deprecated_module(module_name)

    assert module.ProgressStatisticsGenerator is ProgressStatisticsGenerator
    captured = capsys.readouterr()
    assert (
        "'strictdoc.export.html.generators.project_statistics' is deprecated"
        in captured.out
    )
    assert "'strictdoc.features.project_statistics.generator'" in captured.out
    forget_deprecation(module_name)
