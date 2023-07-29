from typing import Optional, Type, Union

from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import Document
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.requirement import (
    Requirement,
)
from strictdoc.backend.sdoc.models.section import FreeText
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.html_fragment_writer import (
    HTMLFragmentWriter,
)
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.text_to_html_writer import TextToHtmlWriter
from strictdoc.export.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)
from strictdoc.helpers.rst import truncated_statement_with_no_rst


class MarkupRenderer:
    @staticmethod
    def create(
        markup,
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
        html_templates: HTMLTemplates,
        config: ProjectConfig,
        context_document: Optional[Document],
    ) -> "MarkupRenderer":
        assert isinstance(html_templates, HTMLTemplates)
        html_fragment_writer: Union[
            RstToHtmlFragmentWriter,
            Type[HTMLFragmentWriter],
            Type[TextToHtmlWriter],
        ]
        if not markup or markup == "RST":
            html_fragment_writer = RstToHtmlFragmentWriter(
                path_to_output_dir=config.export_output_dir,
                context_document=context_document,
            )
        elif markup == "HTML":
            html_fragment_writer = HTMLFragmentWriter
        else:
            html_fragment_writer = TextToHtmlWriter
        return MarkupRenderer(
            html_fragment_writer,
            traceability_index,
            link_renderer,
            html_templates,
            context_document,
        )

    def __init__(  # pylint: disable=too-many-arguments
        self,
        fragment_writer,
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
        html_templates: HTMLTemplates,
        context_document: Optional[Document],
    ):
        assert isinstance(traceability_index, TraceabilityIndex)
        assert isinstance(link_renderer, LinkRenderer)
        assert context_document is None or isinstance(
            context_document, Document
        ), context_document
        assert isinstance(html_templates, HTMLTemplates)

        self.fragment_writer = fragment_writer
        self.traceability_index = traceability_index
        self.link_renderer: LinkRenderer = link_renderer
        self.context_document: Optional[Document] = context_document

        self.cache = {}
        self.rationale_cache = {}

        self.template_anchor = html_templates.jinja_environment().get_template(
            "rst/anchor.jinja"
        )

    def render_requirement_statement(self, requirement):
        assert isinstance(requirement, Requirement)
        assert self.context_document is not None

        if requirement in self.cache:
            return self.cache[requirement]
        output = self.fragment_writer.write(requirement.reserved_statement)
        self.cache[requirement] = output

        return output

    def render_truncated_requirement_statement(self, requirement):
        assert isinstance(requirement, Requirement), requirement
        assert requirement.reserved_statement is not None
        assert self.context_document is not None

        statement_to_render = truncated_statement_with_no_rst(
            requirement.reserved_statement
        )

        output = self.fragment_writer.write(statement_to_render)
        self.cache[requirement] = output

        return output

    def render_requirement_rationale(self, requirement):
        assert isinstance(requirement, Requirement)
        assert self.context_document is not None

        if requirement in self.rationale_cache:
            return self.rationale_cache[requirement]
        output = self.fragment_writer.write(requirement.rationale)
        self.rationale_cache[requirement] = output
        return output

    def render_comment(self, comment):
        assert isinstance(comment, str)
        assert self.context_document is not None

        if comment in self.cache:
            return self.cache[comment]
        output = self.fragment_writer.write(comment)
        self.cache[comment] = output
        return output

    def render_free_text(self, document_type, free_text):
        assert isinstance(free_text, FreeText)
        assert self.context_document is not None

        if (document_type, free_text) in self.cache:
            return self.cache[free_text]

        parts_output = ""
        for part in free_text.parts:
            if isinstance(part, str):
                parts_output += part
            elif isinstance(part, InlineLink):
                # First, we try to get a section with this name, then Anchor.
                node = self.traceability_index.get_section_by_uid_weak(
                    part.link
                )
                if node is None:
                    node = self.traceability_index.get_anchor_by_uid_weak(
                        part.link
                    )
                assert (
                    node is not None
                ), f"Could not find a section or anchor with UID: {part.link}"
                href = self.link_renderer.render_node_link(
                    node, self.context_document, document_type
                )
                parts_output += self.fragment_writer.write_anchor_link(
                    node.title, href
                )
            elif isinstance(part, Anchor):
                parts_output += self.template_anchor.render(
                    anchor=part,
                    traceability_index=self.traceability_index,
                    link_renderer=self.link_renderer,
                    document_type=DocumentType.document(),
                )

        output = self.fragment_writer.write(parts_output)
        self.cache[(document_type, free_text)] = output

        return output

    def render_meta_value(self, meta_field_value):
        assert isinstance(meta_field_value, str)
        assert self.context_document is not None

        # FIXME: Introduce and improve caching.
        output = self.fragment_writer.write(meta_field_value)

        return output
