import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from strictdoc.backend.rst import dump_pretty, dump_rst


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

parser.add_argument('command', type=str, help='TODO', choices=['passthrough'])
parser.add_argument('input_file', type=str, help='TODO')
parser.add_argument('--output-file', type=str, help='TODO')
# parser.add_argument('--strict-whitespace', action='store_true', help='TODO')
# parser.add_argument('--match-full-lines', action='store_true', help='TODO')
# parser.add_argument('--check-prefix', action='store', help='TODO')
# parser.add_argument('--implicit-check-not', action='append', help='TODO')
#
args = parser.parse_args()

print(args.command)

path_to_doc = args.input_file
if not os.path.isfile(path_to_doc):
    sys.stdout.flush()
    err = "Could not open doc file '{}': No such file or directory".format(path_to_doc)
    print(err)
    exit(1)

with open(path_to_doc, 'r') as file:
    doc_content = file.read()

dump_pretty(doc_content)
rst_output = dump_rst(doc_content)

output_file = args.output_file
if output_file:
    output_dir = os.path.dirname(output_file)
    if not os.path.isdir(output_dir):
        print("not a directory: {}".format(output_file))
        exit(1)

    print("writing to file: {}".format(output_file))
    with open(output_file, 'w') as file:
        file.write(rst_output)
