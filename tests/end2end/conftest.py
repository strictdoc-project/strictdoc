import os
import sys

from tests.end2end.sdoc_test_environment import SDocTestEnvironment

STRICTDOC_PATH = os.path.abspath(os.path.join(__file__, "../../.."))
assert os.path.exists(STRICTDOC_PATH), f"does not exist: {STRICTDOC_PATH}"
sys.path.append(STRICTDOC_PATH)

DOWNLOADED_FILES_PATH = os.path.join(STRICTDOC_PATH, "downloaded_files")


test_environment = SDocTestEnvironment(
    is_parallel_execution="STRICTDOC_PARALLELIZE" in os.environ
)
