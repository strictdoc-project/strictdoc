# mypy: disable-error-code="no-any-return,no-redef,no-untyped-call,no-untyped-def,union-attr"
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Union

from jinja2 import Template
from markupsafe import Markup

from strictdoc import __version__
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_grammar import GrammarElement
from strictdoc.backend.sdoc.models.document_view import ViewElement
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.file_tree import Folder
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
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
        standalone: bool,
    ):
        self.document_type: DocumentType = document_type
        self.link_document_type: DocumentType = DocumentType.document()
        self.document: SDocDocument = document
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.link_renderer: LinkRenderer = link_renderer
        self.markup_renderer: MarkupRenderer = markup_renderer
        self.standalone: bool = standalone
        self.document_iterator = self.traceability_index.get_document_iterator(
            self.document
        )
        self.document_tree_iterator: DocumentTreeIterator = (
            DocumentTreeIterator(traceability_index.document_tree)
        )
        self.current_view: ViewElement = document.view.get_current_view(
            project_config.view
        )
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version = __version__

        self.custom_html2pdf_template = None

        self.custom_html2pdf_template: Optional[Template] = None
        if project_config.html2pdf_template is not None:
            with open(project_config.html2pdf_template) as f_:
                self.custom_html2pdf_template = Template(f_.read())

    def has_included_document(self):
        return len(self.document.included_documents) > 0

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        if self.document_type.is_document:
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
        elif self.document_type.is_deeptrace:
            return jinja_environment.render_template_as_markup(
                "screens/document/traceability_deep/index.jinja",
                view_object=self,
            )
        elif self.document_type.is_pdf():
            return jinja_environment.render_template_as_markup(
                "screens/document/pdf/index.jinja", view_object=self
            )
        else:
            raise NotImplementedError(self.document_type)

    def render_table_screen(
        self, jinja_environment: JinjaEnvironment
    ) -> Markup:
        return jinja_environment.render_template_as_markup(
            "screens/document/table/index.jinja", view_object=self
        )

    def render_trace_screen(
        self, jinja_environment: JinjaEnvironment
    ) -> Markup:
        return jinja_environment.render_template_as_markup(
            "screens/document/traceability/index.jinja", view_object=self
        )

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
        nodes: List[Union[SDocDocument, SDocNode]],
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
                    template_folder = "requirement"
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

    def is_empty_tree(self) -> bool:
        return self.document_tree_iterator.is_empty_tree()

    def is_deeptrace(self) -> bool:
        return self.document_type.is_deeptrace

    def has_any_nodes(self) -> bool:
        return self.document.has_any_nodes()

    def iterator_files_first(self):
        yield from self.document_tree_iterator.iterator_files_first()

    def folder_contains_including_documents(self, folder: Folder):
        assert isinstance(folder, Folder), folder
        for file_ in folder.files:
            if not file_.has_extension(".sdoc"):
                continue
            document_ = self.get_document_by_path(file_.get_full_path())
            if not document_.document_is_included():
                return True
        return False

    def render_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_url(url))

    def render_node_link(self, node, context_document, document_type) -> str:
        assert node is not None, node
        return self.link_renderer.render_node_link(
            node, context_document, document_type
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
        if context_document is not None:
            raise NotImplementedError
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

    def table_of_contents(self):
        yield from self.document_iterator.table_of_contents()

    def document_content_iterator(self):
        yield from self.document_iterator.all_content(
            print_fragments=True,
            print_fragments_from_files=False,
        )
