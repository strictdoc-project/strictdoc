from enum import Enum

from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.backend.sdoc.models.section import FreeText, Section
from strictdoc.backend.sdoc.models.type_system import ReferenceType
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

    def write(self, document, single_document):
        document_iterator = DocumentCachingIterator(document)
        output = ""

        if not single_document:
            output += self._print_rst_header(document.title, 0)

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
    def _print_rst_header(string: str, level: int):
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

    def _print_requirement_fields_unused(self, section_content: Requirement):
        output = ""
        if section_content.uid is not None:
            output += f".. _{section_content.uid}:"
            output += "\n\n"

        if section_content.title is not None:
            output += self._print_rst_header(
                section_content.title, section_content.ng_level
            )

        if section_content.uid is not None:
            output += ".. list-table::\n"
            output += "    :align: left\n"
            output += "    :header-rows: 0\n\n"

            output += "    * - **UID:**\n"
            output += f"      - {section_content.uid}\n"
            output += "\n"

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

        requirement_parent_refs = section_content.get_requirement_references(
            ReferenceType.PARENT
        )
        if len(requirement_parent_refs) > 0:
            output += "**Parents:**"
            output += "\n\n"
            for reference in requirement_parent_refs:
                output += f"- ``[{reference.ref_uid}]`` "
                output += f":ref:`{reference.ref_uid}`"
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
