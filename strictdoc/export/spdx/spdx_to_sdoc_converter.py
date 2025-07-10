"""
Experimental code to generate SPDX.

This code is excluded from code coverage calculation because the feature is
highly experimental and most of this code will be removed.
"""

# mypy: disable-error-code="arg-type,no-untyped-call,no-untyped-def,union-attr"
from typing import List, Union

from spdx_tools.spdx3.model import RelationshipType, SpdxDocument
from spdx_tools.spdx3.model.software import File, Package, Snippet

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import (
    DocumentGrammar,
)
from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElement,
    GrammarElementFieldString,
    GrammarElementRelationChild,
    GrammarElementRelationFile,
    GrammarElementRelationParent,
)
from strictdoc.backend.sdoc.models.node import (
    SDocNode,
    SDocNodeField,
)
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    FileEntry,
    FileReference,
    ParentReqReference,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.export.spdx.spdx_sdoc_container import SPDXSDocContainer


class SPDXToSDocConverter:
    @staticmethod
    def convert(spdx_container: SPDXSDocContainer) -> SDocDocument:
        map_spdxref_to_sdoc = {}

        document = SDocDocument(
            mid=None,
            title=spdx_container.document.name,
            config=None,
            view=None,
            grammar=None,
            section_contents=[],
        )

        document.config.requirement_style = "Inline"

        document.grammar = SPDXToSDocConverter.create_grammar_for_spdx()
        document.grammar.parent = document

        #
        # Document.
        #
        document_requirement: SDocNode = SPDXToSDocConverter._convert_document(
            spdx_container.document,
            sdoc_document=document,
            sdoc_parent=document,
        )
        document.section_contents.append(document_requirement)

        #
        # Package.
        #
        package_requirement = SPDXToSDocConverter._convert_package(
            spdx_container.package,
            sdoc_document=document,
            sdoc_parent=document,
        )
        document.section_contents.append(package_requirement)

        #
        # Files.
        #

        file_section = SDocSection(
            parent=document,
            mid=None,
            uid=None,
            custom_level=None,
            title="Files",
            requirement_prefix=None,
            section_contents=[],
        )
        document.section_contents.append(file_section)

        for file_ in spdx_container.files:
            requirement = SPDXToSDocConverter._convert_file(
                file_, document, file_section
            )

            file_section.section_contents.append(requirement)
            map_spdxref_to_sdoc[file_.spdx_id] = requirement

        #
        # Snippets.
        #

        snippets_section = SDocSection(
            parent=document,
            mid=None,
            uid=None,
            custom_level=None,
            title="Snippets",
            requirement_prefix=None,
            section_contents=[],
        )
        document.section_contents.append(snippets_section)

        for snippet_ in spdx_container.snippets:
            requirement = SPDXToSDocConverter._convert_snippet(
                snippet_, document, file_section, spdx_container
            )

            snippets_section.section_contents.append(requirement)
            map_spdxref_to_sdoc[snippet_.spdx_id] = requirement

        for relationship_ in spdx_container.relationships:
            if (
                relationship_.from_element in map_spdxref_to_sdoc
                and relationship_.to[0] in map_spdxref_to_sdoc
            ):
                if relationship_.relationship_type == RelationshipType.CONTAINS:
                    from_element = spdx_container.map_spdx_ref_to_objects[
                        relationship_.from_element
                    ]
                    to_element = spdx_container.map_spdx_ref_to_objects[
                        relationship_.to[0]
                    ]

                    from_element_sdoc = map_spdxref_to_sdoc[
                        from_element.spdx_id
                    ]
                    to_element_sdoc = map_spdxref_to_sdoc[to_element.spdx_id]

                    assert to_element_sdoc.reserved_uid is not None, (
                        to_element_sdoc
                    )

                    from_element_sdoc.relations.append(
                        ChildReqReference(
                            parent=from_element_sdoc,
                            ref_uid=to_element_sdoc.reserved_uid,
                            role="CONTAINS",
                        )
                    )
                if (
                    relationship_.relationship_type
                    == RelationshipType.REQUIREMENT_FOR
                ):
                    from_element = spdx_container.map_spdx_ref_to_objects[
                        relationship_.from_element
                    ]
                    to_element = spdx_container.map_spdx_ref_to_objects[
                        relationship_.to[0]
                    ]

                    from_element_sdoc = map_spdxref_to_sdoc[
                        from_element.spdx_id
                    ]
                    to_element_sdoc = map_spdxref_to_sdoc[to_element.spdx_id]

                    assert to_element_sdoc.reserved_uid is not None, (
                        to_element_sdoc
                    )

                    from_element_sdoc.relations.append(
                        ParentReqReference(
                            parent=from_element_sdoc,
                            ref_uid=to_element_sdoc.reserved_uid,
                            role="REQUIREMENT_FOR",
                        )
                    )
        return document

    @staticmethod
    def _convert_document(document: SpdxDocument, sdoc_document, sdoc_parent):
        requirement = SDocNode(
            parent=sdoc_parent,
            node_type="SPDX_PACKAGE",
            fields=[],
            relations=[],
        )
        requirement.ng_document_reference = DocumentReference()
        requirement.ng_document_reference.set_document(sdoc_document)

        requirement.set_field_value(
            field_name="UID", form_field_index=0, value=document.spdx_id
        )
        requirement.set_field_value(
            field_name="SPDXID", form_field_index=0, value=document.spdx_id
        )
        requirement.set_field_value(
            field_name="TITLE", form_field_index=0, value=document.name
        )
        requirement.set_field_value(
            field_name="STATEMENT", form_field_index=0, value=document.summary
        )
        return requirement

    @staticmethod
    def _convert_package(
        package: Package,
        sdoc_document: SDocDocument,
        sdoc_parent: Union[SDocSection, SDocDocument],
    ) -> SDocNode:
        requirement = SDocNode(
            parent=sdoc_parent,
            node_type="SPDX_PACKAGE",
            fields=[],
            relations=[],
        )
        requirement.ng_document_reference = DocumentReference()
        requirement.ng_document_reference.set_document(sdoc_document)

        requirement.set_field_value(
            field_name="UID", form_field_index=0, value=package.spdx_id
        )
        requirement.set_field_value(
            field_name="SPDXID", form_field_index=0, value=package.spdx_id
        )
        requirement.set_field_value(
            field_name="PRIMARY_PURPOSE",
            form_field_index=0,
            value=package.primary_purpose.name,
        )
        requirement.set_field_value(
            field_name="TITLE", form_field_index=0, value=package.name
        )
        requirement.set_field_value(
            field_name="STATEMENT", form_field_index=0, value=package.summary
        )
        if package.summary is not None:
            requirement.set_field_value(
                field_name="SUMMARY", form_field_index=0, value=package.summary
            )
        return requirement

    @staticmethod
    def _convert_file(
        file: File,
        sdoc_document: SDocDocument,
        sdoc_parent: Union[SDocSection, SDocDocument],
    ) -> SDocNode:
        fields: List[SDocNodeField] = []
        requirement = SDocNode(
            parent=sdoc_parent,
            node_type="SPDX_FILE",
            fields=fields,
            relations=[],
        )
        requirement.ng_document_reference = DocumentReference()
        requirement.ng_document_reference.set_document(sdoc_document)

        requirement.set_field_value(
            field_name="UID", form_field_index=0, value=file.spdx_id
        )
        requirement.set_field_value(
            field_name="SPDXID", form_field_index=0, value=file.spdx_id
        )
        requirement.set_field_value(
            field_name="PRIMARY_PURPOSE",
            form_field_index=0,
            value=file.primary_purpose.name,
        )
        requirement.set_field_value(
            field_name="SUMMARY", form_field_index=0, value=file.summary
        )
        requirement.set_field_value(
            field_name="TITLE", form_field_index=0, value=file.name
        )

        requirement.relations = [
            FileReference(
                parent=requirement,
                g_file_entry=FileEntry(
                    parent=None,
                    g_file_format=None,
                    g_file_path=file.name,
                    g_line_range=None,
                    function=None,
                    clazz=None,
                ),
            )
        ]

        return requirement

    @staticmethod
    def _convert_snippet(
        snippet: Snippet,
        sdoc_document: SDocDocument,
        sdoc_parent: Union[SDocSection, SDocDocument],
        spdx_container: SPDXSDocContainer,
    ) -> SDocNode:
        fields: List[SDocNodeField] = []
        requirement = SDocNode(
            parent=sdoc_parent,
            node_type="SPDX_SNIPPET",
            fields=fields,
            relations=[],
        )
        requirement.ng_document_reference = DocumentReference()
        requirement.ng_document_reference.set_document(sdoc_document)

        requirement.set_field_value(
            field_name="UID", form_field_index=0, value=snippet.spdx_id
        )
        requirement.set_field_value(
            field_name="SPDXID", form_field_index=0, value=snippet.spdx_id
        )
        requirement.set_field_value(
            field_name="PRIMARY_PURPOSE",
            form_field_index=0,
            value=snippet.primary_purpose.name,
        )
        requirement.set_field_value(
            field_name="SUMMARY", form_field_index=0, value=snippet.summary
        )
        requirement.set_field_value(
            field_name="TITLE", form_field_index=0, value=snippet.name
        )

        spdx_file_id = spdx_container.map_spdx_snippets_to_files[
            snippet.spdx_id
        ]
        spdx_file = spdx_container.map_spdx_ref_to_objects[spdx_file_id]

        requirement.relations = [
            FileReference(
                parent=requirement,
                g_file_entry=FileEntry(
                    parent=None,
                    g_file_format=None,
                    g_file_path=spdx_file.name,
                    g_line_range=f"{snippet.line_range.begin}, {snippet.line_range.end - 1}",
                    function=None,
                    clazz=None,
                ),
            )
        ]

        return requirement

    @staticmethod
    def create_grammar_for_spdx():
        elements = []

        #
        # SPDX Document
        #
        fields = [
            GrammarElementFieldString(
                parent=None,
                title="UID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="SPDXID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="TITLE",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="STATEMENT",
                human_title=None,
                required="False",
            ),
        ]

        document_element = GrammarElement(
            parent=None,
            tag="SPDX_DOCUMENT",
            property_is_composite="",
            property_prefix="",
            property_view_style="",
            fields=fields,
            relations=[
                GrammarElementRelationChild(
                    parent=None,
                    relation_type="Child",
                    relation_role="CONTAINS",
                ),
            ],
        )
        elements.append(document_element)

        #
        # SPDX Package
        #
        fields = [
            GrammarElementFieldString(
                parent=None,
                title="UID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="SPDXID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="PRIMARY_PURPOSE",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="TITLE",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="STATEMENT",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="SUMMARY",
                human_title=None,
                required="False",
            ),
        ]

        package_element = GrammarElement(
            parent=None,
            tag="SPDX_PACKAGE",
            property_is_composite="",
            property_prefix="",
            property_view_style="",
            fields=fields,
            relations=[
                GrammarElementRelationChild(
                    parent=None,
                    relation_type="Child",
                    relation_role="CONTAINS",
                ),
            ],
        )
        elements.append(package_element)

        #
        # SPDX File.
        #
        fields = [
            GrammarElementFieldString(
                parent=None,
                title="UID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="SPDXID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="PRIMARY_PURPOSE",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="SUMMARY",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="TITLE",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="STATEMENT",
                human_title=None,
                required="False",
            ),
        ]

        file_element = GrammarElement(
            parent=None,
            tag="SPDX_FILE",
            property_is_composite="",
            property_prefix="",
            property_view_style="",
            fields=fields,
            relations=[
                GrammarElementRelationChild(
                    parent=None,
                    relation_type="Child",
                    relation_role="CONTAINS",
                ),
                GrammarElementRelationFile(
                    parent=None,
                    relation_type="File",
                    relation_role=None,
                ),
            ],
        )
        elements.append(file_element)

        #
        # SPDX Snippet
        #
        fields = [
            GrammarElementFieldString(
                parent=None,
                title="UID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="SPDXID",
                human_title=None,
                required="True",
            ),
            GrammarElementFieldString(
                parent=None,
                title="PRIMARY_PURPOSE",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="SUMMARY",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="TITLE",
                human_title=None,
                required="False",
            ),
            GrammarElementFieldString(
                parent=None,
                title="STATEMENT",
                human_title=None,
                required="False",
            ),
        ]

        elements.append(
            GrammarElement(
                parent=None,
                tag="SPDX_SNIPPET",
                property_is_composite="",
                property_prefix="",
                property_view_style="",
                fields=fields,
                relations=[
                    GrammarElementRelationParent(
                        parent=None,
                        relation_type="Parent",
                        relation_role="REQUIREMENT_FOR",
                    ),
                    GrammarElementRelationFile(
                        parent=None,
                        relation_type="File",
                        relation_role=None,
                    ),
                ],
            )
        )

        #
        # Create Grammar.
        #
        grammar = DocumentGrammar(parent=None, elements=elements)
        return grammar
