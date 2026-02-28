from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.export.markdown.markdown_to_html_fragment_writer import (
    MarkdownToHtmlFragmentWriter,
)
from tests.unit.helpers.document_builder import DocumentBuilder


def test_01_uses_markdown_fragment_writer_for_markdown_markup():
    document_builder = DocumentBuilder()
    document = document_builder.build()
    document.config.markup = SDocMarkup.MARKDOWN

    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree,
        project_config=document_builder.project_config,
    )

    html_templates = HTMLTemplates.create(
        project_config=document_builder.project_config,
        enable_caching=False,
        strictdoc_last_update=traceability_index.strictdoc_last_update,
    )
    link_renderer = LinkRenderer(root_path="", static_path="_static")

    markup_renderer = MarkupRenderer.create(
        markup=document.config.get_markup(),
        traceability_index=traceability_index,
        link_renderer=link_renderer,
        html_templates=html_templates,
        config=document_builder.project_config,
        context_document=document,
    )

    assert isinstance(
        markup_renderer.fragment_writer, MarkdownToHtmlFragmentWriter
    )
