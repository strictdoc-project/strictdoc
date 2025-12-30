# pylint: disable=wrong-import-position
# flake8: noqa: E402

# Needed to ensure that multiprocessing.freeze_support() is called
# in a frozen application (see main() below).
import multiprocessing
import os
import sys
from typing import Any, Dict, Optional

strictdoc_root_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
assert os.path.isdir(strictdoc_root_path)
sys.path.append(strictdoc_root_path)

from strictdoc import environment
from strictdoc.cli.cli_arg_parser import (
    SDocArgsParser,
)
from strictdoc.commands.about_command import AboutCommand
from strictdoc.commands.export import ExportCommand
from strictdoc.commands.import_excel import ImportExcelCommand
from strictdoc.commands.import_reqif import ImportReqIFCommand
from strictdoc.commands.manage_autouid_command import ManageAutoUIDCommand
from strictdoc.commands.server import ServerCommand
from strictdoc.commands.version_command import VersionCommand
from strictdoc.helpers.coverage import register_code_coverage_hook
from strictdoc.helpers.exception import (
    ExceptionInfo,
    StrictDocChildProcessException,
)
from strictdoc.helpers.parallelizer import Parallelizer
from strictdoc.helpers.timing import measure_performance

COMMAND_REGISTRY: Dict[str, Any] = {
    "about": AboutCommand,
    "export": ExportCommand,
    "import": {"excel": ImportExcelCommand, "reqif": ImportReqIFCommand},
    "manage": {"auto-uid": ManageAutoUIDCommand},
    "server": ServerCommand,
    "version": VersionCommand,
}


def _main() -> None:
    # The parser can raise when no arguments or incorrect arguments are provided.
    try:
        parser = SDocArgsParser.create_sdoc_args_parser(COMMAND_REGISTRY)
    except Exception as exception_:
        print(f"error: {str(exception_)}", flush=True)  # noqa: T201
        sys.exit(1)

    if parser.is_debug_mode():
        environment.is_debug_mode = True

    # Ensure that multiprocessing.freeze_support() is called in a frozen
    # application
    # https://github.com/pyinstaller/pyinstaller/issues/7438
    if getattr(sys, "frozen", False):  # pragma: no cover
        multiprocessing.freeze_support()

    # This is crucial for a good performance on macOS. Linux uses 'fork' by default.
    # Changed in version 3.8: On macOS, the spawn start method is now the default.
    # The fork start method should be considered unsafe as it can lead to crashes
    # of the subprocess as macOS system libraries may start threads. See bpo-33725.
    # https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
    # 2024-12-26: StrictDoc has been working with 'fork' just fine, so keep doing it until
    #             anything serious appears against using it.
    if sys.platform != "win32":
        multiprocessing.set_start_method("fork", force=True)
    else:  # pragma: no cover
        pass  # pragma: no cover

    # How to make python 3 print() utf8
    # https://stackoverflow.com/a/3597849/598057
    # sys.stdout.reconfigure(encoding='utf-8') for Python 3.7
    sys.stdout = open(  # pylint: disable=bad-option-value,consider-using-with
        1, "w", encoding="utf-8", closefd=False
    )

    register_code_coverage_hook()

    enable_parallelization = "--no-parallelization" not in sys.argv
    parallelizer = Parallelizer.create(enable_parallelization)

    exception_info: Optional[ExceptionInfo] = None
    try:
        parser.run(parallelizer)
    except StrictDocChildProcessException as exception_info_:
        exception_info = exception_info_.exception_info
    except Exception as exception_:
        exception_info = ExceptionInfo(exception_)
    finally:
        parallelizer.shutdown()

        if exception_info is not None:
            if parser.is_debug_mode():
                print(exception_info.get_stack_trace(), flush=True)  # noqa: T201
            print(exception_info.get_detailed_error_message(), flush=True)  # noqa: T201
            if not parser.is_debug_mode():
                print(  # noqa: T201
                    "Rerun with strictdoc --debug <...> to enable stack trace printing.",
                    flush=True,
                )
            sys.exit(1)


def main() -> None:
    with measure_performance("Total execution time"):
        _main()


if __name__ == "__main__":
    main()
else:  # pragma: no cover
    pass
