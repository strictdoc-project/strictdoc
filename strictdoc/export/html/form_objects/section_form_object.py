import html
import uuid
from typing import Optional

from strictdoc.backend.sdoc.models.section import Section
from strictdoc.server.error_object import ErrorObject


class SectionFormObject(ErrorObject):
    def __init__(
        self,
        *,
        section_mid: Optional[str],
        section_title: str,
        section_statement: str,
    ):
        assert isinstance(section_mid, str)
        assert isinstance(section_title, str)
        assert isinstance(section_statement, str)
        super().__init__()
        self.section_mid: str = section_mid
        self.section_title: str = section_title
        self.section_statement: str = html.escape(section_statement)

    @staticmethod
    def create_new():
        return SectionFormObject(
            section_mid=uuid.uuid4().hex,
            section_title="",
            section_statement="",
        )

    @staticmethod
    def create_from_section(*, section: Section):
        statement = (
            section.free_texts[0].get_parts_as_text()
            if len(section.free_texts) > 0
            else ""
        )
        return SectionFormObject(
            section_mid=section.node_id,
            section_title=section.title,
            section_statement=statement,
        )
