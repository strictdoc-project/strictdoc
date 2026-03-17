import argparse
import os
import re
import sys
from pathlib import Path
from typing import Set

from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.cli.base_command import BaseCommand, CLIValidationError
from strictdoc.commands.manage_assets_config import ManageAssetsCommandConfig
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.rst.directives.wildcard_enhanced_image import (
    WildcardEnhancedImage,
)
from strictdoc.helpers.parallelizer import Parallelizer


class ManageAssetsCommand(BaseCommand):
    HELP = "Manages project assets (images, attachments)."
    DETAILED_HELP = """\
This command helps manage assets in a StrictDoc project.
It can scan for orphaned assets that are no longer referenced by any document
and optionally delete them to keep the repository clean.
"""

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        command_parser = parser

        command_parser.add_argument(
            "input_path",
            type=str,
            help="Path to the project tree.",
        )
        command_parser.add_argument(
            "--clean-unused",
            action="store_true",
            help="If provided, unused assets will be permanently deleted.",
        )
        command_parser.add_argument(
            "--config",
            type=str,
            help="Path to the StrictDoc TOML config file.",
        )

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.config = ManageAssetsCommandConfig(**vars(args))

    def run(self, parallelizer: Parallelizer) -> None:
        try:
            self.config.validate()
        except CLIValidationError as exception_:
            raise exception_

        project_config = ProjectConfigLoader.load_using_manage_assets_config(
            self.config
        )

        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create(
                    project_config=project_config,
                    parallelizer=parallelizer,
                )
            )
        except DocumentTreeError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)

        physical_assets: Set[str] = self._find_physical_assets(
            self.config.input_path, project_config
        )
        referenced_assets: Set[str] = self._find_referenced_assets(
            traceability_index, project_config
        )

        # Calculate unused assets
        # We check if the physical path ends with the referenced path.
        unused_assets = []
        for physical_path in physical_assets:
            is_used = False

            physical_base_posix = Path(physical_path).with_suffix("").as_posix()

            for ref in referenced_assets:
                normalized_ref = ref.replace("@assets", "_assets")

                if normalized_ref.endswith(".*"):
                    # Remove the '.*' from a wildcard enhanced image directive
                    ref_base = normalized_ref[:-2]
                    # Check if the extension-less physical path ends with the reference base
                    if physical_base_posix.endswith(ref_base):
                        is_used = True
                        break
                else:
                    # Standard exact match check
                    if physical_path.endswith(normalized_ref):
                        is_used = True
                        break

            if not is_used:
                unused_assets.append(physical_path)

        if not unused_assets:
            print("No unused assets found. Your project is clean!")  # noqa: T201
            return

        print(f"Found {len(unused_assets)} unused asset(s):")  # noqa: T201
        for asset_str in unused_assets:
            print(f" - {asset_str}")  # noqa: T201

        if self.config.clean_unused:
            print("Deleting unused assets...")  # noqa: T201
            for asset_str in unused_assets:
                asset: Path = Path(asset_str)
                try:
                    os.remove(asset)
                    print(f"Deleted: {asset}")  # noqa: T201
                    if not any(asset.parent.iterdir()):
                        asset.parent.rmdir()
                        print(f"Deleted: {asset.parent}")  # noqa: T201
                except OSError as e:
                    print(f"Error deleting {asset}: {e}")  # noqa: T201
            print("Cleanup complete.")  # noqa: T201
        else:
            print("")  # noqa: T201
            print("Run with --clean-unused to delete these files.")  # noqa: T201

    def _find_referenced_assets(
        self,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
    ) -> Set[str]:
        """Scans the raw document text to extract referenced asset paths."""
        referenced_assets: set[str] = set()

        # Regex to catch ReST image directive
        # e.g., .. image:: ./_assets/0011223344556677889900aabbccddeeff/picture.svg
        asset_regex = re.compile(r"(?:image)\s*::\s*[^\s]*?([@_]assets/[^\s]+)")

        for document in traceability_index.document_tree.document_list:
            # Convert the entire document AST back into its raw string representation
            document_content = SDWriter(project_config).write(document)

            self._extract_assets_from_text(
                document_content, asset_regex, referenced_assets
            )

        return referenced_assets

    def _find_physical_assets(
        self, base_path: str, project_config: ProjectConfig
    ) -> Set[str]:
        """Scans the file system for files residing in _assets directories."""
        physical_assets = set()
        path_obj = Path(base_path).resolve()

        # Get the exact output directory from StrictDoc's config
        output_dir = Path(project_config.output_dir)
        if not output_dir.is_absolute():
            output_dir = (path_obj / output_dir).resolve()
        else:
            output_dir = output_dir.resolve()

        template_dir = None
        if project_config.html2pdf_template is not None:
            template_dir = Path(project_config.html2pdf_template).parent
            if not template_dir.is_absolute():
                template_dir = (path_obj / template_dir).resolve()
            else:
                template_dir = output_dir.resolve()

        # Scan for _asset directories
        for asset_file in path_obj.rglob("_assets/**/*"):
            if asset_file.is_file():
                resolved_asset = asset_file.resolve()

                # skip extensions that are not images
                if (
                    asset_file.suffix.lstrip(".").lower()
                    not in WildcardEnhancedImage.WILDCARD_EXTENSIONS
                ):
                    continue
                # Skip if the asset lives anywhere inside the configured output directory
                if output_dir in resolved_asset.parents:
                    continue
                # Skip if the asset lives anywhere inside the configured template
                if (
                    template_dir is not None
                    and template_dir in resolved_asset.parents
                ):
                    continue

                # Store as posix path for easy regex comparison later
                physical_assets.add(asset_file.as_posix())

        return physical_assets

    def _extract_assets_from_text(
        self, text: str, regex: re.Pattern[str], output_set: Set[str]
    ) -> None:
        if not text:
            return
        matches = regex.findall(text)
        for match in matches:
            # Normalize path (remove trailing spaces, newlines, etc.)
            output_set.add(match.strip())
