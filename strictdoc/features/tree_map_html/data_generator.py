"""
Build tree map data from StrictDoc documents and traceability information.

@relation(SDOC-SRS-157, scope=file)
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Dict, List, Set, Tuple, Union

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.document_iterator import SDocDocumentIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.features.tree_map_html.models import (
    TreeMap,
    TreeMapData,
    TreeMapNode,
)


def _get_coverage_color(ratio: float) -> str:
    assert 0 <= ratio <= 1

    if ratio < 0.5:
        red = 0xFF
        green = int(0xAA + (0xFF - 0xAA) * (ratio / 0.5))
    else:
        red = int(0xFF + (0xAA - 0xFF) * ((ratio - 0.5) / 0.5))
        green = 0xFF
    blue = 0xAA
    return f"#{red:02x}{green:02x}{blue:02x}"


@dataclass
class _NodeCoverage:
    child_nodes: int = 0
    child_nodes_with_source_links: int = 0
    child_nodes_with_test_links: int = 0

    def add_child_coverage(self, child_coverage: "_NodeCoverage") -> None:
        self.child_nodes += child_coverage.child_nodes
        self.child_nodes_with_source_links += (
            child_coverage.child_nodes_with_source_links
        )
        self.child_nodes_with_test_links += (
            child_coverage.child_nodes_with_test_links
        )

    def source_coverage_ratio(self) -> float:
        return self.child_nodes_with_source_links / self.child_nodes

    def test_coverage_ratio(self) -> float:
        return self.child_nodes_with_test_links / self.child_nodes


@dataclass(frozen=True)
class _SourceNode:
    identifier: str
    parent_identifier: str
    weight: int
    label: str
    normative_label: str
    source_color: str
    test_color: str
    is_normative: bool


@dataclass(frozen=True)
class _TreeMapDefinition:
    title: str
    include_node: Callable[[_SourceNode], bool]
    get_label: Callable[[_SourceNode], str]
    get_color: Callable[[_SourceNode], str]


class TreeMapDataGenerator:
    @staticmethod
    def generate(
        *,
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
    ) -> TreeMapData:
        source_nodes = TreeMapDataGenerator._build_source_nodes(
            project_config=project_config,
            traceability_index=traceability_index,
        )
        definitions = TreeMapDataGenerator._default_definitions()
        tree_maps = tuple(
            TreeMapDataGenerator._build_tree_map(
                source_nodes=source_nodes,
                root_identifier=project_config.project_title,
                definition=definition_,
            )
            for definition_ in definitions
        )
        return TreeMapData(tree_maps=tree_maps)

    @staticmethod
    def _build_source_nodes(
        *,
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
    ) -> Tuple[_SourceNode, ...]:
        coverage_by_node: Dict[
            Union[SDocDocument, SDocNode], _NodeCoverage
        ] = {}

        def get_node_coverage(
            node_: Union[SDocDocument, SDocNode],
        ) -> _NodeCoverage:
            cached_coverage = coverage_by_node.get(node_)
            if cached_coverage is not None:
                return cached_coverage

            if (
                node_.section_contents is None
                or len(node_.section_contents) == 0
            ):
                if (
                    not isinstance(node_, SDocNode)
                    or not node_.is_normative_node()
                    or node_.reserved_uid is None
                ):
                    return _NodeCoverage()

                node_coverage = _NodeCoverage(child_nodes=1)
                child_requirements = (
                    traceability_index.get_children_requirements(node_)
                )
                all_children_have_source_links = len(child_requirements) > 0
                all_children_have_test_links = len(child_requirements) > 0

                for child_requirement_ in child_requirements:
                    child_coverage = get_node_coverage(child_requirement_)
                    if child_coverage.child_nodes_with_source_links == 0:
                        all_children_have_source_links = False
                    if child_coverage.child_nodes_with_test_links == 0:
                        all_children_have_test_links = False

                node_coverage.child_nodes_with_source_links = int(
                    all_children_have_source_links
                )
                node_coverage.child_nodes_with_test_links = int(
                    all_children_have_test_links
                )

                file_traceability_index = (
                    traceability_index.get_file_traceability_index()
                )
                file_links = file_traceability_index.get_requirement_file_links(
                    node_
                )
                for file_path_, _ in file_links:
                    if "tests/" in file_path_:
                        node_coverage.child_nodes_with_test_links = 1
                    else:
                        node_coverage.child_nodes_with_source_links = 1
                return node_coverage

            node_coverage = _NodeCoverage()
            for child_node_ in node_.section_contents:
                if not isinstance(child_node_, SDocNode):
                    continue
                if child_node_.node_type == "TEXT":
                    continue
                child_coverage = get_node_coverage(child_node_)
                coverage_by_node[child_node_] = child_coverage
                node_coverage.add_child_coverage(child_coverage)
            return node_coverage

        documents_with_requirements: Set[SDocDocument] = set()
        for document_ in traceability_index.document_tree.document_list:
            if document_.document_is_included():
                continue

            coverage_by_node[document_] = get_node_coverage(document_)
            document_iterator = SDocDocumentIterator(document_)
            for node_, _ in document_iterator.all_content(
                print_fragments=False
            ):
                if not isinstance(node_, SDocNode):
                    continue
                if node_.is_normative_node():
                    documents_with_requirements.add(document_)
                coverage_by_node[node_] = get_node_coverage(node_)

        source_nodes: List[_SourceNode] = [
            _SourceNode(
                identifier=project_config.project_title,
                parent_identifier="",
                weight=0,
                label=project_config.project_title,
                normative_label=project_config.project_title,
                source_color="lightgray",
                test_color="lightgray",
                is_normative=True,
            )
        ]

        for document_ in traceability_index.document_tree.document_list:
            if document_.document_is_included():
                continue

            document_total_size, document_normative_total_size, _ = (
                document_.get_total_size()
            )
            document_title = (
                f"{document_.reserved_title} ({document_total_size})"
            )
            document_normative_title = (
                f"{document_.reserved_title} ({document_normative_total_size})"
            )
            source_color = "white"
            test_color = "white"
            if document_ in documents_with_requirements:
                document_coverage = get_node_coverage(document_)
                if document_coverage.child_nodes > 0:
                    source_color = _get_coverage_color(
                        document_coverage.source_coverage_ratio()
                    )
                    test_color = _get_coverage_color(
                        document_coverage.test_coverage_ratio()
                    )

            source_nodes.append(
                _SourceNode(
                    identifier=document_.reserved_mid,
                    parent_identifier=project_config.project_title,
                    weight=max(document_total_size, 10),
                    label=document_title,
                    normative_label=document_normative_title,
                    source_color=source_color,
                    test_color=test_color,
                    is_normative=document_ in documents_with_requirements,
                )
            )

            document_iterator = SDocDocumentIterator(document_)
            for node_, _ in document_iterator.all_content(
                print_fragments=False
            ):
                if not isinstance(node_, SDocNode):
                    continue

                node_total_size, node_normative_total_size, _ = (
                    node_.get_total_size()
                )
                node_title = (
                    node_.reserved_title
                    if node_.reserved_title is not None
                    else "[TEXT] node"
                )
                normative_title = node_title
                if (
                    node_.section_contents is not None
                    and len(node_.section_contents) > 0
                ):
                    node_title = f"{node_title} ({node_total_size})"
                    normative_title = (
                        f"{normative_title} ({node_normative_total_size})"
                    )

                source_color = "white"
                test_color = "white"
                if (
                    node_.node_type != "TEXT"
                    and document_ in documents_with_requirements
                ):
                    node_coverage = get_node_coverage(node_)
                    if node_coverage.child_nodes > 0:
                        source_color = _get_coverage_color(
                            node_coverage.source_coverage_ratio()
                        )
                        test_color = _get_coverage_color(
                            node_coverage.test_coverage_ratio()
                        )

                source_nodes.append(
                    _SourceNode(
                        identifier=node_.reserved_mid,
                        parent_identifier=node_.parent.reserved_mid,
                        weight=max(node_total_size, 10),
                        label=node_title,
                        normative_label=normative_title,
                        source_color=source_color,
                        test_color=test_color,
                        is_normative=node_.is_normative_node()
                        or (
                            node_.node_type == "SECTION"
                            and node_.ng_has_requirements
                        ),
                    )
                )

        return tuple(source_nodes)

    @staticmethod
    def _build_tree_map(
        *,
        source_nodes: Tuple[_SourceNode, ...],
        root_identifier: str,
        definition: _TreeMapDefinition,
    ) -> TreeMap:
        included_nodes = tuple(
            source_node_
            for source_node_ in source_nodes
            if definition.include_node(source_node_)
        )
        children_by_parent: Dict[str, List[_SourceNode]] = defaultdict(list)
        nodes_by_identifier: Dict[str, _SourceNode] = {}
        for source_node_ in included_nodes:
            nodes_by_identifier[source_node_.identifier] = source_node_
            children_by_parent[source_node_.parent_identifier].append(
                source_node_
            )

        def build_node(source_node_: _SourceNode) -> TreeMapNode:
            return TreeMapNode(
                label=definition.get_label(source_node_),
                weight=source_node_.weight,
                color=definition.get_color(source_node_),
                children=tuple(
                    build_node(child_node_)
                    for child_node_ in children_by_parent[
                        source_node_.identifier
                    ]
                ),
            )

        root_source_node = nodes_by_identifier[root_identifier]
        return TreeMap(
            title=definition.title,
            root=build_node(root_source_node),
        )

    @staticmethod
    def _default_definitions() -> Tuple[_TreeMapDefinition, ...]:
        return (
            _TreeMapDefinition(
                title="Document tree map",
                include_node=lambda _: True,
                get_label=lambda source_node_: source_node_.label,
                get_color=lambda source_node_: (
                    "lightgray"
                    if source_node_.parent_identifier == ""
                    else "white"
                ),
            ),
            _TreeMapDefinition(
                title="Requirements coverage with source",
                include_node=lambda source_node_: source_node_.is_normative,
                get_label=lambda source_node_: source_node_.normative_label,
                get_color=lambda source_node_: source_node_.source_color,
            ),
            _TreeMapDefinition(
                title="Requirements coverage with test",
                include_node=lambda source_node_: source_node_.is_normative,
                get_label=lambda source_node_: source_node_.normative_label,
                get_color=lambda source_node_: source_node_.test_color,
            ),
        )
