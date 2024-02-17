from typing import Optional, Type, Union

from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.section import FreeText, SDocSection
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
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.rst import truncated_statement_with_no_rst


class MarkupRenderer:
    @staticmethod
    def create(
        markup,
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
        html_templates: HTMLTemplates,
        config: ProjectConfig,
        context_document: Optional[SDocDocument],
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

    def __init__(
        self,
        fragment_writer,
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
        html_templates: HTMLTemplates,
        context_document: Optional[SDocDocument],
    ):
        assert isinstance(traceability_index, TraceabilityIndex)
        assert isinstance(link_renderer, LinkRenderer)
        assert context_document is None or isinstance(
            context_document, SDocDocument
        ), context_document
        assert isinstance(html_templates, HTMLTemplates)

        self.fragment_writer = fragment_writer
        self.traceability_index = traceability_index
        self.link_renderer: LinkRenderer = link_renderer
        self.context_document: Optional[SDocDocument] = context_document

        # FIXME: Now that the underlying RST fragment caching is in place,
        # This caching could be removed. It is unlikely that it adds any serious
        # performance improvement.
        self.cache = {}
        self.rationale_cache = {}

        self.template_anchor = html_templates.jinja_environment().get_template(
            "rst/anchor.jinja"
        )

    def render_requirement_statement(self, requirement):
        assert isinstance(requirement, SDocNode)

        if requirement in self.cache:
            return self.cache[requirement]
        output = self.fragment_writer.write(requirement.reserved_statement)
        self.cache[requirement] = output

        return output

    def render_truncated_requirement_statement(self, requirement):
        assert isinstance(requirement, SDocNode), requirement
        assert requirement.reserved_statement is not None

        statement_to_render = truncated_statement_with_no_rst(
            requirement.reserved_statement
        )

        # One day we may want to start caching the truncated statements. Now
        # it doesn't make sense because the deep traceability screen is the only
        # one that uses truncated statements. There is no need to cache
        # something which is used only once.
        output = self.fragment_writer.write(statement_to_render)

        return output

    def render_requirement_rationale(self, requirement):
        assert isinstance(requirement, SDocNode)

        if requirement in self.rationale_cache:
            return self.rationale_cache[requirement]
        output = self.fragment_writer.write(requirement.rationale)
        self.rationale_cache[requirement] = output
        return output

    def render_comment(self, comment):
        assert isinstance(comment, str)

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
                node: Union[SDocSection, Anchor] = assert_cast(
                    self.traceability_index.get_node_by_uid(part.link),
                    (SDocSection, Anchor),
                )
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

        # FIXME: Introduce and improve caching.
        output = self.fragment_writer.write(meta_field_value)

        return output
