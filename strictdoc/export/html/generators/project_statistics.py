from dataclasses import dataclass, field
from typing import List, Optional

from strictdoc import __version__
from strictdoc.backend.sdoc.models.requirement import Requirement
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.document_tree_iterator import DocumentTreeIterator
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.helpers.cast import assert_cast
from strictdoc.helpers.git_client import GitClient


@dataclass
class DocumentStats:
    requirements_total: int = 0
    requirements_no_uid: List[Requirement] = field(default_factory=list)


@dataclass
class DocumentTreeStats:  # pylint: disable=too-many-instance-attributes
    total_documents: int = 0
    total_requirements: int = 0
    total_tbd: int = 0
    total_tbc: int = 0
    git_commit_hash: Optional[str] = None

    # UID
    requirements_no_uid: int = 0
    requirements_no_links: int = 0
    requirements_no_rationale: int = 0

    # STATUS
    requirements_status_none: int = 0
    requirements_status_draft: int = 0
    requirements_status_backlog: int = 0
    requirements_status_active: int = 0
    requirements_status_other: int = 0

    # Document-level stats.
    document_level_stats: List[DocumentStats] = field(
        default_factory=DocumentStats
    )


class ProgressStatisticsGenerator:
    @staticmethod
    def export(  # pylint: disable=too-many-arguments
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        link_renderer: LinkRenderer,
        html_templates: HTMLTemplates,
    ):
        output = ""

        document_tree_iterator = DocumentTreeIterator(
            traceability_index.document_tree
        )

        git_client = GitClient.create()

        document_tree_stats = DocumentTreeStats()
        document_tree_stats.total_documents = len(
            traceability_index.document_tree.document_list
        )
        document_tree_stats.git_commit_hash = git_client.get_commit_hash()

        for document in traceability_index.document_tree.document_list:
            document_iterator = DocumentCachingIterator(document)
            for node in document_iterator.all_content():
                if isinstance(node, Requirement):
                    requirement: Requirement = assert_cast(node, Requirement)
                    document_tree_stats.total_requirements += 1
                    if requirement.reserved_uid is None:
                        document_tree_stats.requirements_no_uid += 1

                    if len(requirement.references) == 0:
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

                    for requirement_field_ in requirement.enumerate_fields():
                        if requirement_field_.field_value is not None:
                            if "TBD" in requirement_field_.field_value:
                                document_tree_stats.total_tbd += 1
                            if "TBC" in requirement_field_.field_value:
                                document_tree_stats.total_tbc += 1

                        elif (
                            requirement_field_.field_value_multiline is not None
                        ):
                            if (
                                "TBD"
                                in requirement_field_.field_value_multiline
                            ):
                                document_tree_stats.total_tbd += 1
                            if (
                                "TBC"
                                in requirement_field_.field_value_multiline
                            ):
                                document_tree_stats.total_tbc += 1

        template = html_templates.jinja_environment().get_template(
            "screens/project_statistics/index.jinja"
        )

        output += template.render(
            document_tree_stats=document_tree_stats,
            project_config=project_config,
            traceability_index=traceability_index,
            link_renderer=link_renderer,
            strictdoc_version=__version__,
            document_tree=traceability_index.document_tree,
            document_tree_iterator=document_tree_iterator,
        )

        return output
