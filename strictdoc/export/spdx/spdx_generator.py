import os.path
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from semantic_version import Version
from spdx_tools.spdx3.model import (
    Element,
    Hash,
    HashAlgorithm,
    ProfileIdentifierType,
    Relationship,
    RelationshipType,
    SpdxDocument,
)
from spdx_tools.spdx3.model.positive_integer_range import PositiveIntegerRange
from spdx_tools.spdx3.model.software import (
    File,
    Package,
    Snippet,
    SoftwarePurpose,
)
from spdx_tools.spdx3.model.spdx_document import CreationInfo
from spdx_tools.spdx3.writer.console.relationship_writer import (
    write_relationship,
)
from spdx_tools.spdx3.writer.console.software.file_writer import write_file
from spdx_tools.spdx3.writer.console.software.package_writer import (
    write_package,
)
from spdx_tools.spdx3.writer.console.software.snippet_writer import (
    write_snippet,
)
from spdx_tools.spdx3.writer.console.spdx_document_writer import (
    write_spdx_document,
)

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.reference import (
    FileReference,
    ParentReqReference,
)
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.sha256 import get_sha256

RELATION_ID_HOW_TO = "SPDXRef-Relationship-How-to-form-ID?"


def create_relationship_summary(
    lhs: Element, rhs: Element, relation: str
) -> str:
    return f"{lhs.summary} --|{relation}|--> {rhs.summary}"


def get_spdx_ref(node: Union[Document, Requirement, FileReference]) -> str:
    if isinstance(node, FileReference):
        return re.sub(r"[/\\ ]", "_", node.get_native_path())

    identifier: Optional[str] = None
    if node.mid_permanent:
        identifier = node.reserved_mid
    elif node.reserved_uid is not None:
        identifier = node.reserved_uid
    else:
        identifier = re.sub(r"[ #-/\\]", "_", node.reserved_title)

    if isinstance(node, Document):
        return "SDocDocument-" + identifier
    if isinstance(node, Requirement):
        return "SDocRequirement-" + identifier
    raise NotImplementedError


class SDocToSPDXConverter:
    @staticmethod
    def create_document(project_config: ProjectConfig) -> SpdxDocument:
        spec_version = Version("1.2.3")
        creation_info = CreationInfo(
            spec_version=spec_version,
            created=datetime.today(),
            created_by=[],
            profile=[ProfileIdentifierType.SOFTWARE],
            data_license="TBD License",
            created_using=["SPDXRef-StrictDoc"],
            comment=f"SPDX 3.0 SBOM for {project_config.project_title}'s requirements.",
        )
        spdx_document = SpdxDocument(
            spdx_id="SPDXRef-DOCUMENT",
            name=f"Requirements for {project_config.project_title}",
            element=["DUMMY_ELEMENT(what is this for?)"],
            root_element=["DUMMY_ROOT_ELEMENT(what is this for?)"],
            creation_info=creation_info,
            summary=f"SPDX Document for project {project_config.project_title}",
            description="TBD",
            comment="TBD",
        )
        return spdx_document

    @staticmethod
    def create_package(project_config: ProjectConfig) -> Package:
        return Package(
            spdx_id="SPDXRef-PACKAGE",
            name="Requirements package",
            summary=f"SPDX Package for project {project_config.project_title}",
            description="TBD",
            comment="TBD",
            verified_using=[
                Hash(
                    algorithm=HashAlgorithm.SHA256,
                    hash_value="TBD: What to calculate for a package?",
                )
            ],
            homepage="TBD",
        )

    @staticmethod
    def create_document_to_file(document: Document, document_bytes) -> File:
        return File(
            spdx_id=f"SPDXRef-File-{get_spdx_ref(document)}",
            name=document.meta.document_filename,
            summary=f"SDPX File for document {document.title}",
            description=document.title,
            comment="TBD",
            verified_using=[
                Hash(
                    algorithm=HashAlgorithm.SHA256,
                    hash_value=get_sha256(document_bytes),
                )
            ],
            primary_purpose=SoftwarePurpose.DOCUMENTATION,
        )

    @staticmethod
    def convert_file_to_file(file: FileReference, file_bytes) -> File:
        return File(
            spdx_id=f"SPDXRef-File-{get_spdx_ref(file)}",
            name=file.get_native_path(),
            summary=f"SPDX File for source file {file.get_native_path()}",
            description="TBD",
            comment="TBD",
            verified_using=[
                Hash(
                    algorithm=HashAlgorithm.SHA256,
                    hash_value=get_sha256(file_bytes),
                )
            ],
            primary_purpose=SoftwarePurpose.DOCUMENTATION,
        )

    @staticmethod
    def convert_requirement_to_snippet(
        requirement: Requirement, document_bytes: bytes
    ) -> Snippet:
        snippet_sha256 = get_sha256(
            document_bytes[requirement.ng_byte_start : requirement.ng_byte_end]
        )
        return Snippet(
            spdx_id=f"SPDXRef-Snippet-{get_spdx_ref(requirement)}",
            primary_purpose=SoftwarePurpose.DOCUMENTATION,
            name=f"Requirement: {requirement.reserved_title}",
            summary=f"SPDX Snippet for requirement {requirement.reserved_uid}",
            description="TBD",
            comment="TBD",
            verified_using=[
                Hash(
                    algorithm=HashAlgorithm.SHA256,
                    hash_value=snippet_sha256,
                )
            ],
            byte_range=PositiveIntegerRange(
                requirement.ng_byte_start, requirement.ng_byte_end
            ),
            line_range=PositiveIntegerRange(
                requirement.ng_line_start, requirement.ng_line_end
            ),
        )


@dataclass
class SPDXSDocContainer:
    files: List[File] = field(default_factory=list)
    snippets: List[Snippet] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)


class SPDXGenerator:
    @staticmethod
    def export_tree(
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        output_spdx_root,
    ):
        Path(output_spdx_root).mkdir(parents=True, exist_ok=True)

        sdoc_spdx_converter: SDocToSPDXConverter = SDocToSPDXConverter()
        spdx_container: SPDXSDocContainer = SPDXSDocContainer()

        """
        SPDX Document and SPDX Package
        """
        spdx_document = sdoc_spdx_converter.create_document(project_config)
        spdx_package = sdoc_spdx_converter.create_package(project_config)
        spdx_container.relationships.append(
            Relationship(
                spdx_id=RELATION_ID_HOW_TO,
                from_element=spdx_document.spdx_id,
                relationship_type=RelationshipType.CONTAINS,
                to=[spdx_package.spdx_id],
                name="TBD",
                summary=create_relationship_summary(
                    spdx_document,
                    spdx_package,
                    "CONTAINS",
                ),
                description="TBD",
                comment="TBD",
            )
        )

        lookup_uid_to_requirement_snippet: Dict[str, Snippet] = {}

        for document_ in traceability_index.document_tree.document_list:
            with open(document_.meta.input_doc_full_path, "rb") as file_:
                document_bytes = file_.read()

            """
            Create SPDX File from SDoc Document.
            """
            spdx_file = sdoc_spdx_converter.create_document_to_file(
                document_, document_bytes
            )
            spdx_container.files.append(spdx_file)
            spdx_container.relationships.append(
                Relationship(
                    spdx_id=RELATION_ID_HOW_TO,
                    from_element=spdx_package.spdx_id,
                    relationship_type=RelationshipType.CONTAINS,
                    to=[spdx_file.spdx_id],
                    summary=create_relationship_summary(
                        spdx_package,
                        spdx_file,
                        "CONTAINS",
                    ),
                )
            )

            document_iterator: DocumentCachingIterator = (
                traceability_index.get_document_iterator(document_)
            )

            for node in document_iterator.all_content():
                if node.is_requirement:
                    if node.reserved_uid is None:
                        continue

                    """
                    Create SPDX Snippet from SDoc Requirement.
                    """
                    spdx_snippet: Snippet = (
                        sdoc_spdx_converter.convert_requirement_to_snippet(
                            node, document_bytes
                        )
                    )
                    lookup_uid_to_requirement_snippet[
                        node.reserved_uid
                    ] = spdx_snippet
                    spdx_container.snippets.append(spdx_snippet)
                    spdx_container.relationships.append(
                        Relationship(
                            spdx_id=RELATION_ID_HOW_TO,
                            from_element=spdx_file.spdx_id,
                            relationship_type=RelationshipType.CONTAINS,
                            to=[spdx_snippet.spdx_id],
                            name="TBD",
                            summary=create_relationship_summary(
                                spdx_file,
                                spdx_snippet,
                                "CONTAINS",
                            ),
                            description="TBD",
                            comment="TBD",
                        )
                    )

                    file_relations = (
                        traceability_index.get_requirement_file_links(node)
                    )
                    file_relation_: FileReference
                    for file_relation_, _ in file_relations:
                        path_to_file = file_relation_.get_native_path()
                        with open(path_to_file, "rb") as file_:
                            file_bytes = file_.read()

                        spdx_file = sdoc_spdx_converter.convert_file_to_file(
                            file_relation_, file_bytes
                        )
                        spdx_container.files.append(spdx_file)
                        spdx_container.relationships.append(
                            Relationship(
                                spdx_id=RELATION_ID_HOW_TO,
                                from_element=spdx_snippet.spdx_id,
                                relationship_type=RelationshipType.REQUIREMENT_FOR,
                                to=[spdx_file.spdx_id],
                                name="TBD",
                                summary=create_relationship_summary(
                                    spdx_snippet,
                                    spdx_file,
                                    "REQUIREMENT_FOR",
                                ),
                                description="TBD",
                                comment="TBD",
                            )
                        )

        """
        Now iterate over requirement nodes again
        """
        for document_ in traceability_index.document_tree.document_list:
            document_iterator: DocumentCachingIterator = (
                traceability_index.get_document_iterator(document_)
            )
            for node in document_iterator.all_content():
                if node.is_requirement:
                    if node.reserved_uid is None:
                        continue

                requirement: Requirement = assert_cast(node, Requirement)
                assert requirement.reserved_uid is not None
                requirement_snippet: Snippet = (
                    lookup_uid_to_requirement_snippet[requirement.reserved_uid]
                )

                for reference_ in requirement.references:
                    if isinstance(reference_, ParentReqReference):
                        parent_requirement_snippet: Snippet = (
                            lookup_uid_to_requirement_snippet[
                                reference_.ref_uid
                            ]
                        )

                        spdx_container.relationships.append(
                            Relationship(
                                spdx_id=RELATION_ID_HOW_TO,
                                from_element=requirement_snippet.spdx_id,
                                relationship_type=RelationshipType.REQUIREMENT_FOR,
                                to=[parent_requirement_snippet.spdx_id],
                                name="TBD",
                                summary=create_relationship_summary(
                                    requirement_snippet,
                                    parent_requirement_snippet,
                                    "REQUIREMENT_FOR",
                                ),
                                description="TBD",
                                comment="TBD",
                            )
                        )

        """Output SPDX to a file"""

        output_path = os.path.join(output_spdx_root, "output.spdx")
        with open(output_path, "w", encoding="utf8") as file:
            write_spdx_document(spdx_document, text_output=file)
            file.write("\n")

            write_package(spdx_package, text_output=file, heading=True)
            file.write("\n")

            for file_ in spdx_container.files:
                write_file(file_, text_output=file)
                file.write("\n")

            for snippet_ in spdx_container.snippets:
                write_snippet(snippet_, text_output=file)
                file.write("\n")

            for relationship_ in spdx_container.relationships:
                write_relationship(relationship_, text_output=file)
                file.write("\n")
