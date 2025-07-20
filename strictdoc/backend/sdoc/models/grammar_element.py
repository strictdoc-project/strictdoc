"""
@relation(SDOC-SRS-21, scope=file)
"""

from collections import OrderedDict
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

from strictdoc.backend.sdoc.models.model import (
    RESERVED_NON_META_FIELDS,
    RequirementFieldName,
)
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID


class RequirementFieldType:
    STRING = "String"
    SINGLE_CHOICE = "SingleChoice"
    MULTIPLE_CHOICE = "MultipleChoice"
    TAG = "Tag"
    REFERENCE = "Reference"


class GrammarReferenceType:
    PARENT_REQ_REFERENCE = "ParentReqReference"
    CHILD_REQ_REFERENCE = "ChildReqReference"
    FILE_REFERENCE = "FileReference"


class ReferenceType:
    PARENT = "Parent"
    CHILD = "Child"
    FILE = "File"

    GRAMMAR_REFERENCE_TYPE_MAP = {
        PARENT: GrammarReferenceType.PARENT_REQ_REFERENCE,
        CHILD: GrammarReferenceType.CHILD_REQ_REFERENCE,
        FILE: GrammarReferenceType.FILE_REFERENCE,
    }


@auto_described
class GrammarElementField:
    def __init__(self) -> None:
        self.title: str = ""
        self.human_title: Optional[str] = None
        self.gef_type: str = ""
        self.required: bool = False
        self.mid: MID = MID.create()

    def get_field_human_name(self) -> str:
        if self.human_title is not None:
            return self.human_title
        return self.title


@auto_described
class GrammarElementFieldString(GrammarElementField):
    def __init__(
        self, parent: Any, title: str, human_title: Optional[str], required: str
    ) -> None:
        super().__init__()
        self.parent: Any = parent
        self.title: str = title
        self.human_title: Optional[str] = human_title
        self.gef_type = RequirementFieldType.STRING
        self.required: bool = required == "True"
        self.mid: MID = MID.create()


@auto_described
class GrammarElementFieldSingleChoice(GrammarElementField):
    def __init__(
        self,
        parent: Any,
        title: str,
        human_title: Optional[str],
        options: List[str],
        required: str,
    ) -> None:
        super().__init__()
        self.parent: Any = parent
        self.title: str = title
        self.human_title: Optional[str] = human_title
        self.gef_type = RequirementFieldType.SINGLE_CHOICE
        self.options: List[str] = options
        self.required: bool = required == "True"
        self.mid: MID = MID.create()


@auto_described
class GrammarElementFieldMultipleChoice(GrammarElementField):
    def __init__(
        self,
        parent: Any,
        title: str,
        human_title: Optional[str],
        options: List[str],
        required: str,
    ) -> None:
        super().__init__()
        self.parent: Any = parent
        self.title: str = title
        self.human_title: Optional[str] = human_title
        self.gef_type = RequirementFieldType.MULTIPLE_CHOICE
        self.options: List[str] = options
        self.required: bool = required == "True"
        self.mid: MID = MID.create()


@auto_described
class GrammarElementFieldTag(GrammarElementField):
    def __init__(
        self, parent: Any, title: str, human_title: Optional[str], required: str
    ) -> None:
        super().__init__()
        self.parent: Any = parent
        self.title: str = title
        self.human_title: Optional[str] = human_title
        self.gef_type = RequirementFieldType.TAG
        self.required: bool = required == "True"
        self.mid: MID = MID.create()


GrammarElementFieldType = Union[
    GrammarElementFieldString,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldTag,
]


@auto_described
class GrammarElementRelationParent:  # noqa: PLW1641
    def __init__(
        self, parent: Any, relation_type: str, relation_role: Optional[str]
    ) -> None:
        assert relation_type == "Parent"
        self.parent: Any = parent
        self.relation_type: str = relation_type
        self.relation_role: Optional[str] = (
            relation_role
            if relation_role is not None and len(relation_role) > 0
            else None
        )
        self.mid: MID = MID.create()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, GrammarElementRelationParent):
            raise AssertionError(self, other)  # pragma: no cover
        return (
            self.mid == other.mid
            and self.relation_type == other.relation_type
            and self.relation_role == other.relation_role
        )


@auto_described
class GrammarElementRelationChild:
    def __init__(
        self, parent: Any, relation_type: str, relation_role: Optional[str]
    ):
        assert relation_type == "Child"
        self.parent: Any = parent
        self.relation_type = relation_type
        self.relation_role: Optional[str] = (
            relation_role
            if relation_role is not None and len(relation_role) > 0
            else None
        )
        self.mid: MID = MID.create()


@auto_described
class GrammarElementRelationFile:
    def __init__(
        self, parent: Any, relation_type: str, relation_role: Optional[str]
    ):
        assert relation_type == "File"
        self.parent: Any = parent
        self.relation_type = relation_type
        self.relation_role: Optional[str] = (
            relation_role
            if relation_role is not None and len(relation_role) > 0
            else None
        )
        self.mid: MID = MID.create()


GrammarElementRelationType = Union[
    GrammarElementRelationParent,
    GrammarElementRelationChild,
    GrammarElementRelationFile,
]


@auto_described()
class GrammarElement:
    def __init__(
        self,
        parent: Any,
        tag: str,
        property_is_composite: str,
        property_prefix: str,
        property_view_style: str,
        fields: List[GrammarElementFieldType],
        relations: List[GrammarElementRelationType],
    ) -> None:
        self.parent: Any = parent
        self.tag: str = tag

        assert property_is_composite in ("", "True", "False")
        self.property_is_composite: Optional[bool] = (
            None
            if property_is_composite == ""
            else (property_is_composite == "True")
        )

        self.property_prefix: Optional[str] = (
            property_prefix if property_prefix not in (None, "") else None
        )

        assert property_view_style in (
            "",
            "Plain",
            "Narrative",
            "Simple",
            "Inline",
            "Table",
            "Zebra",
        )
        self.property_view_style: Optional[str] = (
            property_view_style if property_view_style != "" else None
        )
        self.property_view_style_lower: Optional[str] = (
            property_view_style.lower() if property_view_style != "" else None
        )

        self.fields: List[GrammarElementFieldType] = fields

        self.relations: List[GrammarElementRelationType] = (
            relations if relations is not None and len(relations) > 0 else []
        )

        fields_map: OrderedDict[str, GrammarElementField] = OrderedDict()

        statement_field: Optional[Tuple[str, int]] = None
        description_field: Optional[Tuple[str, int]] = None
        content_field: Optional[Tuple[str, int]] = None
        for field_idx_, field_ in enumerate(fields):
            fields_map[field_.title] = field_
            if field_.title == RequirementFieldName.STATEMENT:
                statement_field = (RequirementFieldName.STATEMENT, field_idx_)
            elif field_.title == "DESCRIPTION":
                description_field = (
                    RequirementFieldName.DESCRIPTION,
                    field_idx_,
                )
            elif field_.title == "CONTENT":
                content_field = (RequirementFieldName.CONTENT, field_idx_)
            else:
                pass
        self.fields_map: Dict[str, GrammarElementField] = fields_map

        self.field_titles: List[str] = list(
            map(lambda field__: field__.title, self.fields)
        )

        self.content_field: Tuple[str, int] = (
            statement_field or description_field or content_field or ("", -1)
        )

        # Use TITLE as a boundary between the single-line and multiline, if
        # TITLE exists. For nodes without a TITLE, use the content field, e.g.,
        # STATEMENT or DESCRIPTION.
        try:
            multiline_field_index = self.get_field_titles().index("TITLE") + 1
        except ValueError:
            multiline_field_index = self.content_field[1]
        self._multiline_field_index: int = multiline_field_index

        self.mid: MID = MID.create()
        self.ng_line_start: Optional[int] = None
        self.ng_col_start: Optional[int] = None

    @staticmethod
    def create_default(tag: str) -> "GrammarElement":
        return GrammarElement(
            parent=None,
            tag=tag,
            property_is_composite="",
            property_prefix="",
            property_view_style="",
            fields=[
                GrammarElementFieldString(
                    parent=None,
                    title="UID",
                    human_title=None,
                    required="False",
                ),
                GrammarElementFieldString(
                    parent=None,
                    title="TITLE",
                    human_title=None,
                    required="False",
                ),
                GrammarElementFieldString(
                    parent=None,
                    title="STATEMENT",
                    human_title=None,
                    required="False",
                ),
            ],
            relations=[],
        )

    @staticmethod
    def create_default_relations(
        parent: "GrammarElement",
    ) -> List[GrammarElementRelationType]:
        return [
            GrammarElementRelationParent(
                parent=parent,
                relation_type="Parent",
                relation_role=None,
            ),
            GrammarElementRelationFile(
                parent=parent,
                relation_type="File",
                relation_role=None,
            ),
        ]

    def is_field_multiline(self, field_name: str) -> bool:
        field_index = self.field_titles.index(field_name)
        return self.is_field_idx_multiline(field_index)

    def is_field_idx_multiline(self, field_idx: int) -> bool:
        # If there is none of TITLE-STATEMENT-DESCRIPTION-CONTENT present, i.e.,
        # multiline_field_index is -1, every field will be treated as multiline.
        return self._multiline_field_index <= field_idx

    def get_view_style(self) -> Optional[str]:
        if self.property_view_style_lower is not None:
            return self.property_view_style_lower
        # For backward compatibility with older versions that didn't have the
        # [[NODE]] syntax and didn't enter the corresponding template migration,
        # keep the TEXT nodes to have a "plain" style unless their type is
        # specified by the grammar.
        if self.tag == "TEXT":
            return "plain"
        return None

    def get_relation_types(self) -> List[str]:
        return list(
            map(lambda relation_: relation_.relation_type, self.relations)
        )

    def get_field_titles(self) -> List[str]:
        return self.field_titles

    def get_tag_lower(self) -> str:
        return self.tag.lower()

    def has_relation_type_role(
        self, relation_type: str, relation_role: Optional[str]
    ) -> bool:
        assert relation_role is None or len(relation_role) > 0
        for relation_ in self.relations:
            if (
                relation_.relation_type == relation_type
                and relation_.relation_role == relation_role
            ):
                return True
        return False

    def enumerate_meta_field_titles(self) -> Generator[str, None, None]:
        for field in self.fields:
            if field.title in (
                RequirementFieldName.TITLE,
                RequirementFieldName.STATEMENT,
            ):
                break
            if field.title in RESERVED_NON_META_FIELDS:
                continue
            yield field.title

    def enumerate_custom_content_field_titles(
        self,
    ) -> Generator[str, None, None]:
        after_title_or_statement = False
        for field in self.fields:
            if field.title in (
                RequirementFieldName.TITLE,
                RequirementFieldName.STATEMENT,
            ):
                after_title_or_statement = True
            if field.title in RESERVED_NON_META_FIELDS:
                continue
            if not after_title_or_statement:
                continue
            yield field.title
