"""
@relation(SDOC-SRS-26, scope=file)
"""

from collections import OrderedDict
from typing import Any, Generator, List, Optional, Tuple, Union

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
)
from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElement,
    ReferenceType,
)
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.model import (
    RESERVED_NON_META_FIELDS,
    RequirementFieldName,
    SDocDocumentIF,
    SDocElementIF,
    SDocNodeIF,
    SDocSectionIF,
)
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    ParentReqReference,
    Reference,
)
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.exception import StrictDocException
from strictdoc.helpers.mid import MID
from strictdoc.helpers.string import ensure_newline


@auto_described
class SDocNodeContext:
    def __init__(self) -> None:
        self.title_number_string: Optional[str] = None


@auto_described
class SDocNodeField:
    def __init__(
        self,
        parent: Optional["SDocNode"],
        field_name: str,
        parts: List[Any],
        multiline__: Optional[str],
    ) -> None:
        self.parent: Optional[SDocNode] = parent
        self.field_name = field_name
        self.parts: List[Any] = parts
        self.multiline: bool = multiline__ is not None and len(multiline__) > 0

    @staticmethod
    def create_from_string(
        parent: Optional["SDocNode"],
        field_name: str,
        field_value: str,
        multiline: bool,
    ) -> "SDocNodeField":
        assert isinstance(field_name, str) and len(field_name) > 0, field_name
        assert isinstance(field_value, str) and len(field_value) > 0, (
            field_value
        )

        return SDocNodeField(
            parent=parent,
            field_name=field_name,
            parts=[field_value],
            multiline__="multiline" if multiline else None,
        )

    def is_multiline(self) -> bool:
        return self.multiline

    def get_text_value(self) -> str:
        text = ""
        for part in self.parts:
            if isinstance(part, str):
                text += part
            elif isinstance(part, InlineLink):
                text += "[LINK: "
                text += part.link
                text += "]"
            elif isinstance(part, Anchor):
                text += "[ANCHOR: "
                text += part.value
                if part.has_title:
                    text += ", "
                    text += part.title
                text += "]"
                text += "\n"
            else:
                raise NotImplementedError(part)  # pragma: no cover
        return text


@auto_described
class SDocNode(SDocNodeIF):
    def __init__(
        self,
        parent: Union[SDocDocumentIF, SDocSectionIF, SDocNodeIF],
        node_type: str,
        fields: List[SDocNodeField],
        relations: List[Reference],
        is_composite: bool = False,
        section_contents: Optional[List[SDocElementIF]] = None,
        node_type_close: Optional[str] = None,
    ) -> None:
        assert parent
        assert isinstance(node_type, str)
        assert isinstance(relations, list), relations

        self.parent: Union[SDocDocumentIF, SDocSectionIF, SDocNodeIF] = parent

        self.node_type: str = node_type

        if node_type_close is not None and len(node_type_close) > 0:
            if node_type != node_type_close:
                raise StrictDocException(
                    "[[NODE]] syntax error: "
                    "Opening and closing tags must match: "
                    f"opening: {node_type}, closing: {node_type_close}."
                )
            assert is_composite
        else:
            assert not is_composite

        self.is_composite: bool = is_composite

        ordered_fields_lookup: OrderedDict[str, List[SDocNodeField]] = (
            OrderedDict()
        )

        has_meta: bool = False
        for field in fields:
            if field.field_name not in RESERVED_NON_META_FIELDS:
                has_meta = True
            ordered_fields_lookup.setdefault(field.field_name, []).append(field)

        self.section_contents: List[SDocElementIF] = (
            section_contents if section_contents is not None else []
        )

        self.relations: List[Reference] = relations

        # TODO: Is it worth to move this to dedicated Presenter* classes to
        # keep this class textx-only?
        self.has_meta: bool = has_meta

        # This property is only used for validating fields against grammar
        # during TextX parsing and processing.
        self.fields_as_parsed = fields

        self.ordered_fields_lookup: OrderedDict[str, List[SDocNodeField]] = (
            ordered_fields_lookup
        )
        self.ng_level: Optional[int] = None
        self.ng_document_reference: Optional[DocumentReference] = None
        self.ng_including_document_reference: Optional[DocumentReference] = None
        self.ng_line_start: Optional[int] = None
        self.ng_line_end: Optional[int] = None
        self.ng_col_start: Optional[int] = None
        self.ng_col_end: Optional[int] = None
        self.ng_byte_start: Optional[int] = None
        self.ng_byte_end: Optional[int] = None
        self.context: SDocNodeContext = SDocNodeContext()

        mid: Optional[str] = None
        mid_fields: Optional[List[SDocNodeField]] = ordered_fields_lookup.get(
            "MID", None
        )
        if mid_fields is not None:
            mid = mid_fields[0].get_text_value()
        self.reserved_mid: MID = MID(mid) if mid is not None else MID.create()
        self.mid_permanent: bool = mid is not None

        self.ng_resolved_custom_level: Optional[str] = None
        self.custom_level: Optional[str] = None
        if RequirementFieldName.LEVEL in ordered_fields_lookup:
            level = ordered_fields_lookup[RequirementFieldName.LEVEL][
                0
            ].get_text_value()
            self.ng_resolved_custom_level = level
            self.custom_level = level

        # This is always true, unless the node is filtered out with --filter-requirements.
        self.ng_whitelisted: bool = True

        self.ng_has_requirements: bool = False

    @staticmethod
    def get_type_string() -> str:
        return "requirement"

    def get_node_type_string(self) -> Optional[str]:
        return self.node_type

    def get_display_node_type_string(self) -> Optional[str]:
        if self.is_composite:
            return f"[[{self.node_type}]]"
        return f"[{self.node_type}]"

    def get_display_title(
        self,
        include_toc_number: bool = True,  # noqa: ARG002
    ) -> str:
        if self.reserved_title is not None:
            return self.reserved_title
        if self.reserved_uid is not None:
            return self.reserved_uid
        if self.node_type == "TEXT":
            if isinstance(self.parent, SDocSectionIF):
                return f'Text node from section "{self.parent.get_display_title()}"'
            if isinstance(self.parent, SDocDocumentIF):
                return f'Text node from document "{self.parent.get_display_title()}"'
        return f"{self.node_type} with no title/UID"

    @property
    def is_root_included_document(self) -> bool:
        return False

    @property
    def is_root(self) -> bool:
        document = assert_cast(self.get_document(), SDocDocumentIF)
        return document.config.root is True

    def has_multiline_fields(self) -> bool:
        """
        FIXME: It should be possible to avoid calculating this every time.
        """

        document = assert_cast(self.get_document(), SDocDocumentIF)
        grammar = assert_cast(document.grammar, DocumentGrammar)
        element: GrammarElement = grammar.elements_by_type[self.node_type]

        for fields_ in self.ordered_fields_lookup.values():
            for field_ in fields_:
                if element.is_field_multiline(field_.field_name):
                    return True
        return False

    def has_any_text_nodes(self) -> bool:
        # The workaround: hasattr(...) makes mypy happy.
        return any(
            node_.__class__.__name__ == "SDocNode"
            and hasattr(node_, "node_type")
            and node_.node_type == "TEXT"
            for node_ in self.section_contents
        )

    #
    # Reserved fields
    #

    @property
    def reserved_uid(self) -> Optional[str]:
        return self._get_cached_field(
            RequirementFieldName.UID, singleline_only=True
        )

    @property
    def reserved_status(self) -> Optional[str]:
        return self._get_cached_field(
            RequirementFieldName.STATUS, singleline_only=True
        )

    @property
    def reserved_tags(self) -> Optional[List[str]]:
        if RequirementFieldName.TAGS not in self.ordered_fields_lookup:
            return None
        field: SDocNodeField = self.ordered_fields_lookup[
            RequirementFieldName.TAGS
        ][0]
        assert not field.is_multiline(), (
            f"Field {RequirementFieldName.TAGS} must be a single-line field."
        )
        tags = field.get_text_value().split(", ")
        return tags

    @property
    def reserved_title(self) -> Optional[str]:
        return self._get_cached_field(
            RequirementFieldName.TITLE, singleline_only=True
        )

    def has_reserved_statement(self) -> bool:
        document = assert_cast(self.get_document(), SDocDocumentIF)
        grammar = assert_cast(document.grammar, DocumentGrammar)
        element: GrammarElement = grammar.elements_by_type[self.node_type]
        return element.content_field[0] in self.ordered_fields_lookup

    @property
    def reserved_statement(self) -> Optional[str]:
        document = assert_cast(self.get_document(), SDocDocumentIF)
        grammar = assert_cast(document.grammar, DocumentGrammar)
        element: GrammarElement = grammar.elements_by_type[self.node_type]
        return self._get_cached_field(
            element.content_field[0], singleline_only=False
        )

    @property
    def rationale(self) -> Optional[str]:
        return self._get_cached_field(
            RequirementFieldName.RATIONALE, singleline_only=False
        )

    def is_requirement(self) -> bool:
        return True

    def is_normative_node(self) -> bool:
        return not self.is_text_node()

    def is_text_node(self) -> bool:
        return self.node_type == "TEXT"

    def is_section(self) -> bool:
        return False

    def is_document(self) -> bool:
        return False

    def get_document(self) -> Optional[SDocDocumentIF]:
        assert self.ng_document_reference is not None, self
        return self.ng_document_reference.get_document()

    def get_including_document(self) -> Optional[SDocDocumentIF]:
        assert self.ng_including_document_reference is not None
        return self.ng_including_document_reference.get_document()

    def get_parent_or_including_document(self) -> SDocDocumentIF:
        assert self.ng_including_document_reference is not None
        including_document_or_none = (
            self.ng_including_document_reference.get_document()
        )
        if including_document_or_none is not None:
            return including_document_or_none

        assert self.ng_document_reference is not None
        document: Optional[SDocDocumentIF] = (
            self.ng_document_reference.get_document()
        )
        assert document is not None, (
            "A valid requirement must always have a reference to the document."
        )
        return document

    def get_display_node_type(self) -> str:
        return "Node"

    def get_debug_info(self) -> str:
        debug_components: List[str] = []
        if self.reserved_mid is not None:
            debug_components.append(f"MID = '{self.reserved_mid}'")
        if self.reserved_uid is not None:
            debug_components.append(f"UID = '{self.reserved_uid}'")
        if self.reserved_title is not None:
            debug_components.append(f"TITLE = '{self.reserved_title}'")

        document: Optional[SDocDocumentIF] = self.get_document()
        if document is not None:
            debug_components.append(f"document = {document.get_debug_info()}")
        return f"Requirement({', '.join(debug_components)})"

    # FIXME: Remove this method. Use get_parent_or_including_document() instead.
    @property
    def parent_or_including_document(self) -> SDocDocumentIF:
        return self.get_parent_or_including_document()

    def document_is_included(self) -> bool:
        assert self.ng_including_document_reference is not None
        return self.ng_including_document_reference.get_document() is not None

    def get_requirement_style_mode(self) -> str:
        document: SDocDocumentIF = assert_cast(
            self.get_document(), SDocDocumentIF
        )
        grammar = assert_cast(document.grammar, DocumentGrammar)
        element: GrammarElement = grammar.elements_by_type[self.node_type]
        if node_style := element.get_view_style():
            return node_style
        return document.config.get_requirement_style_mode()

    def get_content_field_name(self) -> str:
        document = assert_cast(self.get_document(), SDocDocumentIF)
        grammar = assert_cast(document.grammar, DocumentGrammar)

        element: GrammarElement = grammar.elements_by_type[self.node_type]
        return element.content_field[0]

    def get_content_field(self) -> SDocNodeField:
        document = assert_cast(self.get_document(), SDocDocumentIF)
        grammar = assert_cast(document.grammar, DocumentGrammar)

        element: GrammarElement = grammar.elements_by_type[self.node_type]
        return self.ordered_fields_lookup[element.content_field[0]][0]

    def get_field_by_name(self, field_name: str) -> SDocNodeField:
        return self.ordered_fields_lookup[field_name][0]

    def get_anchors(self) -> List[Anchor]:
        this_node_anchors: List[Anchor] = []
        for field_ in self.enumerate_fields():
            for field_part_ in field_.parts:
                if isinstance(field_part_, Anchor):
                    this_node_anchors.append(field_part_)
        return this_node_anchors

    def get_comment_fields(self) -> List[SDocNodeField]:
        if RequirementFieldName.COMMENT not in self.ordered_fields_lookup:
            return []
        return self.ordered_fields_lookup[RequirementFieldName.COMMENT]

    def get_requirement_references(self, ref_type: str) -> List[Reference]:
        if len(self.relations) == 0:
            return []
        references: List[Reference] = []
        for reference in self.relations:
            if reference.ref_type != ref_type:
                continue
            references.append(reference)
        return references

    def get_requirement_reference_uids(
        self,
    ) -> List[Tuple[str, str, Optional[str]]]:
        if len(self.relations) == 0:
            return []
        references: List[Tuple[str, str, Optional[str]]] = []
        for reference in self.relations:
            if reference.ref_type == ReferenceType.PARENT:
                parent_reference: ParentReqReference = assert_cast(
                    reference, ParentReqReference
                )
                references.append(
                    (
                        parent_reference.ref_type,
                        parent_reference.ref_uid,
                        parent_reference.role,
                    )
                )
            elif reference.ref_type == ReferenceType.CHILD:
                child_reference: ChildReqReference = assert_cast(
                    reference, ChildReqReference
                )
                references.append(
                    (
                        child_reference.ref_type,
                        child_reference.ref_uid,
                        child_reference.role,
                    )
                )
        return references

    def enumerate_fields(self) -> Generator[SDocNodeField, None, None]:
        requirement_fields = self.ordered_fields_lookup.values()
        for requirement_field_list in requirement_fields:
            yield from requirement_field_list

    def enumerate_all_fields(
        self,
    ) -> Generator[Tuple[SDocNodeField, str, str], None, None]:
        for field in self.enumerate_fields():
            meta_field_value = field.get_text_value()
            yield field, field.field_name, meta_field_value

    def enumerate_meta_fields(
        self, skip_single_lines: bool = False, skip_multi_lines: bool = False
    ) -> Generator[Tuple[str, SDocNodeField], None, None]:
        document: SDocDocumentIF = assert_cast(
            self.get_document(), SDocDocumentIF
        )

        document_grammar: DocumentGrammar = assert_cast(
            document.grammar, DocumentGrammar
        )

        element: GrammarElement = document_grammar.elements_by_type[
            self.node_type
        ]
        grammar_field_titles = list(map(lambda f: f.title, element.fields))

        reference_field_index: int = element.get_multiline_field_index()

        for field in self.enumerate_fields():
            if field.field_name in RESERVED_NON_META_FIELDS:
                continue
            field_index = grammar_field_titles.index(field.field_name)

            # A field is considered singleline if it goes before the STATEMENT
            # field and vice versa.
            if field_index >= reference_field_index:
                is_single_line_field = False
            else:
                is_single_line_field = True

            if is_single_line_field and skip_single_lines:
                continue
            if (not is_single_line_field) and skip_multi_lines:
                continue

            field_human_title = element.fields_map[field.field_name]
            yield field_human_title.get_field_human_name(), field

    def get_meta_field_value_by_title(self, field_title: str) -> Optional[str]:
        assert isinstance(field_title, str)
        if field_title not in self.ordered_fields_lookup:
            return None
        field: SDocNodeField = self.ordered_fields_lookup[field_title][0]
        return field.get_text_value()

    def get_field_human_title(self, field_name: str) -> str:
        document: SDocDocumentIF = assert_cast(
            self.get_document(), SDocDocumentIF
        )
        document_grammar: DocumentGrammar = assert_cast(
            document.grammar, DocumentGrammar
        )
        element: GrammarElement = document_grammar.elements_by_type[
            self.node_type
        ]
        field_human_title = element.fields_map[field_name]
        return field_human_title.get_field_human_name()

    def get_field_human_title_for_statement(self) -> str:
        document: SDocDocumentIF = assert_cast(
            self.get_document(), SDocDocumentIF
        )
        grammar: DocumentGrammar = assert_cast(
            document.grammar, DocumentGrammar
        )
        element: GrammarElement = grammar.elements_by_type[self.node_type]
        field_human_title = element.fields_map[element.content_field[0]]
        return field_human_title.get_field_human_name()

    def get_prefix(self) -> Optional[str]:
        if (
            own_prefix := self._get_cached_field(
                RequirementFieldName.PREFIX, singleline_only=True
            )
        ) is not None:
            if own_prefix == "None":
                return None
            return own_prefix

        document: SDocDocumentIF = assert_cast(
            self.get_document(), SDocDocumentIF
        )
        grammar: DocumentGrammar = assert_cast(
            document.grammar, DocumentGrammar
        )
        element: GrammarElement = grammar.elements_by_type[self.node_type]
        if (element_prefix := element.property_prefix) is not None:
            if element_prefix == "None":
                return None
            return element_prefix

        # FIXME: Is this a reasonable behavior?
        if (
            isinstance(self.parent, SDocNode)
            and self.parent.node_type == "SECTION"
        ):
            if (parent_prefix := self.parent.get_prefix()) is not None:
                return parent_prefix
            return document.get_prefix()

        return self.parent.get_prefix()

    def get_prefix_for_new_node(self, node_type: str) -> Optional[str]:
        assert isinstance(node_type, str) and len(node_type), node_type

        document: SDocDocumentIF = assert_cast(
            self.get_document(), SDocDocumentIF
        )
        grammar: DocumentGrammar = assert_cast(
            document.grammar, DocumentGrammar
        )
        element: GrammarElement = grammar.elements_by_type[node_type]
        if (element_prefix := element.property_prefix) is not None:
            if element_prefix == "None":
                return None
            return element_prefix

        return self.get_prefix()

    def dump_fields_as_parsed(self) -> str:
        # FIXME:
        # - The name of the method can be improved (used in error messages).
        # - fields can diverge from fields_as_parsed.
        return ", ".join(
            list(
                map(
                    lambda r: r.field_name,
                    self.fields_as_parsed,
                )
            )
        )

    def _get_cached_field(
        self, field_name: str, singleline_only: bool
    ) -> Optional[str]:
        if field_name not in self.ordered_fields_lookup:
            return None
        field: SDocNodeField = self.ordered_fields_lookup[field_name][0]

        if singleline_only and field.is_multiline():
            raise NotImplementedError(
                f"Field {field_name} must be a single-line field."
            )

        return field.get_text_value()

    # Below all mutating methods.

    def set_field_value(
        self,
        *,
        field_name: str,
        form_field_index: int,
        value: Optional[Union[str, SDocNodeField]],
    ) -> None:
        """
        Create or update a field by name with the given value.

        The purpose of this purpose is to provide a single-method API for
        updating any field of a requirement. A requirement might use only some
        fields of a document grammar, so an extra exercise done by the method is
        to ensure that an added field that has not been attached to the
        requirement before will be put at the right index.
        """
        assert isinstance(field_name, str)

        # If a field value is being removed, there is not much to do.
        if value is None or (isinstance(value, str) and len(value) == 0):
            # Comment is a special because there can be multiple comments.
            # Empty comments are simply ignored and do not show up in the
            # updated requirement.
            if field_name == RequirementFieldName.COMMENT:
                return

            if field_name in self.ordered_fields_lookup:
                del self.ordered_fields_lookup[field_name]
            return

        # If a field value is being added or updated.
        document: SDocDocumentIF = assert_cast(
            self.get_document(), SDocDocumentIF
        )
        grammar: DocumentGrammar = assert_cast(
            document.grammar, DocumentGrammar
        )
        element: GrammarElement = grammar.elements_by_type[self.node_type]
        grammar_field_titles = list(map(lambda f: f.title, element.fields))
        field_index = grammar_field_titles.index(field_name)

        multiline = field_index >= element.get_multiline_field_index()
        if multiline and isinstance(value, str):
            value = ensure_newline(value)

        if field_name in self.ordered_fields_lookup:
            if len(self.ordered_fields_lookup[field_name]) > form_field_index:
                self.ordered_fields_lookup[field_name][form_field_index] = (
                    SDocNodeField.create_from_string(
                        self,
                        field_name=field_name,
                        field_value=value,
                        multiline=multiline,
                    )
                    if isinstance(value, str)
                    else value
                )
            else:
                self.ordered_fields_lookup[field_name].insert(
                    form_field_index,
                    SDocNodeField.create_from_string(
                        self,
                        field_name=field_name,
                        field_value=value,
                        multiline=multiline,
                    )
                    if isinstance(value, str)
                    else value,
                )
            return

        new_ordered_fields_lookup = OrderedDict()
        for field_title in grammar_field_titles[:field_index]:
            if field_title in self.ordered_fields_lookup:
                new_ordered_fields_lookup[field_title] = (
                    self.ordered_fields_lookup[field_title]
                )
        new_ordered_fields_lookup[field_name] = [
            SDocNodeField.create_from_string(
                self,
                field_name=field_name,
                field_value=value,
                multiline=multiline,
            )
            if isinstance(value, str)
            else value
        ]
        after_field_index = field_index + 1
        for field_title in grammar_field_titles[after_field_index:]:
            if field_title in self.ordered_fields_lookup:
                new_ordered_fields_lookup[field_title] = (
                    self.ordered_fields_lookup[field_title]
                )
        self.ordered_fields_lookup = new_ordered_fields_lookup
        self._update_has_meta()

    def _update_has_meta(self) -> None:
        has_meta: bool = False
        for field in self.enumerate_fields():
            if field.field_name not in RESERVED_NON_META_FIELDS:
                has_meta = True
        self.has_meta = has_meta


@auto_described
class SDocCompositeNode(SDocNode):
    def __init__(
        self,
        parent: Union[SDocDocumentIF, SDocSectionIF, SDocNodeIF],
        **fields: Any,
    ) -> None:
        super().__init__(parent, **fields, is_composite=True)
