import importlib.util
import sys
import types
from pathlib import Path
from typing import Union


def import_from_path(path: Union[str, Path]) -> types.ModuleType:
    path = Path(path)
    module_name = path.stem
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
