from typing import Optional, List

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)


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
    def create_requirement(  # pylint: disable=too-many-arguments
        parent,
        requirement_type: str,
        uid: Optional[str],
        level: Optional[str],
        title: Optional[str],
        statement: Optional[str],
        statement_multiline: Optional[str],
        rationale: Optional[str],
        rationale_multiline: Optional[str],
        tags: Optional[str],
        comments: Optional[List[str]],
    ) -> Requirement:
        fields: List[RequirementField] = []
        if uid:
            assert isinstance(uid, str) and len(uid) > 0
            fields.append(
                RequirementField(
                    parent=None,
                    field_name="UID",
                    field_value=uid,
                    field_value_multiline=None,
                    field_value_references=None,
                )
            )
        if level:
            assert isinstance(level, str) and len(level) > 0
            fields.append(
                RequirementField(
                    parent=None,
                    field_name="LEVEL",
                    field_value=level,
                    field_value_multiline=None,
                    field_value_references=None,
                )
            )
        if title:
            fields.append(
                RequirementField(
                    parent=None,
                    field_name="TITLE",
                    field_value=title,
                    field_value_multiline=None,
                    field_value_references=None,
                )
            )
        if statement:
            fields.append(
                RequirementField(
                    parent=None,
                    field_name="STATEMENT",
                    field_value=statement,
                    field_value_multiline=None,
                    field_value_references=None,
                )
            )
        if statement_multiline:
            assert isinstance(
                statement_multiline, str
            ), f"{statement_multiline}"
            fields.append(
                RequirementField(
                    parent=None,
                    field_name="STATEMENT",
                    field_value=None,
                    field_value_multiline=statement_multiline,
                    field_value_references=None,
                )
            )
        if rationale:
            fields.append(
                RequirementField(
                    parent=None,
                    field_name="RATIONALE",
                    field_value=rationale,
                    field_value_multiline=None,
                    field_value_references=None,
                )
            )
        if rationale_multiline:
            fields.append(
                RequirementField(
                    parent=None,
                    field_name="RATIONALE",
                    field_value=None,
                    field_value_multiline=rationale_multiline,
                    field_value_references=None,
                )
            )
        if tags is not None:
            assert isinstance(tags, str), f"{tags}"
            fields.append(
                RequirementField(
                    parent=None,
                    field_name="TAGS",
                    field_value=tags,
                    field_value_multiline=None,
                    field_value_references=None,
                )
            )
        if comments is not None:
            assert isinstance(comments, list), f"{comments}"
            for comment in comments:
                assert isinstance(comment, str), f"{comment}"
                fields.append(
                    RequirementField(
                        parent=None,
                        field_name="COMMENT",
                        field_value=None,
                        field_value_multiline=comment,
                        field_value_references=None,
                    )
                )
        return Requirement(
            parent=parent, requirement_type=requirement_type, fields=fields
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

        requirement = SDocObjectFactory.create_requirement(
            parent=parent,
            requirement_type="REQUIREMENT",
            uid=uid,
            level=None,
            title=title,
            statement=None,
            statement_multiline=statement_multiline,
            rationale=None,
            rationale_multiline=rationale_multiline,
            tags=None,
            comments=None,
        )

        requirement.ng_level = level
        return requirement
