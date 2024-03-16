from typing import List, Optional

from strictdoc.backend.sdoc.document_reference import DocumentReference
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.helpers.auto_described import auto_described


@auto_described
class FragmentFromFile:
    def __init__(
        self,
        parent,
        file,
    ):
        self.parent = parent
        self.file = file

        self.ng_level = None
        self.ng_has_requirements = False
        self.ng_document_reference: Optional[DocumentReference] = None
        self.ng_included_document_reference: Optional[DocumentReference] = None
        self.resolved_full_path_to_document_file = None
        self.resolved_document: Optional = None
        self.top_section: Optional = None

    @property
    def document(self):
        raise NotImplementedError

    def has_any_requirements(self) -> bool:
        task_list = list(self.section_contents)
        while len(task_list) > 0:
            section_or_requirement = task_list.pop(0)
            if isinstance(section_or_requirement, FragmentFromFile):
                if section_or_requirement.has_any_requirements():
                    return True
            if section_or_requirement.is_requirement:
                return True
            assert section_or_requirement.is_section, section_or_requirement
            task_list.extend(section_or_requirement.section_contents)
        return False

    @property
    def section_contents(self) -> List:
        return [self.top_section]

    def configure_with_resolved_document(self, document):
        assert document is not None
        self.resolved_document = document

        top_section = SDocSection(
            self,
            mid=None,
            uid=None,
            custom_level=None,
            title=self.resolved_document.title,
            requirement_prefix=self.resolved_document.get_requirement_prefix(),
            free_texts=self.resolved_document.free_texts,
            section_contents=self.resolved_document.section_contents,
            root_section=True,
        )
        top_section.ng_level = self.ng_level
        assert self.ng_included_document_reference is None
        assert self.ng_document_reference is not None
        top_section.ng_document_reference = self.ng_document_reference
        top_section.ng_including_document_reference = self.ng_document_reference
        self.top_section = top_section
