# mypy: disable-error-code="arg-type,attr-defined,no-untyped-call,no-untyped-def"
from enum import Enum
from typing import Optional

from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.rst.rst_templates import RSTTemplates
from strictdoc.helpers.rst import escape_str_after_inline_markup


class TAG(Enum):
    SECTION = 1
    REQUIREMENT = 2
    COMPOSITE_REQUIREMENT = 3


class RSTWriter:
    def __init__(self, index: TraceabilityIndex):
        self.index = index

    def write(self, document: SDocDocument, single_document: bool) -> str:
        document_iterator = DocumentCachingIterator(document)
        output = ""

        if not single_document:
            document_uid: Optional[str] = None
            if document.config.uid is not None:
                document_uid = document.config.uid
            output += self._print_rst_header(
                document.title, 0, reference_uid=document_uid
            )

        for content_node, _ in document_iterator.all_content():
            if isinstance(content_node, SDocSection):
                output += self._print_rst_header(
                    content_node.title,
                    content_node.ng_level,
                    content_node.reserved_uid,
                )

            elif isinstance(content_node, SDocNode):
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

    def _print_requirement_fields(self, section_content: SDocNode):
        requirement_template = RSTTemplates.jinja_environment.get_template(
            "requirement.jinja.rst"
        )
        output = requirement_template.render(
            requirement=section_content,
            index=self.index,
            _print_rst_header=self._print_rst_header_2,
            _print_node_field=self._print_node_field,
        )
        return output

    def _print_node_field(self, object_with_parts: SDocNodeField):
        output = ""
        prev_part = None
        for part in object_with_parts.parts:
            if isinstance(part, str):
                if isinstance(prev_part, InlineLink):
                    output += escape_str_after_inline_markup(part)
                else:
                    output += part
            elif isinstance(part, InlineLink):
                node_or_none = self.index.get_linkable_node_by_uid(part.link)
                # Labels that aren't placed before a section title can still be
                # referenced, but you must give the link an explicit title,
                # using this syntax: :ref:`Link title <label-name>`.
                # https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html
                node_display_title = node_or_none.get_display_title(
                    include_toc_number=False
                )
                output += f":ref:`{node_display_title} <{part.link}>`"
            elif isinstance(part, Anchor):
                output += f".. _{part.value}:\n"
            else:
                raise NotImplementedError
            prev_part = part

        return output
