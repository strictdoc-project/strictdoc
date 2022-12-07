import os
import sys

try:
    strictdoc_root_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    if not os.path.isdir(strictdoc_root_path):
        raise FileNotFoundError
    sys.path.append(strictdoc_root_path)

    from strictdoc import STRICTDOC_ROOT_PATH
    from strictdoc.cli.cli_arg_parser import (
        create_sdoc_args_parser,
        ExportCommandConfig,
        PassthroughCommandConfig,
        DumpGrammarCommandConfig,
        ImportExcelCommandConfig,
        ImportReqIFCommandConfig,
    )
    from strictdoc.commands.about_command import AboutCommand
    from strictdoc.commands.dump_grammar_command import DumpGrammarCommand
    from strictdoc.commands.version_command import VersionCommand
    from strictdoc.core.actions.export_action import ExportAction
    from strictdoc.core.actions.import_action import ImportAction
    from strictdoc.core.actions.passthrough_action import PassthroughAction
    from strictdoc.helpers.parallelizer import Parallelizer
    from strictdoc.server.server import run_strictdoc_server

except FileNotFoundError:
    print("error: could not locate strictdoc's root folder.")
    sys.exit(1)


def _main(parallelizer):
    parser = create_sdoc_args_parser()

    if parser.is_passthrough_command:
        config: PassthroughCommandConfig = parser.get_passthrough_config()
        input_file = config.input_file
        if not os.path.isfile(input_file):
            sys.stdout.flush()
            message = "error: passthrough command's input file does not exist"
            print(f"{message}: {input_file}")
            sys.exit(1)

        output_file = config.output_file
        if output_file:
            output_dir = os.path.dirname(output_file)
            if not os.path.isdir(output_dir):
                print(f"not a directory: {output_file}")
                sys.exit(1)

        passthrough_action = PassthroughAction()
        passthrough_action.passthrough(config)

    elif parser.is_export_command:
        config: ExportCommandConfig = parser.get_export_config(
            STRICTDOC_ROOT_PATH
        )
        parallelization_value = (
            "Disabled" if config.no_parallelization else "Enabled"
        )
        print(f"Parallelization: {parallelization_value}", flush=True)
        export_action = ExportAction(config, parallelizer)
        export_action.build_index()
        export_action.export()

    elif parser.is_server_command:
        server_config = parser.get_server_config()
        run_strictdoc_server(config=server_config)

    elif parser.is_import_command_reqif:
        import_config: ImportReqIFCommandConfig = (
            parser.get_import_config_reqif(STRICTDOC_ROOT_PATH)
        )
        import_action = ImportAction()
        import_action.do_import(import_config)

    elif parser.is_import_command_excel:
        import_config: ImportExcelCommandConfig = (
            parser.get_import_config_excel(STRICTDOC_ROOT_PATH)
        )
        import_action = ImportAction()
        import_action.do_import(import_config)

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
    except Exception as exc:
        raise exc
    finally:
        parallelizer.shutdown()


if __name__ == "__main__":
    main()
