"""
@relation(SDOC-SRS-36, scope=file)

Plain data for SourceFileViewObject.

A source file page shows document nodes: banners in the source code view and
node entries in the aside. The node templates read these nodes through
SDocNode methods and through the traceability index. The classes in this
module hold the same values as plain data:

- SourceFileViewDataCollector runs in the main process. It reads the
  traceability index and creates NodeData records. It renders no HTML.
- NodeData and the other data classes hold no reference to SDocNode objects
  or to the traceability index, so a SourceFileViewObject is small when
  pickled and can be rendered in a worker process.
- SourceFileDataLinkRenderer, SourceFileDataIndex, and FieldDataRenderer let
  the shared node templates render NodeData: they answer the link renderer,
  traceability index, and markup renderer calls of the templates from the
  data.

The method names of NodeData match the SDocNode methods that the node
templates call, so the same templates render both.
"""

from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
    cast,
)

from markupsafe import Markup

from strictdoc.backend.markdown.markdown_to_html_fragment_writer import (
    MarkdownToHtmlFragmentWriter,
)
from strictdoc.backend.rst.rst_inline_link_placeholders import (
    RstInlineLinkPlaceholders,
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
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.file_system.source_tree import SourceFile
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import (
    HTMLTemplates,
    JinjaEnvironment,
)
from strictdoc.export.html.renderers.html_fragment_writer import (
    HTMLFragmentWriter,
)
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.export.html.renderers.markup_renderer import (
    FragmentWriterType,
    MarkupRenderer,
    flatten_html_block_for_markdown,
)
from strictdoc.export.html.renderers.text_to_html_writer import TextToHtmlWriter
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.mid import MID

#
# Data classes.
#


@dataclass
class InlineLinkData:
    """An inline link in a node field, resolved in the main process."""

    title: str
    href: str
    with_icon: bool
    # The length of the link in the source text. RstInlineLinkPlaceholders
    # needs it.
    source_length: int


@dataclass
class AnchorLinkSourceData:
    """The node that contains an inline link to an anchor."""

    display_title: str
    # The link from the document of the anchor to this node.
    href: str

    def get_display_title(self) -> str:
        return self.display_title


@dataclass
class AnchorIncomingLinkData:
    source: AnchorLinkSourceData

    def parent_node(self) -> AnchorLinkSourceData:
        return self.source


@dataclass
class AnchorData:
    """An anchor in a node field."""

    local_anchor: str
    # None if no node links to the anchor, like
    # TraceabilityIndex.get_incoming_links().
    incoming_links: Optional[List[AnchorIncomingLinkData]]

    def get_parent_or_including_document(self) -> None:
        # The anchor templates pass the document to
        # LinkRenderer.render_node_link(). SourceFileDataLinkRenderer reads
        # the link from AnchorLinkSourceData instead and ignores it.
        return None


FieldPart = Union[str, InlineLinkData, AnchorData]


@dataclass
class FieldData:
    field_name: str
    text_value: str
    parts: List[FieldPart]
    # The class name of the fragment writer that MarkupRenderer chooses for
    # this field, for example "RstToHtmlFragmentWriter".
    writer_kind: str
    # The template that MarkupRenderer uses for the anchors in this field.
    anchor_template: str

    def get_text_value(self) -> str:
        return self.text_value


@dataclass
class MarkerData:
    """A marker of a file relation of a node."""

    ng_range_line_begin: Optional[int]
    ng_range_line_end: Optional[int]
    is_range: bool
    is_line: bool
    description: Optional[str]
    role: Optional[str]

    def is_range_marker(self) -> bool:
        return self.is_range

    def is_line_marker(self) -> bool:
        return self.is_line

    def get_description(self) -> Optional[str]:
        return self.description


@dataclass
class NodeContextData:
    title_number_string: Optional[str]
    ng_level: Optional[int]


@dataclass
class NodeLinkData:
    """
    The values of a node that a link to the node needs. Relations and
    incoming links use this class. NodeData extends it.
    """

    reserved_mid: str
    reserved_uid: Optional[str]
    reserved_title: Optional[str]
    display_title: str
    local_anchor: str
    # The link to the node from a source file page, by the folder depth of
    # the page. The collector adds the depth of each page that shows the
    # node.
    links_from_source_file_level: Dict[int, str] = field(default_factory=dict)

    def get_display_title(self) -> str:
        return self.display_title


@dataclass
class NodeIncomingLinkData:
    """An inline link in another node that points to a node."""

    source: NodeLinkData

    def parent_node(self) -> NodeLinkData:
        return self.source


@dataclass
class RelationData:
    node: NodeLinkData
    role: Optional[str]
    display_role: Optional[str]


@dataclass
class MetaFieldData:
    human_title: str
    field: FieldData
    is_single_line: bool


@dataclass
class NodeData(NodeLinkData):
    """
    The values that the node templates read from an SDocNode and from the
    traceability index.

    Some values exist only if the node has a field. The templates read them
    only under this condition. For example, they read the statement only if
    has_reserved_statement() is true. The collector reads these values only
    under the same conditions, because SDocNode raises an exception for a
    missing field.
    """

    node_type: str = ""
    reserved_status: Optional[str] = None
    rationale: Optional[str] = None
    has_meta: bool = False
    is_composite: bool = False
    context: NodeContextData = field(
        default_factory=lambda: NodeContextData(None, None)
    )
    type_string: str = ""
    node_type_string: Optional[str] = None
    is_content_node_value: bool = False
    requirement_style_mode: str = ""
    has_multiline_fields_value: bool = False
    has_reserved_statement_value: bool = False
    # Only if has_reserved_statement() is true.
    content_field_name: Optional[str] = None
    field_human_title_for_statement: Optional[str] = None
    content_field: Optional[FieldData] = None
    # Only if the node has a rationale.
    rationale_field: Optional[FieldData] = None
    comment_fields: List[FieldData] = field(default_factory=list)
    # Only if has_meta is true.
    meta_fields: List[MetaFieldData] = field(default_factory=list)
    # The human titles of the COMMENT and RATIONALE fields, if the node has
    # these fields.
    field_human_titles: Dict[str, str] = field(default_factory=dict)
    has_parent_requirements: bool = False
    has_children_requirements: bool = False
    parents: List[RelationData] = field(default_factory=list)
    children: List[RelationData] = field(default_factory=list)
    file_links: List[Tuple[str, List[MarkerData]]] = field(default_factory=list)
    # None if no other node links to this node, like
    # TraceabilityIndex.get_incoming_links().
    incoming_links: Optional[List[NodeIncomingLinkData]] = None

    #
    # The SDocNode methods that the node templates call.
    #

    def get_type_string(self) -> str:
        return self.type_string

    def get_node_type_string(self) -> Optional[str]:
        return self.node_type_string

    def is_content_node(self) -> bool:
        return self.is_content_node_value

    def get_requirement_style_mode(self) -> str:
        return self.requirement_style_mode

    def has_multiline_fields(self) -> bool:
        return self.has_multiline_fields_value

    def has_reserved_statement(self) -> bool:
        return self.has_reserved_statement_value

    def get_content_field_name(self) -> str:
        return assert_cast(self.content_field_name, str)

    def get_field_human_title(self, field_name: str) -> str:
        return self.field_human_titles[field_name]

    def get_field_human_title_for_statement(self) -> str:
        return assert_cast(self.field_human_title_for_statement, str)

    def get_comment_fields(self) -> List[FieldData]:
        return self.comment_fields

    def enumerate_meta_fields(
        self, skip_single_lines: bool = False, skip_multi_lines: bool = False
    ) -> Iterator[Tuple[str, FieldData]]:
        for meta_field_ in self.meta_fields:
            if meta_field_.is_single_line and skip_single_lines:
                continue
            if (not meta_field_.is_single_line) and skip_multi_lines:
                continue
            yield meta_field_.human_title, meta_field_.field


#
# Main process: collect the data.
#


class SourceFileViewDataCollector:
    """
    Creates NodeData from the traceability index.

    Use cases: static export and server. In the static export, one collector
    serves all source file pages, so the data of a node is created once. The
    server creates one collector for each page that it renders.
    """

    def __init__(
        self,
        *,
        traceability_index: TraceabilityIndex,
        project_config: ProjectConfig,
        html_templates: HTMLTemplates,
    ) -> None:
        self.traceability_index: TraceabilityIndex = traceability_index
        self.project_config: ProjectConfig = project_config
        self._nodes: Dict[str, NodeData] = {}
        self._link_nodes: Dict[str, NodeLinkData] = {}
        # The links that this module creates do not depend on the root path
        # of a page: render_requirement_link_from_source_file() uses only
        # the folder depth of the source file, and render_node_link() and
        # render_local_anchor() do not use the root path.
        self._link_renderer = LinkRenderer(
            root_path="", static_path=project_config.dir_for_sdoc_assets
        )
        # The two markup renderers that a source file page uses. The
        # collector only asks them which fragment writer and which anchor
        # template a field gets. It renders nothing with them.
        self._rst_renderer, self._text_renderer = (
            MarkupRenderer.create(
                markup=markup_,
                traceability_index=traceability_index,
                link_renderer=self._link_renderer,
                html_templates=html_templates,
                config=project_config,
                context_document=None,
            )
            for markup_ in (SDocMarkup.RST, SDocMarkup.TEXT)
        )

    def get_source_file_node_uids(self, source_file: SourceFile) -> List[str]:
        """The nodes of the "Nodes" tab of the aside."""
        nodes = self.traceability_index.get_source_file_reqs(
            source_file.in_doctree_source_file_rel_path_posix
        )
        return [assert_cast(node_.reserved_uid, str) for node_ in nodes or []]

    def collect_nodes(
        self,
        *,
        source_file: SourceFile,
        trace_info: SourceFileTraceabilityInfo,
        node_uids: List[str],
    ) -> Dict[str, NodeData]:
        """
        Return the data of all nodes that a source file page shows: the nodes
        of the aside and the nodes of all markers in the file.
        """
        page_uids: List[str] = list(node_uids)
        for marker_ in trace_info.markers:
            page_uids.extend(req_.uid for req_ in marker_.reqs_objs)
            page_uids.extend(marker_.reqs)

        nodes: Dict[str, NodeData] = {}
        for uid_ in page_uids:
            if uid_ in nodes:
                continue
            node_data = self._get_node_data(uid_)
            self._add_link_for_level(node_data, source_file)
            for relation_ in node_data.parents + node_data.children:
                self._add_link_for_level(relation_.node, source_file)
            for incoming_link_ in node_data.incoming_links or []:
                self._add_link_for_level(incoming_link_.source, source_file)
            nodes[uid_] = node_data
        return nodes

    def _add_link_for_level(
        self, node_data: NodeLinkData, source_file: SourceFile
    ) -> None:
        if source_file.level in node_data.links_from_source_file_level:
            return
        node = self.traceability_index.get_node_by_mid(
            MID(node_data.reserved_mid)
        )
        node_data.links_from_source_file_level[source_file.level] = (
            self._link_renderer.render_requirement_link_from_source_file(
                node, source_file
            )
        )

    def _get_link_node(self, node: SDocNode) -> NodeLinkData:
        mid = str(node.reserved_mid)
        link_node = self._link_nodes.get(mid)
        if link_node is None:
            link_node = NodeLinkData(
                reserved_mid=mid,
                reserved_uid=node.reserved_uid,
                reserved_title=node.reserved_title,
                display_title=node.get_display_title(),
                local_anchor=self._link_renderer.render_local_anchor(node),
            )
            self._link_nodes[mid] = link_node
        return link_node

    def _get_node_data(self, uid: str) -> NodeData:
        node_data = self._nodes.get(uid)
        if node_data is not None:
            return node_data

        ti = self.traceability_index
        node: SDocNode = ti.get_node_by_uid(uid)

        # The templates read the statement, the rationale, and the meta fields
        # only if the node has them. SDocNode raises an exception for a
        # missing field, so these values are read under the same conditions.
        has_reserved_statement = node.has_reserved_statement()
        has_rationale = node.rationale is not None
        comment_fields = [
            self._get_field_data(field_) for field_ in node.get_comment_fields()
        ]
        field_human_titles: Dict[str, str] = {}
        if len(comment_fields) > 0:
            field_human_titles[RequirementFieldName.COMMENT] = (
                node.get_field_human_title(RequirementFieldName.COMMENT)
            )
        if has_rationale:
            field_human_titles[RequirementFieldName.RATIONALE] = (
                node.get_field_human_title(RequirementFieldName.RATIONALE)
            )

        node_data = NodeData(
            reserved_mid=str(node.reserved_mid),
            reserved_uid=node.reserved_uid,
            reserved_title=node.reserved_title,
            display_title=node.get_display_title(),
            local_anchor=self._link_renderer.render_local_anchor(node),
            node_type=node.node_type,
            reserved_status=node.reserved_status,
            rationale=node.rationale,
            has_meta=node.has_meta,
            is_composite=node.is_composite,
            context=NodeContextData(
                title_number_string=node.context.title_number_string,
                ng_level=node.context.ng_level,
            ),
            type_string=node.get_type_string(),
            node_type_string=node.get_node_type_string(),
            is_content_node_value=node.is_content_node(),
            requirement_style_mode=node.get_requirement_style_mode(),
            has_multiline_fields_value=node.has_multiline_fields(),
            has_reserved_statement_value=has_reserved_statement,
            content_field_name=(
                node.get_content_field_name()
                if has_reserved_statement
                else None
            ),
            field_human_title_for_statement=(
                node.get_field_human_title_for_statement()
                if has_reserved_statement
                else None
            ),
            content_field=(
                self._get_field_data(node.get_content_field())
                if has_reserved_statement
                else None
            ),
            rationale_field=(
                self._get_field_data(
                    node.get_field_by_name(RequirementFieldName.RATIONALE)
                )
                if has_rationale
                else None
            ),
            comment_fields=comment_fields,
            meta_fields=self._get_meta_fields(node) if node.has_meta else [],
            field_human_titles=field_human_titles,
            has_parent_requirements=ti.has_parent_requirements(node),
            has_children_requirements=ti.has_children_requirements(node),
            parents=[
                RelationData(
                    node=self._get_link_node(parent_),
                    role=role_,
                    display_role=ti.get_display_role_for_parent_relation(
                        node, parent_, role_
                    ),
                )
                for parent_, role_ in ti.get_parent_relations_with_roles(node)
            ],
            children=[
                RelationData(
                    node=self._get_link_node(child_),
                    role=role_,
                    display_role=ti.get_display_role_for_child_relation(
                        node, child_, role_
                    ),
                )
                for child_, role_ in ti.get_child_relations_with_roles(node)
            ],
            file_links=self._get_file_links(node),
            incoming_links=self._get_node_incoming_links(node),
        )
        self._nodes[uid] = node_data
        return node_data

    def _get_meta_fields(self, node: SDocNode) -> List[MetaFieldData]:
        single_line_fields = {
            id(field_)
            for _, field_ in node.enumerate_meta_fields(skip_multi_lines=True)
        }
        return [
            MetaFieldData(
                human_title=human_title_,
                field=self._get_field_data(field_),
                is_single_line=id(field_) in single_line_fields,
            )
            for human_title_, field_ in node.enumerate_meta_fields()
        ]

    def _get_file_links(
        self, node: SDocNode
    ) -> List[Tuple[str, List[MarkerData]]]:
        return [
            (
                path_,
                [
                    MarkerData(
                        ng_range_line_begin=marker_.ng_range_line_begin,
                        ng_range_line_end=marker_.ng_range_line_end,
                        is_range=marker_.is_range_marker(),
                        is_line=marker_.is_line_marker(),
                        description=marker_.get_description(),
                        role=marker_.role,
                    )
                    for marker_ in markers_ or []
                ],
            )
            for path_, markers_ in self.traceability_index.get_requirement_file_links(
                node
            )
        ]

    def _get_node_incoming_links(
        self, node: SDocNode
    ) -> Optional[List[NodeIncomingLinkData]]:
        incoming_links = self.traceability_index.get_incoming_links(node)
        if incoming_links is None:
            return None
        return [
            NodeIncomingLinkData(
                source=self._get_link_node(link_.parent_node())
            )
            for link_ in incoming_links
        ]

    def _get_node_renderer(self, node: SDocNode) -> MarkupRenderer:
        """
        The same choice as the earlier SourceFileViewObject.get_node_renderer().
        """
        parent_doc = node.get_parent_or_including_document()
        parent_doc_config = parent_doc.config
        if parent_doc_config.markup is SDocMarkup.RST:
            return self._rst_renderer
        return self._text_renderer

    def _get_field_data(self, node_field: SDocNodeField) -> FieldData:
        renderer = (
            self._get_node_renderer(node_field.parent)
            if node_field.parent is not None
            else self._rst_renderer
        )
        writer = renderer._get_writer_for_node_field(node_field)  # noqa: SLF001
        anchor_template = (
            "markup/anchor.jinja"
            if isinstance(
                renderer.fragment_writer,
                (MarkdownToHtmlFragmentWriter, HTMLFragmentWriter),
            )
            else "rst/anchor.jinja"
        )
        parts: List[FieldPart] = []
        for part_ in node_field.parts:
            if isinstance(part_, str):
                parts.append(part_)
            elif isinstance(part_, InlineLink):
                linkable_node = (
                    self.traceability_index.get_linkable_node_by_uid(part_.link)
                )
                parts.append(
                    InlineLinkData(
                        title=(
                            part_.title
                            if part_.title is not None
                            else linkable_node.get_display_title()
                        ),
                        # MarkupRenderer renders inline links without a
                        # context document, so the link does not depend on
                        # the page.
                        href=self._link_renderer.render_node_link(
                            linkable_node, None, DocumentType.DOCUMENT
                        ),
                        with_icon=part_.title is None,
                        source_length=len(part_.get_source_value()),
                    )
                )
            elif isinstance(part_, Anchor):
                parts.append(self._get_anchor_data(part_))
            else:
                raise NotImplementedError(part_)
        return FieldData(
            field_name=node_field.field_name,
            text_value=node_field.get_text_value(),
            parts=parts,
            writer_kind=type(writer).__name__,
            anchor_template=anchor_template,
        )

    def _get_anchor_data(self, anchor: Anchor) -> AnchorData:
        incoming_links = self.traceability_index.get_incoming_links(anchor)
        return AnchorData(
            local_anchor=self._link_renderer.render_local_anchor(anchor),
            incoming_links=(
                [
                    AnchorIncomingLinkData(
                        source=AnchorLinkSourceData(
                            display_title=(
                                link_.parent_node().get_display_title()
                            ),
                            href=self._link_renderer.render_node_link(
                                link_.parent_node(),
                                # The anchor templates pass the same object.
                                cast(
                                    Optional[SDocDocument],
                                    anchor.get_parent_or_including_document(),
                                ),
                                DocumentType.DOCUMENT,
                            ),
                        )
                    )
                    for link_ in incoming_links
                ]
                if incoming_links is not None
                else None
            ),
        )


#
# Rendering: let the shared node templates render the data.
#


class SourceFileDataLinkRenderer(LinkRenderer):
    """
    A LinkRenderer for the data classes of a source file page.

    The shared node templates call LinkRenderer methods with a node. Four of
    these methods need an SDocNode, SDocDocument, or Anchor object: they
    check the type of the node or read its document. This class overrides
    these four methods and returns the links that SourceFileViewDataCollector
    created with a LinkRenderer in the main process. All other methods, for
    example render_url() and render_marker_range_link(), only combine paths
    and are inherited unchanged.
    """

    def render_local_anchor(self, node: Any) -> str:
        if isinstance(node, (NodeLinkData, AnchorData)):
            return node.local_anchor
        return super().render_local_anchor(node)

    def render_node_link(
        self,
        node: Any,
        context_document: Any,  # noqa: ARG002
        document_type: DocumentType,  # noqa: ARG002
        allow_local: bool = True,  # noqa: ARG002
    ) -> str:
        # Only the anchor templates call this method on a source file page.
        assert isinstance(node, AnchorLinkSourceData), node
        return node.href

    def render_requirement_link_from_source_file(
        self, node: Any, source_file: SourceFile
    ) -> str:
        assert isinstance(node, NodeLinkData), node
        return node.links_from_source_file_level[source_file.level]

    def render_source_file_link(
        self,
        requirement: Any,  # noqa: ARG002
        requirement_source_path: str,
    ) -> str:
        source_file_link = f"_source_files/{requirement_source_path}.html"
        if len(self.root_path) == 0:
            return source_file_link
        return f"{self.root_path}/{source_file_link}"


class SourceFileDataIndex:
    """
    Answers the traceability index calls of the node templates from the
    data classes.
    """

    @staticmethod
    def get_requirement_file_links(
        node: NodeData,
    ) -> List[Tuple[str, List[MarkerData]]]:
        return node.file_links

    @staticmethod
    def get_incoming_links(
        node: Union[NodeData, AnchorData],
    ) -> Optional[List[Any]]:
        return node.incoming_links

    @staticmethod
    def has_parent_requirements(node: NodeData) -> bool:
        return node.has_parent_requirements

    @staticmethod
    def has_children_requirements(node: NodeData) -> bool:
        return node.has_children_requirements

    @staticmethod
    def get_parent_relations_with_roles(
        node: NodeData,
    ) -> List[Tuple[NodeLinkData, Optional[str]]]:
        return [(relation_.node, relation_.role) for relation_ in node.parents]

    @staticmethod
    def get_child_relations_with_roles(
        node: NodeData,
    ) -> List[Tuple[NodeLinkData, Optional[str]]]:
        return [(relation_.node, relation_.role) for relation_ in node.children]

    @staticmethod
    def _get_display_role(
        relations: List[RelationData],
        related_node: NodeLinkData,
        role: Optional[str],
    ) -> Optional[str]:
        for relation_ in relations:
            if relation_.node is related_node and relation_.role == role:
                return relation_.display_role
        raise AssertionError(
            f"No relation to {related_node.reserved_mid} with role {role}."
        )

    @staticmethod
    def get_display_role_for_parent_relation(
        node: NodeData, parent: NodeLinkData, role: Optional[str]
    ) -> Optional[str]:
        return SourceFileDataIndex._get_display_role(node.parents, parent, role)

    @staticmethod
    def get_display_role_for_child_relation(
        node: NodeData, child: NodeLinkData, role: Optional[str]
    ) -> Optional[str]:
        return SourceFileDataIndex._get_display_role(node.children, child, role)


class FieldDataRenderer:
    """
    Renders FieldData to HTML with the same steps as
    MarkupRenderer.render_node_field(). One FieldDataRenderer serves one
    page, like the two MarkupRenderers of the earlier SourceFileViewObject.
    """

    def __init__(
        self,
        *,
        project_config: ProjectConfig,
        jinja_environment: JinjaEnvironment,
        link_renderer: SourceFileDataLinkRenderer,
    ) -> None:
        self.project_config: ProjectConfig = project_config
        self.jinja_environment: JinjaEnvironment = jinja_environment
        self.link_renderer: SourceFileDataLinkRenderer = link_renderer
        self._writers: Dict[str, FragmentWriterType] = {}
        self._cache: Dict[int, Markup] = {}

    def _get_writer(self, writer_kind: str) -> FragmentWriterType:
        writer = self._writers.get(writer_kind)
        if writer is not None:
            return writer
        # The same arguments as MarkupRenderer.create() and
        # MarkupRenderer._get_writer_for_node_field() on a source file page.
        if writer_kind == RstToHtmlFragmentWriter.__name__:
            writer = RstToHtmlFragmentWriter(
                project_config=self.project_config,
                context_document=None,
                flat_assets=False,
                reference_path_override=None,
            )
        elif writer_kind == MarkdownToHtmlFragmentWriter.__name__:
            writer = MarkdownToHtmlFragmentWriter(flat_assets=False)
        elif writer_kind == HTMLFragmentWriter.__name__:
            writer = HTMLFragmentWriter()
        elif writer_kind == TextToHtmlWriter.__name__:
            writer = TextToHtmlWriter()
        else:
            raise NotImplementedError(writer_kind)
        self._writers[writer_kind] = writer
        return writer

    def render(self, field_data: FieldData) -> Markup:
        cached = self._cache.get(id(field_data))
        if cached is not None:
            return cached

        writer = self._get_writer(field_data.writer_kind)
        link_placeholders: Optional[RstInlineLinkPlaceholders] = None
        if isinstance(writer, RstToHtmlFragmentWriter):
            link_placeholders = RstInlineLinkPlaceholders(
                [part_ for part_ in field_data.parts if isinstance(part_, str)]
            )

        parts_output = ""
        for part_index, part in enumerate(field_data.parts):
            if isinstance(part, str):
                parts_output += part
            elif isinstance(part, InlineLinkData):
                if link_placeholders is not None:
                    next_part = (
                        field_data.parts[part_index + 1]
                        if part_index + 1 < len(field_data.parts)
                        else None
                    )
                    parts_output += link_placeholders.create_placeholder(
                        source_length=part.source_length,
                        link_html=HTMLFragmentWriter.write_anchor_link(
                            part.title, part.href, with_icon=part.with_icon
                        ),
                        text_after=(
                            next_part if isinstance(next_part, str) else ""
                        ),
                    )
                else:
                    parts_output += writer.write_anchor_link(
                        part.title, part.href, with_icon=part.with_icon
                    )
            elif isinstance(part, AnchorData):
                anchor_html = self.jinja_environment.get_template(
                    field_data.anchor_template
                ).render(
                    anchor=part,
                    traceability_index=SourceFileDataIndex(),
                    link_renderer=self.link_renderer,
                    document_type=DocumentType.DOCUMENT,
                )
                if isinstance(writer, MarkdownToHtmlFragmentWriter):
                    anchor_html = flatten_html_block_for_markdown(anchor_html)
                parts_output += anchor_html
            else:
                raise NotImplementedError(part)

        output = writer.write(parts_output)
        if link_placeholders is not None:
            # Markup.replace() would escape the link HTML, so the
            # placeholders are replaced in a plain string.
            output = Markup(link_placeholders.replace_placeholders(str(output)))
        self._cache[id(field_data)] = output
        return output
