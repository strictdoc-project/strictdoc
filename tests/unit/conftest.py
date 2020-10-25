import os
import sys

saturn_path = os.path.abspath(os.path.join(__file__, "../../../../saturn"))
assert os.path.exists(saturn_path), "does not exist: {}".format(saturn_path)
sys.path.append(saturn_path)
