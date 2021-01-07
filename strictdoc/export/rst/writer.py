from enum import Enum

from strictdoc.backend.dsl.models.requirement import Requirement
from strictdoc.backend.dsl.models.section import FreeText, Section
from strictdoc.backend.dsl.models.special_field import SpecialField
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

    def _print_rst_header(self, string, level):
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

        meta_table_started = False
        if section_content.uid:
            output += ".. _{}:".format(section_content.uid)
            output += "\n\n"
            output += self._print_rst_header(
                section_content.title, section_content.ng_level
            )

            meta_table_started = True
            output += ".. list-table::\n"
            output += "    :align: left\n"
            output += "    :header-rows: 0\n\n"

            output += f"    * - **UID:**\n"
            output += f"      - {section_content.uid}\n"
            output += "\n"
        else:
            output += self._print_rst_header(
                section_content.title, section_content.ng_level
            )
        if section_content.special_fields and len(
            section_content.special_fields
        ):
            if not meta_table_started:
                output += ".. list-table::\n"
                output += "    :align: left\n"
                output += "    :header-rows: 0\n\n"

            special_field: SpecialField
            for special_field in section_content.special_fields:
                output += f"    * - **{special_field.field_name}:**\n"
                output += f"      - {special_field.field_value}\n"
                output += "\n"

        if section_content.statement:
            output += section_content.statement
            output += "\n\n"
        elif section_content.statement_multiline:
            output += section_content.statement_multiline
            output += "\n\n"
        else:
            pass  # raise RuntimeError('Statement is missing')

        if section_content.body:
            output += "\n"
            output += section_content.body
            output += "\n\n"

        for comment in section_content.comments:
            output += "**"
            output += "Comment:"
            output += "** "
            output += comment.get_comment()
            output += "\n\n"

        if section_content.references and len(section_content.references) > 0:
            output += "**Parents:**"
            output += "\n\n"
            for reference in section_content.references:
                output += "- ``[{}]`` ".format(reference.path)
                output += ":ref:`{}`".format(reference.path)
                output += "\n"
            output += "\n"

        if self.index.has_children_requirements(section_content):
            output += "**Children:**"
            output += "\n\n"
            for child_requirement in self.index.get_children_requirements(
                section_content
            ):
                output += "- ``[{}]`` ".format(child_requirement.uid)
                output += ":ref:`{}`".format(child_requirement.uid)
                output += "\n"
            output += "\n"

        return output

    def _print_free_text(self, free_text):
        assert isinstance(free_text, FreeText)
        output = ""
        output += free_text.text
        output += "\n\n"
        return output
