import os
import sys
from pathlib import Path
from typing import List

from strictdoc.backend.markdown.grammar_reader import MarkdownGrammarReader
from strictdoc.backend.markdown.reader import SDMarkdownReader
from strictdoc.backend.markdown.writer import SDMarkdownWriter
from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.core.file_system.file_tree import File
from strictdoc.core.format import ExportContext, Format
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.helpers.parallelizer import NullParallelizer


class MarkdownFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["markdown"]

    @staticmethod
    def supported_extensions() -> List[str]:
        return [".md", ".markdown"]

    @staticmethod
    def supports_import() -> bool:
        return False

    @staticmethod
    def supports_export() -> bool:
        return True

    @staticmethod
    def supports_read() -> bool:
        return True

    @staticmethod
    def read_extensions() -> List[str]:
        return [".md", ".markdown"]

    def read_from_file(
        self, doc_file: File, project_config: ProjectConfig
    ) -> SDocDocument:
        return SDMarkdownReader().read_from_file(
            doc_file.full_path, project_config
        )

    @staticmethod
    def supports_grammar() -> bool:
        return True

    @staticmethod
    def grammar_extensions() -> List[str]:
        return [".gra.md"]

    def read_grammar(
        self, doc_file: File, project_config: ProjectConfig
    ) -> DocumentGrammar:
        return MarkdownGrammarReader().read_from_file(
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

        writer = SDMarkdownWriter()

        output_base_dir = (
            project_config.output_dir
            if project_config.output_dir is not None
            else os.path.join(os.getcwd(), "output")
        )
        output_dir = os.path.join(output_base_dir, "markdown")

        for document in traceability_index.document_tree.document_list:
            assert document.meta
            assert document.meta.document_filename_base
            assert document.meta.input_doc_dir_rel_path

            output = writer.write(document)

            path_to_output_file_dir: str = os.path.join(
                output_dir, document.meta.input_doc_dir_rel_path.relative_path
            )
            Path(path_to_output_file_dir).mkdir(parents=True, exist_ok=True)

            path_to_output_file = os.path.join(
                path_to_output_file_dir,
                document.meta.document_filename_base + ".md",
            )
            with open(
                path_to_output_file,
                "w",
                encoding="utf8",
            ) as file:
                file.write(output)
