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
    DumpGrammarCommandConfig,
    ExportCommandConfig,
    ImportExcelCommandConfig,
    ImportReqIFCommandConfig,
    ManageAutoUIDCommandConfig,
    PassthroughCommandConfig,
    create_sdoc_args_parser,
)
from strictdoc.commands.about_command import AboutCommand
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


def _main(parallelizer):
    parser = create_sdoc_args_parser()

    if parser.is_passthrough_command:
        config: PassthroughCommandConfig = parser.get_passthrough_config()
        input_file = config.input_file
        if not os.path.isfile(input_file):
            sys.stdout.flush()
            message = "error: passthrough command's input file does not exist"
            print(f"{message}: {input_file}")  # noqa: T201
            sys.exit(1)

        output_file = config.output_file
        if output_file:
            output_dir = os.path.dirname(output_file)
            if not os.path.isdir(output_dir):
                print(f"not a directory: {output_file}")  # noqa: T201
                sys.exit(1)

        passthrough_action = PassthroughAction()
        passthrough_action.passthrough(config)

    elif parser.is_export_command:
        config: ExportCommandConfig = parser.get_export_config()
        try:
            config.validate()
        except CLIValidationError as exception_:
            print(f"error: {exception_.args[0]}")  # noqa: T201
            sys.exit(1)
        project_config: ProjectConfig = (
            ProjectConfigLoader.load_from_path_or_get_default(
                path_to_config=config.get_path_to_config(),
                environment=environment,
            )
        )
        project_config.integrate_export_config(config)

        parallelization_value = (
            "Disabled" if config.no_parallelization else "Enabled"
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
        project_config: ProjectConfig = (
            ProjectConfigLoader.load_from_path_or_get_default(
                path_to_config=server_config.get_path_to_config(),
                environment=environment,
            )
        )
        run_strictdoc_server(
            server_config=server_config, project_config=project_config
        )

    elif parser.is_import_command_reqif:
        import_config: ImportReqIFCommandConfig = (
            parser.get_import_config_reqif(environment.path_to_strictdoc)
        )
        import_action = ImportAction()
        import_action.do_import(import_config)

    elif parser.is_import_command_excel:
        import_config: ImportExcelCommandConfig = (
            parser.get_import_config_excel(environment.path_to_strictdoc)
        )
        import_action = ImportAction()
        import_action.do_import(import_config)

    elif parser.is_manage_autouid_command:
        config: ManageAutoUIDCommandConfig = parser.get_manage_autouid_config()
        try:
            config.validate()
        except CLIValidationError as exception_:
            print(f"error: {exception_.args[0]}")  # noqa: T201
            sys.exit(1)
        project_config: ProjectConfig = (
            ProjectConfigLoader.load_from_path_or_get_default(
                path_to_config=config.get_path_to_config(),
                environment=environment,
            )
        )
        # FIXME: This must be improved.
        project_config.export_input_paths = [config.input_path]
        ManageAutoUIDCommand.execute(
            project_config=project_config, parallelizer=parallelizer
        )

    elif parser.is_dump_grammar_command:
        config: DumpGrammarCommandConfig = parser.get_dump_grammar_config()
        DumpGrammarCommand.execute(config)

    elif parser.is_version_command:
        VersionCommand.execute()

    elif parser.is_about_command:
        AboutCommand.execute()

    else:
        raise NotImplementedError


def main():
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
