# mypy: disable-error-code="arg-type,no-any-return,no-redef,no-untyped-call,no-untyped-def,type-arg,union-attr"
import hashlib
import statistics
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from markupsafe import Markup

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.node import (
    SDocNode,
    SDocNodeField,
)
from strictdoc.backend.sdoc.models.reference import (
    ChildReqReference,
    ParentReqReference,
)
from strictdoc.backend.sdoc.models.section import SDocSection
from strictdoc.core.document_iterator import DocumentCachingIterator
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.git.change import (
    ChangeType,
    ChangeUnionType,
    DocumentChange,
    RequirementChange,
    RequirementFieldChange,
    SectionChange,
)
from strictdoc.helpers.cast import assert_cast, assert_optional_cast
from strictdoc.helpers.diff import get_colored_html_diff_string, similar
from strictdoc.helpers.mid import MID


def calculate_similarity(lhs: SDocNode, rhs: SDocNode) -> float:
    similar_fields = []
    for field_name_, field_values_ in lhs.ordered_fields_lookup.items():
        if field_name_ == "COMMENT":
            continue

        if field_name_ not in rhs.ordered_fields_lookup:
            continue

        if field_name_ not in ("TITLE", "STATEMENT", "RATIONALE"):
            continue

        rhs_field_values = rhs.ordered_fields_lookup[field_name_]

        lhs_field_value = field_values_[0].get_text_value()
        rhs_field_value = rhs_field_values[0].get_text_value()

        similar_fields.append(similar(lhs_field_value, rhs_field_value))

    return statistics.mean(similar_fields)


@dataclass
class ProjectTreeDiffStats:
    document_md5_hashes: Set[str] = field(default_factory=set)
    requirement_md5_hashes: Set[str] = field(default_factory=set)
    section_md5_hashes: Set[str] = field(default_factory=set)
    map_nodes_to_hashes: Dict[Any, str] = field(default_factory=dict)
    map_mid_to_nodes: Dict[MID, Any] = field(default_factory=dict)
    map_uid_to_nodes: Dict[str, Any] = field(default_factory=dict)
    map_titles_to_nodes: Dict[str, List] = field(default_factory=dict)
    map_statements_to_nodes: Dict[str, Any] = field(default_factory=dict)
    map_rel_paths_to_docs: Dict[str, SDocDocument] = field(default_factory=dict)

    cache_requirement_to_requirement: Dict[SDocNode, SDocNode] = field(
        default_factory=dict
    )

    def get_md5_by_node(self, node) -> str:
        return self.map_nodes_to_hashes[node]

    def contains_requirement_md5(self, requirement_md5: str) -> bool:
        return requirement_md5 in self.requirement_md5_hashes

    def contains_section_md5(self, section_md5: str) -> bool:
        return section_md5 in self.section_md5_hashes

    def contains_document_md5(self, document_md5: str) -> bool:
        return document_md5 in self.document_md5_hashes

    def contains_requirement_field(
        self, requirement: SDocNode, field_name: str, field_value: str
    ):
        assert isinstance(field_value, str)
        other_requirement: Optional[SDocNode] = self.find_requirement(
            requirement
        )
        if other_requirement is None:
            return False

        if field_name not in other_requirement.ordered_fields_lookup:
            return False

        other_requirement_fields = other_requirement.ordered_fields_lookup[
            field_name
        ]
        for field_ in other_requirement_fields:
            if field_.get_text_value() == field_value:
                return True
        return False

    def get_identical_requirement_field(
        self, requirement: SDocNode, field_name: str, field_value: str
    ) -> Optional[SDocNodeField]:
        assert isinstance(field_value, str)
        other_requirement: Optional[SDocNode] = self.find_requirement(
            requirement
        )
        if other_requirement is None:
            return None

        if field_name not in other_requirement.ordered_fields_lookup:
            return None

        other_requirement_fields = other_requirement.ordered_fields_lookup[
            field_name
        ]
        for field_ in other_requirement_fields:
            if field_.get_text_value() == field_value:
                return field_
        return None

    def contains_requirement_relations(
        self,
        requirement: SDocNode,
        relation_uid: str,
        relation_role: Optional[str],
    ):
        other_requirement: Optional[SDocNode] = self.find_requirement(
            requirement
        )
        if other_requirement is None:
            return False
        for reference_ in other_requirement.relations:
            if isinstance(reference_, (ParentReqReference, ChildReqReference)):
                if (
                    reference_.ref_uid == relation_uid
                    and reference_.role == relation_role
                ):
                    return True
        return False

    def find_requirement(self, requirement: SDocNode) -> Optional[SDocNode]:
        if requirement in self.cache_requirement_to_requirement:
            return self.cache_requirement_to_requirement[requirement]

        requirement_parent_uids = set()
        for parent_ in requirement.relations:
            if isinstance(parent_, ParentReqReference):
                requirement_parent_uids.add(parent_.ref_uid)

        if (
            requirement.mid_permanent
            and requirement.reserved_mid in self.map_mid_to_nodes
        ):
            return self.map_mid_to_nodes[requirement.reserved_mid]
        elif (
            requirement.reserved_uid is None
            or requirement.reserved_uid not in self.map_uid_to_nodes
        ):
            candidate_requirements: Dict[SDocNode, float] = {}

            if (
                requirement.reserved_title is not None
                and requirement.reserved_title in self.map_titles_to_nodes
            ):
                other_requirements = self.map_titles_to_nodes[
                    requirement.reserved_title
                ]
                for other_requirement_ in other_requirements:
                    if (
                        not other_requirement_.reserved_uid
                        in requirement_parent_uids
                    ):
                        candidate_requirements[other_requirement_] = 0

            for candidate_requirement_ in candidate_requirements.keys():
                candidate_requirements[candidate_requirement_] = (
                    calculate_similarity(requirement, candidate_requirement_)
                )

            if len(candidate_requirements) > 0:
                candidate_requirement = max(
                    candidate_requirements, key=candidate_requirements.get
                )
                self.cache_requirement_to_requirement[requirement] = (
                    candidate_requirement
                )
                return candidate_requirement
            return None

        other_requirement: SDocNode = self.map_uid_to_nodes[
            requirement.reserved_uid
        ]
        # FIXME: This is an interesting case when a SDocNode can be promoted
        # or unpromoted to a Section with the same UID preserved. Ignore this
        # case for now.
        if not isinstance(other_requirement, SDocNode):
            return None
        return other_requirement


@dataclass
class ChangeStats:
    _changes: List[ChangeUnionType] = field(default_factory=list)
    _change_counters: Dict[ChangeType, int] = field(default_factory=dict)
    map_nodes_to_changes: Dict[Any, ChangeUnionType] = field(
        default_factory=dict
    )

    @property
    def changes(self):
        return self._changes

    def find_change(self, node: Any):
        return self.map_nodes_to_changes.get(node)

    def get_total_changes(self) -> int:
        return len(self._changes)

    def get_changes_requirements_changed(self) -> Optional[int]:
        return self._change_counters.get(ChangeType.REQUIREMENT)

    def get_changes_sections_stats_string(self) -> str:
        """
        Example: 2 removed, 1 modified, 2 added
        """
        change_components = []
        removed = self._change_counters.get(ChangeType.SECTION_REMOVED)
        if removed is not None:
            change_components.append(f"{removed} removed")
        modified = self._change_counters.get(ChangeType.SECTION_MODIFIED)
        if modified is not None:
            change_components.append(f"{modified} modified")
        added = self._change_counters.get(ChangeType.SECTION_ADDED)
        if added is not None:
            change_components.append(f"{added} added")
        assert len(change_components) > 0
        return ", ".join(change_components)

    def get_changes_requirements_stats_string(self) -> str:
        """
        Example: 2 removed, 1 modified, 2 added
        """
        change_components = []
        removed = self._change_counters.get(ChangeType.REQUIREMENT_REMOVED)
        if removed is not None:
            change_components.append(f"{removed} removed")
        modified = self._change_counters.get(ChangeType.REQUIREMENT_MODIFIED)
        if modified is not None:
            change_components.append(f"{modified} modified")
        added = self._change_counters.get(ChangeType.REQUIREMENT_ADDED)
        if added is not None:
            change_components.append(f"{added} added")
        assert len(change_components) > 0
        return ", ".join(change_components)

    def get_changes_documents_modified(self) -> Optional[int]:
        return self._change_counters.get(ChangeType.DOCUMENT)

    def get_changes_sections_modified(self) -> Optional[int]:
        return self._change_counters.get(ChangeType.SECTION)

    def add_change(self, change: ChangeUnionType):
        self._changes.append(change)
        self._change_counters.setdefault(change.change_type, 0)
        self._change_counters[change.change_type] += 1
        if change.change_type in (
            ChangeType.REQUIREMENT_REMOVED,
            ChangeType.REQUIREMENT_MODIFIED,
            ChangeType.REQUIREMENT_ADDED,
        ):
            self._change_counters.setdefault(ChangeType.REQUIREMENT, 0)
            self._change_counters[ChangeType.REQUIREMENT] += 1
        elif change.change_type in (
            ChangeType.SECTION_REMOVED,
            ChangeType.SECTION_MODIFIED,
            ChangeType.SECTION_ADDED,
        ):
            self._change_counters.setdefault(ChangeType.SECTION, 0)
            self._change_counters[ChangeType.SECTION] += 1
        elif change.change_type in (ChangeType.DOCUMENT_MODIFIED,):
            self._change_counters.setdefault(ChangeType.DOCUMENT, 0)
            self._change_counters[ChangeType.DOCUMENT] += 1

    @staticmethod
    def create_from_two_indexes(
        lhs_index: TraceabilityIndex,
        rhs_index: TraceabilityIndex,
        lhs_stats: ProjectTreeDiffStats,
        rhs_stats: ProjectTreeDiffStats,
    ):
        stats = ChangeStats()

        ChangeStats._iterate_one_index(
            lhs_index, lhs_stats, rhs_stats, stats, "left"
        )
        ChangeStats._iterate_one_index(
            rhs_index, rhs_stats, lhs_stats, stats, "right"
        )

        return stats

    @staticmethod
    def _iterate_one_index(
        index: TraceabilityIndex,
        self_stats: ProjectTreeDiffStats,
        other_stats: ProjectTreeDiffStats,
        change_stats: "ChangeStats",
        side: str,
    ):
        assert side in ("left", "right")

        for document in index.document_tree.document_list:
            """
            The included documents are ignored. All their information should
            be contained in the including documents at this point.
            """
            if document.document_is_included():
                continue

            """
            First, take care of the document node itself. Check if the document
            root-level free text (abstract) has changed.
            """
            if document not in change_stats.map_nodes_to_changes:
                other_document_or_none: Optional[SDocDocument]

                # First, the MID-based match is tried. If no MID is available,
                # try to find a document under the same path.
                if (
                    document.mid_permanent
                    and document.reserved_mid in other_stats.map_mid_to_nodes
                ):
                    other_document_or_none = other_stats.map_mid_to_nodes[
                        document.reserved_mid
                    ]
                else:
                    other_document_or_none = (
                        other_stats.map_rel_paths_to_docs.get(
                            document.meta.input_doc_rel_path.relative_path
                        )
                    )

                uid_modified: bool = False
                title_modified: bool = False
                lhs_colored_title_diff: Optional[Markup] = None
                rhs_colored_title_diff: Optional[Markup] = None

                # If there is another section and the UIDs are not the
                # same, consider the UID modified.
                # If there is no other section, consider the UID
                # modified.
                if other_document_or_none is not None:
                    if (
                        document.reserved_uid
                        != other_document_or_none.reserved_uid
                    ):
                        uid_modified = True
                else:
                    uid_modified = True

                if other_document_or_none is not None:
                    if document.title != other_document_or_none.title:
                        title_modified = True
                        lhs_colored_title_diff = get_colored_html_diff_string(
                            document.title,
                            other_document_or_none.title,
                            "left",
                        )
                        rhs_colored_title_diff = get_colored_html_diff_string(
                            document.title,
                            other_document_or_none.title,
                            "right",
                        )
                else:
                    title_modified = True

                if uid_modified or title_modified:
                    lhs_document: Optional[SDocDocument]
                    rhs_document: Optional[SDocDocument]
                    if side == "left":
                        lhs_document = document
                        rhs_document = other_document_or_none
                    else:
                        lhs_document = other_document_or_none
                        rhs_document = document

                    document_change: DocumentChange = DocumentChange(
                        matched_uid=None,
                        lhs_document=lhs_document,
                        rhs_document=rhs_document,
                        uid_modified=uid_modified,
                        title_modified=title_modified,
                        lhs_colored_title_diff=lhs_colored_title_diff,
                        rhs_colored_title_diff=rhs_colored_title_diff,
                    )
                    change_stats.map_nodes_to_changes[document] = (
                        document_change
                    )
                    if other_document_or_none is not None:
                        change_stats.map_nodes_to_changes[
                            other_document_or_none
                        ] = document_change
                    change_stats.add_change(document_change)

            document_iterator = DocumentCachingIterator(document)

            """
            Now iterate over all nodes and collect the diff information.

            Note that document nodes appear when a document is included to
            another document. We treat a document node as as a section node
            because they both have FREETEXT.
            """
            for node in document_iterator.all_content(
                print_fragments=True, print_fragments_from_files=False
            ):
                if isinstance(node, (SDocSection, SDocDocument)):
                    if node in change_stats.map_nodes_to_changes:
                        continue

                    section_md5 = self_stats.get_md5_by_node(node)
                    section_modified = not other_stats.contains_section_md5(
                        section_md5
                    )
                    if section_modified:
                        matched_mid: Optional[MID] = None
                        matched_uid: Optional[str] = None
                        other_section_or_none: Optional[SDocSection] = None

                        if (
                            node.mid_permanent
                            and node.reserved_mid
                            in other_stats.map_mid_to_nodes
                        ):
                            other_section_or_none = (
                                other_stats.map_mid_to_nodes[node.reserved_mid]
                            )
                            matched_mid = node.reserved_mid
                        if node.reserved_uid is not None:
                            assert len(node.reserved_uid) > 0
                            if other_stats.map_uid_to_nodes.get(
                                node.reserved_uid
                            ):
                                matched_uid = node.reserved_uid
                                other_section_or_none = (
                                    other_stats.map_uid_to_nodes[matched_uid]
                                )
                        # FIXME: This is when a Requirement becomes
                        # a Section with the same UID preserved.
                        if other_section_or_none is not None and not isinstance(
                            other_section_or_none, SDocSection
                        ):
                            other_section_or_none = None
                            matched_uid = None
                            matched_mid = None

                        uid_modified: bool = False
                        title_modified: bool = False
                        lhs_colored_title_diff: Optional[Markup] = None
                        rhs_colored_title_diff: Optional[Markup] = None

                        # If there is another section and the UIDs are not the
                        # same, consider the UID modified.
                        # If there is no other section, consider the UID
                        # modified.
                        if other_section_or_none is not None:
                            if (
                                node.reserved_uid
                                != other_section_or_none.reserved_uid
                            ):
                                uid_modified = True
                        else:
                            uid_modified = True

                        if other_section_or_none is not None:
                            if node.title != other_section_or_none.title:
                                title_modified = True
                                lhs_colored_title_diff = (
                                    get_colored_html_diff_string(
                                        node.title,
                                        other_section_or_none.title,
                                        "left",
                                    )
                                )
                                rhs_colored_title_diff = (
                                    get_colored_html_diff_string(
                                        node.title,
                                        other_section_or_none.title,
                                        "right",
                                    )
                                )
                        else:
                            title_modified = True

                        """
                        Step: Create a section token that is used by JS to match
                        the LHS nodes with RHS nodes.
                        """
                        section_token: Optional[str] = None
                        if other_section_or_none is not None:
                            section_token = MID.create()

                        lhs_section: Optional[Union[SDocSection, SDocDocument]]
                        rhs_section: Optional[Union[SDocSection, SDocDocument]]
                        if side == "left":
                            lhs_section = node
                            rhs_section = other_section_or_none
                        else:
                            lhs_section = other_section_or_none
                            rhs_section = node

                        section_change: SectionChange = SectionChange(
                            matched_mid=matched_mid,
                            matched_uid=matched_uid,
                            section_token=section_token,
                            lhs_section=lhs_section,
                            rhs_section=rhs_section,
                            uid_modified=uid_modified,
                            title_modified=title_modified,
                            lhs_colored_title_diff=lhs_colored_title_diff,
                            rhs_colored_title_diff=rhs_colored_title_diff,
                        )

                        change_stats.map_nodes_to_changes[node] = section_change
                        if other_section_or_none is not None:
                            change_stats.map_nodes_to_changes[
                                other_section_or_none
                            ] = section_change
                        change_stats.add_change(section_change)

                if isinstance(node, SDocNode):
                    """
                    Step: We check if a requirement was modified at all, or if
                    it has already been checked before. Skipping the requirement
                    if there is nothing to do.
                    """
                    # FIXME: Is this 100% valid?

                    if node in change_stats.map_nodes_to_changes:
                        continue

                    requirement: SDocNode = assert_cast(node, SDocNode)
                    requirement_md5 = self_stats.get_md5_by_node(requirement)
                    requirement_modified = (
                        not other_stats.contains_requirement_md5(
                            requirement_md5
                        )
                    )
                    if not requirement_modified:
                        continue

                    other_requirement_or_none: Optional[SDocNode] = (
                        assert_optional_cast(
                            other_stats.find_requirement(requirement), SDocNode
                        )
                    )

                    # If there is no other requirement to compare with,
                    # we simply record this as a trivial change where everything
                    # is tracked as "deleted" or "new".
                    if other_requirement_or_none is None:
                        if side == "left":
                            lhs_requirement = requirement
                            rhs_requirement = None
                        else:
                            lhs_requirement = None
                            rhs_requirement = requirement

                        requirement_change: RequirementChange = (
                            RequirementChange(
                                requirement_token=None,
                                field_changes=[],
                                lhs_requirement=lhs_requirement,
                                rhs_requirement=rhs_requirement,
                            )
                        )
                        change_stats.map_nodes_to_changes[node] = (
                            requirement_change
                        )
                        change_stats.add_change(requirement_change)
                        continue

                    """
                    Step: Starting from here, we will be looking at the
                    difference between this and the other requirement.
                    """
                    other_requirement: SDocNode = other_requirement_or_none

                    field_changes: List[RequirementFieldChange] = []

                    """
                    Step: Create a requirement token that is used by JS to match
                    the LHS nodes with RHS nodes.
                    """
                    requirement_token: str = MID.create()

                    """
                    Iterate over requirement fields.
                    """
                    requirement_fields_iter = iter(
                        requirement.enumerate_all_fields()
                    )
                    other_requirement_fields_iter = iter(
                        other_requirement.enumerate_all_fields()
                    )

                    field_checked_so_far: Set[SDocNodeField] = set()
                    while True:
                        requirement_field_tripple = next(
                            requirement_fields_iter, None
                        )
                        if (
                            requirement_field_tripple is not None
                            and requirement_field_tripple[1] != "COMMENT"
                            and requirement_field_tripple[0]
                            not in field_checked_so_far
                        ):
                            requirement_field_change = ChangeStats.create_field_change(
                                other_stats=other_stats,
                                requirement=requirement,
                                requirement_field=requirement_field_tripple[0],
                                other_requirement=other_requirement,
                                requirement_field_name=requirement_field_tripple[
                                    1
                                ],
                                requirement_field_value=requirement_field_tripple[
                                    2
                                ],
                            )
                            if requirement_field_change is not None:
                                field_changes.append(requirement_field_change)
                                if (
                                    requirement_field_change.lhs_field
                                    is not None
                                ):
                                    field_checked_so_far.add(
                                        requirement_field_change.lhs_field
                                    )
                                if (
                                    requirement_field_change.rhs_field
                                    is not None
                                ):
                                    field_checked_so_far.add(
                                        requirement_field_change.rhs_field
                                    )
                            else:
                                field_checked_so_far.add(
                                    requirement_field_tripple[0]
                                )

                        other_requirement_field_tripple = next(
                            other_requirement_fields_iter, None
                        )
                        if (
                            other_requirement_field_tripple is not None
                            and other_requirement_field_tripple[1] != "COMMENT"
                            and other_requirement_field_tripple[0]
                            not in field_checked_so_far
                        ):
                            requirement_field_change = ChangeStats.create_field_change(
                                other_stats=self_stats,
                                requirement=other_requirement,
                                requirement_field=other_requirement_field_tripple[
                                    0
                                ],
                                other_requirement=requirement,
                                requirement_field_name=other_requirement_field_tripple[
                                    1
                                ],
                                requirement_field_value=other_requirement_field_tripple[
                                    2
                                ],
                            )
                            if requirement_field_change is not None:
                                field_changes.append(requirement_field_change)
                                if (
                                    requirement_field_change.lhs_field
                                    is not None
                                ):
                                    field_checked_so_far.add(
                                        requirement_field_change.lhs_field
                                    )
                                if (
                                    requirement_field_change.rhs_field
                                    is not None
                                ):
                                    field_checked_so_far.add(
                                        requirement_field_change.rhs_field
                                    )
                            else:
                                field_checked_so_far.add(
                                    other_requirement_field_tripple[0]
                                )

                        if (
                            requirement_field_tripple is None
                            and other_requirement_field_tripple is None
                        ):
                            break

                    # COMMENT can appear in requirement several times, so
                    # it is handled separately.
                    comments_changes = ChangeStats.create_comment_field_changes(
                        requirement=requirement,
                        other_requirement=other_requirement,
                    )
                    field_changes.extend(comments_changes)

                    if side == "left":
                        lhs_requirement = requirement
                        rhs_requirement = other_requirement
                    else:
                        lhs_requirement = other_requirement
                        rhs_requirement = requirement

                    requirement_change: RequirementChange = RequirementChange(
                        requirement_token=requirement_token,
                        field_changes=field_changes,
                        lhs_requirement=lhs_requirement,
                        rhs_requirement=rhs_requirement,
                    )

                    change_stats.map_nodes_to_changes[node] = requirement_change
                    if other_requirement_or_none is not None:
                        change_stats.map_nodes_to_changes[
                            other_requirement_or_none
                        ] = requirement_change
                    change_stats.add_change(requirement_change)

    @staticmethod
    def create_field_change(
        *,
        other_stats: ProjectTreeDiffStats,
        requirement: SDocNode,
        requirement_field: SDocNodeField,
        other_requirement: SDocNode,
        requirement_field_name: str,
        requirement_field_value: str,
    ) -> Optional[RequirementFieldChange]:
        assert isinstance(requirement, SDocNode)
        assert isinstance(requirement_field, SDocNodeField)
        assert isinstance(other_requirement, SDocNode)

        other_requirement_field = other_stats.get_identical_requirement_field(
            requirement, requirement_field_name, requirement_field_value
        )
        # If there is an identical field, it means the field
        # is not modified. Nothing to do.
        if other_requirement_field is not None:
            return None

        left_diff = None
        right_diff = None
        other_requirement_fields = other_requirement.ordered_fields_lookup.get(
            requirement_field_name, []
        )
        other_requirement_field = (
            other_requirement_fields[0]
            if len(other_requirement_fields) > 0
            else None
        )

        if other_requirement_field is not None:
            other_requirement_field_value = (
                other_requirement_field.get_text_value()
            )
            left_diff = get_colored_html_diff_string(
                requirement_field_value, other_requirement_field_value, "left"
            )
            right_diff = get_colored_html_diff_string(
                requirement_field_value, other_requirement_field_value, "right"
            )

        return RequirementFieldChange(
            field_name=requirement_field_name,
            lhs_field=requirement_field,
            rhs_field=other_requirement_field,
            left_diff=left_diff,
            right_diff=right_diff,
        )

    @staticmethod
    def create_comment_field_changes(
        *,
        requirement: SDocNode,
        other_requirement: SDocNode,
    ) -> Optional[List[RequirementFieldChange]]:
        assert isinstance(requirement, SDocNode)
        assert isinstance(other_requirement, SDocNode)

        changes = []

        changed_fields: Dict = dict.fromkeys(
            requirement.ordered_fields_lookup.get("COMMENT", []), 1
        )
        changed_other_fields: Dict = dict.fromkeys(
            other_requirement.ordered_fields_lookup.get("COMMENT", []), 1
        )

        if len(changed_fields) == 0 or len(changed_other_fields) == 0:
            for changed_field_ in changed_fields:
                changes.append(
                    RequirementFieldChange(
                        field_name="COMMENT",
                        lhs_field=changed_field_,
                        rhs_field=None,
                        left_diff=None,
                        right_diff=None,
                    )
                )
            for changed_other_field_ in changed_other_fields:
                changes.append(
                    RequirementFieldChange(
                        field_name="COMMENT",
                        lhs_field=None,
                        rhs_field=changed_other_field_,
                        left_diff=None,
                        right_diff=None,
                    )
                )
            return changes

        similarities: List[Tuple[float, SDocNodeField, SDocNodeField]] = []
        for changed_field_ in list(changed_fields.keys()):
            comment_value = changed_field_.get_text_value()
            assert comment_value is not None
            for changed_other_field_ in list(changed_other_fields.keys()):
                comment_other_value = changed_other_field_.get_text_value()
                assert comment_other_value is not None

                similarity = similar(comment_value, comment_other_value)
                if similarity == 1:
                    del changed_fields[changed_field_]
                    del changed_other_fields[changed_other_field_]
                    break

                similarities.append(
                    (similarity, changed_field_, changed_other_field_)
                )

        similarities.sort(key=lambda student: student[0], reverse=True)

        for _, changed_field_, changed_other_field_ in similarities:
            if (
                changed_field_ not in changed_fields
                or changed_other_field_ not in changed_other_fields
            ):
                continue

            # This is the best change.
            comment_value = changed_field_.get_text_value()
            comment_other_value = changed_other_field_.get_text_value()
            assert comment_other_value is not None

            left_diff = get_colored_html_diff_string(
                comment_value,
                comment_other_value,
                "left",
            )
            right_diff = get_colored_html_diff_string(
                comment_value,
                comment_other_value,
                "right",
            )
            changes.append(
                RequirementFieldChange(
                    field_name="COMMENT",
                    lhs_field=changed_field_,
                    rhs_field=changed_other_field_,
                    left_diff=left_diff,
                    right_diff=right_diff,
                )
            )
            del changed_fields[changed_field_]
            del changed_other_fields[changed_other_field_]

        # Iterate over remaining fields.
        for changed_field_ in changed_fields:
            changes.append(
                RequirementFieldChange(
                    field_name="COMMENT",
                    lhs_field=changed_field_,
                    rhs_field=None,
                    left_diff=None,
                    right_diff=None,
                )
            )
        for changed_other_field_ in changed_other_fields:
            changes.append(
                RequirementFieldChange(
                    field_name="COMMENT",
                    lhs_field=None,
                    rhs_field=changed_other_field_,
                    left_diff=None,
                    right_diff=None,
                )
            )

        return changes


class ProjectDiffAnalyzer:
    @staticmethod
    def analyze_document_tree(
        traceability_index: TraceabilityIndex,
    ) -> ProjectTreeDiffStats:
        document_tree_stats: ProjectTreeDiffStats = ProjectTreeDiffStats()

        for document in traceability_index.document_tree.document_list:
            if document.document_is_included():
                continue
            ProjectDiffAnalyzer.analyze_document(document, document_tree_stats)

        return document_tree_stats

    @staticmethod
    def analyze_document(
        document: SDocDocument,
        document_tree_stats: ProjectTreeDiffStats,
    ) -> None:
        document_iterator = DocumentCachingIterator(document)

        map_nodes_to_hashers: Dict[Any, Any] = {document: hashlib.md5()}

        if document.mid_permanent:
            document_tree_stats.map_mid_to_nodes[document.reserved_mid] = (
                document
            )

        document_tree_stats.map_rel_paths_to_docs[
            document.meta.input_doc_rel_path.relative_path
        ] = document

        map_nodes_to_hashers[document].update(document.title.encode("utf-8"))

        for node in document_iterator.all_content(
            print_fragments=True, print_fragments_from_files=False
        ):
            if node.mid_permanent:
                document_tree_stats.map_mid_to_nodes[node.reserved_mid] = node

            if isinstance(node, (SDocSection, SDocDocument)):
                if node.reserved_uid is not None:
                    document_tree_stats.map_uid_to_nodes[node.reserved_uid] = (
                        node
                    )
                hasher = hashlib.md5()
                hasher.update(node.title.encode("utf-8"))
                map_nodes_to_hashers[node] = hasher

            elif isinstance(node, SDocNode):
                if node.reserved_uid is not None:
                    document_tree_stats.map_uid_to_nodes[node.reserved_uid] = (
                        node
                    )

                hasher = hashlib.md5()
                for (
                    field_name_,
                    field_values_,
                ) in node.ordered_fields_lookup.items():
                    requirement_field: SDocNodeField = field_values_[0]
                    requirement_field_value = requirement_field.get_text_value()
                    if field_name_ == "TITLE":
                        this_title_requirements = (
                            document_tree_stats.map_titles_to_nodes.setdefault(
                                requirement_field_value, []
                            )
                        )
                        this_title_requirements.append(node)
                    elif field_name_ == "STATEMENT":
                        document_tree_stats.map_statements_to_nodes[
                            requirement_field_value
                        ] = node

                    hasher.update(requirement_field_value.encode("utf-8"))

                    # If this field appears once, there is nothing else to do.
                    if len(field_values_) == 1:
                        continue

                    # At this point, we are dealing with COMMENT because it is
                    # the only field that can appear several times.
                    for comment_field_ in field_values_[1:]:
                        hasher.update(
                            comment_field_.get_text_value().encode("utf-8")
                        )

                for reference_ in node.relations:
                    if isinstance(
                        reference_, (ParentReqReference, ChildReqReference)
                    ):
                        hasher.update(reference_.ref_uid.encode("utf-8"))
                        if reference_.role is not None:
                            hasher.update(reference_.role.encode("utf-8"))

                map_nodes_to_hashers[node] = hasher
            else:
                raise AssertionError(node)

        def recurse(node):
            assert isinstance(node, (SDocSection, SDocDocument))
            for sub_node_ in node.section_contents:
                if isinstance(sub_node_, SDocSection):
                    map_nodes_to_hashers[node].update(recurse(sub_node_))
                elif isinstance(sub_node_, SDocNode):
                    node_md5 = (
                        map_nodes_to_hashers[sub_node_]
                        .hexdigest()
                        .encode("utf-8")
                    )
                    map_nodes_to_hashers[node].update(node_md5)
                else:
                    raise NotImplementedError(sub_node_)
            return map_nodes_to_hashers[node].hexdigest().encode("utf-8")

        # Keeping this code in case we will need to include child node hashes
        # to parent node hashes recursively. This was the original
        # implementation which we discarded. Now, each node's hash is
        # self-contained.
        # recurse(document)  # noqa: ERA001

        for node_ in document_iterator.all_content(
            print_fragments=True, print_fragments_from_files=False
        ):
            node_md5 = map_nodes_to_hashers[node_].hexdigest().encode("utf-8")
            map_nodes_to_hashers[document].update(node_md5)

        for node_, node_hasher_ in map_nodes_to_hashers.items():
            node_md5 = node_hasher_.hexdigest()
            document_tree_stats.map_nodes_to_hashes[node_] = node_md5

            if isinstance(node_, SDocSection):
                document_tree_stats.section_md5_hashes.add(node_md5)
            elif isinstance(node_, SDocNode):
                document_tree_stats.requirement_md5_hashes.add(node_md5)
            elif isinstance(node_, SDocDocument):
                document_tree_stats.document_md5_hashes.add(node_md5)
            else:
                raise NotImplementedError(node_)
