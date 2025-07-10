# mypy: disable-error-code="no-untyped-call,no-untyped-def,union-attr"
from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, List, Optional, Sequence, Tuple, Union

from jinja2 import Template
from markupsafe import Markup

from strictdoc import __version__
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_view import ViewElement
from strictdoc.backend.sdoc.models.grammar_element import GrammarElement
from strictdoc.backend.sdoc.models.model import SDocElementIF
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.document_iterator import DocumentIterationContext
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.file_tree import File, Folder
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.generators.view_objects.helpers import (
    screen_should_display_file,
    screen_should_display_folder,
)
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.git_client import GitClient
from strictdoc.helpers.string import interpolate_at_pattern_lazy
from strictdoc.server.helpers.turbo import render_turbo_stream


@dataclass
class DocumentScreenViewObject:
    def __init__(
        self,
        *,
        document_type: DocumentType,
        document: SDocDocument,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
        link_renderer: LinkRenderer,
        markup_renderer: MarkupRenderer,
        git_client: GitClient,
        standalone: bool,
    ):
        self.document_type: DocumentType = document_type
        self.link_document_type: DocumentType = DocumentType.DOCUMENT
        self.document: SDocDocument = document
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.link_renderer: LinkRenderer = link_renderer
        self.markup_renderer: MarkupRenderer = markup_renderer
        self.git_client: GitClient = git_client
        self.standalone: bool = standalone
        self.document_iterator = self.traceability_index.get_document_iterator(
            self.document
        )
        self.document_tree_iterator: DocumentTreeIterator = (
            DocumentTreeIterator(
                assert_cast(traceability_index.document_tree, DocumentTree)
            )
        )
        self.current_view: ViewElement = document.view.get_current_view(
            project_config.view
        )
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

        self.custom_html2pdf_template: Optional[Template] = None
        if project_config.html2pdf_template is not None:
            with open(project_config.html2pdf_template) as f_:
                self.custom_html2pdf_template = Template(f_.read())

    def has_included_document(self):
        return len(self.document.included_documents) > 0

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        if self.document_type.is_document():
            if self.document.config.layout == "Website":
                return jinja_environment.render_template_as_markup(
                    "website/document/index.jinja", view_object=self
                )
            return jinja_environment.render_template_as_markup(
                "screens/document/document/index.jinja", view_object=self
            )
        elif self.document_type.is_table():
            return jinja_environment.render_template_as_markup(
                "screens/document/table/index.jinja", view_object=self
            )
        elif self.document_type.is_trace():
            return jinja_environment.render_template_as_markup(
                "screens/document/traceability/index.jinja", view_object=self
            )
        elif self.document_type.is_deeptrace():
            return jinja_environment.render_template_as_markup(
                "screens/document/traceability_deep/index.jinja",
                view_object=self,
            )
        elif self.document_type.is_pdf():
            return jinja_environment.render_template_as_markup(
                "screens/document/pdf/index.jinja", view_object=self
            )
        else:
            raise NotImplementedError(self.document_type)  # pragma: no cover

    def render_updated_screen(
        self, jinja_environment: JinjaEnvironment
    ) -> Markup:
        output = jinja_environment.render_template_as_markup(
            "actions/"
            "document/"
            "create_requirement/"
            "stream_created_requirement.jinja.html",
            view_object=self,
        )

        output += jinja_environment.render_template_as_markup(
            "actions/document/_shared/stream_updated_toc.jinja.html",
            view_object=self,
        )

        return output

    def render_updated_nodes_and_toc(
        self,
        nodes: Sequence[Union[SDocDocument, SDocNode]],
        jinja_environment: JinjaEnvironment,
    ) -> str:
        output: str = ""

        for node_ in nodes:
            template_folder: str
            if isinstance(node_, SDocDocument):
                template_folder = "section"
            elif isinstance(node_, SDocNode):
                if node_.is_text_node():
                    template_folder = "text_node"
                else:
                    template_folder = "node_content"
            else:
                raise NotImplementedError
            content = jinja_environment.render_template_as_markup(
                f"components/{template_folder}/index_extends_node.jinja",
                view_object=self,
                node=node_,
            )
            output += render_turbo_stream(
                content=content,
                action="replace",
                target=f"article-{node_.reserved_mid}",
            )

        toc_content = jinja_environment.render_template_as_markup(
            "screens/document/_shared/toc.jinja", view_object=self
        )
        output += render_turbo_stream(
            content=toc_content,
            action="update",
            target="frame-toc",
        )

        return output

    def render_update_document_content_with_moved_node(
        self, jinja_environment: JinjaEnvironment, moved_node
    ) -> Markup:
        content = jinja_environment.render_template_as_markup(
            "screens/document/document/frame_document_content.jinja.html",
            view_object=self,
        )
        output = render_turbo_stream(
            content=content,
            action="replace",
            target="frame_document_content",
        )
        toc_content = jinja_environment.render_template_as_markup(
            "actions/document/_shared/stream_updated_toc.jinja.html",
            view_object=self,
            last_moved_node_id=moved_node.reserved_mid,
        )
        output += render_turbo_stream(
            toc_content,
            action="update",
            target="frame-toc",
        )
        return output

    def render_document_version(self) -> Optional[str]:
        if self.document.config.version is None:
            return None

        def resolver(variable_name):
            if variable_name == "GIT_VERSION":
                return self.git_client.get_commit_hash()
            elif variable_name == "GIT_BRANCH":
                return self.git_client.get_branch()
            return variable_name

        return interpolate_at_pattern_lazy(
            self.document.config.version, resolver
        )

    def render_document_date(self) -> Optional[str]:
        if self.document.config.date is None:
            return None

        def resolver(variable_name):
            if variable_name == "GIT_COMMIT_DATE":
                return self.git_client.get_commit_date()
            elif variable_name == "GIT_COMMIT_DATETIME":
                return self.git_client.get_commit_datetime()
            return variable_name

        return interpolate_at_pattern_lazy(self.document.config.date, resolver)

    def is_empty_tree(self) -> bool:
        return self.document_tree_iterator.is_empty_tree()

    def is_deeptrace(self) -> bool:
        return self.document_type.is_deeptrace()

    def has_any_nodes(self) -> bool:
        return self.document.has_any_nodes()

    def iterator_files_first(self):
        yield from self.document_tree_iterator.iterator_files_first()

    def render_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_url(url))

    def render_node_link(self, node) -> str:
        assert isinstance(node, SDocNode), node
        return self.link_renderer.render_node_link(
            node, self.document, self.document_type
        )

    def render_document_link(
        self,
        document: SDocDocument,
        context_document: SDocDocument,
        document_type_string: str,
    ) -> str:
        assert document is not None, document
        return self.link_renderer.render_node_link(
            document, context_document, DocumentType(document_type_string)
        )

    @staticmethod
    def render_standalone_document_link(
        document: SDocDocument, context_document: SDocDocument
    ):
        # FIXME: Check if the context_document can be removed.
        assert context_document is None
        root_prefix = document.meta.get_root_path_prefix()
        document_link = document.meta.get_html_standalone_document_link()
        return (
            document_link
            if len(root_prefix) == 0
            else "/".join((root_prefix, document_link))
        )

    def render_static_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_static_url(url))

    def render_local_anchor(self, node) -> str:
        return self.link_renderer.render_local_anchor(node)

    def render_node_statement(self, node) -> Markup:
        return self.markup_renderer.render_node_statement(
            self.document_type, node
        )

    def render_truncated_node_statement(self, node) -> Markup:
        return self.markup_renderer.render_truncated_node_statement(
            self.document_type, node
        )

    def render_node_rationale(self, node) -> Markup:
        return self.markup_renderer.render_node_rationale(
            self.document_type, node
        )

    def render_node_field(self, node_field: SDocNodeField) -> Markup:
        assert isinstance(node_field, SDocNodeField), node_field
        return self.markup_renderer.render_node_field(
            self.document_type, node_field
        )

    def get_page_title(self) -> str:
        return self.document_type.get_page_title()

    def date_today(self) -> str:
        return datetime.today().strftime("%Y-%m-%d")

    def get_document_by_path(self, full_path: str) -> SDocDocument:
        return self.traceability_index.document_tree.get_document_by_path(
            full_path
        )

    def get_grammar_elements(self) -> List[GrammarElement]:
        return self.document.grammar.elements

    def table_of_contents(
        self,
    ) -> Iterator[Tuple[SDocElementIF, DocumentIterationContext]]:
        yield from self.document_iterator.table_of_contents()

    def document_has_any_toc_nodes(self) -> bool:
        return any(self.table_of_contents())

    def document_content_iterator(
        self,
    ) -> Iterator[Tuple[SDocElementIF, DocumentIterationContext]]:
        yield from self.document_iterator.all_content(
            print_fragments=True,
        )

    def should_display_folder(self, folder: Folder) -> bool:
        return screen_should_display_folder(
            folder,
            self.traceability_index,
            self.project_config,
            must_only_include_non_included_sdoc=True,
        )

    def should_display_file(self, file: File) -> bool:
        return screen_should_display_file(
            file,
            self.traceability_index,
            self.project_config,
            must_only_include_non_included_sdoc=True,
        )

    def should_display_included_documents_for_document(
        self, document: SDocDocument
    ) -> bool:
        return (
            self.project_config.export_included_documents
            and len(document.included_documents) > 0
        )

    def should_display_stable_link(
        self, node: Union[SDocDocument, SDocSection, SDocNode]
    ) -> bool:
        assert isinstance(node, (SDocDocument, SDocSection, SDocNode)), node
        return node.reserved_uid is not None

    def should_display_old_section_as_deprecated(self) -> bool:
        return self.project_config.is_new_section_behavior()

    def get_stable_link(
        self, node: Union[SDocDocument, SDocSection, SDocNode]
    ) -> str:
        """
        Get a stable link for a given node.

        An example of a link produced: ../../#SDOC_UG_CONTACT
        The copy_stable_link_button_controller.js consumes this link and
        transforms it into a link like: http://127.0.0.1:5111/#SDOC_UG_CONTACT.
        """

        assert isinstance(node, (SDocDocument, SDocSection, SDocNode)), node
        base_url = self.link_renderer.render_url("")
        if node.reserved_uid is not None:
            return base_url + "#" + node.reserved_uid
        if node.reserved_mid is not None and node.mid_permanent:
            return base_url + "#" + node.reserved_mid
        return base_url
