import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

import argparse

from pathlib import Path

from strictdoc.export.html.export import DocumentTreeHTMLExport
from strictdoc.core.document_finder import DocumentFinder

from strictdoc.backend.rst.rst_reader import RSTReader


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

parser.add_argument('input_file', type=str, help='TODO')
parser.add_argument('--output-file', type=str, help='TODO')
# parser.add_argument('--strict-whitespace', action='store_true', help='TODO')
# parser.add_argument('--match-full-lines', action='store_true', help='TODO')
# parser.add_argument('--check-prefix', action='store', help='TODO')
# parser.add_argument('--implicit-check-not', action='append', help='TODO')
#
args = parser.parse_args()

print(args.command)

if args.command == 'passthrough':
    path_to_doc = args.input_file
    if not os.path.isfile(path_to_doc):
        sys.stdout.flush()
        err = "Could not open doc file '{}': No such file or directory".format(path_to_doc)
        print(err)
        exit(1)

    with open(path_to_doc, 'r') as file:
        doc_content = file.read()

    document = RSTReader.read_rst(doc_content)

    document.dump_pretty()
    rst_output = document.dump_rst()

    output_file = args.output_file
    if output_file:
        output_dir = os.path.dirname(output_file)
        if not os.path.isdir(output_dir):
            print("not a directory: {}".format(output_file))
            exit(1)

        print("writing to file: {}".format(output_file))
        with open(output_file, 'w') as file:
            file.write(rst_output)

        exit(0)

if args.command == 'export':
    path_to_single_file_or_doc_root = args.input_file

    document_tree = DocumentFinder.find_sdoc_content(path_to_single_file_or_doc_root)

    writer = DocumentTreeHTMLExport()
    output = writer.export(document_tree)

    output_file = "output/export.html"

    Path("output").mkdir(parents=True, exist_ok=True)

    output_dir = os.path.dirname(output_file)
    if not os.path.isdir(output_dir):
        print("not a directory: {}".format(output_file))
        exit(1)

    print("writing to file: {}".format(output_file))
    with open(output_file, 'w') as file:
        file.write(output)

    exit(0)
