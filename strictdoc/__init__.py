import os

__version__ = "0.0.33"

STRICTDOC_ROOT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
assert os.path.isabs(STRICTDOC_ROOT_PATH), f"{STRICTDOC_ROOT_PATH}"
