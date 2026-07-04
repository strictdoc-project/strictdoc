"""
@relation(SDOC-SRS-54, scope=file)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    Any,
    Generator,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

from jinja2 import Template
from markupsafe import Markup

from strictdoc import __version__
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.document_view import ViewElement
from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElement,
    GrammarElementFieldMultipleChoice,
    GrammarElementFieldSingleChoice,
    GrammarElementFieldTag,
)
from strictdoc.backend.sdoc.models.model import (
    RequirementFieldName,
    SDocDocumentIF,
    SDocElementIF,
    SDocNodeIF,
)
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.core.document_iterator import DocumentIterationContext
from strictdoc.core.document_tree import DocumentTree
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.file_system.file_tree import File, FileOrFolderEntry, Folder
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.generators.view_objects.helpers import (
    screen_should_display_file,
    screen_should_display_folder,
)
from strictdoc.export.html.html_templates import HTMLTemplates, JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import MarkupRenderer
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.file_system import file_open_read_utf8
from strictdoc.helpers.git_client import GitClient
from strictdoc.helpers.string import interpolate_at_pattern_lazy
from strictdoc.server.helpers.turbo import render_turbo_stream


class TableCellEditMode(str, Enum):
    AUTOCOMPLETE = "autocomplete"
    SINGLELINE = "singleline"
    MULTILINE = "multiline"
    READONLY = "readonly"


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
        jinja_environment: JinjaEnvironment,
        git_client: GitClient,
    ):
        self.document_type: DocumentType = document_type
        self.link_document_type: DocumentType = DocumentType.DOCUMENT
        self.document: SDocDocument = document
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self.link_renderer: LinkRenderer = link_renderer
        self.markup_renderer: MarkupRenderer = markup_renderer
        self.jinja_environment: JinjaEnvironment = jinja_environment
        self.git_client: GitClient = git_client
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
            with file_open_read_utf8(project_config.html2pdf_template) as f_:
                self.custom_html2pdf_template = Template(f_.read())

    def has_included_document(self) -> bool:
        return len(self.document.included_documents) > 0

    def render_screen(self) -> Markup:
        if self.document_type.is_document():
            if self.document.config.layout == "Website":
                return self.jinja_environment.render_template_as_markup(
                    "website/document/index.jinja", view_object=self
                )
            return self.jinja_environment.render_template_as_markup(
                "screens/document/document/index.jinja", view_object=self
            )
        elif self.document_type.is_table():
            return self.jinja_environment.render_template_as_markup(
                "screens/document/table/index.jinja", view_object=self
            )
        elif self.document_type.is_trace():
            return self.jinja_environment.render_template_as_markup(
                "features/trace/index.jinja", view_object=self
            )
        elif self.document_type.is_deeptrace():
            return self.jinja_environment.render_template_as_markup(
                "features/deep_trace/index.jinja",
                view_object=self,
            )
        elif self.document_type.is_pdf():
            return self.jinja_environment.render_template_as_markup(
                "features/html2pdf/index.jinja", view_object=self
            )
        else:
            raise NotImplementedError(self.document_type)  # pragma: no cover

    def render_updated_screen(self) -> Markup:
        output = self.jinja_environment.render_template_as_markup(
            "actions/"
            "document/"
            "create_requirement/"
            "stream_created_requirement.jinja.html",
            view_object=self,
        )

        output += self.jinja_environment.render_template_as_markup(
            "actions/document/_shared/stream_updated_toc.jinja.html",
            view_object=self,
        )

        output += self.jinja_environment.render_template_as_markup(
            "actions/document/_shared/stream_updated_viewtype_menu.jinja.html",
            view_object=self,
        )

        return output

    def render_updated_nodes_and_toc(
        self,
        nodes: Sequence[Union[SDocDocument, SDocNode]],
        node_updated: bool = False,
    ) -> str:
        output: str = ""

        if node_updated:
            # The TOC is rendered before the individual nodes intentionally:
            # toc.jinja calls table_of_contents() -> all_content(), which
            # iterates every node and writes the correct title_number_string
            # into each node's context as a side effect. The node templates
            # rendered below then read those values and display the right
            # section numbers. Reversing this order would cause nodes whose
            # level changed (e.g. a title was added or removed) to render
            # with stale numbers.
            #
            # FIXME: This is a bit hacky. A cleaner solution would be to
            # separate the calculation of title_number_string from the rendering
            # of the TOC, so that the side effect is explicit and not tied to
            # the TOC template.
            toc_content = self.jinja_environment.render_template_as_markup(
                "screens/document/_shared/toc.jinja", view_object=self
            )
            output += render_turbo_stream(
                content=toc_content,
                action="update",
                target="frame-toc",
            )

            viewtype_menu_content = (
                self.jinja_environment.render_template_as_markup(
                    "screens/document/_shared/viewtype_menu.jinja",
                    view_object=self,
                )
            )
            output += render_turbo_stream(
                content=viewtype_menu_content,
                action="update",
                target="frame-viewtype-menu",
            )

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
            content = self.jinja_environment.render_template_as_markup(
                f"components/{template_folder}/index_extends_node.jinja",
                view_object=self,
                node=node_,
            )
            output += render_turbo_stream(
                content=content,
                action="replace",
                target=f"article-{node_.reserved_mid}",
            )

        return output

    def render_update_document_content_with_moved_node(
        self, moved_node: Any
    ) -> Markup:
        content = self.jinja_environment.render_template_as_markup(
            "screens/document/document/frame_document_content.jinja.html",
            view_object=self,
        )
        output = render_turbo_stream(
            content=content,
            action="replace",
            target="frame_document_content",
        )
        toc_content = self.jinja_environment.render_template_as_markup(
            "actions/document/_shared/stream_updated_toc.jinja.html",
            view_object=self,
            last_moved_node_id=moved_node.reserved_mid,
        )
        output += render_turbo_stream(
            toc_content,
            action="update",
            target="frame-toc",
        )

        output += self.jinja_environment.render_template_as_markup(
            "actions/document/_shared/stream_updated_viewtype_menu.jinja.html",
            view_object=self,
        )

        return output

    def render_document_version(
        self, included_document: Optional[SDocDocument] = None
    ) -> Optional[str]:
        # 'document' is the main view document or an included document
        # (e.g., a bundle PDF member); defaults to the main view document.
        document_ = (
            included_document
            if included_document is not None
            else self.document
        )
        if document_.config.version is None:
            return None

        def resolver(variable_name: str) -> str:
            if variable_name == "GIT_VERSION":
                return self.git_client.get_commit_hash()
            elif variable_name == "GIT_BRANCH":
                return self.git_client.get_branch()
            return variable_name

        return interpolate_at_pattern_lazy(document_.config.version, resolver)

    def render_document_date(
        self, included_document: Optional[SDocDocument] = None
    ) -> Optional[str]:
        # 'document' is the main view document or an included document
        # (e.g., a bundle PDF member); defaults to the main view document.
        document_ = (
            included_document
            if included_document is not None
            else self.document
        )
        if document_.config.date is None:
            return None

        def resolver(variable_name: str) -> str:
            if variable_name == "GIT_COMMIT_DATE":
                return self.git_client.get_commit_date()
            elif variable_name == "GIT_COMMIT_DATETIME":
                return self.git_client.get_commit_datetime()
            return variable_name

        return interpolate_at_pattern_lazy(document_.config.date, resolver)

    def render_metadata_value(self, metadata_value: str) -> str:
        """
        FIXME: Remove duplication of Git-resolvers in this class.
        """

        def resolver(variable_name: str) -> str:
            if variable_name == "GIT_VERSION":
                return self.git_client.get_commit_hash()
            elif variable_name == "GIT_BRANCH":
                return self.git_client.get_branch()
            elif variable_name == "GIT_COMMIT_DATE":
                return self.git_client.get_commit_date()
            elif variable_name == "GIT_COMMIT_DATETIME":
                return self.git_client.get_commit_datetime()
            return variable_name

        return interpolate_at_pattern_lazy(metadata_value, resolver)

    def is_empty_tree(self) -> bool:
        return self.document_tree_iterator.is_empty_tree()

    def is_deeptrace(self) -> bool:
        return self.document_type.is_deeptrace()

    def has_any_nodes(self) -> bool:
        return self.document.has_any_nodes()

    def iterator_files_first(self) -> Iterator[FileOrFolderEntry]:
        yield from self.document_tree_iterator.iterator_files_first()

    def render_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_url(url))

    def render_node_link(self, node: SDocNode) -> str:
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

    def render_current_view_document_link(self, document: SDocDocument) -> str:
        assert isinstance(document, SDocDocument), document
        assert document.meta is not None
        assert self.document.meta is not None
        return document.meta.get_html_link(
            self.document_type,
            self.document.meta.level,
        )

    def render_static_url(self, url: str) -> Markup:
        return Markup(self.link_renderer.render_static_url(url))

    def render_local_anchor(
        self, node: Union[Anchor, SDocNode, SDocDocument]
    ) -> str:
        return self.link_renderer.render_local_anchor(node)

    def render_node_statement(self, node: SDocNode) -> Markup:
        return self.markup_renderer.render_node_statement(
            self.document_type, node
        )

    def render_truncated_node_statement(self, node: SDocNode) -> Markup:
        return self.markup_renderer.render_truncated_node_statement(
            self.document_type, node
        )

    def render_node_rationale(self, node: SDocNode) -> Markup:
        return self.markup_renderer.render_node_rationale(
            self.document_type, node
        )

    def render_node_field(self, node_field: SDocNodeField) -> Markup:
        assert isinstance(node_field, SDocNodeField), node_field
        return self.markup_renderer.render_node_field(
            self.document_type, node_field
        )

    def render_issues(
        self,
        node: Union[SDocNodeIF, SDocDocumentIF],
        field: Optional[str] = None,
    ) -> str:
        issues = self.traceability_index.validation_index.get_issues(
            node, field=field
        )
        if issues is None:
            return ""
        issues_html = ""
        for issue_ in issues:
            issue_html = self.jinja_environment.render_template_as_markup(
                "components/issue/index.jinja",
                issue=issue_,
                view_object=self,
            )
            issues_html += issue_html
        return issues_html

    def get_page_title(self) -> str:
        return self.document_type.get_page_title()

    def get_document_level(self) -> int:
        assert self.document.meta is not None
        return self.document.meta.level

    def date_today(self) -> str:
        return datetime.today().strftime("%Y-%m-%d")

    def get_document_by_path(self, full_path: str) -> SDocDocument:
        return self.traceability_index.document_tree.get_document_by_path(
            full_path
        )

    def get_grammar_elements(self) -> List[GrammarElement]:
        assert self.document.grammar is not None
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
        self, node: Union[SDocDocument, SDocNode]
    ) -> bool:
        assert isinstance(node, (SDocDocument, SDocNode)), node
        return node.reserved_uid is not None

    def get_stable_link(self, node: Union[SDocDocument, SDocNode]) -> str:
        """
        Get a stable link for a given node.

        An example of a link produced: ../../#SDOC_UG_CONTACT
        The copy_to_clipboard_controller.js consumes this link and
        transforms it into a link like: http://127.0.0.1:5111/?a=SDOC_UG_CONTACT.
        """

        assert isinstance(node, (SDocDocument, SDocNode)), node
        base_url = self.link_renderer.render_url("")
        if node.reserved_uid is not None:
            return base_url + "#" + node.reserved_uid
        if node.reserved_mid is not None and node.mid_permanent:
            return base_url + "#" + node.reserved_mid
        return base_url

    def get_html2pdf_classes(self, node: SDocNode) -> str:
        """
        Get CSS classes for html2pdf4doc for a given node.

        html2pdf4doc rules for `Narrative` requirement style:
        * If no multi-line content:
            the node is not split at all (with or without a title)
            -> add .html2pdf4doc-no-break to node.
         * ASSUMPTION:
            We assume that the number of single-line strings is no greater
            than the height of the page
        """

        assert isinstance(node, SDocNode), node

        html2pdf4doc_classes = []

        if (
            node.node_type
            in self.project_config.html2pdf_forced_page_break_nodes
        ):
            html2pdf4doc_classes.append("sdoc-html2pdf4doc-break-before")

        if not node.has_multiline_fields():
            if node.get_requirement_style_mode() == "narrative":
                html2pdf4doc_classes.append("html2pdf4doc-no-break")

            # The section that does not break away from its children.
            if node.has_child_nodes():
                html2pdf4doc_classes.append("html2pdf4doc-no-hanging")

        return " ".join(html2pdf4doc_classes)

    #
    # Document Level Actions
    #

    def can_edit_document(self, document: SDocDocument) -> bool:
        """
        Determines if the document's root configuration (title, metadata) can be edited.
        """
        return self.traceability_index.can_edit_document(document)

    #
    # Node Level Actions
    #

    def can_edit_node(self, node: Union[SDocDocument, SDocNode]) -> bool:
        return self.traceability_index.can_edit_node(node)

    def can_delete_node(self, node: Union[SDocDocument, SDocNode]) -> bool:
        return self.traceability_index.can_delete_node(node)

    def can_clone_node(self, node: Union[SDocDocument, SDocNode]) -> bool:
        return self.traceability_index.can_clone_node(node)

    def can_add_node(self, node: Union[SDocDocument, SDocNode]) -> bool:
        return self.traceability_index.can_add_node(node)

    def can_insert_next_to_node(
        self, node: Union[SDocDocument, SDocNode]
    ) -> bool:
        return self.traceability_index.can_insert_next_to_node(node)

    def get_table_first_editable_field_name(
        self, element_type: str
    ) -> Optional[str]:
        grammar = self.document.grammar
        if grammar is None:
            return None
        element = grammar.elements_by_type.get(element_type)
        if element is None:
            return None
        preferred_fields = (
            "TITLE",
            "STATEMENT",
            "RATIONALE",
            "DESCRIPTION",
            "CONTENT",
            "COMMENT",
        )
        for field_name in preferred_fields:
            if (
                field_name in element.field_titles
                and self.is_table_cell_editable(element_type, field_name)
            ):
                return field_name
        for field_name in element.field_titles:
            if field_name in ("UID", "MID", "LEVEL", "STATUS", "TAGS"):
                continue
            if self.is_table_cell_editable(element_type, field_name):
                return field_name
        for field_name in element.field_titles:
            if self.is_table_cell_editable(element_type, field_name):
                return field_name
        return None

    def can_move_node(self, node: Union[SDocDocument, SDocNode]) -> bool:
        return self.traceability_index.can_move_node(node)

    # Table editing
    #

    def get_table_cell_edit_mode(
        self, element_type: str, field_name: str
    ) -> TableCellEditMode:
        """
        Returns the editing mode for a table cell:
          AUTOCOMPLETE — SingleChoice / MultipleChoice / Tag field
          SINGLELINE   — single-line STRING field (meta fields)
          MULTILINE    — multi-line STRING field (STATEMENT, RATIONALE, COMMENT, custom content)
          READONLY     — field not declared in grammar for this element type
        """
        grammar = self.document.grammar
        if grammar is None:
            return TableCellEditMode.READONLY
        element = grammar.elements_by_type.get(element_type)
        if element is None:
            return TableCellEditMode.READONLY
        field = element.fields_map.get(field_name)
        if field is None:
            return TableCellEditMode.READONLY
        if isinstance(
            field,
            (
                GrammarElementFieldSingleChoice,
                GrammarElementFieldMultipleChoice,
                GrammarElementFieldTag,
            ),
        ):
            return TableCellEditMode.AUTOCOMPLETE
        if element.is_field_multiline(field_name):
            return TableCellEditMode.MULTILINE
        return TableCellEditMode.SINGLELINE

    def is_table_cell_editable(
        self, element_type: str, field_name: str
    ) -> bool:
        """Returns True if the field is declared in grammar and can be edited on TABLE screen."""
        return (
            self.get_table_cell_edit_mode(element_type, field_name)
            != TableCellEditMode.READONLY
        )

    def is_table_cell_multiple_choice(
        self, element_type: str, field_name: str
    ) -> bool:
        grammar = self.document.grammar
        if grammar is None:
            return False
        element = grammar.elements_by_type.get(element_type)
        if element is None:
            return False
        field = element.fields_map.get(field_name)
        if field is None:
            return False
        return isinstance(
            field,
            (GrammarElementFieldMultipleChoice, GrammarElementFieldTag),
        )

    def enumerate_table_columns(self) -> Generator[str, None, None]:
        """
        Yields column identifiers for the TABLE screen in display order.

        Only yields columns that exist in at least one grammar element.
        Column order:
          1. Non-reserved meta fields (before TITLE/STATEMENT)
          2. RELATIONS  — if any grammar element has relations
          3. TITLE      — if any grammar element has TITLE
          4. STATEMENT  — if any grammar element has STATEMENT
          5. RATIONALE  — if any grammar element has RATIONALE
          6. COMMENT    — if any grammar element has COMMENT
          7. Non-reserved content fields (after TITLE/STATEMENT)

        TYPE and LEVEL are not yielded — they are always present and
        rendered as fixed first columns in the template.
        """
        assert self.document.grammar is not None
        assert self.document.grammar.elements is not None
        seen: Set[str] = set()

        for element in self.document.grammar.elements:
            for title in element.enumerate_table_meta_field_titles():
                if title not in seen:
                    seen.add(title)
                    yield title

        if any(element.relations for element in self.document.grammar.elements):
            yield "RELATIONS"

        for name in (
            RequirementFieldName.TITLE,
            RequirementFieldName.STATEMENT,
            RequirementFieldName.RATIONALE,
            RequirementFieldName.COMMENT,
        ):
            if any(
                name in element.fields_map
                for element in self.document.grammar.elements
            ):
                yield name

        for element in self.document.grammar.elements:
            for (
                title
            ) in element.enumerate_table_non_reserved_content_field_titles():
                if title not in seen:
                    seen.add(title)
                    yield title

    @staticmethod
    def create_for_table_screen(
        document: SDocDocument,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
        html_templates: HTMLTemplates,
        git_client: GitClient,
        jinja_environment: JinjaEnvironment,
    ) -> "DocumentScreenViewObject":
        assert document.meta is not None
        link_renderer = LinkRenderer(
            root_path=document.meta.get_root_path_prefix(),
            static_path=project_config.dir_for_sdoc_assets,
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
            document_type=DocumentType.TABLE,
            document=document,
            traceability_index=traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            markup_renderer=markup_renderer,
            jinja_environment=jinja_environment,
            git_client=git_client,
        )
