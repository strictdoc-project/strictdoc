import os
import sys
from pathlib import Path
from typing import List

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.grammar_reader import SDocGrammarReader
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.reader import SDReader
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.core.file_system.file_tree import File
from strictdoc.core.format import ExportContext, Format
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.helpers.parallelizer import NullParallelizer


class SDocFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["sdoc"]

    @staticmethod
    def supported_extensions() -> List[str]:
        return [".sdoc"]

    @staticmethod
    def supports_import() -> bool:
        return False

    @staticmethod
    def supports_export() -> bool:
        return True

    @staticmethod
    def supports_convert_output() -> bool:
        return True

    def write_converted_document(
        self,
        document: SDocDocument,
        output_dir: str,
        filename_stem: str,
        project_config: ProjectConfig,
    ) -> None:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        path_to_output_document = os.path.join(
            output_dir, filename_stem + self.supported_extensions()[0]
        )
        document_content = SDWriter(project_config).write(document)
        with open(path_to_output_document, "w", encoding="utf8") as output_file:
            output_file.write(document_content)

    @staticmethod
    def supports_read() -> bool:
        return True

    @staticmethod
    def read_extensions() -> List[str]:
        return [".sdoc"]

    def read_from_file(
        self, doc_file: File, project_config: ProjectConfig
    ) -> SDocDocument:
        return SDReader().read_from_file(doc_file.full_path, project_config)

    @staticmethod
    def supports_grammar() -> bool:
        return True

    @staticmethod
    def grammar_extensions() -> List[str]:
        return [".sgra"]

    def read_grammar(
        self, doc_file: File, project_config: ProjectConfig
    ) -> DocumentGrammar:
        return SDocGrammarReader().read_from_file(
            doc_file.full_path, project_config
        )

    def export_complete_tree(self, context: ExportContext, handle: str) -> None:
        assert handle in self.handles(), handle
        project_config = context.project_config
        assert project_config.input_paths
        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create(
                    project_config=project_config,
                    parallelizer=NullParallelizer(),
                )
            )
        except DocumentTreeError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)
        else:
            assert traceability_index.document_tree

        writer = SDWriter(
            project_config, node_filter=traceability_index.node_filter
        )

        output_base_dir = (
            project_config.output_dir
            if project_config.output_dir is not None
            else os.path.join(os.getcwd(), "output")
        )
        output_dir = os.path.join(output_base_dir, "sdoc")
        for document in traceability_index.document_tree.document_list:
            assert document.meta
            assert document.meta.document_filename_base
            assert document.meta.input_doc_dir_rel_path
            output, fragments_dict = writer.write_with_fragments(
                document,
            )

            path_to_output_file_dir: str = os.path.join(
                output_dir, document.meta.input_doc_dir_rel_path.relative_path
            )
            Path(path_to_output_file_dir).mkdir(parents=True, exist_ok=True)
            path_to_output_file = os.path.join(
                path_to_output_file_dir, document.meta.document_filename_base
            )
            path_to_output_file += ".sdoc"
            with open(path_to_output_file, "w", encoding="utf8") as file:
                file.write(output)

            for fragment_path_, fragment_content_ in fragments_dict.items():
                path_to_output_fragment = os.path.join(
                    path_to_output_file_dir, fragment_path_
                )
                with open(
                    path_to_output_fragment, "w", encoding="utf8"
                ) as file_:
                    file_.write(fragment_content_)
