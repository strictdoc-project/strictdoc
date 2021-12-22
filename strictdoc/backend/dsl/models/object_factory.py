from typing import Optional

from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.requirement import Requirement


class SDocObjectFactory:
    @staticmethod
    def create_document(title: Optional[str]):
        return Document(
            name=None,
            title=title if title else "NONAME",
            config=None,
            grammar=None,
            free_texts=[],
            section_contents=[],
        )

    @staticmethod
    def create_requirement_from_dict(requirement_dict, parent, level):
        assert requirement_dict is not None
        assert parent
        assert isinstance(level, int)
        assert level > 0

        uid = None
        if "UID" in requirement_dict:
            uid_ = requirement_dict["UID"]
            if isinstance(uid_, str):
                uid = uid_

        title = None
        if "TITLE" in requirement_dict:
            title_ = requirement_dict["TITLE"]
            if isinstance(title_, str):
                title = title_

        statement_multiline = None
        if "STATEMENT" in requirement_dict:
            statement_multiline_ = requirement_dict["STATEMENT"]
            if isinstance(statement_multiline_, str):
                statement_multiline = statement_multiline_

        rationale_multiline = None
        if "RATIONALE" in requirement_dict:
            rationale_multiline_ = requirement_dict["RATIONALE"]
            if isinstance(rationale_multiline_, str):
                rationale_multiline = rationale_multiline_

        requirement = Requirement(
            parent=parent,
            requirement_type="REQUIREMENT",
            statement=None,
            statement_multiline=statement_multiline,
            uid=uid,
            level=None,
            status=None,
            tags=None,
            references=[],
            title=title,
            body=None,
            rationale=None,
            rationale_multiline=rationale_multiline,
            comments=[],
            special_fields=[],
            requirements=None,
        )

        requirement.ng_level = level
        return requirement
