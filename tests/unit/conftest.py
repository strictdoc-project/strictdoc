import os
import sys

import pytest

from strictdoc.core.environment import SDocRuntimeEnvironment
from strictdoc.core.project_config import ProjectConfig

strictdoc_root_path = os.path.abspath(os.path.join(__file__, "../../.."))
assert os.path.exists(
    strictdoc_root_path
), f"does not exist: {strictdoc_root_path}"
sys.path.append(strictdoc_root_path)


@pytest.fixture
def default_project_config():
    return ProjectConfig.default_config(
        SDocRuntimeEnvironment(strictdoc_root_path)
    )
