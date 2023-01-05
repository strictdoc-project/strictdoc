from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory
from strictdoc.backend.sdoc.models.reference import ParentReqReference


class DocumentBuilder:
    def __init__(self):
        self.document: Document = self._create_empty_document()
        self.requirements = []

    def add_requirement(self, uid):
        parent = self.document
        # level = None
        statement = "System X shall do Y"
        statement_multiline = None
        # status = None
        tags = None
        # references = []
        title = "Requirement title"
        # body = None
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

    def add_requirement_parent(self, req_id, parent_req_id):
        requirement = next(r for r in self.requirements if r.uid == req_id)
        assert requirement

        reference = ParentReqReference(requirement, parent_req_id)
        requirement.references.append(reference)

    def build(self):
        return self.document

    @staticmethod
    def _create_empty_document() -> Document:
        config = DocumentConfig(
            parent=None,
            version="0.0.1",
            uid="DOC-1",
            classification=None,
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
        return document
