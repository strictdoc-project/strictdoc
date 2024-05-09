# pylint: disable=wrong-import-position
# flake8: noqa: E402

# Needed to ensure that multiprocessing.freeze_support() is called
# in a frozen application (see main() below).
import multiprocessing
import os
import sys

strictdoc_root_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if not os.path.isdir(strictdoc_root_path):
    raise FileNotFoundError
sys.path.append(strictdoc_root_path)

from strictdoc import environment
from strictdoc.cli.cli_arg_parser import (
    CLIValidationError,
    DiffCommandConfig,
    DumpGrammarCommandConfig,
    ExportCommandConfig,
    ImportExcelCommandConfig,
    ImportReqIFCommandConfig,
    ManageAutoUIDCommandConfig,
    PassthroughCommandConfig,
    create_sdoc_args_parser,
)
from strictdoc.commands.about_command import AboutCommand
from strictdoc.commands.diff_command import DiffCommand
from strictdoc.commands.dump_grammar_command import DumpGrammarCommand
from strictdoc.commands.manage_autouid_command import ManageAutoUIDCommand
from strictdoc.commands.version_command import VersionCommand
from strictdoc.core.actions.export_action import ExportAction
from strictdoc.core.actions.import_action import ImportAction
from strictdoc.core.actions.passthrough_action import PassthroughAction
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.parallelizer import Parallelizer
from strictdoc.server.server import run_strictdoc_server


def _main(parallelizer: Parallelizer) -> None:
    parser = create_sdoc_args_parser()

    project_config: ProjectConfig
    if parser.is_passthrough_command:
        passthrough_config: PassthroughCommandConfig = (
            parser.get_passthrough_config()
        )
        input_file = passthrough_config.input_file
        if not os.path.exists(input_file):
            sys.stdout.flush()
            message = "error: passthrough command's input path is neither a folder or a file."
            print(f"{message}: {input_file}")  # noqa: T201
            sys.exit(1)

        project_config = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=os.getcwd(),
            environment=environment,
        )
        project_config.integrate_passthrough_config(passthrough_config)

        passthrough_action = PassthroughAction()
        passthrough_action.passthrough(project_config)

    elif parser.is_export_command:
        export_config: ExportCommandConfig = parser.get_export_config()
        try:
            export_config.validate()
        except CLIValidationError as exception_:
            print(f"error: {exception_.args[0]}")  # noqa: T201
            sys.exit(1)
        project_config = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=export_config.get_path_to_config(),
            environment=environment,
        )
        project_config.integrate_export_config(export_config)

        parallelization_value = (
            "Disabled" if export_config.no_parallelization else "Enabled"
        )
        print(  # noqa: T201
            f"Parallelization: {parallelization_value}", flush=True
        )
        export_action = ExportAction(
            project_config=project_config,
            parallelizer=parallelizer,
        )
        export_action.build_index()
        export_action.export()

    elif parser.is_server_command:
        server_config = parser.get_server_config()
        try:
            server_config.validate()
        except CLIValidationError as exception_:
            print(f"error: {exception_.args[0]}")  # noqa: T201
            sys.exit(1)
        project_config = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=server_config.get_path_to_config(),
            environment=environment,
        )
        run_strictdoc_server(
            server_config=server_config, project_config=project_config
        )

    elif parser.is_import_command_reqif:
        project_config = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=os.getcwd(),
            environment=environment,
        )
        import_reqif_config: ImportReqIFCommandConfig = (
            parser.get_import_config_reqif(environment.path_to_strictdoc)
        )
        import_action = ImportAction()
        import_action.do_import(import_reqif_config, project_config)

    elif parser.is_import_command_excel:
        project_config = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=os.getcwd(),
            environment=environment,
        )
        import_excel_config: ImportExcelCommandConfig = (
            parser.get_import_config_excel(environment.path_to_strictdoc)
        )
        import_action = ImportAction()
        import_action.do_import(import_excel_config, project_config)

    elif parser.is_manage_autouid_command:
        manage_config: ManageAutoUIDCommandConfig = (
            parser.get_manage_autouid_config()
        )
        try:
            manage_config.validate()
        except CLIValidationError as exception_:
            print(f"error: {exception_.args[0]}")  # noqa: T201
            sys.exit(1)
        project_config = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=manage_config.get_path_to_config(),
            environment=environment,
        )
        # FIXME: This must be improved.
        project_config.export_input_paths = [manage_config.input_path]
        # FIXME: This must be improved.
        project_config.autouuid_include_sections = (
            manage_config.include_sections
        )

        ManageAutoUIDCommand.execute(
            project_config=project_config, parallelizer=parallelizer
        )

    elif parser.is_dump_grammar_command:
        dump_config: DumpGrammarCommandConfig = parser.get_dump_grammar_config()
        DumpGrammarCommand.execute(dump_config)

    elif parser.is_version_command:
        VersionCommand.execute()

    elif parser.is_about_command:
        AboutCommand.execute()

    elif parser.is_diff_command:
        diff_config: DiffCommandConfig = parser.get_diff_config()
        project_config = ProjectConfigLoader.load_from_path_or_get_default(
            path_to_config=os.getcwd(),
            environment=environment,
        )
        DiffCommand.execute(
            project_config=project_config, diff_config=diff_config
        )

    else:
        raise NotImplementedError


def main() -> None:
    # Ensure that multiprocessing.freeze_support() is called in a frozen
    # application
    # https://github.com/pyinstaller/pyinstaller/issues/7438
    if getattr(sys, "frozen", False):
        multiprocessing.freeze_support()

    # How to make python 3 print() utf8
    # https://stackoverflow.com/a/3597849/598057
    # sys.stdout.reconfigure(encoding='utf-8') for Python 3.7
    sys.stdout = open(  # pylint: disable=bad-option-value,consider-using-with
        1, "w", encoding="utf-8", closefd=False
    )

    enable_parallelization = "--no-parallelization" not in sys.argv
    parallelizer = Parallelizer.create(enable_parallelization)
    try:
        _main(parallelizer)
    except StrictDocException as exception:
        print(f"error: {exception.args[0]}")  # noqa: T201
        sys.exit(1)
    except Exception as exc:
        raise exc
    finally:
        parallelizer.shutdown()


if __name__ == "__main__":
    main()
