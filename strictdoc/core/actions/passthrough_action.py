# mypy: disable-error-code="no-untyped-call,no-untyped-def,union-attr"
import os
import sys
from pathlib import Path

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.helpers.parallelizer import NullParallelizer


class PassthroughAction:
    @staticmethod
    def passthrough(project_config: ProjectConfig):
        assert project_config.passthrough_input_path is not None
        project_config.export_input_paths = [
            project_config.passthrough_input_path
        ]
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

        writer = SDWriter()

        output_dir = (
            project_config.passthrough_output_dir
            if project_config.passthrough_output_dir is not None
            else os.path.join(os.getcwd(), "output", "sdoc")
        )
        for document in traceability_index.document_tree.document_list:
            output, fragments_dict = writer.write_with_fragments(
                document,
                convert_free_text_to_text=project_config.passthrough_free_text_to_text,
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
