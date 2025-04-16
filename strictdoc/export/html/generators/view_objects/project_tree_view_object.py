from dataclasses import dataclass

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.file_tree import File, Folder
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.generators.view_objects.helpers import (
    screen_should_display_file,
    screen_should_display_folder,
)
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer


@dataclass
class ProjectTreeViewObject:
    def __init__(
        self,
        *,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
    ):
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config

        link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        self.link_renderer: LinkRenderer = link_renderer

        self.document_tree_iterator: DocumentTreeIterator = (
            DocumentTreeIterator(traceability_index.document_tree)
        )
        self.standalone: bool = False
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__
        self.contains_included_documents = (
            traceability_index.contains_included_documents
        )

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "screens/project_index/index.jinja", view_object=self
        )

    def render_map(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "screens/project_index/project_map.jinja.js", view_object=self
        )

    def render_static_url(self, url: str) -> str:
        return self.link_renderer.render_static_url(url)

    def render_url(self, url: str) -> str:
        return self.link_renderer.render_url(url)

    def render_static_url_with_prefix(self, url: str) -> str:
        return self.link_renderer.render_static_url_with_prefix(url)

    def is_empty_tree(self) -> bool:
        return self.document_tree_iterator.is_empty_tree()

    def should_display_fragments_toggle(self) -> bool:
        return self.project_config.export_included_documents

    def should_display_folder(self, folder: Folder) -> bool:
        return screen_should_display_folder(
            folder,
            self.traceability_index,
            self.project_config,
            must_only_include_non_included_sdoc=False,
        )

    def should_display_file(self, file: File) -> bool:
        return screen_should_display_file(
            file,
            self.traceability_index,
            self.project_config,
            must_only_include_non_included_sdoc=False,
        )
