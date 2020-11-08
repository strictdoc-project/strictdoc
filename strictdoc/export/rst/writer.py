from enum import Enum

from strictdoc.backend.dsl.models.requirement import Requirement
from strictdoc.backend.dsl.models.section import FreeText, Section
from strictdoc.core.document_iterator import DocumentCachingIterator


class TAG(Enum):
    SECTION = 1
    REQUIREMENT = 2
    COMPOSITE_REQUIREMENT = 3


class RSTWriter:
    def __init__(self):
        pass

    def write(self, document):
        document_iterator = DocumentCachingIterator(document)
        output = ""

        output += self._print_rst_header(document.name, 0)
        for free_text in document.free_texts:
            output += self._print_free_text(free_text)

        for content_node in document_iterator.all_content():
            if isinstance(content_node, Section):
                output += self._print_rst_header(content_node.title, content_node.ng_level)
                for free_text in content_node.free_texts:
                    output += self._print_free_text(free_text)

            elif isinstance(content_node, Requirement):
                output += self._print_rst_header(content_node.title, content_node.ng_level)
                output += self._print_requirement_fields(content_node)

        return output.lstrip()

    def _print_rst_header(self, string, level):
        chars = {
            0: '$',
            1: '=',
            2: '-',
            3: '~',
            4: '^',
            5: '"',
            6: '#',
            7: "'",
        }
        header_char = chars[level]
        output = ''
        output += string
        output += "\n"
        output += header_char.rjust(len(string), header_char)
        output += "\n"
        output += "\n"
        return output

    def _print_requirement_fields(self, section_content):
        output = ''

        if section_content.uid:
            output += "``["
            output += section_content.uid
            output += "]``"
            output += "\n"
            output += "\n"

        if section_content.statement:
            output += section_content.statement
            output += "\n"
            output += "\n"
        elif section_content.statement_multiline:
            output += section_content.statement_multiline
            output += "\n"
            output += "\n"
        else:
            pass  # raise RuntimeError('Statement is missing')

        if section_content.body:
            output += "\n"
            output += section_content.body
            output += "\n"
            output += "\n"

        for comment in section_content.comments:
            output += '**'
            output += "Comment:"
            output += '** '
            output += comment.get_comment()
            output += "\n"
            output += "\n"

        return output

    def _print_free_text(self, free_text):
        assert isinstance(free_text, FreeText)
        output = ''
        output += free_text.text
        output += '\n'
        output += '\n'

        return output
