from enum import Enum

from strictdoc.backend.dsl.models.requirement import Requirement, CompositeRequirement
from strictdoc.backend.dsl.models.section import Section, FreeText
from strictdoc.core.document_iterator import DocumentCachingIterator


class TAG(Enum):
    SECTION = 1
    REQUIREMENT = 2
    COMPOSITE_REQUIREMENT = 3


class SDWriter:
    def __init__(self):
        pass

    def write(self, document):
        document_iterator = DocumentCachingIterator(document)
        output = ""

        output += "[DOCUMENT]"
        output += "\n"

        output += "NAME: "
        output += document.name
        output += "\n"

        for free_text in document.free_texts:
            output += "\n"
            output += self._print_free_text(free_text)

        closing_tags = []
        for content_node in document_iterator.all_content():
            while len(closing_tags) > 0 and content_node.ng_level <= closing_tags[-1][1]:
                closing_tag, level = closing_tags.pop()
                output += self._print_closing_tag(closing_tag)

            output += "\n"

            if isinstance(content_node, Section):
                output += self._print_section(content_node)
                closing_tags.append((TAG.SECTION, content_node.ng_level))
            elif isinstance(content_node, Requirement):
                if isinstance(content_node, CompositeRequirement):
                    output += "[COMPOSITE-REQUIREMENT]\n"
                    closing_tags.append((TAG.COMPOSITE_REQUIREMENT, content_node.ng_level))
                else:
                    output += "[REQUIREMENT]\n"

                output += self._print_requirement_fields(content_node)

        for closing_tag, level in reversed(closing_tags):
            output += self._print_closing_tag(closing_tag)

        return output

    def _print_section(self, section):
        assert isinstance(section, Section)
        output = ''
        output += "[SECTION]"
        output += "\n"
        output += "LEVEL: "
        output += str(section.level)
        output += "\n"
        output += "TITLE: "
        output += str(section.title)
        output += "\n"
        for free_text in section.free_texts:
            output += "\n"
            output += self._print_free_text(free_text)
        return output

    def _print_requirement_fields(self, section_content):
        output = ''

        if section_content.uid:
            output += "UID: "
            output += section_content.uid
            output += "\n"

        if section_content.status:
            output += "STATUS: "
            output += section_content.status
            output += "\n"

        if section_content.tags:
            output += "TAGS: "
            output += ', '.join(section_content.tags)
            output += '\n'

        if section_content.references:
            output += "REFS:"
            output += "\n"

            for reference in section_content.references:
                output += "- TYPE: "
                output += reference.ref_type
                output += "\n"
                output += "  VALUE: "
                output += reference.path
                output += "\n"

        if section_content.title:
            output += "TITLE: "
            output += section_content.title
            output += "\n"

        if section_content.statement:
            output += "STATEMENT: "
            output += section_content.statement
            output += "\n"
        elif section_content.statement_multiline:
            output += "STATEMENT: >>>"
            output += "\n"
            output += section_content.statement_multiline
            output += "\n"
            output += "<<<"
            output += "\n"
        else:
            raise RuntimeError('Statement is missing: {}'.format(section_content))

        if section_content.body:
            output += "BODY: >>>"
            output += "\n"
            output += section_content.body
            output += "\n"
            output += "<<<"
            output += "\n"

        for comment in section_content.comments:
            if comment.comment_multiline:
                output += "COMMENT: >>>\n"
                output += comment.comment_multiline
                output += "\n<<<\n"
            else:
                output += "COMMENT: "
                output += comment.comment_single
                output += "\n"

        return output

    def _print_closing_tag(self, closing_tag):
        output = ''
        if closing_tag == TAG.SECTION:
            output += '\n'
            output += '[/SECTION]'
            output += '\n'
        if closing_tag == TAG.COMPOSITE_REQUIREMENT:
            output += '\n'
            output += '[/COMPOSITE-REQUIREMENT]'
            output += '\n'
        return output

    def _print_free_text(self, free_text):
        assert isinstance(free_text, FreeText)
        output = ''
        output += '[FREETEXT]'
        output += '\n'
        output += free_text.text.rstrip()
        output += '\n'
        output += '[/FREETEXT]'
        output += '\n'
        return output
