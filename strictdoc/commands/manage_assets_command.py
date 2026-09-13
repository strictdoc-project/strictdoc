import argparse
import os
import re
import sys
from pathlib import Path
from typing import Set

from strictdoc.backend.rst.directives.wildcard_enhanced_image import (
    WildcardEnhancedImage,
)
from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.cli.base_command import BaseCommand, CLIValidationError
from strictdoc.commands.manage_assets_config import ManageAssetsCommandConfig
from strictdoc.core.asset_manager import AssetManager
from strictdoc.core.project_config import ProjectConfig, ProjectConfigLoader
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.helpers.parallelizer import Parallelizer


class ManageAssetsCommand(BaseCommand):
    """
    Identify and remove orphaned assets, and asset folders.

    @relation(SDOC-LLR-217, scope=class)
    """

    HELP = "Manages project assets (images)."
    DETAILED_HELP = """\
This command helps manage assets in a StrictDoc project.
It can scan for orphaned images that are no longer referenced by any document
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
            "--clean-unused-images",
            action="store_true",
            help="If provided, unused images will be permanently deleted.",
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

        assert traceability_index.asset_manager is not None
        physical_assets: Set[str] = self._find_physical_assets(
            traceability_index.asset_manager
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
                if ref.endswith(".*"):
                    # Remove the '.*' from a wildcard enhanced image directive
                    ref_base = ref[:-2]
                    # Check if the extension-less physical path ends with the reference base
                    if physical_base_posix.endswith(ref_base):
                        is_used = True
                        break
                else:
                    # Standard exact match check
                    if physical_path.endswith(ref):
                        is_used = True
                        break

            if not is_used:
                unused_assets.append(physical_path)

        if not unused_assets:
            print("No unused images found. Your project is clean!")  # noqa: T201
            return

        print(f"Found {len(unused_assets)} unused image(s):")  # noqa: T201
        for asset_str in unused_assets:
            print(f" - {asset_str}")  # noqa: T201

        if self.config.clean_unused_images:
            self._delete_unused_assets(unused_assets)
        else:
            print("")  # noqa: T201
            print("Run with --clean-unused-images to delete these files.")  # noqa: T201

    def _delete_unused_assets(self, unused_assets: list[str]) -> None:
        print("Deleting unused images...")  # noqa: T201
        deleted_assets: list[Path] = []
        failed_assets: list[tuple[Path, OSError]] = []
        for asset_str in unused_assets:
            asset = Path(asset_str)
            try:
                os.remove(asset)
                deleted_assets.append(asset)
                print(f"Deleted: {asset.as_posix()}")  # noqa: T201
                if not any(asset.parent.iterdir()):
                    asset.parent.rmdir()
                    print(  # noqa: T201
                        f"Deleted: {asset.parent.as_posix()}"
                    )
            except OSError as exception_:
                failed_assets.append((asset, exception_))
                print(  # noqa: T201
                    f"Could not delete {asset.as_posix()}: {exception_}"
                )

        print(  # noqa: T201
            f"Cleanup complete: {len(deleted_assets)} deleted, "
            f"{len(failed_assets)} failed."
        )

    def _find_referenced_assets(
        self,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
    ) -> Set[str]:
        """Scans the raw document text to extract paths of referenced images."""
        referenced_assets: set[str] = set()

        # Regex to catch image directive
        # e.g., .. image:: ./_assets/0011223344556677889900aabbccddeeff/picture.svg
        #       <img src="./_assets/0011223344556677889900aabbccddeeff/picture.svg" />
        #       ![](./_assets/0011223344556677889900aabbccddeeff/picture.svg)
        #       ![](_assets/0011223344556677889900aabbccddeeff/picture.svg)
        asset_regex = re.compile(
            r"(image::\s+|src=\"|\]\()"
            r"(?:\./)?(_assets/[^\s'\"\)\]>]+)"
        )

        for document in traceability_index.document_tree.document_list:
            # Convert the entire document AST back into its raw string representation
            document_content = SDWriter(project_config).write(document)

            self._extract_assets_from_text(
                document_content, asset_regex, referenced_assets
            )

        return referenced_assets

    def _find_physical_assets(self, asset_manager: AssetManager) -> Set[str]:
        """Finds image files in asset directories registered for the project."""
        physical_assets: Set[str] = set()

        # Scan registered _assets directories
        for asset_dir_ in asset_manager.iterate():
            for asset_file_ in Path(asset_dir_.full_path).rglob("*"):
                if not asset_file_.is_file():
                    continue

                # skip extensions that are not images
                if (
                    asset_file_.suffix.lstrip(".").lower()
                    not in WildcardEnhancedImage.WILDCARD_EXTENSIONS
                ):
                    continue

                # Store as posix path for easy regex comparison later
                physical_assets.add(asset_file_.as_posix())

        return physical_assets

    def _extract_assets_from_text(
        self, text: str, regex: re.Pattern[str], output_set: Set[str]
    ) -> None:
        if not text:
            return

        for match in regex.finditer(text):
            extracted_path = match.group(2)
            output_set.add(extracted_path.strip())
