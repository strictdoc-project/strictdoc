import html

from strictdoc.backend.sdoc.models.section import Section
from strictdoc.helpers.auto_described import auto_described
from strictdoc.helpers.mid import MID
from strictdoc.server.error_object import ErrorObject


@auto_described
class SectionFormObject(ErrorObject):
    def __init__(
        self,
        *,
        section_uid: str,
        section_mid: str,
        section_title: str,
        section_statement: str,
    ):
        assert isinstance(section_uid, str)
        assert isinstance(section_mid, str)
        assert isinstance(section_title, str)
        assert isinstance(section_statement, str)

        super().__init__()
        self.section_uid: str = section_uid
        self.section_mid: str = section_mid
        self.section_title: str = section_title
        self.section_statement: str = html.escape(section_statement)
        self.section_statement_unescaped: str = section_statement

    @staticmethod
    def create_new():
        return SectionFormObject(
            section_uid="",
            section_mid=MID.create().get_string_value(),
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
            section_uid=section.reserved_uid
            if section.reserved_uid is not None
            else "",
            section_mid=section.mid.get_string_value(),
            section_title=section.title,
            section_statement=statement,
        )
