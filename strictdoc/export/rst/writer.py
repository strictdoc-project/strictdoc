from enum import Enum
from typing import Optional

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.sdoc.models.section import FreeText, Section
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.rst.rst_templates import RSTTemplates


class TAG(Enum):
    SECTION = 1
    REQUIREMENT = 2
    COMPOSITE_REQUIREMENT = 3


class RSTWriter:
    def __init__(self, index: TraceabilityIndex):
        self.index = index

    def write(self, document: Document, single_document):
        document_iterator = DocumentCachingIterator(document)
        output = ""

        if not single_document:
            document_uid: Optional[str] = None
            if document.config.uid is not None:
                document_uid = document.config.uid
            output += self._print_rst_header(
                document.title, 0, reference_uid=document_uid
            )

        for free_text in document.free_texts:
            output += self._print_free_text(free_text)

        for content_node in document_iterator.all_content():
            if isinstance(content_node, Section):
                output += self._print_rst_header(
                    content_node.title,
                    content_node.ng_level,
                    content_node.reserved_uid,
                )
                for free_text in content_node.free_texts:
                    output += self._print_free_text(free_text)

            elif isinstance(content_node, Requirement):
                output += self._print_requirement_fields(content_node)

        if output.endswith("\n\n"):
            output = output[:-1]
        return output.lstrip()

    @staticmethod
    def _print_rst_header_2(string: str, level: int):
        assert isinstance(string, str), string
        assert isinstance(level, int), level
        chars = {
            0: "$",
            1: "=",
            2: "-",
            3: "~",
            4: "^",
            5: '"',
            6: "#",
            7: "'",
        }
        header_char = chars[level]
        output = ""
        output += string
        output += "\n"
        output += header_char.rjust(len(string), header_char)
        return output

    @staticmethod
    def _print_rst_header(
        string: str, level: int, reference_uid: Optional[str]
    ):
        assert isinstance(string, str), string
        assert isinstance(level, int), level
        chars = {
            0: "$",
            1: "=",
            2: "-",
            3: "~",
            4: "^",
            5: '"',
            6: "#",
            7: "'",
        }
        header_char = chars[level]
        output = ""

        # An RST reference looks like this:
        # .. _SDOC-HIGH-VALIDATION:
        if reference_uid is not None:
            assert len(reference_uid) > 0, reference_uid
            output += f".. _{reference_uid}:\n\n"

        output += string
        output += "\n"
        output += header_char.rjust(len(string), header_char)
        output += "\n\n"
        return output

    def _print_requirement_fields(self, section_content: Requirement):
        requirement_template = RSTTemplates.jinja_environment.get_template(
            "requirement.jinja.rst"
        )
        output = requirement_template.render(
            requirement=section_content,
            index=self.index,
            _print_rst_header=self._print_rst_header_2,
        )
        return output

    def _print_free_text(self, free_text):
        assert isinstance(free_text, FreeText)
        if len(free_text.parts) == 0:
            return ""
        output = ""
        for part in free_text.parts:
            if isinstance(part, str):
                output += part
            elif isinstance(part, InlineLink):
                output += f":ref:`{part.link}`"
            else:
                raise NotImplementedError
        output += "\n"
        return output
