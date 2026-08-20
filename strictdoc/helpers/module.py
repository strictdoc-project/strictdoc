import importlib.util
import sys
import types
from pathlib import Path
from typing import Union


def import_from_path(path: Union[str, Path]) -> types.ModuleType:
    path = Path(path)
    module_name = path.stem

    # Put the module on a real, importable path rather than only inside
    # this process' sys.modules. multiprocessing's "spawn"/"forkserver"
    # start methods (spawn is the only one available on Windows) re-create
    # worker processes with a copy of the parent's sys.path, so a plain
    # "import <module_name>" in the worker - which is exactly what pickle
    # does to resolve a function object defined in this module - can find
    # and load the same file. Without this, functions from a project's
    # strictdoc_config.py (e.g. a custom_node_prefix_function/
    # custom_node_uid_function hook) fail to unpickle in worker processes.
    #
    # Inserted at the front, not appended: some other, unrelated
    # strictdoc_config.py may already be reachable earlier on sys.path (for
    # example, StrictDoc's own integration test harness sets PYTHONPATH to
    # the repository root, which has its own strictdoc_config.py). Since
    # "strictdoc_config" is a fixed, StrictDoc-mandated filename, a same-name
    # collision with an unrelated real package is far less likely than a
    # collision with a *different* project's own config, so this file must
    # win the name lookup regardless of what else is already on sys.path.
    module_dir = str(path.parent.resolve())
    if module_dir in sys.path:
        sys.path.remove(module_dir)
    sys.path.insert(0, module_dir)

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
