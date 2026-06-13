import argparse
import os
import sys
from typing import Optional, Union

from strictdoc.backend.markdown.writer import SDMarkdownWriter
from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.errors.document_tree_error import DocumentTreeError
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.grammar_element import GrammarElement
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.cli.base_command import BaseCommand, CLIValidationError
from strictdoc.commands.manage_new_config import ManageNewCommandConfig
from strictdoc.core.analyzers.document_stats import DocumentTreeStats
from strictdoc.core.analyzers.document_uid_analyzer import DocumentUIDAnalyzer
from strictdoc.core.file_system.document_finder import DocumentFinder
from strictdoc.core.project_config import ProjectConfigLoader
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.mid import MID
from strictdoc.helpers.parallelizer import Parallelizer


class ManageNewCommand(BaseCommand):
    HELP = "Creates a new node with a unique MID/UID."
    DETAILED_HELP = """\
This command creates a new node with a unique MID and UID in the specified
document. Required fields (as defined by the document grammar) are set to TBD;
non-required fields are left empty.

Use --document-path to select the target document, --parent-uid-or-mid to
select the parent node within that document, or both together. When neither is
provided and the project tree contains exactly one document, the new node is
added to that document's root level.
"""

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "project_root_path",
            type=str,
            help="Path to the project tree root.",
        )
        parser.add_argument(
            "--document-path",
            type=str,
            dest="document_path",
            default=None,
            help=(
                "Path to the specific document where the new node shall be "
                "added."
            ),
        )
        parser.add_argument(
            "--parent-uid-or-mid",
            type=str,
            dest="parent_uid_or_mid",
            default=None,
            help=(
                "UID or MID of the existing document or composite (section) "
                "node that will become the parent of the new node."
            ),
        )
        parser.add_argument(
            "--config",
            type=str,
            help="Path to the StrictDoc TOML config file.",
        )

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.config = ManageNewCommandConfig(**vars(args))

    def run(self, parallelizer: Parallelizer) -> None:  # noqa: ARG002
        manage_config: ManageNewCommandConfig = self.config
        try:
            manage_config.validate()
        except CLIValidationError as exc:
            raise exc

        project_config = ProjectConfigLoader.load_using_manage_new_config(
            manage_config
        )

        parent_uid_or_mid: Optional[str] = manage_config.parent_uid_or_mid
        document_path: Optional[str] = manage_config.document_path
        document_path_abs: Optional[str] = (
            os.path.abspath(document_path)
            if document_path is not None
            else None
        )

        # Phase 1: find and parse all documents.
        document_tree, _ = DocumentFinder.find_sdoc_content(
            project_config=project_config, parallelizer=parallelizer
        )

        # Early exit when neither selector is given: we can report the
        # ambiguity right after documents are found, before building the graph.
        if parent_uid_or_mid is None and document_path_abs is None:
            document_list = document_tree.document_list
            if len(document_list) == 0:
                print(  # noqa: T201
                    "error: The project tree contains no documents."
                )
                sys.exit(1)
            if len(document_list) > 1:
                print(  # noqa: T201
                    "error: The project tree contains more than one document. "
                    "Use --document-path or --parent-uid-or-mid to specify "
                    "the target document or section."
                )
                sys.exit(1)

        # Phase 2: build the traceability graph.
        try:
            traceability_index: TraceabilityIndex = (
                TraceabilityIndexBuilder.create_from_document_tree(
                    document_tree,
                    project_config,
                )
            )
        except DocumentTreeError as exc:
            print(exc.to_print_message())  # noqa: T201
            sys.exit(1)

        # Resolve the parent node.
        parent: Union[SDocDocument, SDocNode]

        if parent_uid_or_mid is not None:
            parent = ManageNewCommand._find_parent(
                traceability_index, parent_uid_or_mid
            )
            # When --document-path is also given, validate that the parent
            # belongs to that document.
            if document_path_abs is not None:
                parent_doc: SDocDocument = (
                    parent
                    if isinstance(parent, SDocDocument)
                    else assert_cast(parent.get_document(), SDocDocument)
                )
                if (
                    parent_doc.meta is None
                    or os.path.abspath(parent_doc.meta.input_doc_full_path)
                    != document_path_abs
                ):
                    print(  # noqa: T201
                        f"error: Node '{parent_uid_or_mid}' is not present in "
                        f"document '{document_path}'."
                    )
                    sys.exit(1)
        elif document_path_abs is not None:
            parent = ManageNewCommand._find_document_by_path(
                traceability_index, document_path_abs, document_path
            )
        else:
            # Single-document case already validated above; take the only doc.
            parent = traceability_index.document_tree.document_list[0]

        # Validate the parent can hold children.
        if isinstance(parent, SDocNode):
            if not parent.is_composite:
                print(  # noqa: T201
                    f"error: Node '{parent_uid_or_mid}' is not a document or "
                    "composite (section) node and cannot hold child nodes."
                )
                sys.exit(1)

        # Determine the document that will be written to disk.
        if isinstance(parent, SDocDocument):
            document: SDocDocument = parent
        else:
            document = parent.get_document()  # type: ignore[assignment]

        if document.meta is None:
            print(  # noqa: T201
                "error: The target document has no file metadata and cannot "
                "be written."
            )
            sys.exit(1)

        if document.autogen:
            print(  # noqa: T201
                "error: The target document is auto-generated and cannot be "
                "modified."
            )
            sys.exit(1)

        # Determine the node type to create (first non-SECTION, non-TEXT
        # grammar element, usually REQUIREMENT).
        assert document.grammar is not None
        node_type: Optional[str] = None
        for element in document.grammar.elements:
            if element.tag not in ("SECTION", "TEXT"):
                node_type = element.tag
                break
        if node_type is None:
            print(  # noqa: T201
                "error: The document grammar has no element type suitable for "
                "creating a new node (no non-SECTION, non-TEXT element found)."
            )
            sys.exit(1)

        # Determine the prefix and generate the next UID.
        grammar_element: GrammarElement = document.grammar.elements_by_type[
            node_type
        ]
        uid_field_name = "UID"
        has_uid_field = uid_field_name in {
            f.title for f in grammar_element.fields
        }

        new_uid: Optional[str] = None
        if has_uid_field:
            prefix: Optional[str] = parent.get_prefix_for_new_node(node_type)
            if prefix is None or len(prefix) == 0:
                prefix = "REQ-"
            document_tree_stats: DocumentTreeStats = (
                DocumentUIDAnalyzer.analyze_document_tree(traceability_index)
            )
            new_uid = document_tree_stats.get_next_requirement_uid(prefix)

        # Build the fields for the new node.
        # - UID: use generated value (if grammar has a UID field)
        # - MID: auto-generated in SDocNode.__init__; set mid_permanent=True
        #        so the writer persists it when enable_mid is set.
        # - Required non-reserved fields: set to "TBD"
        # - Non-required fields: omit
        fields = []

        for gef in grammar_element.fields:
            field_name = gef.title
            if field_name == "MID":
                # MID is handled via reserved_mid; skip here.
                continue
            if field_name == uid_field_name:
                if new_uid is not None:
                    fields.append(
                        SDocNodeField.create_from_string(
                            parent=None,
                            field_name=field_name,
                            field_value=new_uid,
                            multiline=False,
                        )
                    )
                continue
            if gef.required:
                fields.append(
                    SDocNodeField.create_from_string(
                        parent=None,
                        field_name=field_name,
                        field_value="TBD",
                        multiline=False,
                    )
                )

        new_node = SDocNode(
            parent=parent,
            node_type=node_type,
            fields=fields,
            relations=[],
        )
        new_node.ng_document_reference = DocumentReference()
        new_node.ng_document_reference.set_document(document)
        for field in fields:
            field.parent = new_node

        # Attach the new node to the parent.
        parent.section_contents.append(new_node)

        # Write the modified document back to disk.
        doc_filename: str = document.meta.document_filename
        if doc_filename.endswith(".sdoc"):
            document_content = SDWriter(project_config).write(document)
            with open(
                document.meta.input_doc_full_path, "w", encoding="utf8"
            ) as output_file:
                output_file.write(document_content)
        elif doc_filename.endswith(".md"):
            SDMarkdownWriter.write_to_file(document)
        else:
            print(  # noqa: T201
                f"error: Unsupported document format: {doc_filename}"
            )
            sys.exit(1)

        # Report what was created.
        parent_desc: str
        if isinstance(parent, SDocDocument):
            parent_desc = f"document root of '{doc_filename}'"
        elif parent.reserved_uid is not None:
            parent_desc = f"node '{parent.reserved_uid}' in '{doc_filename}'"
        else:
            parent_desc = (
                f"node (MID={parent.reserved_mid}) in '{doc_filename}'"
            )

        uid_info = f"  UID: {new_uid}\n" if new_uid is not None else ""
        print(  # noqa: T201
            f"Created new {node_type} node:\n"
            f"{uid_info}"
            f"  MID: {new_node.reserved_mid}\n"
            f"  Parent: {parent_desc}"
        )

    @staticmethod
    def _find_parent(
        traceability_index: TraceabilityIndex,
        uid_or_mid: str,
    ) -> Union[SDocDocument, SDocNode]:
        # Try UID lookup first (fast graph-database path, then full-scan
        # fallback which also handles document UIDs).
        node = traceability_index.get_linkable_node_by_uid_weak(uid_or_mid)
        if node is None:
            node = traceability_index.get_node_by_uid_weak(uid_or_mid)

        # If not found by UID, try MID lookup.
        if node is None:
            node = traceability_index.get_node_by_mid_weak(MID(uid_or_mid))

        if node is None:
            print(  # noqa: T201
                f"error: No node found with UID or MID '{uid_or_mid}'."
            )
            sys.exit(1)
        if not isinstance(node, (SDocDocument, SDocNode)):
            print(  # noqa: T201
                f"error: Node '{uid_or_mid}' is not a document or requirement "
                "node."
            )
            sys.exit(1)
        return node

    @staticmethod
    def _find_document_by_path(
        traceability_index: TraceabilityIndex,
        document_path_abs: str,
        document_path_display: Optional[str],
    ) -> SDocDocument:
        for doc in traceability_index.document_tree.document_list:
            if doc.meta is None:
                continue
            if (
                os.path.abspath(doc.meta.input_doc_full_path)
                == document_path_abs
            ):
                return doc
        print(  # noqa: T201
            f"error: Document '{document_path_display}' was not found in the "
            "project tree."
        )
        sys.exit(1)
