import concurrent.futures
import datetime
import glob
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
from strictdoc.helpers.file_modification_time import get_file_modification_time
from strictdoc.helpers.file_system import sync_dir
from strictdoc.helpers.timing import timing_decorator, measure_performance


class ExportAction:
    def __init__(self, strictdoc_src_path):
        self.strictdoc_src_path = strictdoc_src_path
        self.cwd = os.getcwd()

        strict_own_files = glob.iglob('{}/strictdoc/**/*'.format(self.strictdoc_src_path), recursive=True)
        strict_own_files = [f for f in strict_own_files if f.endswith('.html') or f.endswith('.py')]
        latest_strictdoc_own_file = max(strict_own_files, key=os.path.getctime)
        self.strictdoc_last_update = get_file_modification_time(latest_strictdoc_own_file)

    @timing_decorator('Export')
    def export(self, path_to_single_file_or_doc_root, output_dir):
        if isinstance(path_to_single_file_or_doc_root, str):
            path_to_single_file_or_doc_root = [path_to_single_file_or_doc_root]
        output_dir = output_dir if output_dir else "output"

        if not os.path.isabs(output_dir):
            output_dir = os.path.join(self.cwd, output_dir)

        output_html_root = '{}/html'.format(output_dir)
        output_html_static_files = '{}/_static'.format(output_html_root)

        Path(output_html_root).mkdir(parents=True, exist_ok=True)

        document_tree, asset_dirs = DocumentFinder.find_sdoc_content(
            path_to_single_file_or_doc_root, output_html_root
        )

        traceability_index = TraceabilityIndex.create(document_tree)

        writer = DocumentTreeHTMLGenerator()
        output = writer.export(document_tree)

        output_file = '{}/index.html'.format(output_html_root)

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

        static_files_src = os.path.join(self.strictdoc_src_path, 'strictdoc/export/html/static')
        sync_dir(static_files_src, output_html_static_files)
        for asset_dir in asset_dirs:
            source_path = asset_dir['full_path']
            output_relative_path = asset_dir['relative_path']
            destination_path = os.path.join(output_html_root, output_relative_path)
            sync_dir(source_path, destination_path)

        print('Export completed. Documentation tree can be found at:\n{}'.format(output_html_root))

    def _export_with_performance(self, document, document_tree, traceability_index):
        document_meta: DocumentMeta = document.meta
        full_output_path = os.path.join(self.strictdoc_src_path, document_meta.get_html_doc_path())

        # If file exists we want to check its modification path in order to skip
        # its generation in case it has not changed since the last generation.
        if os.path.isfile(full_output_path):
            output_file_mtime = get_file_modification_time(full_output_path)
            sdoc_mtime = get_file_modification_time(document_meta.sdoc_full_path)

            if (sdoc_mtime < output_file_mtime and
                self.strictdoc_last_update < output_file_mtime):
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
