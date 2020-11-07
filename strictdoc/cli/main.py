import os
import sys
from multiprocessing import freeze_support

STRICTDOC_ROOT_PATH = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(STRICTDOC_ROOT_PATH)

from strictdoc.helpers.parallelizer import Parallelizer
from strictdoc.cli.cli_arg_parser import cli_args_parser
from strictdoc.core.actions.export_action import ExportAction
from strictdoc.core.actions.passthrough_action import PassthroughAction


def main():
    # Initializing the parallelizer early in the startup process because otherwise
    # fork() used by Python's multiprocessing library results in the following error:
    #
    # """
    # objc[7522]: +[__NSPlaceholderDictionary initialize] may have been in progress
    # in another thread when fork() was called. We cannot safely call it or ignore
    # it in the fork() child process. Crashing instead. Set a breakpoint on
    # objc_initializeAfterForkError to debug.
    # """
    enable_parallelization = '--no-parallelization' not in sys.argv
    PARALLELIZER = Parallelizer.create(enable_parallelization)


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
        parallelization_value = 'Enabled' if enable_parallelization else 'Disabled'
        print("Parallelization: {}".format(parallelization_value), flush=True)
        export_controller = ExportAction(STRICTDOC_ROOT_PATH, PARALLELIZER)
        export_controller.export(args.input_paths, args.output_dir)

    else:
        raise NotImplementedError


if __name__ == '__main__':
    main()
