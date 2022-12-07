from typing import Optional

from strictdoc.backend.sdoc.models.section import Section
from strictdoc.server.error_object import ErrorObject


class SectionFormObject(ErrorObject):
    def __init__(
        self,
        *,
        section_mid: Optional[str],
        section_title: Optional[str],
        section_statement: Optional[str],
    ):
        super().__init__()
        self.section_mid: Optional[str] = section_mid
        self._section_title: Optional[str] = section_title
        self._section_statement: Optional[str] = section_statement

    @property
    def section_title(self) -> str:
        if self._section_title is not None:
            assert len(self._section_title) > 0, self._section_title
            return self._section_title
        else:
            return ""

    @property
    def section_statement(self) -> str:
        if self._section_statement is not None:
            assert len(self._section_statement) > 0, self._section_statement
            return self._section_statement
        else:
            return ""

    @staticmethod
    def create_from_section(*, section: Section):
        if len(section.free_texts) == 0:
            return SectionFormObject(
                section_mid=section.node_id,
                section_title=section.title,
                section_statement=None,
            )
        document_free_text = ""
        for free_text in section.free_texts:
            document_free_text += free_text.get_parts_as_text()
        return SectionFormObject(
            section_mid=section.node_id,
            section_title=section.title,
            section_statement=document_free_text,
        )
