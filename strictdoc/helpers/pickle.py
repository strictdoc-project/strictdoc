import pickle
from typing import Any, Optional


def pickle_dump(obj: Any) -> bytes:
    return pickle.dumps(obj, 0)


def pickle_load(content: bytes) -> Optional[Any]:
    try:
        return pickle.loads(content)
    except AttributeError:
        # Known issue: when SDoc schema, e.g., core classes, changes,
        # unpicking results in Exceptions. So far, only the AttributeError
        # was observed.
        return None
