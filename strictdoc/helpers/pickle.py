import pickle
from typing import Any


def pickle_dump(obj) -> bytes:
    return pickle.dumps(obj, 0)


def pickle_load(content: bytes) -> Any:
    return pickle.loads(content)
