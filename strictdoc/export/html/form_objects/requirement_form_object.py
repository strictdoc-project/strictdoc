import html
from typing import Optional

from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.server.error_object import ErrorObject


class RequirementFormObject(ErrorObject):
    def __init__(
        self,
        *,
        requirement_mid: Optional[str],
        requirement_uid: Optional[str],
        requirement_title: Optional[str],
        requirement_statement: Optional[str],
        requirement_rationale: Optional[str],
    ):
        super().__init__()
        self.requirement_mid: Optional[str] = requirement_mid
        self._requirement_uid: Optional[str] = requirement_uid
        self._requirement_title: Optional[str] = requirement_title
        if requirement_statement is not None:
            requirement_statement = html.escape(requirement_statement)
        self._requirement_statement: Optional[str] = requirement_statement
        if requirement_rationale is not None:
            requirement_rationale = html.escape(requirement_rationale)
        self._requirement_rationale: Optional[str] = requirement_rationale

    @property
    def requirement_uid(self) -> str:
        if self._requirement_uid is not None:
            assert len(self._requirement_uid) > 0, self._requirement_uid
            return self._requirement_uid
        else:
            return ""

    @property
    def requirement_title(self) -> str:
        if self._requirement_title is not None:
            assert len(self._requirement_title) > 0, self._requirement_title
            return self._requirement_title
        else:
            return ""

    @property
    def requirement_statement(self) -> str:
        if self._requirement_statement is not None:
            assert (
                len(self._requirement_statement) > 0
            ), self._requirement_statement
            return self._requirement_statement
        else:
            return ""

    @property
    def requirement_rationale(self) -> str:
        if self._requirement_rationale is not None:
            assert (
                len(self._requirement_rationale) > 0
            ), self._requirement_rationale
            return self._requirement_rationale
        else:
            return ""

    @staticmethod
    def create_from_requirement(*, requirement: Requirement):
        return RequirementFormObject(
            requirement_mid=requirement.node_id,
            requirement_uid=requirement.uid,
            requirement_title=requirement.title,
            requirement_statement=(
                requirement.get_statement_single_or_multiline()
            ),
            requirement_rationale=(
                requirement.get_rationale_single_or_multiline()
            ),
        )
