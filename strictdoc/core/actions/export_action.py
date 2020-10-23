import os
from pathlib import Path

from strictdoc.core.document_finder import DocumentFinder
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.export import SingleDocumentTableHTMLExport, SingleDocumentTraceabilityHTMLExport
from strictdoc.export.html.generators.document import DocumentHTMLGenerator
from strictdoc.export.html.generators.document_tree import DocumentTreeHTMLGenerator
from strictdoc.export.html.renderer import SingleDocumentFragmentRenderer
from strictdoc.export.rst.export import SingleDocumentRSTExport
from strictdoc.helpers.file_system import sync_dir


class ExportAction:
    def __init__(self, root_path):
        self.root_path = root_path

    def export(self, path_to_single_file_or_doc_root):
        renderer = SingleDocumentFragmentRenderer()

        if isinstance(path_to_single_file_or_doc_root, str):
            path_to_single_file_or_doc_root = [path_to_single_file_or_doc_root]

        document_tree = DocumentFinder.find_sdoc_content(path_to_single_file_or_doc_root)

        traceability_index = TraceabilityIndex.create(document_tree)

        writer = DocumentTreeHTMLGenerator()
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

        # Single Document pages (RST)
        Path("output/rst").mkdir(parents=True, exist_ok=True)
        for document in document_tree.document_list:
            document_content = SingleDocumentRSTExport.export(document_tree,
                                                              document,
                                                              traceability_index)

            document_out_file = "output/rst/{}.rst".format(document.name)
            print("writing to file: {}".format(document_out_file))
            with open(document_out_file, 'w') as file:
                file.write(document_content)

        # Single Document pages
        for document in document_tree.document_list:
            document_content = DocumentHTMLGenerator.export(document_tree,
                                                            document,
                                                            traceability_index,
                                                            renderer)
            document_out_file = "output/{}.html".format(document.name)
            print("writing to file: {}".format(document_out_file))
            with open(document_out_file, 'w') as file:
                file.write(document_content)

        # Single Document Table pages
        for document in document_tree.document_list:
            document_content = SingleDocumentTableHTMLExport.export(
                document_tree, document, traceability_index, renderer
            )
            document_out_file = "output/{} - Table.html".format(document.name)
            print("writing to file: {}".format(document_out_file))
            with open(document_out_file, 'w') as file:
                file.write(document_content)

        # Single Document Traceability pages
        for document in document_tree.document_list:
            document_content = SingleDocumentTraceabilityHTMLExport.export(
                document_tree, document, traceability_index, renderer
            )
            document_out_file = "output/{} - Traceability.html".format(document.name)
            print("writing to file: {}".format(document_out_file))
            with open(document_out_file, 'w') as file:
                file.write(document_content)

        # Single Document Deep Traceability pages
        for document in document_tree.document_list:
            document_content = SingleDocumentTraceabilityHTMLExport.export_deep(
                document_tree, document, traceability_index, renderer
            )
            document_out_file = "output/{} - Traceability Deep.html".format(document.name)
            print("writing to file: {}".format(document_out_file))
            with open(document_out_file, 'w') as file:
                file.write(document_content)

        static_files_src = os.path.join(self.root_path, 'strictdoc/export/html/static')
        static_files_dest = os.path.join(self.root_path, 'output/static')
        sync_dir(static_files_src, static_files_dest)
