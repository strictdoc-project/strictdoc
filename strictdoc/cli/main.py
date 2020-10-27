import os
import sys

STRICTDOC_ROOT_PATH = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(STRICTDOC_ROOT_PATH)

from strictdoc.cli.cli_arg_parser import cli_args_parser
from strictdoc.core.actions.export_action import ExportAction
from strictdoc.core.actions.passthrough_action import PassthroughAction


def main():
    parser = cli_args_parser()
    args = parser.parse_args()

    if args.command == 'passthrough':
        input_file = args.input_file
        if not os.path.isfile(input_file):
            sys.stdout.flush()
            err = "error: passthrough command's input file does not exist: {}".format(input_file)
            print(err)
            exit(1)

        output_file = args.output_file
        if output_file:
            output_dir = os.path.dirname(output_file)
            if not os.path.isdir(output_dir):
                print("not a directory: {}".format(output_file))
                exit(1)

        passthrough_action = PassthroughAction()
        passthrough_action.passthrough(input_file, output_file)

    elif args.command == 'export':
        export_controller = ExportAction(STRICTDOC_ROOT_PATH)
        export_controller.export(args.input_paths, args.output_dir)

    else:
        raise NotImplementedError


if __name__ == '__main__':
    main()
