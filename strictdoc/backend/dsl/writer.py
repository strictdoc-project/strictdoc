from enum import Enum

from strictdoc.backend.dsl.models.document_config import DocumentConfig
from strictdoc.backend.dsl.models.inline_link import InlineLink
from strictdoc.backend.dsl.models.requirement import (
    Requirement,
    CompositeRequirement,
)
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

            config_special_fields = document_config.special_fields
            if config_special_fields:
                output += "SPECIAL_FIELDS:"
                output += "\n"

                for config_special_field in config_special_fields:
                    output += "- NAME: "
                    output += config_special_field.field_name
                    output += "\n"
                    output += "  TYPE: "
                    output += config_special_field.field_type
                    output += "\n"
                    if config_special_field.field_required:
                        output += "  REQUIRED: Yes"
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
        if document_grammar:
            output += "\n[GRAMMAR]\n"
            output += "ELEMENTS:\n"
            for element in document_grammar.elements:
                output += "- TAG: "
                output += element.tag
                output += "\n  FIELDS:\n"
                for grammar_field in element.fields:
                    output += "  - TITLE: "
                    output += grammar_field.title
                    output += "\n"
                    output += "    TYPE: "
                    output += grammar_field.field_type
                    output += "\n"
                    output += "    REQUIRED: "
                    output += "True" if grammar_field.required else "False"
                    output += "\n"

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
                    output += "[COMPOSITE_REQUIREMENT]\n"
                    closing_tags.append(
                        (TAG.COMPOSITE_REQUIREMENT, content_node.ng_level)
                    )
                else:
                    output += "[REQUIREMENT]\n"

                output += self._print_requirement_fields(content_node)

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
    def _print_requirement_fields(section_content: Requirement):
        output = ""

        default_fields_order = [
            "UID",
            "LEVEL",
            "STATUS",
            "TAGS",
            "SPECIAL_FIELDS",
            "REFS",
            "TITLE",
            "STATEMENT",
            "BODY",
            "RATIONALE",
            "COMMENT",
        ]
        for field_name in default_fields_order:
            if field_name not in section_content.ordered_fields_lookup:
                continue
            fields = section_content.ordered_fields_lookup[field_name]
            for field in fields:
                if field.field_value:
                    output += f"{field_name}: "
                    output += field.field_value
                    output += "\n"
                elif field.field_value_multiline:
                    output += f"{field_name}: >>>"
                    output += "\n"
                    output += field.field_value_multiline.rstrip()
                    output += "\n"
                    output += "<<<"
                    output += "\n"
                elif field.field_value_special_fields:
                    output += "SPECIAL_FIELDS:"
                    output += "\n"
                    for special_field in field.field_value_special_fields:
                        output += (
                            f"  "
                            f"{special_field.field_name}: "
                            f"{special_field.field_value}"
                        )
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
                else:
                    raise NotImplementedError(field) from None
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
        for part in free_text.parts:
            if isinstance(part, str):
                output += part
            elif isinstance(part, InlineLink):
                output += "[LINK: "
                output += part.link
                output += "]"
            else:
                raise NotImplementedError
        if output[-1] != "\n":
            output += "\n"
        output += "[/FREETEXT]"
        output += "\n"
        return output
