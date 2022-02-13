from enum import Enum

from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.document_config import DocumentConfig
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
    CompositeRequirement,
)
from strictdoc.backend.sdoc.models.section import Section, FreeText
from strictdoc.backend.sdoc.models.type_system import (
    GrammarElementFieldString,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldTag,
)
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

        output += "TITLE: "
        output += document.name
        output += "\n"

        document_config: DocumentConfig = document.config
        if document_config:
            version = document_config.version
            if version:
                output += f"VERSION: {version}"
                output += "\n"

            number = document_config.number
            if number:
                output += f"NUMBER: {number}"
                output += "\n"

            markup = document_config.markup
            auto_levels_specified = document_config.ng_auto_levels_specified

            if markup or auto_levels_specified:
                output += "OPTIONS:"
                output += "\n"

                if markup:
                    output += "  MARKUP: "
                    output += markup
                    output += "\n"

                if auto_levels_specified:
                    output += "  AUTO_LEVELS: "
                    output += "On" if document_config.auto_levels else "Off"
                    output += "\n"

        document_grammar = document.grammar
        if not document_grammar.is_default:
            output += "\n[GRAMMAR]\n"
            output += "ELEMENTS:\n"
            for element in document_grammar.elements:
                output += "- TAG: "
                output += element.tag
                output += "\n  FIELDS:\n"
                for grammar_field in element.fields:
                    output += SDWriter._print_grammar_field_type(grammar_field)
        for free_text in document.free_texts:
            output += "\n"
            output += self._print_free_text(free_text)
        closing_tags = []
        for content_node in document_iterator.all_content():
            while (
                len(closing_tags) > 0
                and content_node.ng_level <= closing_tags[-1][1]
            ):
                closing_tag, _ = closing_tags.pop()
                output += self._print_closing_tag(closing_tag)

            output += "\n"

            if isinstance(content_node, Section):
                output += self._print_section(content_node)
                closing_tags.append((TAG.SECTION, content_node.ng_level))
            elif isinstance(content_node, Requirement):
                if isinstance(content_node, CompositeRequirement):
                    output += "[COMPOSITE_"
                    output += content_node.requirement_type
                    output += "]\n"
                    closing_tags.append(
                        (TAG.COMPOSITE_REQUIREMENT, content_node.ng_level)
                    )
                else:
                    output += "["
                    output += content_node.requirement_type
                    output += "]\n"

                output += self._print_requirement_fields(
                    section_content=content_node, document=document
                )

        for closing_tag, _ in reversed(closing_tags):
            output += self._print_closing_tag(closing_tag)

        return output

    def _print_section(self, section):
        assert isinstance(section, Section)
        output = ""
        output += "[SECTION]"
        output += "\n"

        if section.uid:
            output += "UID: "
            output += section.uid
            output += "\n"

        if section.level:
            output += "LEVEL: "
            output += section.level
            output += "\n"

        output += "TITLE: "
        output += str(section.title)
        output += "\n"
        for free_text in section.free_texts:
            output += "\n"
            output += self._print_free_text(free_text)
        return output

    @staticmethod
    def _print_requirement_fields(
        section_content: Requirement, document: Document
    ):
        output = ""

        element = document.grammar.elements_by_type[
            section_content.requirement_type
        ]
        for element_field in element.fields:
            field_name = element_field.title
            if field_name not in section_content.ordered_fields_lookup:
                continue
            fields = section_content.ordered_fields_lookup[field_name]
            for field in fields:
                if field.field_value_multiline is not None:
                    output += f"{field_name}: >>>"
                    output += "\n"
                    if len(field.field_value_multiline) > 0:
                        output += field.field_value_multiline.rstrip()
                        output += "\n"
                    output += "<<<"
                    output += "\n"
                elif field.field_value_references:
                    output += "REFS:"
                    output += "\n"

                    for reference in field.field_value_references:
                        output += "- TYPE: "
                        output += reference.ref_type
                        output += "\n"
                        output += "  VALUE: "
                        output += reference.path
                        output += "\n"
                elif field.field_value is not None:
                    if len(field.field_value) > 0:
                        output += f"{field_name}: "
                        output += field.field_value
                    else:
                        output += f"{field_name}:"
                    output += "\n"
                else:
                    output += f"{field_name}: "
                    output += "\n"

        return output

    @staticmethod
    def _print_closing_tag(closing_tag):
        output = ""
        if closing_tag == TAG.SECTION:
            output += "\n"
            output += "[/SECTION]"
            output += "\n"
        if closing_tag == TAG.COMPOSITE_REQUIREMENT:
            output += "\n"
            output += "[/COMPOSITE_REQUIREMENT]"
            output += "\n"
        return output

    @staticmethod
    def _print_free_text(free_text):
        assert isinstance(free_text, FreeText)
        output = ""
        output += "[FREETEXT]"
        output += "\n"
        output += SDWriter.print_free_text_content(free_text)
        if output[-1] != "\n":
            output += "\n"
        output += "[/FREETEXT]"
        output += "\n"
        return output

    @staticmethod
    def _print_grammar_field_type(grammar_field):
        output = ""
        output += "  - TITLE: "
        output += grammar_field.title
        output += "\n"
        output += "    TYPE: "

        if isinstance(grammar_field, GrammarElementFieldString):
            output += "String"
        elif isinstance(grammar_field, GrammarElementFieldSingleChoice):
            output += "SingleChoice("
            output += ", ".join(grammar_field.options)
            output += ")"
        elif isinstance(grammar_field, GrammarElementFieldMultipleChoice):
            output += "MultipleChoice("
            output += ", ".join(grammar_field.options)
            output += ")"
        elif isinstance(grammar_field, GrammarElementFieldTag):
            output += "Tag"
        else:
            raise NotImplementedError from None

        output += "\n"
        output += "    REQUIRED: "
        output += "True" if grammar_field.required else "False"
        output += "\n"
        return output

    @staticmethod
    def print_free_text_content(free_text):
        assert isinstance(free_text, FreeText)
        output = ""
        for part in free_text.parts:
            if isinstance(part, str):
                output += part
            elif isinstance(part, InlineLink):
                output += "[LINK: "
                output += part.link
                output += "]"
            else:
                raise NotImplementedError
        return output
