import uuid
from collections import OrderedDict
from typing import Optional, List

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.node import Node
from strictdoc.backend.sdoc.models.reference import Reference
from strictdoc.backend.sdoc.models.type_system import (
    RequirementFieldName,
    RESERVED_NON_META_FIELDS,
)

MULTILINE_WORD_THRESHOLD = 6


class RequirementContext:
    def __init__(self):
        self.title_number_string = None


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

    def __str__(self):
        return (
            f"{self.__class__.__name__}("
            f"field_name: {self.field_name}, "
            f"field_value: {self.field_value}, "
            f"field_value_multiline: {self.field_value_multiline}, "
            f"field_value_references: {self.field_value_references}, "
            ")"
        )

    def __repr__(self):
        return self.__str__()


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
        title = None
        statement = None
        statement_multiline = None
        rationale = None
        rationale_multiline = None
        comments: List[RequirementComment] = []

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

        if RequirementFieldName.TITLE in ordered_fields_lookup:
            title = ordered_fields_lookup[RequirementFieldName.TITLE][
                0
            ].field_value
        if RequirementFieldName.STATEMENT in ordered_fields_lookup:
            field = ordered_fields_lookup[RequirementFieldName.STATEMENT][0]
            if field.field_value_multiline is not None:
                statement_multiline = field.field_value_multiline
            else:
                statement = field.field_value
        if RequirementFieldName.RATIONALE in ordered_fields_lookup:
            field = ordered_fields_lookup[RequirementFieldName.RATIONALE][0]
            if field.field_value_multiline:
                rationale_multiline = field.field_value_multiline
            else:
                rationale = field.field_value
        if RequirementFieldName.COMMENT in ordered_fields_lookup:
            for comment_field in ordered_fields_lookup[
                RequirementFieldName.COMMENT
            ]:
                field = comment_field
                if field.field_value_multiline is not None:
                    comments.append(
                        RequirementComment(
                            parent=self,
                            comment_single=None,
                            comment_multiline=field.field_value_multiline,
                        )
                    )
                else:
                    comments.append(
                        RequirementComment(
                            parent=self,
                            comment_single=field.field_value,
                            comment_multiline=None,
                        )
                    )

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

        self.title = title
        self.statement: Optional[str] = statement
        self.rationale = rationale
        self.comments = comments
        self.requirements = requirements

        self.statement_multiline: Optional[str] = statement_multiline
        self.rationale_multiline: Optional[str] = rationale_multiline

        # TODO: Is it worth to move this to dedicated Presenter* classes to
        # keep this class textx-only?
        self.has_meta: bool = has_meta
        self.fields: List[RequirementField] = fields
        self.ordered_fields_lookup: OrderedDict[
            str, List[RequirementField]
        ] = ordered_fields_lookup
        self.ng_level: Optional[int] = None
        self.ng_document_reference: Optional[DocumentReference] = None
        self.context = RequirementContext()

        self.node_id = uuid.uuid4().hex

    def __str__(self):
        return (
            f"{self.__class__.__name__}("
            f"ng_level: {self.ng_level}, "
            f"level: {self.level}, "
            f"uid: {self.uid}, "
            f"title_or_none: {self.title}, "
            f"statement: {self.statement}"
            ")"
        )

    def __repr__(self):
        return self.__str__()

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

    def get_statement_single_or_multiline(self) -> Optional[str]:
        if self.statement_multiline is not None:
            return self.statement_multiline
        if self.statement is not None:
            return self.statement
        return None

    def get_rationale_single_or_multiline(self):
        if self.rationale:
            return self.rationale
        if self.rationale_multiline:
            return self.rationale_multiline
        return None

    def enumerate_fields(self):
        requirement_fields = self.ordered_fields_lookup.values()
        for requirement_field in requirement_fields:
            for single_field in requirement_field:
                yield single_field

    def enumerate_meta_fields(
        self, skip_single_lines=False, skip_multi_lines=False
    ):
        for field in self.fields:
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

    def dump_fields(self):
        return ", ".join(
            list(
                map(
                    lambda r: r.field_name,
                    self.fields,
                )
            )
        )


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


class Body:
    def __init__(self, parent, content):
        self.parent = parent
        self.content = content.strip()

    def __str__(self):
        return f"Body({self.content})"

    def __repr__(self):
        return self.__str__()


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

    def __str__(self):
        return (
            f"Comment("
            f"comment_single: {self.comment_single}, "
            f"comment_multiline: {self.comment_multiline}"
            f")"
        )

    def __repr__(self):
        return self.__str__()

    def get_comment(self):
        comment = (
            self.comment_single
            if self.comment_single
            else self.comment_multiline
        )
        return comment
