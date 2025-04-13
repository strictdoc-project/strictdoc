# mypy: disable-error-code="no-untyped-call,no-untyped-def,union-attr"
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.generators.view_objects.project_statistics_view_object import (
    ProjectStatisticsViewObject,
)
from strictdoc.export.html.generators.view_objects.project_tree_stats import (
    DocumentTreeStats,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.git_client import GitClient


class ProgressStatisticsGenerator:
    @staticmethod
    def export(
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
        html_templates: HTMLTemplates,
    ):
        git_client = GitClient()

        document_tree_stats: DocumentTreeStats = DocumentTreeStats()
        document_tree_stats.total_documents = len(
            traceability_index.document_tree.document_list
        )
        document_tree_stats.git_commit_hash = git_client.get_commit_hash()

        for document in traceability_index.document_tree.document_list:
            document_iterator = DocumentCachingIterator(document)
            for node in document_iterator.all_content(
                print_fragments=False, print_fragments_from_files=False
            ):
                if isinstance(node, SDocSection):
                    document_tree_stats.total_sections += 1
                    if not node.has_any_text_nodes():
                        document_tree_stats.sections_without_text_nodes += 1

                elif isinstance(node, SDocNode):
                    if (
                        node.is_normative_node()
                        and node.node_type == "REQUIREMENT"
                    ):
                        requirement: SDocNode = assert_cast(node, SDocNode)
                        document_tree_stats.total_requirements += 1

                        if requirement.reserved_uid is None:
                            document_tree_stats.requirements_no_uid += 1

                        if requirement.reserved_status != "Backlog":
                            if document.config.root:
                                if (
                                    len(
                                        traceability_index.get_children_requirements(
                                            requirement
                                        )
                                    )
                                    == 0
                                ):
                                    document_tree_stats.requirements_root_no_links += 1
                            else:
                                if (
                                    len(
                                        traceability_index.get_parent_requirements(
                                            requirement
                                        )
                                    )
                                    == 0
                                ):
                                    document_tree_stats.requirements_no_links += 1

                        # RATIONALE
                        if (
                            requirement.ordered_fields_lookup.get("RATIONALE")
                            is None
                        ):
                            document_tree_stats.requirements_no_rationale += 1

                        # STATUS
                        if requirement.reserved_status is None:
                            document_tree_stats.requirements_status_none += 1
                        else:
                            if requirement.reserved_status == "Backlog":
                                document_tree_stats.requirements_status_backlog += 1
                            elif requirement.reserved_status == "Draft":
                                document_tree_stats.requirements_status_draft += 1
                            elif requirement.reserved_status == "Active":
                                document_tree_stats.requirements_status_active += 1
                            else:
                                document_tree_stats.requirements_status_other += 1

                    for requirement_field_ in node.enumerate_fields():
                        field_value = requirement_field_.get_text_value()
                        if field_value is not None:
                            if "TBD" in field_value:
                                document_tree_stats.total_tbd += 1
                            if "TBC" in field_value:
                                document_tree_stats.total_tbc += 1

        view_object = ProjectStatisticsViewObject(
            document_tree_stats=document_tree_stats,
            traceability_index=traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
        )
        return view_object.render_screen(html_templates.jinja_environment())
