# mypy: disable-error-code="no-untyped-def,type-arg"
from typing import List, Optional

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.helpers.auto_described import auto_described


@auto_described
class DocumentFromFile:
    def __init__(
        self,
        parent,
        file,
    ):
        self.parent = parent
        self.file = file

        self.ng_has_requirements = False
        self.ng_document_reference: Optional[DocumentReference] = None
        self.ng_included_document_reference: Optional[DocumentReference] = None
        self.ng_resolved_custom_level = None
        self.ng_whitelisted = True
        self.resolved_full_path_to_document_file = None
        self.resolved_document: Optional = None  # type: ignore[valid-type]

    @property
    def document(self):
        raise NotImplementedError

    def has_any_requirements(self) -> bool:
        task_list = list(self.section_contents)
        while len(task_list) > 0:
            section_or_requirement = task_list.pop(0)
            if isinstance(section_or_requirement, DocumentFromFile):
                if section_or_requirement.has_any_requirements():
                    return True
            if section_or_requirement.is_requirement:
                return True
            assert section_or_requirement.is_section, section_or_requirement
            task_list.extend(section_or_requirement.section_contents)
        return False

    @property
    def section_contents(self) -> List:
        return [self.resolved_document]

    def configure_with_resolved_document(self, resolved_document):
        assert self.ng_included_document_reference is None
        assert self.ng_document_reference is not None

        assert resolved_document is not None
        self.resolved_document = resolved_document

        including_document_or_section = self.parent

        if including_document_or_section.__class__.__name__ == "SDocDocument":
            including_document = including_document_or_section
        elif including_document_or_section.__class__.__name__ == "SDocSection":
            including_document = including_document_or_section.document
        else:
            raise AssertionError(including_document_or_section)

        resolved_document.ng_including_document_from_file = self
        resolved_document.ng_including_document_reference.set_document(
            including_document
        )

        including_document.included_documents.append(resolved_document)
