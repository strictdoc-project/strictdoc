import os
import sys

from strictdoc.core.project_config import ProjectConfig

sys.path.append(os.path.dirname(__file__))

from user_plugin import UserPlugin


def create_config() -> ProjectConfig:
    config = ProjectConfig(
        project_title="StrictDoc Documentation",
        user_plugin=UserPlugin()
    )
    return config
