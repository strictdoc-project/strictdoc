import argparse
import sys

from strictdoc.backend.markdown.writer import SDMarkdownWriter
from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.cli.base_command import BaseCommand, CLIValidationError
from strictdoc.commands.format_config import FormatCommandConfig
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.helpers.parallelizer import Parallelizer


class FormatCommand(BaseCommand):
    """
    @relation(SDOC-SRS-212, SDOC-SRS-213, scope=class)
    """

    HELP = "Format SDoc and Markdown documents."
    DETAILED_HELP = """\
This command reads all SDoc and Markdown documents in the project tree and
writes them back formatted:

- The command aligns the misaligned RST grid tables and Markdown pipe tables.
- The command wraps the text according to the project's `document_line_width`
  configuration option (set in strictdoc_config.py).

If `document_line_width` is not configured, the command does not wrap the text.
"""

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "input_path",
            type=str,
            help="Path to the project tree.",
        )
        parser.add_argument(
            "--config",
            type=str,
            help="Path to the StrictDoc TOML config file.",
        )

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.config: FormatCommandConfig = FormatCommandConfig(**vars(args))

    def run(self, parallelizer: Parallelizer) -> None:
        format_config: FormatCommandConfig = self.config
        try:
            format_config.validate()
        except CLIValidationError as exception_:
            raise exception_

        project_config: ProjectConfig = (
            ProjectConfigLoader.load_using_format_config(format_config)
        )

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

        line_width = project_config.document_line_width
        sdoc_writer = SDWriter(project_config, format_tables=True)

        for document in traceability_index.document_tree.document_list:
            assert document.meta is not None

            if document.autogen:
                continue

            filename = document.meta.document_filename
            if filename.endswith(".sdoc"):
                document_content = sdoc_writer.write(document)
                with open(
                    document.meta.input_doc_full_path, "w", encoding="utf8"
                ) as output_file:
                    output_file.write(document_content)
            elif filename.endswith(".md"):
                SDMarkdownWriter.write_to_file(
                    document, line_width=line_width, format_tables=True
                )
