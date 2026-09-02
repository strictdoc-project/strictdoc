from strictdoc.core.project_config import ProjectConfig
from strictdoc.features.eurobot_test_dashboard.feature import (
    EurobotTestDashboardFeature,
)


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="Test project",
        project_features=[EurobotTestDashboardFeature()],
    )
    return config
