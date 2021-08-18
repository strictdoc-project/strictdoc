from strictdoc.backend.dsl.models.document import Document
from strictdoc.backend.dsl.models.document_config import DocumentConfig
from strictdoc.backend.dsl.models.reference import Reference
from strictdoc.backend.dsl.models.requirement import Requirement


class DocumentBuilder:
    def __init__(self):
        self.document = self._create_empty_document()
        self.requirements = []

    def add_requirement(self, uid):
        parent = self.document
        statement = "System X shall do Y"
        statement_multiline = None
        status = None
        tags = []
        references = []
        title = "Requirement title"
        body = None
        rationale = None
        rationale_multiline = None
        comments = []
        special_fields = []

        requirement = Requirement(
            parent,
            statement,
            statement_multiline,
            uid,
            status,
            tags,
            references,
            title,
            body,
            rationale,
            rationale_multiline,
            comments,
            special_fields,
        )
        requirement.ng_level = 1
        self.requirements.append(requirement)
        self.document.section_contents.append(requirement)

        return requirement

    def add_requirement_parent(self, req_id, parent_req_id):
        requirement = next(r for r in self.requirements if r.uid == req_id)
        assert requirement

        reference = Reference(requirement, "Parent", parent_req_id)
        requirement.references.append(reference)

    def build(self):
        return self.document

    @staticmethod
    def _create_empty_document() -> Document:
        config = DocumentConfig(None, "0.0.1", "DOC-1", [], None)
        free_texts = []
        section_contents = []
        document = Document(
            None, "Test Document", config, free_texts, section_contents
        )
        return document
