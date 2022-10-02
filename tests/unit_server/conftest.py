import os
import sys

STRICTDOC_ROOT_PATH = os.path.abspath(
    os.path.join(__file__, "../../../../strictdoc")
)
assert os.path.exists(STRICTDOC_ROOT_PATH), "does not exist: {}".format(
    STRICTDOC_ROOT_PATH
)
sys.path.append(STRICTDOC_ROOT_PATH)
