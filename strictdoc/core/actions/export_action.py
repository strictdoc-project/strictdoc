import concurrent.futures
import datetime
import os
from functools import partial
from multiprocessing.pool import Pool
from pathlib import Path

from strictdoc.core.document_finder import DocumentFinder
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.export import SingleDocumentTableHTMLExport, SingleDocumentTraceabilityHTMLExport
from strictdoc.export.html.generators.document import DocumentHTMLGenerator
from strictdoc.export.html.generators.document_tree import DocumentTreeHTMLGenerator
from strictdoc.export.html.renderer import SingleDocumentFragmentRenderer
from strictdoc.export.rst.export import SingleDocumentRSTExport
from strictdoc.helpers.file_system import sync_dir
from strictdoc.helpers.timing import timing_decorator, measure_performance


class ExportAction:
    def __init__(self, root_path):
        self.root_path = root_path

    @timing_decorator('Export')
    def export(self, path_to_single_file_or_doc_root):
        if isinstance(path_to_single_file_or_doc_root, str):
            path_to_single_file_or_doc_root = [path_to_single_file_or_doc_root]

        output_root = 'output'
        output_root_html = 'output/html'
        Path(output_root_html).mkdir(parents=True, exist_ok=True)

        document_tree = DocumentFinder.find_sdoc_content(path_to_single_file_or_doc_root, output_root_html)

        traceability_index = TraceabilityIndex.create(document_tree)

        writer = DocumentTreeHTMLGenerator()
        output = writer.export(document_tree)

        output_file = '{}/index.html'.format(output_root_html)

        with open(output_file, 'w') as file:
            file.write(output)

        # Single Document pages (RST)
        Path("output/rst").mkdir(parents=True, exist_ok=True)
        for document in document_tree.document_list:
            document_content = SingleDocumentRSTExport.export(document_tree,
                                                              document,
                                                              traceability_index)

            document_out_file = "output/rst/{}.rst".format(document.name)
            with open(document_out_file, 'w') as file:
                file.write(document_content)

            document.renderer = SingleDocumentFragmentRenderer()

            # HACK:
            # ProcessPoolExecutor doesn't work because of non-picklable parts
            # of textx. The offending fields are stripped down because they
            # are not used anyway.
            document._tx_parser = None
            document._tx_attrs = None
            document._tx_metamodel = None
            document._tx_peg_rule = None

        export_binding = partial(self._export_with_performance,
                                 document_tree=document_tree,
                                 traceability_index=traceability_index)

        # TODO: Not ready for ProcessPoolExecutor: Traceability index is a shared object.
        with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
            executor.map(export_binding, document_tree.document_list)

        static_files_src = os.path.join(self.root_path, 'strictdoc/export/html/static')
        static_files_dest = os.path.join(self.root_path, 'output/html/_static')
        sync_dir(static_files_src, static_files_dest)

    def _export_with_performance(self, document, document_tree, traceability_index):
        document_meta: DocumentMeta = document.meta
        full_output_path = os.path.join(self.root_path, document_meta.get_html_doc_path())

        # If file exists we want to check its modification path in order to skip
        # its generation in case it has not changed since the last generation.
        if os.path.isfile(full_output_path):
            sdoc_mtime_timestamp = (os.path.getmtime(document_meta.sdoc_full_path))
            sdoc_mtime = datetime.datetime.fromtimestamp(sdoc_mtime_timestamp)

            output_file_mtime_timestamp = (os.path.getmtime(full_output_path))
            output_file_mtime = datetime.datetime.fromtimestamp(output_file_mtime_timestamp)

            if sdoc_mtime < output_file_mtime:
                with measure_performance('Skip: {}'.format(document.name)):
                    return

        with measure_performance('Published: {}'.format(document.name)):
            self._export(document, document_tree, traceability_index)

    def _export(self, document, document_tree, traceability_index):
        document_meta: DocumentMeta = document.meta

        document_output_folder = document_meta.output_folder_rel_path
        Path(document_output_folder).mkdir(parents=True, exist_ok=True)

        # Single Document pages
        document_content = DocumentHTMLGenerator.export(document_tree,
                                                        document,
                                                        traceability_index,
                                                        document.renderer)

        document_out_file = document_meta.get_html_doc_path()
        with open(document_out_file, 'w') as file:
            file.write(document_content)

        # Single Document Table pages
        document_content = SingleDocumentTableHTMLExport.export(
            document_tree, document, traceability_index, document.renderer
        )
        document_out_file = document_meta.get_html_table_path()

        with open(document_out_file, 'w') as file:
            file.write(document_content)

        # Single Document Traceability pages
        document_content = SingleDocumentTraceabilityHTMLExport.export(
            document_tree, document, traceability_index, document.renderer
        )
        document_out_file = document_meta.get_html_traceability_path()

        with open(document_out_file, 'w') as file:
            file.write(document_content)

        # Single Document Deep Traceability pages
        document_content = SingleDocumentTraceabilityHTMLExport.export_deep(
            document_tree, document, traceability_index, document.renderer
        )
        document_out_file = document_meta.get_html_deep_traceability_path()

        with open(document_out_file, 'w') as file:
            file.write(document_content)

        return document
