"""
Example of a user-defined custom Format, registered via a project's own
`strictdoc_config.py` (see the sibling file in this directory), that lets
StrictDoc convert between SDoc and a simple flat CSV representation in both
directions: `strictdoc convert` (CSV -> SDoc) and `strictdoc export
--formats=csv` (SDoc -> CSV, the tree-wide direction, same as any other
export format).

This is intentionally minimal: it only supports a document made of
top-level sections directly containing requirements (UID/TITLE/STATEMENT),
no nested sections, no custom grammar. That's enough to demonstrate the
extension points a real custom Format would use:

- add_import_arguments()/build_import_options(): own CLI flags for
  `strictdoc convert`, parsed into a type-safe, format-owned dataclass.
- import_file(): parses the external format into an in-memory SDocDocument.
- export_complete_tree(): the reverse direction, writing the whole document
  tree out in this format, the same extension point HTML/Excel/ReqIF/etc.
  use for `strictdoc export`.

None of this requires any change to StrictDoc's core Format/Convert/Export
machinery -- a new Format only ever touches its own module.
"""

import argparse
import csv
import os
from dataclasses import dataclass
from typing import List

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory
from strictdoc.core.format import ExportContext, Format
from strictdoc.core.project_config import ProjectConfig

CSV_FIELDNAMES = ["TYPE", "PARENT_SECTION", "UID", "TITLE", "STATEMENT"]


@dataclass
class CSVImportOptions:
    input_path: str


def _write_csv(document: SDocDocument, path_to_csv: str) -> None:
    with open(path_to_csv, "w", newline="", encoding="utf8") as csv_file:
        writer = csv.DictWriter(
            csv_file, fieldnames=CSV_FIELDNAMES, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerow(
            {
                "TYPE": "DOCUMENT",
                "PARENT_SECTION": "",
                "UID": "",
                "TITLE": document.title,
                "STATEMENT": "",
            }
        )
        for node in document.section_contents:
            if not isinstance(node, SDocNode) or node.node_type != "SECTION":
                continue
            section_title = node.reserved_title or ""
            writer.writerow(
                {
                    "TYPE": "SECTION",
                    "PARENT_SECTION": "",
                    "UID": "",
                    "TITLE": section_title,
                    "STATEMENT": "",
                }
            )
            for child in node.section_contents:
                if (
                    not isinstance(child, SDocNode)
                    or child.node_type != "REQUIREMENT"
                ):
                    continue
                statement = child.reserved_statement or ""
                writer.writerow(
                    {
                        "TYPE": "REQUIREMENT",
                        "PARENT_SECTION": section_title,
                        "UID": child.reserved_uid or "",
                        "TITLE": child.reserved_title or "",
                        # Multiline fields are stored/returned with a
                        # trailing newline (see ensure_newline() usage
                        # around STATEMENT fields); strip it so a
                        # single-line STATEMENT round-trips byte-for-byte.
                        "STATEMENT": statement.rstrip("\n"),
                    }
                )


class CSVFormat(Format):
    @staticmethod
    def handles() -> List[str]:
        return ["csv"]

    @staticmethod
    def supported_extensions() -> List[str]:
        return [".csv"]

    @staticmethod
    def supports_import() -> bool:
        return True

    @staticmethod
    def supports_export() -> bool:
        return True

    @staticmethod
    def supports_read() -> bool:
        return False

    @staticmethod
    def supports_grammar() -> bool:
        return False

    def export_complete_tree(self, context: ExportContext, handle: str) -> None:
        assert handle in self.handles(), handle
        output_csv_root = os.path.join(context.project_config.output_dir, "csv")
        for document in context.traceability_index.document_tree.document_list:
            assert document.meta
            path_to_output_dir = os.path.join(
                output_csv_root,
                document.meta.input_doc_dir_rel_path.relative_path,
            )
            os.makedirs(path_to_output_dir, exist_ok=True)
            path_to_csv = os.path.join(
                path_to_output_dir,
                f"{document.meta.document_filename_base}.csv",
            )
            _write_csv(document, path_to_csv)

    @classmethod
    def add_import_arguments(
        cls,
        parser: argparse.ArgumentParser,  # noqa: ARG003
    ) -> None:
        # CSV needs no format-specific flags beyond the generic input_path/
        # output_path already added by `convert` itself.
        return

    @classmethod
    def build_import_options(cls, args: argparse.Namespace) -> CSVImportOptions:
        return CSVImportOptions(input_path=args.input_path)

    def import_file(  # type: ignore[override]
        self,
        import_options: CSVImportOptions,
        project_config: ProjectConfig,  # noqa: ARG002
    ) -> SDocDocument:
        with open(
            import_options.input_path, newline="", encoding="utf8"
        ) as csv_file:
            rows = list(csv.DictReader(csv_file))

        document_title = "NONAME"
        if rows and rows[0]["TYPE"] == "DOCUMENT":
            document_title = rows[0]["TITLE"]
            rows = rows[1:]

        document = SDocObjectFactory.create_document(document_title)
        document.grammar = DocumentGrammar.create_default(document)

        current_section = None
        for row in rows:
            if row["TYPE"] == "SECTION":
                section = SDocNode.create_section(
                    document, document, row["TITLE"]
                )
                document.section_contents.append(section)
                current_section = section
            elif row["TYPE"] == "REQUIREMENT":
                assert current_section is not None, (
                    "REQUIREMENT row with no preceding SECTION row."
                )
                requirement = SDocObjectFactory.create_requirement(
                    parent=current_section,
                    node_type="REQUIREMENT",
                    uid=row["UID"] or None,
                    title=row["TITLE"] or None,
                    statement_multiline=row["STATEMENT"] or None,
                )
                current_section.section_contents.append(requirement)

        return document
