from enum import Enum

from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.sdoc.models.section import FreeText, Section
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.traceability_index import TraceabilityIndex


class TAG(Enum):
    SECTION = 1
    REQUIREMENT = 2
    COMPOSITE_REQUIREMENT = 3


class RSTWriter:
    def __init__(self, index: TraceabilityIndex):
        self.index = index

    def write(self, document, single_document):
        document_iterator = DocumentCachingIterator(document)
        output = ""

        if not single_document:
            output += self._print_rst_header(document.name, 0)

        for free_text in document.free_texts:
            output += self._print_free_text(free_text)

        for content_node in document_iterator.all_content():
            if isinstance(content_node, Section):
                output += self._print_rst_header(
                    content_node.title, content_node.ng_level
                )
                for free_text in content_node.free_texts:
                    output += self._print_free_text(free_text)

            elif isinstance(content_node, Requirement):
                output += self._print_requirement_fields(content_node)

        return output.lstrip()

    @staticmethod
    def _print_rst_header(string, level):
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
        output += "\n\n"
        return output

    def _print_requirement_fields(self, section_content: Requirement):
        output = ""

        if section_content.uid:
            output += f".. _{section_content.uid}:"
            output += "\n\n"
            output += self._print_rst_header(
                section_content.title, section_content.ng_level
            )

            output += ".. list-table::\n"
            output += "    :align: left\n"
            output += "    :header-rows: 0\n\n"

            output += "    * - **UID:**\n"
            output += f"      - {section_content.uid}\n"
            output += "\n"
        else:
            output += self._print_rst_header(
                section_content.title, section_content.ng_level
            )

        if section_content.statement:
            output += section_content.statement
            output += "\n\n"
        elif section_content.statement_multiline:
            output += section_content.statement_multiline
            output += "\n\n"
        else:
            pass  # raise RuntimeError('Statement is missing')

        for comment in section_content.comments:
            output += "**"
            output += "Comment:"
            output += "** "
            output += comment.get_comment()
            output += "\n\n"

        requirement_references = section_content.get_requirement_references()
        if len(requirement_references) > 0:
            output += "**Parents:**"
            output += "\n\n"
            for reference in requirement_references:
                output += f"- ``[{reference.path}]`` "
                output += f":ref:`{reference.path}`"
                output += "\n"
            output += "\n"

        if self.index.has_children_requirements(section_content):
            output += "**Children:**"
            output += "\n\n"
            for child_requirement in self.index.get_children_requirements(
                section_content
            ):
                output += f"- ``[{child_requirement.uid}]`` "
                output += f":ref:`{child_requirement.uid}`"
                output += "\n"
            output += "\n"

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
                node = self.index.get_node_by_uid(part.link)
                output += f"`{node.title}`_"
            else:
                raise NotImplementedError
        output += "\n"
        return output
