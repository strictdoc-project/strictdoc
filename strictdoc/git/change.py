from enum import Enum
from typing import Dict, List, Optional, Union

from markupsafe import Markup

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import (
    SDocNode,
    SDocNodeField,
)
from strictdoc.helpers.auto_described import auto_described


class ChangeType(str, Enum):
    DOCUMENT = "Document"
    DOCUMENT_MODIFIED = "Document modified"

    REQUIREMENT = "Node"
    REQUIREMENT_REMOVED = "Node removed"
    REQUIREMENT_MODIFIED = "Node modified"
    REQUIREMENT_ADDED = "Node added"


@auto_described
class DocumentChange:
    def __init__(
        self,
        *,
        matched_uid: Optional[str],
        lhs_document: Optional[SDocDocument],
        rhs_document: Optional[SDocDocument],
        uid_modified: bool,
        title_modified: bool,
        lhs_colored_uid_diff: Optional[Markup],
        rhs_colored_uid_diff: Optional[Markup],
        lhs_colored_title_diff: Optional[Markup],
        rhs_colored_title_diff: Optional[Markup],
        document_token: str,
        is_included_document: bool,
    ):
        assert lhs_document is not None or rhs_document is not None
        if matched_uid is not None:
            assert len(matched_uid) > 0
        self.matched_uid: Optional[str] = matched_uid
        self.uid_modified: bool = uid_modified
        self.title_modified: bool = title_modified

        self.lhs_colored_uid_diff: Optional[Markup] = lhs_colored_uid_diff
        self.rhs_colored_uid_diff: Optional[Markup] = rhs_colored_uid_diff

        self.lhs_colored_title_diff: Optional[Markup] = lhs_colored_title_diff
        self.rhs_colored_title_diff: Optional[Markup] = rhs_colored_title_diff

        self.lhs_document: Optional[SDocDocument] = lhs_document
        self.rhs_document: Optional[SDocDocument] = rhs_document

        self.change_type: ChangeType = ChangeType.DOCUMENT_MODIFIED
        self.document_token: str = document_token
        self.is_included_document: bool = is_included_document

    def get_colored_uid_diff(self, side: str) -> Optional[Markup]:
        assert self.uid_modified
        if side == "left":
            return self.lhs_colored_uid_diff
        if side == "right":
            return self.rhs_colored_uid_diff
        raise AssertionError(f"Must not reach here: {side}")

    def get_colored_title_diff(self, side: str) -> Optional[Markup]:
        assert self.title_modified
        if side == "left":
            return self.lhs_colored_title_diff
        if side == "right":
            return self.rhs_colored_title_diff
        raise AssertionError(f"Must not reach here: {side}")


@auto_described
class RequirementFieldChange:
    def __init__(
        self,
        *,
        field_name: str,
        lhs_field: Optional[SDocNodeField],
        rhs_field: Optional[SDocNodeField],
        left_diff: Optional[Markup],
        right_diff: Optional[Markup],
    ):
        assert isinstance(field_name, str) and len(field_name) > 0
        assert lhs_field is not None or rhs_field is not None
        assert (left_diff is None and right_diff is None) or (
            left_diff is not None and right_diff is not None
        )

        self.field_name: str = field_name
        self.lhs_field: Optional[SDocNodeField] = lhs_field
        self.rhs_field: Optional[SDocNodeField] = rhs_field
        self.left_diff: Optional[Markup] = left_diff
        self.right_diff: Optional[Markup] = right_diff

    def get_colored_free_text_diff(self, side: str) -> Optional[Markup]:
        if side == "left":
            return self.left_diff
        if side == "right":
            return self.right_diff
        raise AssertionError(f"Must not reach here: {side}")


@auto_described
class RequirementChange:
    def __init__(
        self,
        *,
        requirement_token: Optional[str],
        lhs_requirement: Optional[SDocNode],
        rhs_requirement: Optional[SDocNode],
        field_changes: List[RequirementFieldChange],
    ):
        assert requirement_token is None or len(requirement_token) > 0
        assert lhs_requirement is not None or rhs_requirement is not None

        self.requirement_token: Optional[str] = requirement_token
        self.lhs_requirement: Optional[SDocNode] = lhs_requirement
        self.rhs_requirement: Optional[SDocNode] = rhs_requirement

        self.field_changes: List[RequirementFieldChange] = field_changes

        map_fields_to_changes: Dict[SDocNodeField, RequirementFieldChange] = {}
        for field_change_ in field_changes:
            if field_change_.lhs_field is not None:
                map_fields_to_changes[field_change_.lhs_field] = field_change_
            if field_change_.rhs_field is not None:
                map_fields_to_changes[field_change_.rhs_field] = field_change_
        self.map_fields_to_changes: Dict[
            SDocNodeField, RequirementFieldChange
        ] = map_fields_to_changes

        if requirement_token is not None:
            change_type = ChangeType.REQUIREMENT_MODIFIED
        elif lhs_requirement is not None:
            change_type = ChangeType.REQUIREMENT_REMOVED
        elif rhs_requirement is not None:
            change_type = ChangeType.REQUIREMENT_ADDED
        else:
            raise AssertionError("Must not reach here.")  # pragma: no cover
        self.change_type = change_type

    def is_paired_change(self) -> bool:
        return (
            self.lhs_requirement is not None
            and self.rhs_requirement is not None
        )

    def get_field_change(
        self, requirement_field: SDocNodeField
    ) -> Optional[RequirementFieldChange]:
        assert isinstance(requirement_field, SDocNodeField)
        return self.map_fields_to_changes.get(requirement_field)


ChangeUnionType = Union[DocumentChange, RequirementChange]
