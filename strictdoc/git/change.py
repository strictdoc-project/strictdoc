from typing import Dict, List, Optional, Union

from strictdoc.backend.sdoc.models.requirement import RequirementField
from strictdoc.helpers.auto_described import auto_described


class SectionChange:
    def __init__(
        self,
        *,
        matched_uid: Optional[str],
        free_text_modified: bool,
        colored_free_text_diff: Optional[str],
    ):
        if matched_uid is not None:
            assert len(matched_uid) > 0
        self.matched_uid: Optional[str] = matched_uid
        self.free_text_modified: bool = free_text_modified
        self.colored_free_text_diff: Optional[str] = colored_free_text_diff


@auto_described
class RequirementFieldChange:
    def __init__(
        self,
        *,
        field_name: str,
        lhs_field: Optional[RequirementField],
        rhs_field: Optional[RequirementField],
        left_diff: Optional[str],
        right_diff: Optional[str],
    ):
        assert isinstance(field_name, str) and len(field_name) > 0
        assert lhs_field is not None or rhs_field is not None
        assert (left_diff is None and right_diff is None) or (
            left_diff is not None and right_diff is not None
        )

        self.field_name: str = field_name
        self.lhs_field: Optional[RequirementField] = lhs_field
        self.rhs_field: Optional[RequirementField] = rhs_field
        self.left_diff: Optional[str] = left_diff
        self.right_diff: Optional[str] = right_diff


class RequirementChange:
    def __init__(
        self,
        *,
        requirement_token: Optional[str],
        field_changes: List[RequirementFieldChange],
    ):
        assert requirement_token is None or len(requirement_token) > 0
        self.requirement_token: Optional[str] = requirement_token
        self.field_changes: List[RequirementFieldChange] = field_changes

        map_fields_to_changes: Dict[
            RequirementField, RequirementFieldChange
        ] = {}
        for field_change_ in field_changes:
            if field_change_.lhs_field is not None:
                map_fields_to_changes[field_change_.lhs_field] = field_change_
            if field_change_.rhs_field is not None:
                map_fields_to_changes[field_change_.rhs_field] = field_change_
        self.map_fields_to_changes: Dict[
            RequirementField, RequirementFieldChange
        ] = map_fields_to_changes

    def get_field_change(
        self, requirement_field: RequirementField
    ) -> Optional[RequirementFieldChange]:
        assert isinstance(requirement_field, RequirementField)
        return self.map_fields_to_changes.get(requirement_field)


ChangeUnionType = Union[SectionChange, RequirementChange]
