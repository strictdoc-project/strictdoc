# mypy: disable-error-code="union-attr"
from collections import OrderedDict
from typing import Any, Generator, List, Optional, Tuple, Union

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.object import SDocObject
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    ParentReqReference,
    Reference,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc.models.type_system import (
    RESERVED_NON_META_FIELDS,
    ReferenceType,
    RequirementFieldName,
)
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.mid import MID


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
        field_value: Optional[str],
        field_value_multiline: Optional[str],
    ) -> None:
        self.parent = parent
        self.field_name = field_name

        if field_value_multiline is not None:
            rstripped_field_value_multiline = field_value_multiline.rstrip()

            # Edge case: empty multiline field should have one newline symbol.
            # Example:
            # COMMENT: >>>
            #
            # <<<
            if (
                len(rstripped_field_value_multiline) == 0
                and len(field_value_multiline) != 0
            ):
                field_value_multiline = "\n"
            else:
                field_value_multiline = rstripped_field_value_multiline

        self._field_value_multiline: Optional[str] = field_value_multiline
        self._field_value: Optional[str] = field_value

        self.resolved_field_value: str
        if self._field_value is not None:
            self._resolved_field_value = self._field_value
        elif self._field_value_multiline is not None:
            self._resolved_field_value = self._field_value_multiline
        else:
            raise AssertionError(
                "A requirement field must have at least one value."
            )

    def is_multiline(self) -> bool:
        return self._field_value_multiline is not None

    def get_value(self) -> str:
        return self._resolved_field_value


@auto_described
class SDocNode(SDocObject):
    def __init__(
        self,
        parent: Union[SDocDocument, SDocSection, "SDocCompositeNode"],
        requirement_type: str,
        mid: Optional[str],
        fields: List[SDocNodeField],
        relations: List[Reference],
        requirements: Optional[List["SDocNode"]] = None,
    ) -> None:
        assert parent
        assert isinstance(requirement_type, str)
        assert isinstance(relations, list), relations

        self.parent: Union[
            "SDocDocument", "SDocSection", "SDocCompositeNode"
        ] = parent

        self.requirement_type: str = requirement_type

        ordered_fields_lookup: OrderedDict[str, List[SDocNodeField]] = (
            OrderedDict()
        )

        has_meta: bool = False
        for field in fields:
            if field.field_name not in RESERVED_NON_META_FIELDS:
                has_meta = True
            ordered_fields_lookup.setdefault(field.field_name, []).append(field)

        self.requirements: Optional[List["SDocNode"]] = requirements

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

        self.reserved_mid: MID = MID(mid) if mid is not None else MID.create()
        self.mid_permanent: bool = mid is not None

        # HEF4
        self.ng_resolved_custom_level: Optional[str] = None
        self.custom_level: Optional[str] = None
        if RequirementFieldName.LEVEL in ordered_fields_lookup:
            level = ordered_fields_lookup[RequirementFieldName.LEVEL][
                0
            ].get_value()
            self.ng_resolved_custom_level = level
            self.custom_level = level

        # This is always true, unless the node is filtered out with --filter-requirements.
        self.ng_whitelisted = True

    @staticmethod
    def get_type_string() -> str:
        return "requirement"

    def get_node_type_string(self) -> Optional[str]:
        return self.requirement_type

    def get_title(self) -> Optional[str]:
        return self.reserved_title

    @property
    def is_root_included_document(self) -> bool:
        return False

    @property
    def is_root(self) -> bool:
        return self.document.config.root is True

    # Reserved fields

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
        assert (
            not field.is_multiline()
        ), f"Field {RequirementFieldName.TAGS} must be a single-line field."
        tags = field.get_value().split(", ")
        return tags

    @property
    def reserved_title(self) -> Optional[str]:
        return self._get_cached_field(
            RequirementFieldName.TITLE, singleline_only=True
        )

    @property
    def reserved_statement(self) -> Optional[str]:
        element: GrammarElement = self.document.grammar.elements_by_type[
            self.requirement_type
        ]
        return self._get_cached_field(
            element.content_field[0], singleline_only=False
        )

    @property
    def rationale(self) -> Optional[str]:
        return self._get_cached_field(
            RequirementFieldName.RATIONALE, singleline_only=False
        )

    @property
    def comments(self) -> List[str]:
        if RequirementFieldName.COMMENT not in self.ordered_fields_lookup:
            return []
        comments = []
        for field in self.ordered_fields_lookup[RequirementFieldName.COMMENT]:
            comments.append(field.get_value())
        return comments

    # Other properties
    @property
    def is_requirement(self) -> bool:
        return True

    @property
    def is_section(self) -> bool:
        return False

    @property
    def is_composite_requirement(self) -> bool:
        return False

    @property
    def document(self) -> SDocDocument:
        document: Optional[SDocDocument] = (
            self.ng_document_reference.get_document()
        )
        assert (
            document is not None
        ), "A valid requirement must always have a reference to the document."
        return document

    def get_document(self) -> Optional[SDocDocument]:
        return self.ng_document_reference.get_document()

    def get_included_document(self) -> Optional[SDocDocument]:
        return self.ng_including_document_reference.get_document()

    @property
    def parent_or_including_document(self) -> SDocDocument:
        including_document_or_none = (
            self.ng_including_document_reference.get_document()
        )
        if including_document_or_none is not None:
            return including_document_or_none

        document: Optional[SDocDocument] = (
            self.ng_document_reference.get_document()
        )
        assert (
            document is not None
        ), "A valid requirement must always have a reference to the document."
        return document

    def document_is_included(self) -> bool:
        return self.ng_including_document_reference.get_document() is not None

    def get_requirement_style_mode(self) -> str:
        assert self.ng_document_reference.get_document() is not None
        return self.ng_document_reference.get_document().config.get_requirement_style_mode()

    def get_content_field_name(self) -> str:
        element: GrammarElement = self.document.grammar.elements_by_type[
            self.requirement_type
        ]
        return element.content_field[0]

    def has_requirement_references(self, ref_type: str) -> bool:
        if len(self.relations) == 0:
            return False
        for reference in self.relations:
            if reference.ref_type == ref_type:
                return True
        return False

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

    def get_parent_requirement_reference_uids(
        self,
    ) -> List[Tuple[str, Optional[str]]]:
        if not self.relations or len(self.relations) == 0:
            return []
        references: List[Tuple[str, Optional[str]]] = []
        for reference in self.relations:
            if reference.ref_type != ReferenceType.PARENT:
                continue
            parent_reference: ParentReqReference = assert_cast(
                reference, ParentReqReference
            )
            references.append((parent_reference.ref_uid, parent_reference.role))
        return references

    def get_child_requirement_reference_uids(
        self,
    ) -> List[Tuple[str, Optional[str]]]:
        if not self.relations or len(self.relations) == 0:
            return []
        references: List[Tuple[str, Optional[str]]] = []
        for reference in self.relations:
            if reference.ref_type != ReferenceType.CHILD:
                continue
            child_reference: ChildReqReference = assert_cast(
                reference, ChildReqReference
            )
            references.append((child_reference.ref_uid, child_reference.role))
        return references

    def enumerate_fields(self) -> Generator[SDocNodeField, None, None]:
        requirement_fields = self.ordered_fields_lookup.values()
        for requirement_field_list in requirement_fields:
            yield from requirement_field_list

    def enumerate_all_fields(
        self,
    ) -> Generator[Tuple[SDocNodeField, str, str], None, None]:
        for field in self.enumerate_fields():
            meta_field_value = field.get_value()
            yield field, field.field_name, meta_field_value

    def enumerate_meta_fields(
        self, skip_single_lines: bool = False, skip_multi_lines: bool = False
    ) -> Generator[Tuple[str, str], None, None]:
        element: GrammarElement = self.document.grammar.elements_by_type[
            self.requirement_type
        ]
        grammar_field_titles = list(map(lambda f: f.title, element.fields))
        statement_field_index: int = element.content_field[1]
        for field in self.enumerate_fields():
            if field.field_name in RESERVED_NON_META_FIELDS:
                continue
            meta_field_value = field.get_value()
            field_index = grammar_field_titles.index(field.field_name)

            # A field is considered singleline if it goes before the STATEMENT
            # field and vice versa.
            if field_index > statement_field_index:
                is_single_line_field = False
            else:
                is_single_line_field = True

            if is_single_line_field and skip_single_lines:
                continue
            if (not is_single_line_field) and skip_multi_lines:
                continue

            field_human_title = element.fields_map[field.field_name]
            yield field_human_title.get_field_human_name(), meta_field_value

    def get_meta_field_value_by_title(self, field_title: str) -> Optional[str]:
        assert isinstance(field_title, str)
        if field_title not in self.ordered_fields_lookup:
            return None
        field: SDocNodeField = self.ordered_fields_lookup[field_title][0]
        return field.get_value()

    def get_field_human_title(self, field_name: str) -> str:
        element: GrammarElement = self.document.grammar.elements_by_type[
            self.requirement_type
        ]
        field_human_title = element.fields_map[field_name]
        return field_human_title.get_field_human_name()

    def get_field_human_title_for_statement(self) -> str:
        element: GrammarElement = self.document.grammar.elements_by_type[
            self.requirement_type
        ]
        field_human_title = element.fields_map[element.content_field[0]]
        return field_human_title.get_field_human_name()

    def get_requirement_prefix(self) -> str:
        parent: Union[SDocSection, SDocDocument] = assert_cast(
            self.parent, (SDocSection, SDocDocument, SDocCompositeNode)
        )
        return parent.get_requirement_prefix()

    def dump_fields_as_parsed(self) -> str:
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

        return field.get_value()

    # Below all mutating methods.

    def set_field_value(
        self, *, field_name: str, form_field_index: int, value: Optional[str]
    ) -> None:
        """
        The purpose of this purpose is to provide a single-method API for
        updating any field of a requirement. A requirement might use only some
        fields of a document grammar, so an extra exercise done by the method is
        to ensure that an added field that has not been attached to the
        requirement before will be put at the right index.
        """
        assert isinstance(field_name, str)

        # If a field value is being removed, there is not much to do.
        if value is None or len(value) == 0:
            # Comment is a special because there can be multiple comments.
            # Empty comments are simply ignored and do not show up in the
            # updated requirement.
            if field_name == RequirementFieldName.COMMENT:
                return

            if field_name in self.ordered_fields_lookup:
                del self.ordered_fields_lookup[field_name]
            return

        # If a field value is being added or updated.

        document: SDocDocument = self.document
        grammar_or_none: Optional[DocumentGrammar] = document.grammar
        assert grammar_or_none is not None
        grammar: DocumentGrammar = grammar_or_none

        element: GrammarElement = grammar.elements_by_type[
            self.requirement_type
        ]
        grammar_field_titles = list(map(lambda f: f.title, element.fields))
        field_index = grammar_field_titles.index(field_name)

        field_value = None
        field_value_multiline = None
        if field_index < element.content_field[1]:
            field_value = value
        else:
            field_value_multiline = value

        if field_name in self.ordered_fields_lookup:
            if len(self.ordered_fields_lookup[field_name]) > form_field_index:
                self.ordered_fields_lookup[field_name][form_field_index] = (
                    SDocNodeField(
                        self,
                        field_name=field_name,
                        field_value=field_value,
                        field_value_multiline=field_value_multiline,
                    )
                )
            else:
                self.ordered_fields_lookup[field_name].insert(
                    form_field_index,
                    SDocNodeField(
                        self,
                        field_name=field_name,
                        field_value=field_value,
                        field_value_multiline=field_value_multiline,
                    ),
                )
            return

        new_ordered_fields_lookup = OrderedDict()
        for field_title in grammar_field_titles[:field_index]:
            if field_title in self.ordered_fields_lookup:
                new_ordered_fields_lookup[field_title] = (
                    self.ordered_fields_lookup[field_title]
                )
        new_ordered_fields_lookup[field_name] = [
            SDocNodeField(
                self,
                field_name=field_name,
                field_value=field_value,
                field_value_multiline=field_value_multiline,
            )
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
        parent: Union[SDocDocument, SDocSection, "SDocCompositeNode"],
        **fields: Any,
    ) -> None:
        super().__init__(parent, **fields)
        self.ng_document_reference: Optional[DocumentReference] = None
        self.ng_including_document_reference: Optional[DocumentReference] = None
        self.ng_has_requirements = False

    @property
    def is_composite_requirement(self) -> bool:
        return True

    @property
    def document(self) -> SDocDocument:
        document = self.ng_document_reference.get_document()
        assert document is not None
        return document

    def document_is_included(self) -> bool:
        return self.ng_including_document_reference.get_document() is not None

    def get_requirement_prefix(self) -> str:
        return self.parent.get_requirement_prefix()
