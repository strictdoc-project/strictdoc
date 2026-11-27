import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.cli.base_command import BaseCommand, CLIValidationError
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.features.static_editing.apply_changes import (
    ChangeApplier,
    ChangeResult,
    ChangesFileError,
    ChangeStatus,
    load_changes_file,
)
from strictdoc.helpers.parallelizer import Parallelizer


class ApplyChangesCommand(BaseCommand):
    """
    @relation(SDOC-SRS-216, scope=class)
    """

    HELP = "Apply the changes exported by the static editor."
    DETAILED_HELP = """\
This command applies one or more JSON files that the static editor
(STATIC_EDITING feature) exports to the documents of the project.

The command applies the changes of one node together or not at all. If a
field has changed since the export in a conflicting way, the command reports
a conflict and leaves the node unchanged. A change that the documents already
contain is skipped.

The command exits with the code 1 if a change has a conflict or an error.
With --dry-run, the command reports the result without writing any file.
"""

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "input_path",
            type=str,
            help="Path to the project tree.",
        )
        parser.add_argument(
            "changes_files",
            type=str,
            nargs="+",
            help="One or more JSON files exported by the static editor.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Report the result without writing any file.",
        )
        parser.add_argument(
            "--config",
            type=str,
            help="Path to the StrictDoc config file.",
        )

    def __init__(self, args: argparse.Namespace) -> None:
        self.input_path: str = args.input_path
        self.changes_files: List[str] = args.changes_files
        self.dry_run: bool = args.dry_run
        self.config_path: Optional[str] = args.config

    def run(self, parallelizer: Parallelizer) -> None:
        if self.config_path is not None and not os.path.exists(
            self.config_path
        ):
            raise CLIValidationError(
                "Provided path to a configuration file does not exist: "
                f"{self.config_path}"
            )

        try:
            changes_by_file = [
                (path_, load_changes_file(path_))
                for path_ in self.changes_files
            ]
        except ChangesFileError as exception_:
            print(f"error: {exception_}")  # noqa: T201
            sys.exit(1)

        project_config = self._load_project_config()
        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create(
                    project_config=project_config,
                    parallelizer=parallelizer,
                    skip_source_files=True,
                )
            )
        except DocumentTreeError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)

        applier = ChangeApplier(traceability_index)
        results: List[ChangeResult] = []
        for path_to_changes_file_, changes_ in changes_by_file:
            print(f"{path_to_changes_file_}:")  # noqa: T201
            for change_ in changes_:
                result = applier.apply_change(change_)
                results.append(result)
                self._print_result(result)

        if not self.dry_run:
            self._write_documents(applier, project_config)

        has_failures = self._print_summary(applier, results)
        if has_failures:
            sys.exit(1)

    def _load_project_config(self) -> ProjectConfig:
        path_to_input_dir: str = self.input_path
        if os.path.isfile(path_to_input_dir):
            path_to_input_dir = os.path.dirname(path_to_input_dir)
        project_config: ProjectConfig = (
            ProjectConfigLoader.load_from_path_or_get_default(
                path_to_config=self.config_path
                if self.config_path is not None
                else path_to_input_dir
            )
        )
        project_config.input_paths = [self.input_path]
        if project_config.source_root_path is None:
            project_config.source_root_path = str(
                Path(self.input_path).resolve()
            )
        # The traceability index needs an HTML output path.
        project_config.export_output_html_root = "NOT_RELEVANT"
        project_config.validate_and_finalize()
        return project_config

    @staticmethod
    def _print_result(result: ChangeResult) -> None:
        location = f" ({result.document_path})" if result.document_path else ""
        print(  # noqa: T201
            f"  {result.node_label}{location}: {result.status.value}"
        )
        for message_ in result.messages:
            print(f"    {message_}")  # noqa: T201

    def _write_documents(
        self, applier: ChangeApplier, project_config: ProjectConfig
    ) -> None:
        sdoc_writer = SDWriter(project_config)
        for path_to_document_, document_ in applier.modified_documents.items():
            if path_to_document_.endswith(".md"):
                from strictdoc.backend.markdown.writer import (  # noqa: PLC0415
                    SDMarkdownWriter,
                )

                SDMarkdownWriter.write_to_file(
                    document_, line_width=project_config.document_line_width
                )
                continue
            document_content = sdoc_writer.write(document_)
            with open(path_to_document_, "w", encoding="utf8") as output_file:
                output_file.write(document_content)

    def _print_summary(
        self, applier: ChangeApplier, results: List[ChangeResult]
    ) -> bool:
        def count(status: ChangeStatus) -> int:
            return sum(1 for result_ in results if result_.status == status)

        applied = count(ChangeStatus.APPLIED)
        already_applied = count(ChangeStatus.ALREADY_APPLIED)
        conflicts = count(ChangeStatus.CONFLICT)
        errors = count(ChangeStatus.ERROR)
        documents = len(applier.modified_documents)
        verb = "Would apply" if self.dry_run else "Applied"
        print(  # noqa: T201
            f"{verb} {applied} change(s) to {documents} document(s). "
            f"Already applied: {already_applied}. "
            f"Conflicts: {conflicts}. Errors: {errors}."
        )
        if self.dry_run:
            print("Dry run: no files were written.")  # noqa: T201
        return conflicts > 0 or errors > 0
