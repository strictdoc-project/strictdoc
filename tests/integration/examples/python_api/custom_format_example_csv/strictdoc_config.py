import os
import sys

# Make the sibling csv_format.py importable: strictdoc loads this config
# file directly by path (not as a package), so the directory containing it
# is not automatically added to sys.path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from csv_format import CSVFormat  # noqa: E402

from strictdoc.core.project_config import ProjectConfig  # noqa: E402


def create_config() -> ProjectConfig:
    return ProjectConfig(
        formats=[*ProjectConfig.default_formats(), CSVFormat()]
    )
