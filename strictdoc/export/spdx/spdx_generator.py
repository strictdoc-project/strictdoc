# mypy: disable-error-code="arg-type,no-redef,no-untyped-call,no-untyped-def,union-attr"
import os.path
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union

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
from spdx_tools.spdx3.payload import Payload
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
from spdx_tools.spdx3.writer.json_ld.json_ld_writer import write_payload

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.reference import (
    FileReference,
    ParentReqReference,
)
from strictdoc.backend.sdoc.writer import SDWriter
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.spdx.spdx_sdoc_container import SPDXSDocContainer
from strictdoc.export.spdx.spdx_to_sdoc_converter import SPDXToSDocConverter
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.sha256 import get_sha256

RELATION_ID_HOW_TO = "SPDXRef-Relationship-How-to-form-ID?"


def create_relationship_summary(
    lhs: Element, rhs: Element, relation: str
) -> str:
    return f"{lhs.summary} --|{relation}|--> {rhs.summary}"


def get_spdx_ref(node: Union[SDocDocument, SDocNode, FileReference]) -> str:
    if isinstance(node, FileReference):
        return re.sub(r"[/\\ ]", "_", node.get_native_path())

    identifier: Optional[str] = None
    if node.mid_permanent:
        identifier = node.reserved_mid
    elif node.reserved_uid is not None:
        identifier = node.reserved_uid
    else:
        identifier = re.sub(r"[ #-/\\]", "_", node.reserved_title)

    if isinstance(node, SDocDocument):
        return "SDocDocument-" + identifier
    if isinstance(node, SDocNode):
        return "SDocRequirement-" + identifier
    raise NotImplementedError


class SDocToSPDXConverter:
    @staticmethod
    def create_document(project_config: ProjectConfig) -> SpdxDocument:
        spec_version = Version("3.0.0")
        creation_info = CreationInfo(
            spec_version=spec_version,
            created=datetime.today(),
            created_by=[],
            profile=[ProfileIdentifierType.SOFTWARE],
            data_license="CC0 1.0",
            created_using=["SPDXRef-StrictDoc"],
            comment=f"SPDX 3.0 SBOM for {project_config.project_title}'s requirements.",
        )
        spdx_document = SpdxDocument(
            spdx_id="SPDXRef-DOCUMENT",
            name=f"Requirements for {project_config.project_title}",
            element=[],
            root_element=[],
            creation_info=creation_info,
            summary=f"SPDX Document for project {project_config.project_title}",
            description=None,
            comment=None,
        )
        return spdx_document

    @staticmethod
    def create_package(project_config: ProjectConfig) -> Package:
        return Package(
            spdx_id="SPDXRef-PACKAGE",
            name="Requirements package",
            summary=f"SPDX Package for project {project_config.project_title}",
            description=None,
            comment=None,
            verified_using=[
                Hash(
                    algorithm=HashAlgorithm.SHA256,
                    hash_value="TBD: What to calculate for a package?",
                )
            ],
            primary_purpose=SoftwarePurpose.BOM,
            homepage=None,
        )

    @staticmethod
    def create_document_to_file(document: SDocDocument, document_bytes) -> File:
        return File(
            spdx_id=f"SPDXRef-File-{get_spdx_ref(document)}",
            name=document.meta.document_filename,
            summary=f"SDPX File for document {document.title}",
            description=None,
            comment=None,
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
            description=None,
            comment=None,
            verified_using=[
                Hash(
                    algorithm=HashAlgorithm.SHA256,
                    hash_value=get_sha256(file_bytes),
                )
            ],
            primary_purpose=SoftwarePurpose.SOURCE,
        )

    @staticmethod
    def convert_requirement_to_snippet(
        requirement: SDocNode, document_bytes: bytes, spdx_file: File
    ) -> Snippet:
        snippet_sha256 = get_sha256(
            document_bytes[requirement.ng_byte_start : requirement.ng_byte_end]
        )
        assert requirement.reserved_uid is not None
        return Snippet(
            spdx_id=requirement.reserved_uid,
            primary_purpose=SoftwarePurpose.DOCUMENTATION,
            name=f"Requirement '{requirement.reserved_title}'",
            summary=f"SPDX Snippet for requirement {requirement.reserved_uid}",
            description=requirement.reserved_statement.partition("\n")[0],
            comment=(
                "This snippet has been generated from a requirement "
                f"defined in a StrictDoc file: {spdx_file.name}."
            ),
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
        spdx_container.document = spdx_document

        spdx_package = sdoc_spdx_converter.create_package(project_config)
        spdx_container.package = spdx_package

        spdx_document.root_element = [spdx_package.spdx_id]

        spdx_container.relationships.append(
            Relationship(
                spdx_id=RELATION_ID_HOW_TO,
                from_element=spdx_document.spdx_id,
                relationship_type=RelationshipType.CONTAINS,
                to=[spdx_package.spdx_id],
                name=None,
                summary=create_relationship_summary(
                    spdx_document,
                    spdx_package,
                    "CONTAINS",
                ),
                description=None,
                comment=None,
            )
        )

        lookup_uid_to_requirement_snippet: Dict[str, Snippet] = {}
        lookup_file_name_to_spdx_file: Dict[str, File] = {}

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
            spdx_container.map_spdx_ref_to_objects[spdx_file.spdx_id] = (
                spdx_file
            )

            document_iterator: DocumentCachingIterator = (
                traceability_index.get_document_iterator(document_)
            )

            for node in document_iterator.all_content():
                if node.is_requirement:
                    if node.reserved_uid is None:
                        continue

                    assert (
                        node.reserved_title is not None
                    ), "The current implementation only supports requirements with a title."

                    """
                    Create SPDX Snippet from SDoc Requirement.
                    """
                    spdx_snippet: Snippet = (
                        sdoc_spdx_converter.convert_requirement_to_snippet(
                            node, document_bytes, spdx_file
                        )
                    )
                    lookup_uid_to_requirement_snippet[node.reserved_uid] = (
                        spdx_snippet
                    )
                    spdx_container.snippets.append(spdx_snippet)
                    spdx_container.map_spdx_ref_to_objects[
                        spdx_snippet.spdx_id
                    ] = spdx_snippet
                    spdx_container.map_spdx_snippets_to_files[
                        spdx_snippet.spdx_id
                    ] = spdx_file.spdx_id

                    spdx_container.relationships.append(
                        Relationship(
                            spdx_id=RELATION_ID_HOW_TO,
                            from_element=spdx_file.spdx_id,
                            relationship_type=RelationshipType.CONTAINS,
                            to=[spdx_snippet.spdx_id],
                            name=None,
                            summary=create_relationship_summary(
                                spdx_file,
                                spdx_snippet,
                                "CONTAINS",
                            ),
                            description=None,
                            comment=None,
                        )
                    )

                    file_relations = (
                        traceability_index.get_requirement_file_links(node)
                    )
                    file_relation_: FileReference
                    for file_relation_, _ in file_relations:
                        path_to_file = file_relation_.get_native_path()
                        if path_to_file in lookup_file_name_to_spdx_file:
                            continue

                        with open(path_to_file, "rb") as file_:
                            file_bytes = file_.read()

                        source_spdx_file = (
                            sdoc_spdx_converter.convert_file_to_file(
                                file_relation_, file_bytes
                            )
                        )
                        lookup_file_name_to_spdx_file[path_to_file] = (
                            source_spdx_file
                        )
                        spdx_container.map_spdx_ref_to_objects[
                            source_spdx_file.spdx_id
                        ] = source_spdx_file

                        spdx_container.files.append(source_spdx_file)
                        spdx_container.relationships.append(
                            Relationship(
                                spdx_id=RELATION_ID_HOW_TO,
                                from_element=spdx_snippet.spdx_id,
                                relationship_type=RelationshipType.REQUIREMENT_FOR,
                                to=[source_spdx_file.spdx_id],
                                name=None,
                                summary=create_relationship_summary(
                                    spdx_snippet,
                                    source_spdx_file,
                                    "REQUIREMENT_FOR",
                                ),
                                description=None,
                                comment=None,
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

                requirement: SDocNode = assert_cast(node, SDocNode)
                assert requirement.reserved_uid is not None
                requirement_snippet: Snippet = (
                    lookup_uid_to_requirement_snippet[requirement.reserved_uid]
                )

                for reference_ in requirement.relations:
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
                                name=None,
                                summary=create_relationship_summary(
                                    requirement_snippet,
                                    parent_requirement_snippet,
                                    "REQUIREMENT_FOR",
                                ),
                                description=None,
                                comment=None,
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

        if True:
            payload: Payload = Payload()

            payload.add_element(spdx_document)
            payload.add_element(spdx_package)
            for spdx_file_ in spdx_container.files:
                payload.add_element(spdx_file_)
            for spdx_snippet_ in spdx_container.snippets:
                payload.add_element(spdx_snippet_)

            path_to_output_spdx_json = os.path.join(
                output_spdx_root, "output.spdx"
            )

            write_payload(payload, path_to_output_spdx_json)

        if True:
            sdoc_document = SPDXToSDocConverter.convert(spdx_container)

            sdoc_output = SDWriter(project_config).write(sdoc_document)

            sdoc_output_path = os.path.join(
                output_spdx_root, "output.spdx.sdoc"
            )
            with open(sdoc_output_path, "w", encoding="utf8") as file_:
                file_.write(sdoc_output)
