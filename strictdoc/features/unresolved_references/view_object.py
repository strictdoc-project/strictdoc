from dataclasses import dataclass, field
from typing import List, Optional

from markupsafe import Markup

from strictdoc import __version__
from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode, SDocNodeField
from strictdoc.backend.sdoc.models.reference import FileReference
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    RelationMarkerType,
)
from strictdoc.core.file_system.source_tree import SourceFile
from strictdoc.core.file_traceability_index import (
    FileTraceabilityIndex,
    MissingSourceRequirementRelation,
)
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import JinjaEnvironment
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.helpers.cast import assert_cast


@dataclass
class UnresolvedReference:
    reference_type: str
    target: str
    owner: str
    owner_url: str
    context: str
    role: Optional[str]


@dataclass
class UnresolvedReferenceGroup:
    identifier: str
    title: str
    entries: List[UnresolvedReference] = field(default_factory=list)


class UnresolvedReferencesViewObject:
    def __init__(
        self,
        *,
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
    ) -> None:
        self.project_config: ProjectConfig = project_config
        self.traceability_index: TraceabilityIndex = traceability_index
        self.link_renderer: LinkRenderer = link_renderer
        self.is_running_on_server: bool = project_config.is_running_on_server
        self.strictdoc_version: str = __version__
        self.groups: List[UnresolvedReferenceGroup] = self._collect_groups()
        self.total: int = sum(len(group_.entries) for group_ in self.groups)

    def get_document_level(self) -> int:
        return 0

    def render_screen(self, jinja_environment: JinjaEnvironment) -> Markup:
        return jinja_environment.render_template_as_markup(
            "features/unresolved_references/index.jinja", view_object=self
        )

    def render_static_url(self, url: str) -> str:
        return self.link_renderer.render_static_url(url)

    def render_url(self, url: str) -> str:
        return self.link_renderer.render_url(url)

    def _collect_groups(self) -> List[UnresolvedReferenceGroup]:
        requirement_relations: UnresolvedReferenceGroup = (
            UnresolvedReferenceGroup(
                "requirement_relations", "Parent and child relations"
            )
        )
        file_relations: UnresolvedReferenceGroup = UnresolvedReferenceGroup(
            "file_relations", "File relations"
        )
        source_markers: UnresolvedReferenceGroup = UnresolvedReferenceGroup(
            "source_markers", "Source markers"
        )
        inline_links: UnresolvedReferenceGroup = UnresolvedReferenceGroup(
            "inline_links", "Inline links"
        )

        for (
            node_,
            relation_,
        ) in self.traceability_index.get_all_missing_relations():
            document: SDocDocument = assert_cast(
                node_.get_document(), SDocDocument
            )
            if isinstance(relation_, FileReference):
                group: UnresolvedReferenceGroup = file_relations
                target: str = relation_.get_posix_path()
            else:
                group = requirement_relations
                target = relation_.ref_uid
            group.entries.append(
                self._node_reference(
                    node=node_,
                    reference_type=relation_.ref_type,
                    target=target,
                    context=document.reserved_title,
                    role=relation_.role,
                )
            )

        for missing_ in self._get_missing_source_relations():
            source_path: str = (
                missing_.source_file.in_doctree_source_file_rel_path_posix
            )
            marker: RelationMarkerType = missing_.marker
            source_line: Optional[int] = marker.ng_source_line_begin
            owner: str = (
                f"{source_path}:{source_line}"
                if source_line is not None
                else source_path
            )
            owner_url: str = (
                self.link_renderer.render_source_file_link_from_root_2(
                    missing_.source_file
                )
            )
            if (
                marker.ng_range_line_begin is not None
                and marker.ng_range_line_end is not None
            ):
                owner_url += (
                    f"##{marker.ng_range_line_begin}#{marker.ng_range_line_end}"
                )
            elif source_line is not None:
                owner_url += f"#line-{source_line}"
            description: Optional[str] = marker.get_description()
            source_markers.entries.append(
                UnresolvedReference(
                    reference_type="Source marker",
                    target=missing_.requirement_uid,
                    owner=owner,
                    owner_url=owner_url,
                    context=(description if description is not None else ""),
                    role=marker.role,
                )
            )

        for (
            node_,
            link_,
        ) in self.traceability_index.get_all_unresolved_inline_links():
            document = assert_cast(node_.get_document(), SDocDocument)
            context: str = document.reserved_title
            if isinstance(link_.parent, SDocNodeField):
                context += f": {link_.parent.field_name}"
            inline_links.entries.append(
                self._node_reference(
                    node=node_,
                    reference_type="Inline link",
                    target=link_.link,
                    context=context,
                    role=None,
                )
            )

        return [
            requirement_relations,
            file_relations,
            source_markers,
            inline_links,
        ]

    def _get_missing_source_relations(
        self,
    ) -> List[MissingSourceRequirementRelation]:
        missing_relations: List[MissingSourceRequirementRelation] = []
        file_index: FileTraceabilityIndex = (
            self.traceability_index.get_file_traceability_index()
        )
        for trace_info_ in file_index.trace_infos:
            source_file: SourceFile = assert_cast(
                trace_info_.source_file, SourceFile
            )
            for marker_ in trace_info_.markers:
                if (
                    not marker_.is_begin()
                    or marker_.is_forward()
                    or marker_.ng_is_nodoc
                ):
                    continue
                for requirement_uid_ in marker_.reqs:
                    if (
                        self.traceability_index.get_node_by_uid_weak2(
                            requirement_uid_
                        )
                        is None
                    ):
                        missing_relations.append(
                            MissingSourceRequirementRelation(
                                source_file, marker_, requirement_uid_
                            )
                        )
        missing_relations.sort(
            key=lambda relation_: (
                relation_.source_file.in_doctree_source_file_rel_path_posix,
                relation_.marker.ng_source_line_begin
                if relation_.marker.ng_source_line_begin is not None
                else 0,
                relation_.marker.ng_source_column_begin
                if relation_.marker.ng_source_column_begin is not None
                else 0,
            )
        )
        return missing_relations

    def _node_reference(
        self,
        *,
        node: SDocNode,
        reference_type: str,
        target: str,
        context: str,
        role: Optional[str],
    ) -> UnresolvedReference:
        return UnresolvedReference(
            reference_type=reference_type,
            target=target,
            owner=(
                node.reserved_uid
                if node.reserved_uid is not None
                else node.get_display_title()
            ),
            owner_url=self.link_renderer.render_node_link(
                node, None, DocumentType.DOCUMENT
            ),
            context=context,
            role=role,
        )
