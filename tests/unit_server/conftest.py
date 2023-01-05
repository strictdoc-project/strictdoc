import os
import sys

STRICTDOC_ROOT_PATH = os.path.abspath(os.path.join(__file__, "../../.."))
assert os.path.exists(
    STRICTDOC_ROOT_PATH
), f"does not exist: {STRICTDOC_ROOT_PATH}"
sys.path.append(STRICTDOC_ROOT_PATH)
