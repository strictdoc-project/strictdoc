from collections import OrderedDict
from typing import Optional, List

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document_grammar import (
    RESERVED_NON_META_FIELDS,
)
from strictdoc.backend.sdoc.models.node import Node
from strictdoc.backend.sdoc.models.reference import Reference


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
        self.field_value: Optional[str] = field_value
        self.field_value_multiline: Optional[str] = field_value_multiline
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
        tags = None
        references = []
        title = None
        statement = None
        statement_multiline = None
        rationale = None
        rationale_multiline = None
        comments: [RequirementComment] = []

        ordered_fields_lookup: OrderedDict[
            str, List[RequirementField]
        ] = OrderedDict()

        has_meta: bool = False
        for field in fields:
            if field.field_name not in RESERVED_NON_META_FIELDS:
                has_meta = True
            ordered_fields_lookup.setdefault(field.field_name, []).append(field)

        if "UID" in ordered_fields_lookup:
            uid = ordered_fields_lookup["UID"][0].field_value
        if "LEVEL" in ordered_fields_lookup:
            level = ordered_fields_lookup["LEVEL"][0].field_value
        if "STATUS" in ordered_fields_lookup:
            status = ordered_fields_lookup["STATUS"][0].field_value
        if "TAGS" in ordered_fields_lookup:
            tags = ordered_fields_lookup["TAGS"][0].field_value.split(", ")
        if "REFS" in ordered_fields_lookup:
            references = ordered_fields_lookup["REFS"][0].field_value_references
        if "TITLE" in ordered_fields_lookup:
            title = ordered_fields_lookup["TITLE"][0].field_value
        if "STATEMENT" in ordered_fields_lookup:
            field = ordered_fields_lookup["STATEMENT"][0]
            if field.field_value_multiline:
                statement_multiline = field.field_value_multiline
            else:
                statement = field.field_value
        if "RATIONALE" in ordered_fields_lookup:
            field = ordered_fields_lookup["RATIONALE"][0]
            if field.field_value_multiline:
                rationale_multiline = field.field_value_multiline
            else:
                rationale = field.field_value
        if "COMMENT" in ordered_fields_lookup:
            for comment_field in ordered_fields_lookup["COMMENT"]:
                field = comment_field
                if field.field_value_multiline:
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
        self.tags: Optional[str] = tags

        assert isinstance(references, List)
        self.references: List[Reference] = references

        self.title = title
        self.statement: Optional[str] = statement
        self.rationale = rationale
        self.comments = comments
        self.requirements = requirements

        # For multiline fields:
        # Due to the details of how matching single vs multistring lines is
        # implemented, the rstrip() is done to simplify SDoc code generation.
        self.statement_multiline: Optional[str] = (
            statement_multiline.rstrip() if statement_multiline else None
        )
        self.rationale_multiline = (
            rationale_multiline.rstrip() if rationale_multiline else None
        )

        # TODO: Is it worth to move this to dedicated Presenter* classes to
        # keep this class textx-only?
        self.has_meta: bool = has_meta
        self.fields: List[RequirementField] = fields
        self.ordered_fields_lookup: OrderedDict[
            str, List[RequirementField]
        ] = ordered_fields_lookup
        self.ng_level = None
        self.ng_document_reference: Optional[DocumentReference] = None
        self.context = RequirementContext()

    def __str__(self):
        return (
            f"{self.__class__.__name__}("
            f"ng_level: {self.ng_level}, "
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

    def get_requirement_references(self):
        if not self.references or len(self.references) == 0:
            return []
        references = []
        for reference in self.references:
            if reference.ref_type != "Parent":
                continue
            references.append(reference)
        return references

    def get_statement_single_or_multiline(self):
        if self.statement:
            return self.statement
        if self.statement_multiline:
            return self.statement_multiline
        return None

    def get_rationale_single_or_multiline(self):
        if self.rationale:
            return self.rationale
        if self.rationale_multiline:
            return self.rationale_multiline
        return None

    def append_to_multiline_statement(self, new_statement):
        statement_field = self.ordered_fields_lookup["STATEMENT"][0]
        statement_field.field_value_multiline += new_statement.rstrip()
        self.statement_multiline = statement_field.field_value_multiline

    def enumerate_fields(self):
        requirement_fields = self.ordered_fields_lookup.values()
        for requirement_field in requirement_fields:
            for single_field in requirement_field:
                yield single_field

    def enumerate_meta_fields(self):
        for field in self.fields:
            if field.field_name in RESERVED_NON_META_FIELDS:
                continue
            yield field.field_name, field.field_value

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
        self.ng_sections = []
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

        # Due to the details of how matching single vs multistring lines is
        # implemented, the rstrip() is done to simplify SDoc code generation.
        self.comment_multiline: Optional[str] = (
            comment_multiline.rstrip() if comment_multiline else None
        )

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
