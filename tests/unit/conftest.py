import os
import sys

strictdoc_root_path = os.path.abspath(os.path.join(__file__, "../../.."))
assert os.path.exists(
    strictdoc_root_path
), f"does not exist: {strictdoc_root_path}"
sys.path.append(strictdoc_root_path)
