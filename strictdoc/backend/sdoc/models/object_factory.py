# mypy: disable-error-code="arg-type,no-untyped-call,no-untyped-def"
from typing import List, Optional

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.type_system import RequirementFieldName


class SDocObjectFactory:
    @staticmethod
    def create_document(title: Optional[str]):
        return SDocDocument(
            mid=None,
            title=title if title else "NONAME",
            config=None,
            view=None,
            grammar=None,
            free_texts=[],
            section_contents=[],
        )

    @staticmethod
    def create_requirement(
        parent,
        node_type: Optional[str] = "REQUIREMENT",
        uid: Optional[str] = None,
        level: Optional[str] = None,
        title: Optional[str] = None,
        statement: Optional[str] = None,
        statement_multiline: Optional[str] = None,
        rationale: Optional[str] = None,
        rationale_multiline: Optional[str] = None,
        tags: Optional[str] = None,
        comments: Optional[List[str]] = None,
    ) -> SDocNode:
        fields: List[SDocNodeField] = []
        if uid is not None:
            assert isinstance(uid, str) and len(uid) > 0
            fields.append(
                SDocNodeField.create_from_string(
                    parent=None,
                    field_name=RequirementFieldName.UID,
                    field_value=uid,
                    multiline=False,
                )
            )
        if level:
            assert isinstance(level, str) and len(level) > 0
            fields.append(
                SDocNodeField.create_from_string(
                    parent=None,
                    field_name=RequirementFieldName.LEVEL,
                    field_value=level,
                    multiline=False,
                )
            )
        if title is not None:
            fields.append(
                SDocNodeField.create_from_string(
                    parent=None,
                    field_name=RequirementFieldName.TITLE,
                    field_value=title,
                    multiline=False,
                )
            )
        if statement:
            fields.append(
                SDocNodeField.create_from_string(
                    parent=None,
                    field_name=RequirementFieldName.STATEMENT,
                    field_value=statement,
                    multiline=False,
                )
            )
        if statement_multiline is not None:
            assert isinstance(
                statement_multiline, str
            ), f"{statement_multiline}"
            fields.append(
                SDocNodeField.create_from_string(
                    parent=None,
                    field_name=RequirementFieldName.STATEMENT,
                    field_value=statement_multiline,
                    multiline=True,
                )
            )
        if rationale:
            fields.append(
                SDocNodeField.create_from_string(
                    parent=None,
                    field_name=RequirementFieldName.RATIONALE,
                    field_value=rationale,
                    multiline=False,
                )
            )
        if rationale_multiline:
            fields.append(
                SDocNodeField.create_from_string(
                    parent=None,
                    field_name=RequirementFieldName.RATIONALE,
                    field_value=rationale_multiline,
                    multiline=True,
                )
            )
        if tags is not None:
            assert isinstance(tags, str), f"{tags}"
            fields.append(
                SDocNodeField.create_from_string(
                    parent=None,
                    field_name=RequirementFieldName.TAGS,
                    field_value=tags,
                    multiline=False,
                )
            )
        if comments is not None:
            assert isinstance(comments, list), f"{comments}"
            for comment in comments:
                assert isinstance(comment, str), f"{comment}"
                fields.append(
                    SDocNodeField.create_from_string(
                        parent=None,
                        field_name=RequirementFieldName.COMMENT,
                        field_value=comment,
                        multiline=True,
                    )
                )
        requirement = SDocNode(
            parent=parent,
            node_type=node_type,
            fields=fields,
            relations=[],
        )
        requirement.ng_document_reference = DocumentReference()
        if isinstance(parent, SDocDocument):
            requirement.ng_document_reference.set_document(parent)
        else:
            requirement.ng_document_reference.set_document(parent.document)
        return requirement

    @staticmethod
    def create_requirement_from_dict(requirement_dict, parent, level):
        assert requirement_dict is not None
        assert parent
        assert isinstance(level, int)
        assert level > 0

        uid = None
        if RequirementFieldName.UID in requirement_dict:
            uid_ = requirement_dict[RequirementFieldName.UID]
            if isinstance(uid_, str):
                uid = uid_

        title = None
        if RequirementFieldName.TITLE in requirement_dict:
            title_ = requirement_dict[RequirementFieldName.TITLE]
            if isinstance(title_, str):
                title = title_

        statement_multiline = None
        if RequirementFieldName.STATEMENT in requirement_dict:
            statement_multiline_ = requirement_dict[
                RequirementFieldName.STATEMENT
            ]
            if isinstance(statement_multiline_, str):
                statement_multiline = statement_multiline_

        rationale_multiline = None
        if RequirementFieldName.RATIONALE in requirement_dict:
            rationale_multiline_ = requirement_dict[
                RequirementFieldName.RATIONALE
            ]
            if isinstance(rationale_multiline_, str):
                rationale_multiline = rationale_multiline_

        requirement = SDocObjectFactory.create_requirement(
            parent=parent,
            node_type="REQUIREMENT",
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

        return requirement
