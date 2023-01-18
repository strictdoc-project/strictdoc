import uuid
from collections import OrderedDict
from typing import Optional, List, Dict, Any

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
    GrammarElement,
)
from strictdoc.backend.sdoc.models.node import Node
from strictdoc.backend.sdoc.models.reference import Reference
from strictdoc.backend.sdoc.models.type_system import (
    RequirementFieldName,
    RESERVED_NON_META_FIELDS,
)
from strictdoc.helpers.auto_described import auto_described

MULTILINE_WORD_THRESHOLD = 6


@auto_described
class RequirementContext:
    def __init__(self):
        self.title_number_string = None


@auto_described
class RequirementField:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        parent,
        field_name: str,
        field_value: Optional[str],
        field_value_multiline: Optional[str],
        field_value_references: Optional[List[Reference]],
    ):
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

        self.field_value_multiline: Optional[str] = field_value_multiline

        self.field_value: Optional[str] = field_value

        self.field_value_references: Optional[
            List[Reference]
        ] = field_value_references

    def get_value(self):
        value = (
            self.field_value if self.field_value else self.field_value_multiline
        )
        return value


class Requirement(Node):  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=too-many-arguments
        self,
        parent,
        requirement_type: str,
        fields: List[RequirementField],
        requirements=None,
    ):
        assert parent
        assert isinstance(requirement_type, str)

        self.parent = parent

        self.requirement_type: str = requirement_type

        uid = None
        level = None
        status = None
        tags: Optional[List[str]] = None
        references: List[Reference] = []

        ordered_fields_lookup: OrderedDict[
            str, List[RequirementField]
        ] = OrderedDict()

        has_meta: bool = False
        for field in fields:
            if field.field_name not in RESERVED_NON_META_FIELDS:
                has_meta = True
            ordered_fields_lookup.setdefault(field.field_name, []).append(field)

        if RequirementFieldName.UID in ordered_fields_lookup:
            uid = ordered_fields_lookup[RequirementFieldName.UID][0].field_value
        if RequirementFieldName.LEVEL in ordered_fields_lookup:
            level = ordered_fields_lookup[RequirementFieldName.LEVEL][
                0
            ].field_value
        if RequirementFieldName.STATUS in ordered_fields_lookup:
            status = ordered_fields_lookup[RequirementFieldName.STATUS][
                0
            ].field_value
        if RequirementFieldName.TAGS in ordered_fields_lookup:
            tags = ordered_fields_lookup[RequirementFieldName.TAGS][
                0
            ].field_value.split(", ")
        if RequirementFieldName.REFS in ordered_fields_lookup:
            references_opt: Optional[List[Reference]] = ordered_fields_lookup[
                RequirementFieldName.REFS
            ][0].field_value_references
            assert references_opt is not None
            references = references_opt

        # TODO: Why textX creates empty uid when the sdoc doesn't declare the
        # UID field?
        self.uid = (
            uid.strip() if (isinstance(uid, str) and len(uid) > 0) else None
        )
        self.level: Optional[str] = level
        self.status = status
        self.tags: Optional[List[str]] = tags

        assert isinstance(references, List)
        self.references: List[Reference] = references

        self.requirements = requirements

        # TODO: Is it worth to move this to dedicated Presenter* classes to
        # keep this class textx-only?
        self.has_meta: bool = has_meta

        # This property is only used for validating fields against grammar
        # during TextX parsing and processing.
        self.fields_as_parsed = fields

        self.ordered_fields_lookup: OrderedDict[
            str, List[RequirementField]
        ] = ordered_fields_lookup
        self.ng_level: Optional[int] = None
        self.ng_document_reference: Optional[DocumentReference] = None
        self.context = RequirementContext()

        self.node_id: str = uuid.uuid4().hex

        # Cache for accessing the reserved fields values.
        self.ng_reserved_fields_cache: Dict[str, Any] = {}

    # Reserved fields

    @property
    def reserved_title(self) -> Optional[str]:
        if RequirementFieldName.TITLE not in self.ordered_fields_lookup:
            return None
        return self.ordered_fields_lookup[RequirementFieldName.TITLE][
            0
        ].field_value

    @property
    def reserved_statement(self) -> Optional[str]:
        if RequirementFieldName.STATEMENT in self.ng_reserved_fields_cache:
            return self.ng_reserved_fields_cache[RequirementFieldName.STATEMENT]
        if RequirementFieldName.STATEMENT not in self.ordered_fields_lookup:
            self.ng_reserved_fields_cache[RequirementFieldName.STATEMENT] = None
            return None
        field: RequirementField = self.ordered_fields_lookup[
            RequirementFieldName.STATEMENT
        ][0]
        if field.field_value_multiline is not None:
            statement = field.field_value_multiline
        elif field.field_value is not None:
            statement = field.field_value
        else:
            raise NotImplementedError(self)
        self.ng_reserved_fields_cache[
            RequirementFieldName.STATEMENT
        ] = statement
        return statement

    @property
    def rationale(self) -> Optional[str]:
        if RequirementFieldName.RATIONALE in self.ng_reserved_fields_cache:
            return self.ng_reserved_fields_cache[RequirementFieldName.RATIONALE]
        if RequirementFieldName.RATIONALE not in self.ordered_fields_lookup:
            self.ng_reserved_fields_cache[RequirementFieldName.RATIONALE] = None
            return None
        field: RequirementField = self.ordered_fields_lookup[
            RequirementFieldName.RATIONALE
        ][0]
        if field.field_value_multiline is not None:
            rationale = field.field_value_multiline
        elif field.field_value is not None:
            rationale = field.field_value
        else:
            raise NotImplementedError(self)
        self.ng_reserved_fields_cache[
            RequirementFieldName.RATIONALE
        ] = rationale
        return rationale

    @property
    def comments(self) -> List[str]:
        if RequirementFieldName.COMMENT in self.ng_reserved_fields_cache:
            return self.ng_reserved_fields_cache[RequirementFieldName.COMMENT]
        if RequirementFieldName.COMMENT not in self.ordered_fields_lookup:
            self.ng_reserved_fields_cache[RequirementFieldName.COMMENT] = []
            return []
        comments = []
        for field in self.ordered_fields_lookup[RequirementFieldName.COMMENT]:
            if field.field_value_multiline is not None:
                comments.append(field.field_value_multiline)
            elif field.field_value is not None:
                comments.append(field.field_value)
            else:
                raise NotImplementedError
        self.ng_reserved_fields_cache[RequirementFieldName.COMMENT] = comments
        return comments

    # Other properties
    @property
    def is_requirement(self):
        return True

    @property
    def is_section(self):
        return False

    @property
    def is_composite_requirement(self):
        return False

    @property
    def document(self):
        return self.ng_document_reference.get_document()

    def is_inline_requirement(self):
        return (
            self.ng_document_reference.get_document().config.is_inline_requirements()  # noqa: E501
        )

    def has_requirement_references(self, ref_type):
        if not self.references or len(self.references) == 0:
            return False
        for reference in self.references:
            if reference.ref_type == ref_type:
                return True
        return False

    def get_requirement_references(self, ref_type):
        if not self.references or len(self.references) == 0:
            return []
        references = []
        for reference in self.references:
            if reference.ref_type != ref_type:
                continue
            references.append(reference)
        return references

    def enumerate_fields(self):
        requirement_fields = self.ordered_fields_lookup.values()
        for requirement_field in requirement_fields:
            for single_field in requirement_field:
                yield single_field

    def enumerate_meta_fields(
        self, skip_single_lines=False, skip_multi_lines=False
    ):
        for field in self.enumerate_fields():
            if field.field_name in RESERVED_NON_META_FIELDS:
                continue
            meta_field_value = (
                field.field_value
                if field.field_value
                else field.field_value_multiline
            )
            if (
                len(meta_field_value.splitlines()) > 1
                or len(meta_field_value.split(" ")) > MULTILINE_WORD_THRESHOLD
            ):
                is_single_line_field = False
            else:
                is_single_line_field = True

            if is_single_line_field and skip_single_lines:
                continue
            if (not is_single_line_field) and skip_multi_lines:
                continue

            yield field.field_name, meta_field_value

    def get_meta_field_value_by_title(self, field_title: str) -> Optional[str]:
        assert isinstance(field_title, str)
        if field_title not in self.ordered_fields_lookup:
            return None
        field: RequirementField = self.ordered_fields_lookup[field_title][0]
        meta_field_value_or_none: Optional[str] = (
            field.field_value
            if field.field_value
            else field.field_value_multiline
        )
        assert meta_field_value_or_none
        meta_field_value = meta_field_value_or_none
        return meta_field_value

    def dump_fields_as_parsed(self):
        return ", ".join(
            list(
                map(
                    lambda r: r.field_name,
                    self.fields_as_parsed,
                )
            )
        )

    # Below all mutating methods.

    def set_field_value(
        self, *, field_name: str, form_field_index: int, value: Optional[str]
    ):
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
            if field_name in self.ordered_fields_lookup:
                del self.ordered_fields_lookup[field_name]
            return

        singleline_fields = {"UID", "TITLE"}
        multiline_fields = {"STATEMENT", "RATIONALE", "COMMENT"}

        field_value = None
        field_value_multiline = None
        field_value_references = None
        if field_name in singleline_fields:
            field_value = value
        elif field_name in multiline_fields:
            field_value_multiline = value
        else:
            raise NotImplementedError(value)

        # FIXME: This will go away.
        if field_name == RequirementFieldName.UID:
            self.uid = field_value
        elif field_name == RequirementFieldName.TAGS:
            self.tags = field_value.split(", ")
        elif field_name == RequirementFieldName.LEVEL:
            self.level = field_value
        elif field_name == RequirementFieldName.STATUS:
            self.status = field_value
        if field_name in self.ng_reserved_fields_cache:
            del self.ng_reserved_fields_cache[field_name]

        if field_name in self.ordered_fields_lookup:
            if len(self.ordered_fields_lookup[field_name]) > form_field_index:
                self.ordered_fields_lookup[field_name][
                    form_field_index
                ] = RequirementField(
                    self,
                    field_name=field_name,
                    field_value=field_value,
                    field_value_multiline=field_value_multiline,
                    field_value_references=field_value_references,
                )
            else:
                self.ordered_fields_lookup[field_name].insert(
                    form_field_index,
                    RequirementField(
                        self,
                        field_name=field_name,
                        field_value=field_value,
                        field_value_multiline=field_value_multiline,
                        field_value_references=field_value_references,
                    ),
                )
            return

        new_ordered_fields_lookup = OrderedDict()
        document: Document = self.document
        grammar_or_none: Optional[DocumentGrammar] = document.grammar
        assert grammar_or_none is not None
        grammar: DocumentGrammar = grammar_or_none

        element: GrammarElement = grammar.elements_by_type["REQUIREMENT"]
        grammar_field_titles = list(map(lambda f: f.title, element.fields))
        field_index = grammar_field_titles.index(field_name)
        for field_title in grammar_field_titles[:field_index]:
            if field_title in self.ordered_fields_lookup:
                new_ordered_fields_lookup[
                    field_title
                ] = self.ordered_fields_lookup[field_title]
        new_ordered_fields_lookup[field_name] = [
            RequirementField(
                self,
                field_name=field_name,
                field_value=field_value,
                field_value_multiline=field_value_multiline,
                field_value_references=field_value_references,
            )
        ]
        after_field_index = field_index + 1
        for field_title in grammar_field_titles[after_field_index:]:
            if field_title in self.ordered_fields_lookup:
                new_ordered_fields_lookup[
                    field_title
                ] = self.ordered_fields_lookup[field_title]
        self.ordered_fields_lookup = new_ordered_fields_lookup
        self._update_has_meta()

    def _update_has_meta(self):
        has_meta: bool = False
        for field in self.enumerate_fields():
            if field.field_name not in RESERVED_NON_META_FIELDS:
                has_meta = True
        self.has_meta = has_meta


@auto_described
class CompositeRequirement(Requirement):
    def __init__(self, parent, **fields):
        super().__init__(parent, **fields)
        self.ng_document_reference: Optional[DocumentReference] = None
        self.ng_has_requirements = False

    @property
    def is_composite_requirement(self):
        return True

    @property
    def document(self):
        return self.ng_document_reference.get_document()


@auto_described
class Body:
    def __init__(self, parent, content):
        self.parent = parent
        self.content = content.strip()


@auto_described
class RequirementComment:
    def __init__(
        self,
        parent,
        comment_single: Optional[str],
        comment_multiline: Optional[str],
    ):
        self.parent = parent
        self.comment_single: Optional[str] = comment_single
        self.comment_multiline: Optional[str] = comment_multiline

        # The case when both are None is when a multi-line field has no text
        # but only an empty space:
        # [REQUIREMENT]
        # COMMENT: <empty space symbol>
        # assert comment_single is not None or comment_multiline is not None
        # TODO: One solution to simplify this would be to disallow empty fields
        # in the grammar completely.

    def get_comment(self):
        comment = (
            self.comment_single
            if self.comment_single
            else self.comment_multiline
        )
        return comment
