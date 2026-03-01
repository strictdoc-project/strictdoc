import re
from typing import List, Optional, Sequence, Tuple

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import (
    DocumentCustomMetadataKeyValuePair,
)
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.reference import ParentReqReference
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.helpers.cast import assert_cast


class SDMarkdownWriter:
    default_meta_style = "backslash"
    allowed_meta_styles = {"bullet", "backslash", "two_spaces"}

    @staticmethod
    def write(document: SDocDocument) -> str:
        meta_style = SDMarkdownWriter._resolve_meta_style(document)

        top_level_blocks: List[str] = []
        document_meta_block = SDMarkdownWriter._serialize_document_metadata(
            document, meta_style
        )
        if document_meta_block is not None and len(document_meta_block) > 0:
            top_level_blocks.append(document_meta_block)

        for node in document.section_contents:
            if not isinstance(node, SDocNode):
                continue
            node_block = SDMarkdownWriter._serialize_node(
                node=node,
                heading_level=2,
                meta_style=meta_style,
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
    def write_to_file(document: SDocDocument) -> None:
        document_content = SDMarkdownWriter.write(document)
        document_meta: DocumentMeta = assert_cast(document.meta, DocumentMeta)
        with open(
            document_meta.input_doc_full_path,
            "w",
            encoding="utf8",
        ) as output_file:
            output_file.write(document_content)

    @staticmethod
    def _resolve_meta_style(document: SDocDocument) -> str:
        style = document.ng_markdown_meta_style
        if style in SDMarkdownWriter.allowed_meta_styles:
            return assert_cast(style, str)
        return SDMarkdownWriter.default_meta_style

    @staticmethod
    def _serialize_document_metadata(
        document: SDocDocument, meta_style: str
    ) -> Optional[str]:
        metadata_entries: List[Tuple[str, str]] = []
        seen_keys = set()

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
        return SDMarkdownWriter._serialize_meta_fields(
            metadata_entries, meta_style
        )

    @staticmethod
    def _serialize_node(
        node: SDocNode, heading_level: int, meta_style: str
    ) -> Optional[str]:
        if node.autogen:
            return None

        if node.node_type == "TEXT":
            return SDMarkdownWriter._serialize_text_node(node)

        if node.reserved_title is None:
            return None

        heading_hashes = "#" * max(1, heading_level)
        heading_text = (
            f"{heading_hashes} {SDMarkdownWriter._to_lf(node.reserved_title)}"
        )

        body_blocks: List[str] = []
        own_fields_block = SDMarkdownWriter._serialize_node_fields(
            node, meta_style
        )
        if own_fields_block is not None and len(own_fields_block) > 0:
            body_blocks.append(own_fields_block)

        for child_node in node.section_contents:
            if isinstance(child_node, SDocNode):
                child_block = SDMarkdownWriter._serialize_node(
                    node=child_node,
                    heading_level=heading_level + 1,
                    meta_style=meta_style,
                )
                if child_block is None or len(child_block) == 0:
                    continue
                body_blocks.append(child_block)

        if len(body_blocks) == 0:
            return heading_text

        return heading_text + "\n\n" + "\n\n".join(body_blocks)

    @staticmethod
    def _serialize_node_fields(
        node: SDocNode, meta_style: str
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

        for field in node.enumerate_fields():
            if field.field_name == "TITLE":
                continue

            field_name = field.field_name
            field_human_name = SDMarkdownWriter._resolve_human_field_name(
                node=node, field_name=field_name
            )
            field_value = SDMarkdownWriter._to_lf(field.get_text_value())

            if element is None or field_name not in element.fields_map:
                is_content_field = SDMarkdownWriter._is_multi_paragraph(
                    field_value
                )
            else:
                is_content_field = element.is_field_multiline(field_name)

            if is_content_field:
                content_fields.append((field_human_name, field_value))
            else:
                meta_fields.append((field_human_name, field_value))

        parent_relations_field = SDMarkdownWriter._serialize_parent_relations(
            node
        )
        if parent_relations_field is not None:
            meta_fields.append(parent_relations_field)

        field_blocks: List[str] = []
        if len(meta_fields) > 0:
            field_blocks.append(
                SDMarkdownWriter._serialize_meta_fields(meta_fields, meta_style)
            )
        if len(content_fields) > 0:
            field_blocks.append(
                SDMarkdownWriter._serialize_content_fields(content_fields)
            )

        if len(field_blocks) == 0:
            return None
        return "\n\n".join(field_blocks)

    @staticmethod
    def _serialize_parent_relations(
        node: SDocNode,
    ) -> Optional[Tuple[str, str]]:
        if len(node.relations) == 0:
            return None

        relation_uids: List[str] = []
        for relation in node.relations:
            if not isinstance(relation, ParentReqReference):
                continue
            if relation.role is not None:
                continue
            relation_uid = relation.ref_uid.strip()
            if len(relation_uid) == 0:
                continue
            relation_uids.append(relation_uid)

        if len(relation_uids) == 0:
            return None
        return "Relations", ", ".join(relation_uids)

    @staticmethod
    def _resolve_human_field_name(node: SDocNode, field_name: str) -> str:
        document = node.get_document()
        if document is None or document.grammar is None:
            return field_name
        grammar = assert_cast(document.grammar, DocumentGrammar)
        element = grammar.elements_by_type.get(node.node_type, None)
        if element is None:
            return field_name
        if field_name not in element.fields_map:
            return field_name
        return element.fields_map[field_name].get_field_human_name()

    @staticmethod
    def _serialize_text_node(node: SDocNode) -> Optional[str]:
        statement_fields = node.ordered_fields_lookup.get("STATEMENT", None)
        if statement_fields is None or len(statement_fields) == 0:
            return None
        statement_value = SDMarkdownWriter._to_lf(
            statement_fields[0].get_text_value()
        )
        return statement_value.strip("\n")

    @staticmethod
    def _serialize_meta_fields(
        fields: Sequence[Tuple[str, str]], meta_style: str
    ) -> str:
        lines: List[str] = []

        if meta_style == "bullet":
            for field_name, field_value in fields:
                value = SDMarkdownWriter._meta_value_to_single_line(field_value)
                lines.append(f"- **{field_name}**: {value}")
            return "\n".join(lines)

        if meta_style == "two_spaces":
            for field_name, field_value in fields:
                value = SDMarkdownWriter._meta_value_to_single_line(field_value)
                lines.append(f"**{field_name}**: {value}  ")
            return "\n".join(lines)

        # Backslash style (default)
        field_count = len(fields)
        for field_index, (field_name, field_value) in enumerate(fields):
            value = SDMarkdownWriter._meta_value_to_single_line(field_value)
            suffix = " \\" if field_index < field_count - 1 else ""
            lines.append(f"**{field_name}**: {value}{suffix}")
        return "\n".join(lines)

    @staticmethod
    def _serialize_content_fields(fields: Sequence[Tuple[str, str]]) -> str:
        output_blocks: List[str] = []
        for field_name, field_value in fields:
            output_blocks.append(
                SDMarkdownWriter._serialize_single_content_field(
                    field_name, field_value
                )
            )
        return "\n\n".join(output_blocks)

    @staticmethod
    def _serialize_single_content_field(
        field_name: str, field_value: str
    ) -> str:
        normalized_value = SDMarkdownWriter._to_lf(field_value).strip("\n")
        if SDMarkdownWriter._is_multi_paragraph(normalized_value):
            if len(normalized_value) > 0:
                return f"**{field_name}**:\n\n{normalized_value}"
            return f"**{field_name}**:"
        if len(normalized_value) > 0:
            return f"**{field_name}**: {normalized_value}"
        return f"**{field_name}**:"

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
