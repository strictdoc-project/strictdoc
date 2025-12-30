# pylint: disable=wrong-import-position
# flake8: noqa: E402

# Needed to ensure that multiprocessing.freeze_support() is called
# in a frozen application (see main() below).
import multiprocessing
import os
import sys
from typing import Optional

strictdoc_root_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
assert os.path.isdir(strictdoc_root_path)
sys.path.append(strictdoc_root_path)

from strictdoc import environment
from strictdoc.cli.cli_arg_parser import (
    ImportExcelCommandConfig,
    ImportReqIFCommandConfig,
    SDocArgsParser,
    create_sdoc_args_parser,
)
from strictdoc.core.actions.import_action import ImportAction
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.helpers.coverage import register_code_coverage_hook
from strictdoc.helpers.exception import (
    ExceptionInfo,
    StrictDocChildProcessException,
)
from strictdoc.helpers.parallelizer import Parallelizer
from strictdoc.helpers.timing import measure_performance


def _main_internal(parallelizer: Parallelizer, parser: SDocArgsParser) -> None:
    register_code_coverage_hook()

    project_config: ProjectConfig

    if parser.run(parallelizer):
        return

    #
    # FIXME: Migrate the remaining commands.
    #
    if parser.is_import_command_reqif:
        project_config = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=os.getcwd(),
        )
        import_reqif_config: ImportReqIFCommandConfig = (
            parser.get_import_config_reqif(environment.path_to_strictdoc)
        )
        import_action = ImportAction()
        import_action.do_import(import_reqif_config, project_config)

    elif parser.is_import_command_excel:
        project_config = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=os.getcwd(),
        )
        import_excel_config: ImportExcelCommandConfig = (
            parser.get_import_config_excel(environment.path_to_strictdoc)
        )
        import_action = ImportAction()
        import_action.do_import(import_excel_config, project_config)

    else:
        raise NotImplementedError


def _main() -> None:
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

    enable_parallelization = "--no-parallelization" not in sys.argv

    # NOTE: The parser can exit before the _main starts when no arguments
    #       or incorrect arguments are provided. In those cases, it is still
    #       important that the parallelizer is correctly shut down.
    try:
        parser = create_sdoc_args_parser()
    except Exception as exception_:
        print(f"error: {str(exception_)}", flush=True)  # noqa: T201
        sys.exit(1)

    if parser.is_debug_mode():
        environment.is_debug_mode = True

    parallelizer = Parallelizer.create(enable_parallelization)

    exception_info: Optional[ExceptionInfo] = None
    try:
        _main_internal(parallelizer, parser)
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
