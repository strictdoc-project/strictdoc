import argparse
import os
from typing import List, cast

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.cli.base_command import CLIValidationError
from strictdoc.commands.convert_config import ConvertCommandConfig
from strictdoc.core.format import Format
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.timing import timing_decorator


def _find_format_by_handle(
    project_config: ProjectConfig, handle: str
) -> Format:
    for format_ in project_config.formats:
        if handle in format_.handles():
            return format_
    raise CLIValidationError(f"Unknown format: '{handle}'.")


def _discover_input_format_handle(
    project_config: ProjectConfig, input_path: str
) -> str:
    _, extension = os.path.splitext(input_path)
    for format_ in project_config.formats:
        if not format_.supports_import():
            continue
        handle = format_.handle_for_extension(extension)
        if handle is not None:
            return handle
    raise CLIValidationError(
        f"Cannot auto-discover the input format from the extension "
        f"'{extension}' of '{input_path}'. Pass --input-format explicitly."
    )


class ConvertAction:
    @staticmethod
    @timing_decorator("Convert")
    def do_convert(
        args: argparse.Namespace,
        convert_config: ConvertCommandConfig,
        project_config: ProjectConfig,
    ) -> None:
        input_format_handle = (
            convert_config.input_format
            if convert_config.input_format is not None
            else _discover_input_format_handle(
                project_config, convert_config.input_path
            )
        )
        input_format = _find_format_by_handle(
            project_config, input_format_handle
        )
        if not input_format.supports_import():
            raise CLIValidationError(
                f"Format '{input_format_handle}' does not support being a "
                f"convert input format."
            )

        output_format = _find_format_by_handle(
            project_config, convert_config.output_format
        )
        if not output_format.supports_convert_output():
            raise CLIValidationError(
                f"Format '{convert_config.output_format}' does not support "
                f"being a convert output format."
            )

        import_options = input_format.build_import_options(args)
        result = input_format.import_file(import_options, project_config)
        documents: List[SDocDocument] = (
            cast(List[SDocDocument], result)
            if isinstance(result, list)
            else [cast(SDocDocument, result)]
        )

        for document_ in documents:
            filename_stem = input_format.import_output_filename_stem(
                document_, convert_config
            )
            output_format.write_converted_document(
                document_,
                convert_config.output_path,
                filename_stem,
                project_config,
            )
