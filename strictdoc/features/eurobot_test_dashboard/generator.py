"""
Computes the Eurobot test dashboard's four coverage gaps:

1. RULE nodes no REQUIREMENT covers.
2. REQUIREMENT nodes covering no RULE.
3. REQUIREMENT nodes no TEST_CASE verifies.
4. TEST_CASE nodes whose STATUS is not Passed.

Each gap is computed once per revision scope (no filter, one revision only,
cumulative up to one revision), so the template can render every scope's
list up front without a server round-trip.

@relation(SDOC-SRS-97, scope=file)
"""

from typing import List, Optional

from markupsafe import Markup

from strictdoc.backend.sdoc.models.grammar_element import (
    GrammarElementFieldSingleChoice,
)
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.document_iterator import SDocDocumentIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.document_type import DocumentType
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.features.eurobot_test_dashboard.models import (
    CoverageGap,
    DashboardScope,
    GapItem,
)
from strictdoc.features.eurobot_test_dashboard.view_object import (
    EurobotTestDashboardViewObject,
)

TARGET_REVISION_FIELD_NAME = "TARGET_REVISION"
STATUS_PASSED = "Passed"


def _make_item(
    node: SDocNode, link_renderer: LinkRenderer, status: Optional[str] = None
) -> GapItem:
    return GapItem(
        uid=node.reserved_uid or "(no UID)",
        title=node.reserved_title or "",
        url=link_renderer.render_node_link(
            node, context_document=None, document_type=DocumentType.DOCUMENT
        ),
        status=status,
    )


class EurobotTestDashboardGenerator:
    @staticmethod
    def export(
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
        html_templates: HTMLTemplates,
    ) -> Markup:
        scopes = EurobotTestDashboardGenerator.compute_scopes(
            traceability_index, link_renderer
        )
        view_object = EurobotTestDashboardViewObject(
            traceability_index=traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            scopes=scopes,
        )
        return view_object.render_screen(html_templates.jinja_environment())

    @staticmethod
    def compute_scopes(
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
    ) -> List[DashboardScope]:
        """
        The gap computation on its own, independent of HTML/Jinja
        rendering, so it can be exercised directly by unit tests.
        """

        rule_nodes: List[SDocNode] = []
        requirement_nodes: List[SDocNode] = []
        test_case_nodes: List[SDocNode] = []

        for document in traceability_index.document_tree.document_list:
            document_iterator = SDocDocumentIterator(document)
            for node, _ in document_iterator.all_content(print_fragments=False):
                if not isinstance(node, SDocNode):
                    continue
                if node.node_type == "RULE":
                    rule_nodes.append(node)
                elif node.node_type == "REQUIREMENT":
                    requirement_nodes.append(node)
                elif node.node_type == "TEST_CASE":
                    test_case_nodes.append(node)

        revision_options: List[str] = (
            EurobotTestDashboardGenerator._get_target_revision_options(
                requirement_nodes
            )
        )

        def revision_index(requirement_node: SDocNode) -> Optional[int]:
            value = requirement_node.get_meta_field_value_by_title(
                TARGET_REVISION_FIELD_NAME
            )
            if value is None or value not in revision_options:
                # Covers both "no value" and a placeholder like TBD/TBC,
                # which StrictDoc accepts on every SingleChoice field but
                # which has no position in the declared, ordered choice
                # list a revision scope resolves against.
                return None
            return revision_options.index(value)

        def requirement_in_scope(
            requirement_node: SDocNode,
            scope_index: Optional[int],
            cumulative: bool,
        ) -> bool:
            if scope_index is None:
                return True
            node_index = revision_index(requirement_node)
            if node_index is None:
                return False
            return (
                node_index <= scope_index
                if cumulative
                else node_index == scope_index
            )

        def build_gaps(
            scope_index: Optional[int], cumulative: bool
        ) -> List[CoverageGap]:
            gap1_items: List[GapItem] = []
            for rule_node in rule_nodes:
                covering_requirements = [
                    requirement_node
                    for requirement_node in traceability_index.get_children_requirements(
                        rule_node
                    )
                    if requirement_node.node_type == "REQUIREMENT"
                    and requirement_in_scope(
                        requirement_node, scope_index, cumulative
                    )
                ]
                if len(covering_requirements) == 0:
                    gap1_items.append(_make_item(rule_node, link_renderer))

            gap2_items: List[GapItem] = []
            gap3_items: List[GapItem] = []
            for requirement_node in requirement_nodes:
                if not requirement_in_scope(
                    requirement_node, scope_index, cumulative
                ):
                    continue

                parent_rules = [
                    parent_node
                    for parent_node in traceability_index.get_parent_requirements(
                        requirement_node
                    )
                    if parent_node.node_type == "RULE"
                ]
                if len(parent_rules) == 0:
                    gap2_items.append(
                        _make_item(requirement_node, link_renderer)
                    )

                verifying_tests = [
                    child_node
                    for child_node in traceability_index.get_children_requirements(
                        requirement_node
                    )
                    if child_node.node_type == "TEST_CASE"
                ]
                if len(verifying_tests) == 0:
                    gap3_items.append(
                        _make_item(requirement_node, link_renderer)
                    )

            gap4_items: List[GapItem] = []
            for test_case_node in test_case_nodes:
                if test_case_node.reserved_status == STATUS_PASSED:
                    continue
                if scope_index is not None:
                    parent_requirements = [
                        parent_node
                        for parent_node in traceability_index.get_parent_requirements(
                            test_case_node
                        )
                        if parent_node.node_type == "REQUIREMENT"
                    ]
                    if not any(
                        requirement_in_scope(
                            parent_node, scope_index, cumulative
                        )
                        for parent_node in parent_requirements
                    ):
                        continue
                gap4_items.append(
                    _make_item(
                        test_case_node,
                        link_renderer,
                        status=test_case_node.reserved_status,
                    )
                )

            return [
                CoverageGap(
                    name="Rules with no covering requirement",
                    items=gap1_items,
                ),
                CoverageGap(
                    name="Requirements covering no rule", items=gap2_items
                ),
                CoverageGap(
                    name="Requirements with no covering test",
                    items=gap3_items,
                ),
                CoverageGap(name="Tests not yet passed", items=gap4_items),
            ]

        scopes: List[DashboardScope] = [
            DashboardScope(
                key="all", label="All revisions", gaps=build_gaps(None, False)
            )
        ]
        for revision_index_, revision_ in enumerate(revision_options):
            scopes.append(
                DashboardScope(
                    key=revision_,
                    label=f"{revision_} only",
                    gaps=build_gaps(revision_index_, False),
                )
            )
            scopes.append(
                DashboardScope(
                    key=f"{revision_}_cumulative",
                    label=f"Up to and including {revision_}",
                    gaps=build_gaps(revision_index_, True),
                )
            )

        return scopes

    @staticmethod
    def _get_target_revision_options(
        requirement_nodes: List[SDocNode],
    ) -> List[str]:
        """
        The TARGET_REVISION SingleChoice field's declared choices, in
        declaration order (e.g. ["C1", "C2"]), read off the first
        REQUIREMENT element found. Declaration order is what "cumulative up
        to revision X" resolves against, since major-letter codenames are
        not guaranteed to sort alphabetically by when they happened.
        """

        for requirement_node in requirement_nodes:
            document = requirement_node.get_document()
            if document is None:
                continue
            grammar = document.grammar
            if grammar is None:
                continue
            element = grammar.elements_by_type.get("REQUIREMENT")
            if element is None:
                continue
            field = element.fields_map.get(TARGET_REVISION_FIELD_NAME)
            if isinstance(field, GrammarElementFieldSingleChoice):
                return list(field.options)
        return []
