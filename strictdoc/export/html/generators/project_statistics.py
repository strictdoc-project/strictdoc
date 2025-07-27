from datetime import datetime
from typing import List, Union

from markupsafe import Markup

from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.backend.sdoc_source_code.models.source_file_info import (
    SourceFileTraceabilityInfo,
)
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.statistics.metric import Metric, MetricSection
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
    ) -> Markup:
        """
        Export default project statistics to an HTML page.

        @relation(SDOC-SRS-97, scope=function)
        """

        git_client = GitClient()

        document_tree_stats: DocumentTreeStats = DocumentTreeStats()

        document_tree_stats.total_documents = len(
            traceability_index.document_tree.document_list
        )
        document_tree_stats.git_commit_hash = git_client.get_commit_hash()

        for document in traceability_index.document_tree.document_list:
            document_iterator = DocumentCachingIterator(document)
            for node, _ in document_iterator.all_content(print_fragments=False):
                if isinstance(node, SDocSection) or (
                    isinstance(node, SDocNode) and node.node_type == "SECTION"
                ):
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

                        # RATIONALE.
                        if (
                            requirement.ordered_fields_lookup.get("RATIONALE")
                            is None
                        ):
                            document_tree_stats.requirements_no_rationale += 1

                        # STATUS.
                        if requirement.reserved_status is None:
                            document_tree_stats.requirements_status_breakdown[
                                None
                            ] += 1
                        else:
                            document_tree_stats.requirements_status_breakdown[
                                requirement.reserved_status
                            ] += 1

                    for requirement_field_ in node.enumerate_fields():
                        field_value = requirement_field_.get_text_value()
                        if "TBD" in field_value:
                            document_tree_stats.total_tbd += 1
                        if "TBC" in field_value:
                            document_tree_stats.total_tbc += 1

        document_tree_stats.sort_requirements_status_breakdown()

        if traceability_index.document_tree.source_tree is not None:
            for (
                source_file_
            ) in traceability_index.document_tree.source_tree.source_files:
                document_tree_stats.total_source_files += 1
                source_file_info_: SourceFileTraceabilityInfo = traceability_index.get_file_traceability_index().get_coverage_info(
                    source_file_.in_doctree_source_file_rel_path_posix
                )
                if source_file_info_.get_coverage() == 100:
                    document_tree_stats.total_source_files_complete_coverage += 1
                elif source_file_info_.get_coverage() == 0:
                    document_tree_stats.total_source_files_no_coverage += 1
                else:
                    document_tree_stats.total_source_files_partial_coverage += 1

        #
        # Create all metrics.
        #

        metrics: List[Union[Metric, MetricSection]] = []

        section = MetricSection(name="General information", metrics=[])
        metrics.append(section)

        section.metrics.append(
            Metric(name="Project name", value=project_config.project_title)
        )
        section.metrics.append(
            Metric(
                name="Statistics generation date",
                value=datetime.today().strftime("%Y-%m-%d %H:%M:%S"),
            )
        )
        section.metrics.append(
            Metric(
                name="Last modification of project data",
                value=traceability_index.strictdoc_last_update.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            )
        )
        section.metrics.append(
            Metric(
                name="Git commit/release",
                value=document_tree_stats.git_commit_hash,
            )
        )
        section.metrics.append(
            Metric(
                name="Total documents",
                value=str(document_tree_stats.total_documents),
            )
        )

        section = MetricSection(name="Sections", metrics=[])
        metrics.append(section)

        section.metrics.append(
            Metric(
                name="Total sections",
                value=str(document_tree_stats.total_sections),
                link="search?q=node.is_section()",
            )
        )
        section.metrics.append(
            Metric(
                name="Sections without any text",
                value=str(document_tree_stats.sections_without_text_nodes),
                link="search?q=(node.is_section() and not node.contains_any_text)",
            )
        )

        section = MetricSection(name="Requirements", metrics=[])
        metrics.append(section)

        section.metrics.append(
            Metric(
                name="Total requirements",
                value=str(document_tree_stats.total_requirements),
                link="search?q=node.is_requirement()",
            )
        )
        section.metrics.append(
            Metric(
                name="Requirements with no UID",
                value=str(document_tree_stats.requirements_no_uid),
                link='search?q=(node.is_requirement() and node["UID"] == None)',
            )
        )
        section.metrics.append(
            Metric(
                name="Root-level requirements not connected to by any requirement",
                value=str(document_tree_stats.requirements_root_no_links),
                link='search?q=(node.is_requirement() and node.is_root and node["STATUS"] != "Backlog" and not node.has_child_requirements)',
            )
        )
        section.metrics.append(
            Metric(
                name="Non-root-level requirements not connected to any parent requirement",
                value=str(document_tree_stats.requirements_no_links),
                link='search?q=(node.is_requirement() and not node.is_root and node["STATUS"] != "Backlog" and not node.has_parent_requirements)',
            )
        )
        section.metrics.append(
            Metric(
                name="Requirements with no RATIONALE",
                value=str(document_tree_stats.requirements_no_rationale),
                link='search?q=(node.is_requirement() and node["RATIONALE"] == None)',
            )
        )

        #
        # If there are requirement statuses, collect status metrics.
        #
        statuses = document_tree_stats.requirements_status_breakdown.keys()
        if any(key is not None for key in statuses):
            section = MetricSection(
                name="Requirements status breakdown", metrics=[]
            )
            metrics.append(section)

            for (
                status_,
                status_count_,
            ) in document_tree_stats.requirements_status_breakdown.items():
                status_query_value = (
                    f'"{status_}"' if status_ is not None else "None"
                )
                section.metrics.append(
                    Metric(
                        name=f"Requirements with status {status_}",
                        value=str(status_count_),
                        link='search?q=(node.is_requirement() and node["STATUS"] == '
                        + status_query_value
                        + ")",
                    )
                )

        #
        # Source files metrics.
        #

        section = MetricSection(name="Source files", metrics=[])
        metrics.append(section)

        section.metrics.append(
            Metric(
                name="Total source files",
                value=str(document_tree_stats.total_source_files),
                link="search?q=node.is_source_file()",
            )
        )
        section.metrics.append(
            Metric(
                name="Total source files with complete requirements coverage",
                value=str(
                    document_tree_stats.total_source_files_complete_coverage
                ),
                link="search?q=node.is_source_file_with_complete_coverage()",
            )
        )
        section.metrics.append(
            Metric(
                name="Total source files with partial requirements coverage",
                value=str(
                    document_tree_stats.total_source_files_partial_coverage
                ),
                link="search?q=node.is_source_file_with_partial_coverage()",
            )
        )
        section.metrics.append(
            Metric(
                name="Total source files with no requirements coverage",
                value=str(document_tree_stats.total_source_files_no_coverage),
                link="search?q=node.is_source_file_with_no_coverage()",
            )
        )

        #
        # TBD/TBC metrics.
        #

        section = MetricSection(name="TBD/TBC", metrics=[])
        metrics.append(section)

        section.metrics.append(
            Metric(
                name="Total TBD",
                value=str(document_tree_stats.total_tbd),
                link='search?q=node.contains("TBD")',
            )
        )
        section.metrics.append(
            Metric(
                name="Total TBC",
                value=str(document_tree_stats.total_tbc),
                link='search?q=node.contains("TBC")',
            )
        )

        #
        # Return the final view object.
        #
        view_object = ProjectStatisticsViewObject(
            traceability_index=traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            metrics=metrics,
        )
        return view_object.render_screen(html_templates.jinja_environment())
