# mypy: disable-error-code="no-untyped-call,union-attr"
from dataclasses import dataclass
from typing import Iterator, List, Optional, Union

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_view import DocumentView
from strictdoc.backend.sdoc.models.model import SDocExtendedElementIF
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.file_tree import FileOrFolderEntry
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.source_tree import SourceFile
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates, JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.helpers.cast import assert_cast


@dataclass
class SearchScreenViewObject:
    def __init__(
        self,
        *,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
        templates: HTMLTemplates,
        search_results: List[SDocExtendedElementIF],
        search_value: str,
        error: Optional[str],
    ) -> None:
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.templates: HTMLTemplates = templates
        self.search_results: List[SDocExtendedElementIF] = search_results
        self.search_value: str = search_value
        self.error: Optional[str] = error

        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        markup_renderer = MarkupRenderer.create(
            "RST",
            traceability_index,
            link_renderer,
            templates,
            project_config,
            None,
        )

        self.link_renderer: LinkRenderer = link_renderer
        self.markup_renderer: MarkupRenderer = markup_renderer
        self.standalone: bool = False
        self.document_tree_iterator: DocumentTreeIterator = (
            DocumentTreeIterator(
                assert_cast(traceability_index.document_tree, DocumentTree)
            )
        )
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__
        self.current_view = DocumentView.create_default(None).views[0]
        self.document_type: DocumentType = DocumentType.DOCUMENT
        self.link_document_type: DocumentType = DocumentType.DOCUMENT
        self.document: Optional[SDocDocument] = None

    def render_truncated_node_statement(self, node: SDocNode) -> Markup:
        return self.markup_renderer.render_truncated_node_statement(
            self.document_type, node
        )

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "screens/search/index.jinja", view_object=self
        )

    def is_empty_tree(self) -> bool:
        return self.document_tree_iterator.is_empty_tree()

    def iterator_files_first(self) -> Iterator[FileOrFolderEntry]:
        yield from self.document_tree_iterator.iterator_files_first()

    def render_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_url(url))

    def render_static_url_with_prefix(self, url: str) -> str:
        return self.link_renderer.render_static_url_with_prefix(url)

    def render_node_link(
        self, incoming_link: Union[SDocDocument, SDocNode, SDocSection, Anchor]
    ) -> str:
        return self.link_renderer.render_node_link(
            incoming_link, None, DocumentType.DOCUMENT
        )

    def render_static_url(self, url: str) -> str:
        return self.link_renderer.render_static_url(url)

    def render_source_file_link_from_root_2(
        self, source_file: SourceFile
    ) -> str:
        return Markup(
            self.link_renderer.render_source_file_link_from_root_2(source_file)
        )

    def render_local_anchor(
        self, node: Union[Anchor, SDocNode, SDocSection, SDocDocument]
    ) -> str:
        return self.link_renderer.render_local_anchor(node)
