import argparse
import os
import sys

from pathlib import Path

from strictdoc.helpers.file_system import sync_dir

ROOT_PATH = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(ROOT_PATH)

from strictdoc.backend.rst.rst_reader import RSTReader
from strictdoc.export.html.export import DocumentTreeHTMLExport, SingleDocumentHTMLExport, \
    SingleDocumentTraceabilityHTMLExport
from strictdoc.core.document_finder import DocumentFinder
from strictdoc.core.traceability_index import TraceabilityIndex

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

    traceability_index = TraceabilityIndex.create(document_tree)

    writer = DocumentTreeHTMLExport()
    output = writer.export(document_tree)

    output_file = "output/index.html"

    Path("output").mkdir(parents=True, exist_ok=True)

    output_dir = os.path.dirname(output_file)
    if not os.path.isdir(output_dir):
        print("not a directory: {}".format(output_file))
        exit(1)

    print("writing to file: {}".format(output_file))
    with open(output_file, 'w') as file:
        file.write(output)

    # Single Document pages
    for document in document_tree.document_list:
        document_content = SingleDocumentHTMLExport.export(document)
        document_out_file = "output/{}.html".format(document.name)
        print("writing to file: {}".format(document_out_file))
        with open(document_out_file, 'w') as file:
            file.write(document_content)

    # Single Document Traceability pages
    for document in document_tree.document_list:
        document_content = SingleDocumentTraceabilityHTMLExport.export(
            document_tree, document, traceability_index
        )
        document_out_file = "output/{} - Traceability.html".format(document.name)
        print("writing to file: {}".format(document_out_file))
        with open(document_out_file, 'w') as file:
            file.write(document_content)

    static_files_src = os.path.join(ROOT_PATH, 'strictdoc/export/html/static')
    static_files_dest = os.path.join(ROOT_PATH, 'output/static')
    sync_dir(static_files_src, static_files_dest)
    exit(0)
