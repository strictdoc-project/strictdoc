import os
import tempfile
from typing import Optional

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.document_grammar import DocumentGrammar
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.object_factory import SDocObjectFactory
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    ParentReqReference,
)
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.core.document_meta import DocumentMeta
from strictdoc.core.project_config import ProjectConfig
from strictdoc.helpers.paths import SDocRelativePath


class DocumentBuilder:
    def __init__(self, uid="DOC-1"):
        self.project_config: ProjectConfig = ProjectConfig.default_config()
        self.document: SDocDocument = self._create_empty_document(
            self.project_config, uid
        )
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
            node_type="REQUIREMENT",
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
        requirement: SDocNode = next(
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
        requirement.relations.append(reference)

    def build(self):
        return self.document

    @staticmethod
    def _create_empty_document(
        project_config: ProjectConfig, uid: str
    ) -> SDocDocument:
        config = DocumentConfig(
            parent=None,
            version="0.0.1",
            date=None,
            uid=uid,
            classification=None,
            requirement_prefix=None,
            root=None,
            enable_mid=None,
            markup=None,
            auto_levels=None,
            layout=None,
            requirement_style=None,
            requirement_in_toc=None,
            default_view=None,
            custom_metadata=None,
        )
        section_contents = []
        document = SDocDocument(
            mid=None,
            title="Test Document",
            config=config,
            view=None,
            grammar=None,
            section_contents=section_contents,
        )
        document.grammar = DocumentGrammar.create_default(document)

        # FIXME: Rework how these files are created in a better way.
        tmpdir = tempfile.gettempdir()
        temp_file_path = os.path.join(tmpdir, "input.sdoc")

        document.meta = DocumentMeta(
            level=0,
            file_tree_mount_folder="",
            document_filename="input.sdoc",
            document_filename_base="input",
            input_doc_full_path=temp_file_path,
            input_doc_rel_path=SDocRelativePath("input.sdoc"),
            input_doc_dir_rel_path=SDocRelativePath(""),
            input_doc_assets_dir_rel_path=SDocRelativePath("_assets"),
            output_document_dir_full_path="FOO",
            output_document_dir_rel_path=SDocRelativePath("BAR"),
        )
        writer = SDWriter(project_config=project_config)
        writer.write_to_file(document)

        return document
