# mypy: disable-error-code="no-any-return,no-redef,no-untyped-call,no-untyped-def,union-attr"
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Union

from jinja2 import Environment, Template

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

    def render_screen(self, jinja_environment: Environment):
        if self.document_type.is_document:
            if self.document.config.layout == "Website":
                template = jinja_environment.get_template(
                    "website/document/index.jinja"
                )
            else:
                template = jinja_environment.get_template(
                    "screens/document/document/index.jinja"
                )
        elif self.document_type.is_table():
            template = jinja_environment.get_template(
                "screens/document/table/index.jinja"
            )
        elif self.document_type.is_trace():
            template = jinja_environment.get_template(
                "screens/document/traceability/index.jinja"
            )
        elif self.document_type.is_deeptrace:
            template = jinja_environment.get_template(
                "screens/document/traceability_deep/index.jinja"
            )
        elif self.document_type.is_pdf():
            template = jinja_environment.get_template(
                "screens/document/pdf/index.jinja"
            )
        else:
            raise NotImplementedError(self.document_type)
        return template.render(view_object=self)

    def render_table_screen(self, jinja_environment: Environment):
        template = jinja_environment.get_template(
            "screens/document/table/index.jinja"
        )
        return template.render(view_object=self)

    def render_trace_screen(self, jinja_environment: Environment):
        template = jinja_environment.get_template(
            "screens/document/traceability/index.jinja"
        )
        return template.render(view_object=self)

    def render_updated_screen(self, jinja_environment: Environment) -> str:
        template = jinja_environment.get_template(
            "actions/"
            "document/"
            "create_requirement/"
            "stream_created_requirement.jinja.html"
        )
        output = template.render(view_object=self)

        toc_template = jinja_environment.get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        output += toc_template.render(view_object=self)

        return output

    def render_updated_nodes_and_toc(
        self,
        nodes: List[Union[SDocDocument, SDocNode]],
        jinja_environment: Environment,
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
            template = jinja_environment.get_template(
                f"components/{template_folder}/index_extends_node.jinja"
            )
            output += render_turbo_stream(
                content=template.render(view_object=self, node=node_),
                action="replace",
                target=f"article-{node_.reserved_mid}",
            )

        toc_template = jinja_environment.get_template(
            "screens/document/_shared/toc.jinja"
        )
        output += render_turbo_stream(
            content=toc_template.render(view_object=self),
            action="update",
            target="frame-toc",
        )

        return output

    def render_update_document_content_with_moved_node(
        self, jinja_environment: Environment, moved_node
    ) -> str:
        template = jinja_environment.get_template(
            "screens/document/document/frame_document_content.jinja.html"
        )
        output = render_turbo_stream(
            content=template.render(view_object=self),
            action="replace",
            target="frame_document_content",
        )
        toc_template = jinja_environment.get_template(
            "actions/document/_shared/stream_updated_toc.jinja.html"
        )
        output += render_turbo_stream(
            toc_template.render(
                view_object=self,
                last_moved_node_id=moved_node.reserved_mid,
            ),
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

    def render_url(self, url: str):
        return self.link_renderer.render_url(url)

    def render_node_link(self, incoming_link, document, document_type):
        assert incoming_link is not None, incoming_link
        return self.link_renderer.render_node_link(
            incoming_link, document, document_type
        )

    def render_static_url(self, url: str):
        return self.link_renderer.render_static_url(url)

    def render_local_anchor(self, node):
        return self.link_renderer.render_local_anchor(node)

    def render_free_text(self, document_type, free_text):
        return self.markup_renderer.render_free_text(document_type, free_text)

    def render_node_statement(self, node):
        return self.markup_renderer.render_node_statement(
            self.document_type, node
        )

    def render_truncated_node_statement(self, node):
        return self.markup_renderer.render_truncated_node_statement(
            self.document_type, node
        )

    def render_node_rationale(self, node):
        return self.markup_renderer.render_node_rationale(
            self.document_type, node
        )

    def render_node_field(self, node_field: SDocNodeField):
        assert isinstance(node_field, SDocNodeField), node_field
        return self.markup_renderer.render_node_field(
            self.document_type, node_field
        )

    def get_page_title(self):
        return self.document_type.get_page_title()

    def date_today(self):
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
