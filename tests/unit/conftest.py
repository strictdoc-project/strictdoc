import os
import sys

strictdoc_root_path = os.path.abspath(
    os.path.join(__file__, "../../../../strictdoc")
)
assert os.path.exists(strictdoc_root_path), "does not exist: {}".format(
    strictdoc_root_path
)
sys.path.append(strictdoc_root_path)
