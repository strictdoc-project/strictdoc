from datetime import datetime
from typing import Optional

from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.traceability_index_builder import TraceabilityIndexBuilder
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.generators.view_objects.document_screen_view_object import (
    DocumentScreenViewObject,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.helpers.git_client import GitClient
from tests.unit.helpers.document_builder import DocumentBuilder


def create_document_screen_view_object(
    *,
    node_count: int = 0,
    threshold: int = 0,
    is_running_on_server: bool = True,
    document_type: DocumentType = DocumentType.DOCUMENT,
    custom_css_path: Optional[str] = None,
) -> DocumentScreenViewObject:
    document_builder = DocumentBuilder()
    for node_idx_ in range(node_count):
        document_builder.add_requirement(f"REQ-{node_idx_:03d}")
    document = document_builder.build()

    project_config = document_builder.project_config
    project_config.lazy_document_loading_threshold = threshold
    project_config.is_running_on_server = is_running_on_server
    project_config.custom_css_path = custom_css_path
    # Required by get_project_hash(), which the page head calls into via
    # static_search_head.jinja whenever a screen is actually rendered.
    project_config.input_paths = ["/tmp/some/project"]

    document_tree = DocumentTree(
        file_tree=[],
        document_list=[document],
        map_docs_by_paths={},
        map_docs_by_rel_paths={},
        map_grammars_by_filenames={},
    )
    traceability_index = TraceabilityIndexBuilder.create_from_document_tree(
        document_tree, project_config=project_config
    )

    link_renderer = LinkRenderer(root_path="", static_path="_static")
    html_templates = HTMLTemplates.create(
        project_config=project_config,
        enable_caching=False,
        strictdoc_last_update=datetime.today(),
    )
    markup_renderer = MarkupRenderer.create(
        markup=document.config.get_markup(),
        traceability_index=traceability_index,
        link_renderer=link_renderer,
        html_templates=html_templates,
        config=project_config,
        context_document=document,
    )
    return DocumentScreenViewObject(
        document_type=document_type,
        document=document,
        traceability_index=traceability_index,
        project_config=project_config,
        link_renderer=link_renderer,
        markup_renderer=markup_renderer,
        jinja_environment=html_templates.jinja_environment(),
        git_client=GitClient(),
    )
