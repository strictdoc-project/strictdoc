from typing import Dict, Optional, Tuple, Union

from markupsafe import Markup

from strictdoc.backend.markdown.markdown_to_html_fragment_writer import (
    MarkdownToHtmlFragmentWriter,
)
from strictdoc.backend.rst.rst_to_html_fragment_writer import (
    RstToHtmlFragmentWriter,
)
from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.model import RequirementFieldName
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.html_fragment_writer import (
    HTMLFragmentWriter,
)
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.text_to_html_writer import TextToHtmlWriter
from strictdoc.helpers.rst import escape_str_after_inline_markup

FragmentWriterType = Union[
    RstToHtmlFragmentWriter,
    MarkdownToHtmlFragmentWriter,
    HTMLFragmentWriter,
    TextToHtmlWriter,
]


class MarkupRenderer:
    @staticmethod
    def create(
        markup: Optional[str],
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
        html_templates: HTMLTemplates,
        config: ProjectConfig,
        context_document: Optional[SDocDocument],
        flat_assets: bool = False,
        reference_path_override: Optional[str] = None,
    ) -> "MarkupRenderer":
        assert isinstance(html_templates, HTMLTemplates)
        html_fragment_writer: FragmentWriterType
        if not markup or markup == SDocMarkup.RST:
            html_fragment_writer = RstToHtmlFragmentWriter(
                project_config=config,
                context_document=context_document,
                flat_assets=flat_assets,
                reference_path_override=reference_path_override,
            )
        elif markup == SDocMarkup.MARKDOWN:
            html_fragment_writer = MarkdownToHtmlFragmentWriter(
                flat_assets=flat_assets
            )
        elif markup == SDocMarkup.HTML:
            html_fragment_writer = HTMLFragmentWriter()
        else:
            html_fragment_writer = TextToHtmlWriter()
        return MarkupRenderer(
            html_fragment_writer,
            traceability_index,
            link_renderer,
            html_templates,
            context_document,
            flat_assets=flat_assets,
            primary_markup=markup,
        )

    def __init__(
        self,
        fragment_writer: FragmentWriterType,
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
        html_templates: HTMLTemplates,
        context_document: Optional[SDocDocument],
        flat_assets: bool = False,
        primary_markup: Optional[str] = None,
    ) -> None:
        assert isinstance(traceability_index, TraceabilityIndex)
        assert isinstance(link_renderer, LinkRenderer)
        assert context_document is None or isinstance(
            context_document, SDocDocument
        ), context_document
        assert isinstance(html_templates, HTMLTemplates)

        self.fragment_writer: FragmentWriterType = fragment_writer
        self.traceability_index: TraceabilityIndex = traceability_index
        self.link_renderer: LinkRenderer = link_renderer
        self.context_document: Optional[SDocDocument] = context_document
        self.flat_assets: bool = flat_assets

        # Cache of fragment writers keyed by markup string. Pre-populated with
        # the primary writer so the dispatch method reuses it without creating
        # duplicates for the common case.
        primary_key: str = primary_markup or SDocMarkup.RST
        self._writers_by_markup: Dict[str, FragmentWriterType] = {
            primary_key: fragment_writer
        }

        # FIXME: Now that the underlying RST fragment caching is in place,
        # This caching could be removed. It is unlikely that it adds any serious
        # performance improvement.
        self.cache: Dict[Tuple[DocumentType, SDocNodeField], Markup] = {}

        if isinstance(
            fragment_writer, (MarkdownToHtmlFragmentWriter, HTMLFragmentWriter)
        ):
            self.template_anchor = (
                html_templates.jinja_environment().get_template(
                    "markup/anchor.jinja"
                )
            )
        else:
            self.template_anchor = (
                html_templates.jinja_environment().get_template(
                    "rst/anchor.jinja"
                )
            )

    def _get_writer_for_node_field(
        self, node_field: SDocNodeField
    ) -> FragmentWriterType:
        """
        Return the fragment writer appropriate for the node field's markup.

        When the bundle document (RST by default) contains sub-documents with
        different markup (e.g. Markdown), nodes from those sub-documents must be
        rendered with the correct writer, not the bundle's primary RST writer.
        """
        if node_field.parent is None:
            return self.fragment_writer
        doc = node_field.parent.get_document()
        if doc is None or doc.config is None:
            return self.fragment_writer
        markup = doc.config.markup  # raw value; None means RST
        key = markup or SDocMarkup.RST
        if key not in self._writers_by_markup:
            if not markup or markup == SDocMarkup.RST:
                self._writers_by_markup[key] = self.fragment_writer
            elif markup == SDocMarkup.MARKDOWN:
                self._writers_by_markup[key] = MarkdownToHtmlFragmentWriter(
                    flat_assets=self.flat_assets
                )
            elif markup == SDocMarkup.HTML:
                self._writers_by_markup[key] = HTMLFragmentWriter()
            else:
                self._writers_by_markup[key] = TextToHtmlWriter()
        return self._writers_by_markup[key]

    def render_node_statement(
        self, document_type: DocumentType, node: SDocNode
    ) -> Markup:
        assert isinstance(node, SDocNode)
        return self.render_node_field(document_type, node.get_content_field())

    def render_truncated_node_statement(
        self, document_type: DocumentType, node: SDocNode
    ) -> Markup:
        assert isinstance(node, SDocNode)
        # FIXME: Double-check and switch to truncating using CSS.
        # https://github.com/strictdoc-project/strictdoc/issues/1925
        return self.render_node_field(document_type, node.get_content_field())

    def render_node_rationale(
        self, document_type: DocumentType, node: SDocNode
    ) -> Markup:
        assert isinstance(node, SDocNode)
        return self.render_node_field(
            document_type,
            node.get_field_by_name(RequirementFieldName.RATIONALE),
        )

    def render_node_field(
        self, document_type: DocumentType, node_field: SDocNodeField
    ) -> Markup:
        assert isinstance(node_field, SDocNodeField), node_field

        if (document_type, node_field) in self.cache:
            return self.cache[(document_type, node_field)]

        fragment_writer = self._get_writer_for_node_field(node_field)

        prev_part = None
        parts_output = ""
        for part in node_field.parts:
            if isinstance(part, str):
                if isinstance(prev_part, InlineLink) and isinstance(
                    fragment_writer, RstToHtmlFragmentWriter
                ):
                    parts_output += escape_str_after_inline_markup(part)
                else:
                    parts_output += part
            elif isinstance(part, InlineLink):
                linkable_node = (
                    self.traceability_index.get_linkable_node_by_uid(part.link)
                )
                href = self.link_renderer.render_node_link(
                    linkable_node, self.context_document, document_type
                )
                parts_output += fragment_writer.write_anchor_link(
                    linkable_node.get_display_title(), href
                )
            elif isinstance(part, Anchor):
                parts_output += self.template_anchor.render(
                    anchor=part,
                    traceability_index=self.traceability_index,
                    link_renderer=self.link_renderer,
                    document_type=DocumentType.DOCUMENT,
                )
            else:
                raise NotImplementedError
            prev_part = part

        output = fragment_writer.write(parts_output)
        self.cache[(document_type, node_field)] = output

        return output
