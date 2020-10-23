import argparse
import os
import sys

ROOT_PATH = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(ROOT_PATH)

from strictdoc.core.actions.export_action import ExportAction
from strictdoc.core.actions.passthrough_action import PassthroughAction

# for arg in sys.argv:
#     if arg == '--help':
#         # print_help()
#         assert 0
#         exit(0)
#
# for arg in sys.argv:
#     if arg == '--version':
#         # print_version()
#         assert 0
#         exit(0)

# if os.path.getsize(check_file) == 0:
#     sys.stdout.flush()
#     print("error: no check strings found with prefix 'CHECK:'", file=sys.stderr)
#     exit(2)

parser = argparse.ArgumentParser()

parser.add_argument('command', type=str, help='TODO', choices=[
    'passthrough', 'export'
])

parser.add_argument('input_file', type=str, nargs='+', help='TODO')
parser.add_argument('--output-file', type=str, help='TODO')

args = parser.parse_args()

print(args.command)

if args.command == 'passthrough':
    paths_to_docs = args.input_file
    if len(paths_to_docs) != 1:
        sys.stdout.flush()
        err = "passthrough command's input must be a single file".format(path_to_doc)
        print(err)
        exit(1)

    output_file = args.output_file
    if output_file:
        output_dir = os.path.dirname(output_file)
        if not os.path.isdir(output_dir):
            print("not a directory: {}".format(output_file))
            exit(1)

    passthrough_action = PassthroughAction()
    passthrough_action.passthrough(paths_to_docs, output_file)

elif args.command == 'export':
    export_controller = ExportAction(ROOT_PATH)
    export_controller.export(args.input_file)

else:
    raise NotImplementedError
