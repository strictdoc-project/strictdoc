import os
import sys

strictdoc_path = os.path.abspath(os.path.join(__file__, "../../../../strictdoc"))
assert os.path.exists(strictdoc_path), "does not exist: {}".format(strictdoc_path)
sys.path.append(strictdoc_path)
