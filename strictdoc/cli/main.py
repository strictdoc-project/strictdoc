import os
import sys

try:
    STRICTDOC_ROOT_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    if not os.path.isdir(STRICTDOC_ROOT_PATH):
        raise FileNotFoundError
    sys.path.append(STRICTDOC_ROOT_PATH)

    from strictdoc.cli.cli_arg_parser import create_sdoc_args_parser
    from strictdoc.core.actions.export_action import ExportAction
    from strictdoc.core.actions.passthrough_action import PassthroughAction
    from strictdoc.helpers.parallelizer import Parallelizer
except FileNotFoundError:
    print("error: could not locate strictdoc's root folder.")
    sys.exit(1)


def _main(parallelizer):
    parser = create_sdoc_args_parser()

    if parser.is_passthrough_command:
        config = parser.get_passthrough_config()
        input_file = config.input_file
        if not os.path.isfile(input_file):
            sys.stdout.flush()
            message = "error: passthrough command's input file does not exist"
            print("{}: {}".format(message, input_file))
            sys.exit(1)

        output_file = config.output_file
        if output_file:
            output_dir = os.path.dirname(output_file)
            if not os.path.isdir(output_dir):
                print("not a directory: {}".format(output_file))
                sys.exit(1)

        passthrough_action = PassthroughAction()
        passthrough_action.passthrough(config)

    elif parser.is_export_command:
        config = parser.get_export_config(STRICTDOC_ROOT_PATH)
        parallelization_value = (
            "Disabled" if config.no_parallelization else "Enabled"
        )
        print("Parallelization: {}".format(parallelization_value), flush=True)
        export_action = ExportAction()
        export_action.export(config, parallelizer)

    else:
        raise NotImplementedError


def main():
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
