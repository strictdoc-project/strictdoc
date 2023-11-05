from typing import Optional

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    ParentReqReference,
)
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    RequirementField,
)


class DocumentBuilder:
    def __init__(self):
        self.document: Document = self._create_empty_document()
        self.requirements = []

    def add_requirement(self, uid):
        parent = self.document
        statement = "System X shall do Y"
        statement_multiline = None
        tags = None
        title = "Requirement title"
        rationale = None
        rationale_multiline = None
        comments = []

        requirement = SDocObjectFactory.create_requirement(
            parent=parent,
            requirement_type="REQUIREMENT",
            uid=uid,
            level=None,
            title=title,
            statement=statement,
            statement_multiline=statement_multiline,
            rationale=rationale,
            rationale_multiline=rationale_multiline,
            comments=comments,
            tags=tags,
        )
        requirement.ng_level = 1
        self.requirements.append(requirement)
        self.document.section_contents.append(requirement)
        requirement.ng_document_reference = DocumentReference()
        requirement.ng_document_reference.set_document(self.document)
        return requirement

    def add_requirement_relation(
        self,
        *,
        relation_type: str,
        source_requirement_id,
        target_requirement_id,
        role: Optional[str],
    ):
        assert relation_type in ("Parent", "Child")
        requirement: Requirement = next(
            r
            for r in self.requirements
            if r.reserved_uid == source_requirement_id
        )
        assert requirement is not None

        reference = (
            ParentReqReference(requirement, target_requirement_id, role=role)
            if relation_type == "Parent"
            else ChildReqReference(
                requirement, target_requirement_id, role=role
            )
        )
        requirement.references.append(reference)
        if "REFS" not in requirement.ordered_fields_lookup:
            requirement.ordered_fields_lookup["REFS"] = [
                RequirementField(
                    parent=requirement,
                    field_name="REFS",
                    field_value=None,
                    field_value_multiline=None,
                    field_value_references=requirement.references,
                )
            ]
        else:
            requirement.ordered_fields_lookup["REFS"][0] = RequirementField(
                parent=requirement,
                field_name="REFS",
                field_value=None,
                field_value_multiline=None,
                field_value_references=requirement.references,
            )

    def build(self):
        return self.document

    @staticmethod
    def _create_empty_document() -> Document:
        config = DocumentConfig(
            parent=None,
            version="0.0.1",
            uid="DOC-1",
            classification=None,
            requirement_prefix=None,
            root=None,
            markup=None,
            auto_levels=None,
            requirement_style=None,
            requirement_in_toc=None,
        )
        free_texts = []
        section_contents = []
        document = Document(
            "Test Document", config, None, free_texts, section_contents
        )
        document.grammar = DocumentGrammar.create_default(document)
        return document
