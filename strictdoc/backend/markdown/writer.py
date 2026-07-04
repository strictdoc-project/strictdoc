import re
from typing import List, Optional, Sequence, Tuple

from strictdoc.backend.markdown.formatter import wrap_md_text
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import (
    DocumentCustomMetadataKeyValuePair,
)
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldType,
    GrammarElementRelationType,
    RequirementFieldType,
)
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    FileReference,
    ParentReqReference,
)
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.helpers.cast import assert_cast


class SDMarkdownWriter:
    @staticmethod
    def write(document: SDocDocument, line_width: Optional[int] = None) -> str:
        top_level_blocks: List[str] = []
        document_meta_block = SDMarkdownWriter._serialize_document_metadata(
            document
        )
        if document_meta_block is not None and len(document_meta_block) > 0:
            top_level_blocks.append(document_meta_block)

        for node in document.section_contents:
            if not isinstance(node, SDocNode):
                continue
            node_block = SDMarkdownWriter._serialize_node(
                node=node,
                heading_level=2,
                line_width=line_width,
            )
            if node_block is None or len(node_block) == 0:
                continue
            top_level_blocks.append(node_block)

        output = "# " + SDMarkdownWriter._to_lf(document.title)
        if len(top_level_blocks) > 0:
            output += "\n\n"
            output += "\n\n".join(top_level_blocks)
        output += "\n"
        return SDMarkdownWriter._to_lf(output)

    @staticmethod
    def write_to_file(
        document: SDocDocument, line_width: Optional[int] = None
    ) -> None:
        document_content = SDMarkdownWriter.write(
            document, line_width=line_width
        )
        document_meta: DocumentMeta = assert_cast(document.meta, DocumentMeta)
        with open(
            document_meta.input_doc_full_path,
            "w",
            encoding="utf8",
        ) as output_file:
            output_file.write(document_content)

    @staticmethod
    def _serialize_document_metadata(
        document: SDocDocument,
    ) -> Optional[str]:
        metadata_entries: List[Tuple[str, str]] = []
        seen_keys = set()

        if (
            document.grammar is not None
            and document.grammar.import_from_file is not None
        ):
            metadata_entries.append(
                ("Grammar", document.grammar.import_from_file)
            )
            seen_keys.add("GRAMMAR")

        custom_metadata = document.config.custom_metadata
        if custom_metadata is not None:
            for entry in custom_metadata.entries:
                if (
                    not isinstance(entry, DocumentCustomMetadataKeyValuePair)
                    or entry.key is None
                    or entry.value is None
                ):
                    continue
                metadata_entries.append((entry.key, entry.value))
                seen_keys.add(entry.key.upper())

        default_config_entries: Sequence[Tuple[str, Optional[str]]] = (
            ("UID", document.config.uid),
            ("VERSION", document.config.version),
            ("DATE", document.config.date),
            ("CLASSIFICATION", document.config.classification),
            ("PREFIX", document.config.requirement_prefix),
        )
        for entry_key, entry_value in default_config_entries:
            if entry_value is None or entry_key in seen_keys:
                continue
            metadata_entries.append((entry_key, entry_value))
            seen_keys.add(entry_key)

        if len(metadata_entries) == 0:
            return None
        return SDMarkdownWriter._serialize_meta_fields(metadata_entries)

    @staticmethod
    def _serialize_node(
        node: SDocNode,
        heading_level: int,
        line_width: Optional[int] = None,
    ) -> Optional[str]:
        if node.autogen:
            return None

        if node.node_type == "TEXT":
            return SDMarkdownWriter._serialize_text_node(
                node, line_width=line_width
            )

        if node.reserved_title is None:
            return None

        heading_hashes = "#" * max(1, heading_level)
        heading_text = (
            f"{heading_hashes} {SDMarkdownWriter._to_lf(node.reserved_title)}"
        )

        body_blocks: List[str] = []
        own_fields_block = SDMarkdownWriter._serialize_node_fields(
            node, line_width=line_width
        )
        if own_fields_block is not None and len(own_fields_block) > 0:
            body_blocks.append(own_fields_block)

        for child_node in node.section_contents:
            if isinstance(child_node, SDocNode):
                child_block = SDMarkdownWriter._serialize_node(
                    node=child_node,
                    heading_level=heading_level + 1,
                    line_width=line_width,
                )
                if child_block is None or len(child_block) == 0:
                    continue
                body_blocks.append(child_block)

        if len(body_blocks) == 0:
            return heading_text

        return heading_text + "\n\n" + "\n\n".join(body_blocks)

    @staticmethod
    def _serialize_node_fields(
        node: SDocNode, line_width: Optional[int] = None
    ) -> Optional[str]:
        meta_fields: List[Tuple[str, str]] = []
        content_fields: List[Tuple[str, str]] = []

        document = node.get_document()
        document_grammar = None
        element = None
        if document is not None and document.grammar is not None:
            document_grammar = assert_cast(document.grammar, DocumentGrammar)
            element = document_grammar.elements_by_type.get(
                node.node_type, None
            )

        # Determine whether MID will be auto-injected for this node (MD-24).
        # The default grammar also carries MID, so guard with is_default to
        # avoid injecting MID into plain Markdown documents.
        should_inject_mid = (
            document_grammar is not None
            and not document_grammar.is_default
            and element is not None
            and "MID" in element.fields_map
            and "MID" not in node.ordered_fields_lookup
        )

        # Emit TYPE for every non-TEXT node when:
        # - the grammar defines element types beyond the built-in set (MD-26), OR
        # - a SECTION node carries a MID field (MD-24): TYPE: SECTION must
        #   accompany the MID on every write so the reader does not misidentify
        #   the heading as a REQUIREMENT on re-read.
        section_has_mid = node.node_type == "SECTION" and (
            should_inject_mid or "MID" in node.ordered_fields_lookup
        )
        if (
            document_grammar is not None
            and node.node_type != "TEXT"
            and (document_grammar.has_custom_elements() or section_has_mid)
        ):
            meta_fields.append(("TYPE", node.node_type))

        if should_inject_mid:
            meta_fields.append(("MID", node.reserved_mid))

        for field in node.enumerate_fields():
            if field.field_name == "TITLE":
                continue

            field_name = field.field_name
            field_human_name = SDMarkdownWriter._resolve_human_field_name(
                node=node, field_name=field_name
            )
            field_value = SDMarkdownWriter._to_lf(field.get_text_value())

            if element is None or field_name not in element.fields_map:
                is_content_field = field.is_multiline() or (
                    SDMarkdownWriter._is_multi_paragraph(field_value)
                )
            else:
                is_content_field = element.is_field_multiline(field_name)

            if is_content_field:
                content_fields.append((field_human_name, field_value))
            else:
                meta_fields.append((field_human_name, field_value))

        relations_block = SDMarkdownWriter._serialize_relations(node)

        field_blocks: List[str] = []
        if len(meta_fields) > 0:
            field_blocks.append(
                SDMarkdownWriter._serialize_meta_fields(meta_fields)
            )
        if relations_block is not None:
            relations_field_block = f"**Relations**:\n{relations_block}"
            if len(meta_fields) > 0:
                field_blocks[-1] = (
                    f"{field_blocks[-1]}\n{relations_field_block}"
                )
            else:
                field_blocks.append(relations_field_block)
        if len(content_fields) > 0:
            field_blocks.append(
                SDMarkdownWriter._serialize_content_fields(
                    content_fields, line_width=line_width
                )
            )

        if len(field_blocks) == 0:
            return None
        return "\n\n".join(field_blocks)

    @staticmethod
    def _serialize_relations(node: SDocNode) -> Optional[str]:
        """
        Serialize all relations to a multiline dict-list block.

        Returns the block *value* (the bullet list), or None when there are no
        relations. The caller emits the **Relations** header directly after the
        metadata block, without an empty line.
        """
        if len(node.relations) == 0:
            return None

        item_lines: List[str] = []
        for relation in node.relations:
            if isinstance(relation, ParentReqReference):
                item = SDMarkdownWriter._serialize_relation_dict(
                    kv=[
                        ("Type", "Parent"),
                        ("ID", relation.ref_uid),
                        ("Role", relation.role),
                    ]
                )
            elif isinstance(relation, ChildReqReference):
                item = SDMarkdownWriter._serialize_relation_dict(
                    kv=[
                        ("Type", "Child"),
                        ("ID", relation.ref_uid),
                        ("Role", relation.role),
                    ]
                )
            elif isinstance(relation, FileReference):
                entry = relation.g_file_entry
                item = SDMarkdownWriter._serialize_relation_dict(
                    kv=[
                        ("Type", "File"),
                        ("Path", entry.g_file_path),
                        ("Lines", entry.g_line_range),
                        ("Element", entry.element),
                        ("ID", entry.id),
                        ("Hash", entry.hash),
                    ]
                )
            else:
                continue
            if item is not None:
                item_lines.append(item)

        if not item_lines:
            return None
        return "\n".join(item_lines)

    @staticmethod
    def _serialize_relation_dict(
        kv: List[Tuple[str, Optional[str]]],
    ) -> Optional[str]:
        """
        Serialize one relation as a bullet-list dict item.

        Continuation lines are indented by 2 spaces (aligning with the first
        key character after the ``- `` marker) per SDOC-LLR-211.
        Optional key-value pairs with a None value are omitted.
        """
        pairs = [(k, v) for k, v in kv if v is not None]
        if len(pairs) == 0:
            return None

        lines: List[str] = []
        for i, (key, value) in enumerate(pairs):
            entry = f"**{key}**: `{value}`"
            if i == 0:
                prefix = "- "
            else:
                prefix = "  "
            if i < len(pairs) - 1:
                lines.append(f"{prefix}{entry} \\")
            else:
                lines.append(f"{prefix}{entry}")
        return "\n".join(lines)

    @staticmethod
    def _resolve_human_field_name(node: SDocNode, field_name: str) -> str:
        document = node.get_document()
        if document is None or document.grammar is None:
            return field_name
        grammar = assert_cast(document.grammar, DocumentGrammar)
        # For imported (custom) grammars, always write the field key name so
        # that the reader can recover it via .upper(). Human titles in custom
        # grammars are arbitrary strings (e.g. "Example Human Title" for key
        # "DERIVED_RATIONALE") and do not round-trip through the reader's
        # name.upper() normalisation. For the built-in default grammar the
        # human title is always a simple capitalisation variant of the key
        # (e.g. "Statement" for "STATEMENT"), so .upper() recovers it safely.
        if grammar.import_from_file is not None:
            return field_name
        element = grammar.elements_by_type.get(node.node_type, None)
        if element is None:
            return field_name
        if field_name not in element.fields_map:
            return field_name
        return element.fields_map[field_name].get_field_human_name()

    @staticmethod
    def _serialize_text_node(
        node: SDocNode, line_width: Optional[int] = None
    ) -> Optional[str]:
        statement_fields = node.ordered_fields_lookup.get("STATEMENT", None)
        if statement_fields is None or len(statement_fields) == 0:
            return None
        statement_value = SDMarkdownWriter._to_lf(
            statement_fields[0].get_text_value()
        ).strip("\n")
        if line_width is not None:
            statement_value = wrap_md_text(statement_value, line_width)

        # When the grammar's TEXT element declares a MID field, emit
        # **TYPE**: TEXT \ **MID**: <mid> before the statement body so that
        # the TEXT node's machine identifier is preserved across read/write cycles.
        document = node.get_document()
        if document is not None and document.grammar is not None:
            grammar = assert_cast(document.grammar, DocumentGrammar)
            text_element = grammar.elements_by_type.get("TEXT", None)
            if (
                text_element is not None
                and "MID" in text_element.fields_map
                and not grammar.is_default
            ):
                existing_mid_fields = node.ordered_fields_lookup.get(
                    "MID", None
                )
                if existing_mid_fields:
                    mid_str = existing_mid_fields[0].get_text_value()
                else:
                    mid_str = str(node.reserved_mid)
                meta_block = SDMarkdownWriter._serialize_meta_fields(
                    [("TYPE", "TEXT"), ("MID", mid_str)]
                )
                if len(statement_value) > 0:
                    return f"{meta_block}\n\n{statement_value}"
                return meta_block

        return statement_value

    @staticmethod
    def _serialize_meta_fields(
        fields: Sequence[Tuple[str, str]],
    ) -> str:
        lines: List[str] = []
        field_count = len(fields)
        for field_index, (field_name, field_value) in enumerate(fields):
            value = SDMarkdownWriter._meta_value_to_single_line(field_value)
            suffix = " \\" if field_index < field_count - 1 else ""
            lines.append(f"**{field_name}**: {value}{suffix}")
        return "\n".join(lines)

    @staticmethod
    def _serialize_content_fields(
        fields: Sequence[Tuple[str, str]],
        line_width: Optional[int] = None,
    ) -> str:
        output_blocks: List[str] = []
        for field_name, field_value in fields:
            output_blocks.append(
                SDMarkdownWriter._serialize_single_content_field(
                    field_name, field_value, line_width=line_width
                )
            )
        return "\n\n".join(output_blocks)

    # Lines that start with a Markdown structural element — these cannot follow
    # a field name on the same line, so they force the block format.
    _MD_BLOCK_START_RE = re.compile(
        r"^("
        r"[-*+] "  # unordered list
        r"|\d+[.)]\s"  # ordered list
        r"|#{1,6} "  # ATX heading
        r"|`{3}"  # fenced code block
        r"|~{3}"  # fenced code block (tilde)
        r"|>"  # blockquote
        r"|\|"  # table cell
        r"|\s"  # indented block
        r")"
    )

    @staticmethod
    def _serialize_single_content_field(
        field_name: str,
        field_value: str,
        line_width: Optional[int] = None,
    ) -> str:
        normalized_value = SDMarkdownWriter._to_lf(field_value).strip("\n")
        if line_width is not None:
            normalized_value = wrap_md_text(normalized_value, line_width)
        if len(normalized_value) == 0:
            return f"**{field_name}**:"
        use_block = SDMarkdownWriter._is_multi_paragraph(
            normalized_value
        ) or SDMarkdownWriter._MD_BLOCK_START_RE.match(normalized_value)
        if use_block:
            return f"**{field_name}**:\n\n{normalized_value}"
        return f"**{field_name}**: {normalized_value}"

    @staticmethod
    def _meta_value_to_single_line(field_value: str) -> str:
        normalized = SDMarkdownWriter._to_lf(field_value)
        return re.sub(r"\s*\n\s*", " ", normalized).strip()

    @staticmethod
    def _is_multi_paragraph(field_value: str) -> bool:
        return re.search(r"\n[ \t]*\n", field_value) is not None

    @staticmethod
    def _to_lf(value: str) -> str:
        return value.replace("\r\n", "\n").replace("\r", "\n")


class MarkdownGrammarWriter:
    @staticmethod
    def write(grammar: DocumentGrammar) -> str:
        output_blocks: List[str] = ["# StrictDoc Markdown Grammar"]

        for element in grammar.elements:
            element_lines = [f"## Element: {element.tag}"]
            element_properties: List[Tuple[str, str]] = []
            if element.property_is_composite is not None:
                element_properties.append(
                    (
                        "Composite",
                        "True" if element.property_is_composite else "False",
                    )
                )
            if element.property_prefix is not None:
                element_properties.append(("Prefix", element.property_prefix))
            if element.property_view_style is not None:
                element_properties.append(
                    ("View Style", element.property_view_style)
                )
            if len(element_properties) > 0:
                element_lines.append(
                    MarkdownGrammarWriter._serialize_properties(
                        element_properties
                    )
                )

            for field in element.fields:
                element_lines.append(
                    MarkdownGrammarWriter._serialize_field(field)
                )

            if len(element.relations) > 0:
                relation_blocks = [
                    MarkdownGrammarWriter._serialize_relation(relation)
                    for relation in element.relations
                ]
                element_lines.append(
                    "### Relations\n\n" + "\n\n".join(relation_blocks)
                )

            output_blocks.append("\n\n".join(element_lines))

        return "\n\n".join(output_blocks) + "\n"

    @staticmethod
    def write_to_file(grammar: DocumentGrammar, file_path: str) -> None:
        with open(file_path, "w", encoding="utf8") as output_file:
            output_file.write(MarkdownGrammarWriter.write(grammar))

    @staticmethod
    def _serialize_field(field: GrammarElementFieldType) -> str:
        field_properties = [
            ("Type", MarkdownGrammarWriter._serialize_field_type(field)),
            ("Required", "True" if field.required else "False"),
        ]
        if field.human_title is not None:
            field_properties.insert(1, ("Human Title", field.human_title))
        return (
            f"### Field: {field.title}\n\n"
            + MarkdownGrammarWriter._serialize_properties(field_properties)
        )

    @staticmethod
    def _serialize_field_type(field: GrammarElementFieldType) -> str:
        if field.gef_type == RequirementFieldType.SINGLE_CHOICE:
            assert isinstance(field, GrammarElementFieldSingleChoice)
            return f"SingleChoice({', '.join(field.options)})"
        if field.gef_type == RequirementFieldType.MULTIPLE_CHOICE:
            assert isinstance(field, GrammarElementFieldMultipleChoice)
            return f"MultipleChoice({', '.join(field.options)})"
        return field.gef_type

    @staticmethod
    def _serialize_relation(relation: GrammarElementRelationType) -> str:
        output = f"#### Relation: {relation.relation_type}"
        properties: List[Tuple[str, str]] = []
        if relation.relation_role is not None:
            properties.append(("Role", relation.relation_role))
        if relation.reverse_relation_role is not None:
            properties.append(("Reverse Role", relation.reverse_relation_role))
        if len(properties) > 0:
            output += "\n\n" + MarkdownGrammarWriter._serialize_properties(
                properties
            )
        return output

    @staticmethod
    def _serialize_properties(fields: List[Tuple[str, str]]) -> str:
        return "\n".join(
            f"**{field_name}**: {field_value}"
            for field_name, field_value in fields
        )
