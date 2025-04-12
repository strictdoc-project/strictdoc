"""
@relation(SDOC-SRS-109, scope=file)
"""

from typing import List, Optional, Union

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.model import (
    SDocDocumentFromFileIF,
    SDocDocumentIF,
    SDocElementIF,
    SDocNodeIF,
    SDocSectionIF,
)
from strictdoc.helpers.auto_described import auto_described


@auto_described
class DocumentFromFile(SDocDocumentFromFileIF):
    def __init__(
        self,
        parent: Union[SDocDocumentIF, SDocSectionIF],
        file: str,
    ) -> None:
        self.parent: Union[SDocDocumentIF, SDocSectionIF] = parent
        self.file: str = file

        self.ng_has_requirements: bool = False
        self.ng_document_reference: Optional[DocumentReference] = None
        self.ng_included_document_reference: Optional[DocumentReference] = None
        self.ng_resolved_custom_level: Optional[str] = None
        self.ng_whitelisted: bool = True
        self.resolved_full_path_to_document_file: Optional[str] = None
        self.resolved_document: Optional[SDocDocumentIF] = None

    def has_any_requirements(self) -> bool:
        task_list: List[SDocElementIF] = list(self.section_contents)
        while len(task_list) > 0:
            element = task_list.pop(0)
            if isinstance(element, SDocNodeIF):
                if element.is_normative_node():
                    return True
                continue

            if isinstance(element, SDocDocumentFromFileIF):
                if element.has_any_requirements():
                    return True

            task_list.extend(element.section_contents)
        return False

    @property
    def section_contents(self) -> List[SDocDocumentIF]:
        assert self.resolved_document is not None
        return [self.resolved_document]

    def configure_with_resolved_document(
        self, resolved_document: SDocDocument
    ) -> None:
        assert self.ng_included_document_reference is None
        assert self.ng_document_reference is not None

        assert resolved_document is not None
        self.resolved_document = resolved_document

        including_document_or_section = self.parent

        if isinstance(including_document_or_section, SDocDocumentIF):
            including_document = including_document_or_section
        elif isinstance(including_document_or_section, SDocSectionIF):
            including_document_: Optional[SDocDocumentIF] = (
                including_document_or_section.get_document()
            )
            assert isinstance(including_document_, SDocDocumentIF)
            including_document = including_document_
        else:
            raise AssertionError(including_document_or_section)

        resolved_document.ng_including_document_from_file = self

        assert resolved_document.ng_including_document_reference is not None
        resolved_document.ng_including_document_reference.set_document(
            including_document
        )

        including_document.included_documents.append(resolved_document)
