import calendar
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import DefaultDict, Dict, List, Optional, Tuple

from markupsafe import Markup

from strictdoc.backend.sdoc.models.document import SDocDocument
from strictdoc.backend.sdoc.models.model import RequirementFieldName
from strictdoc.backend.sdoc.models.node import SDocNode
from strictdoc.core.project_config import ProjectConfig
from strictdoc.core.traceability_index import TraceabilityIndex
from strictdoc.export.html.generators.view_objects.work_planner_view_object import (
    WorkPlannerBacklogWorkPackage,
    WorkPlannerDocumentOption,
    WorkPlannerEpicCard,
    WorkPlannerLane,
    WorkPlannerMonth,
    WorkPlannerTeamGroup,
    WorkPlannerViewObject,
    WorkPlannerWorkPackageLane,
)
from strictdoc.export.html.html_templates import HTMLTemplates
from strictdoc.export.html.renderers.link_renderer import LinkRenderer
from strictdoc.helpers.cast import assert_cast

STATUS_TO_CSS_CLASS = {
    "Ready": "ready",
    "WIP": "wip",
    "Done": "done",
    "Draft": "draft",
}

_STACK_EPSILON = 1e-9
_MIN_VISIBLE_SPAN = 1e-6


@dataclass
class _ScheduledEpic:
    epic: WorkPlannerEpicCard
    work_package: Optional[SDocNode]
    start_dt: datetime
    end_dt: datetime


def _get_field_text(node: SDocNode, field_name: str) -> Optional[str]:
    if field_name not in node.ordered_fields_lookup:
        return None
    field = node.ordered_fields_lookup[field_name][0]
    text = field.get_text_value().strip()
    if len(text) == 0:
        return None
    return text


def _parse_iso_8601(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    normalized = value.strip()
    if len(normalized) == 0:
        return None
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _iterate_month_keys(
    start_key: Tuple[int, int], end_key: Tuple[int, int]
) -> List[Tuple[int, int]]:
    current_year, current_month = start_key
    end_year, end_month = end_key
    result: List[Tuple[int, int]] = []
    while (current_year, current_month) <= (end_year, end_month):
        result.append((current_year, current_month))
        if current_month == 12:
            current_year += 1
            current_month = 1
        else:
            current_month += 1
    return result


def _month_key(value: datetime) -> Tuple[int, int]:
    return value.year, value.month


def _month_label(value: Tuple[int, int]) -> str:
    return f"{value[0]:04d}-{value[1]:02d}"


def _month_fraction(value: datetime) -> float:
    days_in_month = calendar.monthrange(value.year, value.month)[1]
    month_start = value.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    elapsed_seconds = (value - month_start).total_seconds()
    return elapsed_seconds / (days_in_month * 24 * 60 * 60)


def _assign_stack_levels(epics: List[WorkPlannerEpicCard]) -> None:
    # Greedy interval partitioning: place each epic onto the first level whose
    # current right edge does not overlap the epic's left edge. This minimizes
    # the number of levels for interval graphs and satisfies SDOC-LLR-211.
    row_ends: List[float] = []
    for epic in sorted(
        epics,
        key=lambda current: (
            current.start_offset,
            current.end_offset,
            current.title.lower(),
        ),
    ):
        for row_index, row_end in enumerate(row_ends):
            if epic.start_offset >= row_end - _STACK_EPSILON:
                epic.stack_level = row_index
                row_ends[row_index] = epic.end_offset
                break
        else:
            epic.stack_level = len(row_ends)
            row_ends.append(epic.end_offset)


class WorkPlannerHTMLGenerator:
    @staticmethod
    def create_view_object(
        *,
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
    ) -> WorkPlannerViewObject:
        work_packages: List[SDocNode] = []

        document_options: List[WorkPlannerDocumentOption] = []
        for document in traceability_index.document_tree.document_list:
            document_options.append(
                WorkPlannerDocumentOption(
                    mid=document.reserved_mid.get_string_value(),
                    title=document.title,
                )
            )
            for node in document.iterate_nodes("WORK_PACKAGE"):
                work_package = assert_cast(node, SDocNode)
                work_packages.append(work_package)

        scheduled_epics: List[_ScheduledEpic] = []
        backlog_epics: List[WorkPlannerEpicCard] = []
        backlog_epics_by_work_package_mid: DefaultDict[
            str, List[WorkPlannerEpicCard]
        ] = defaultdict(list)
        scheduled_epics_by_work_package_mid: DefaultDict[
            str, List[WorkPlannerEpicCard]
        ] = defaultdict(list)

        month_keys: List[Tuple[int, int]] = []

        for document in traceability_index.document_tree.document_list:
            for node in document.iterate_nodes("EPIC"):
                epic_node = assert_cast(node, SDocNode)
                parent_work_package: Optional[SDocNode] = None
                for parent in traceability_index.get_parent_requirements(
                    epic_node
                ):
                    if parent.node_type == "WORK_PACKAGE":
                        parent_work_package = assert_cast(parent, SDocNode)
                        break

                time_start_text = _get_field_text(
                    epic_node, RequirementFieldName.TIME_START
                )
                time_end_text = _get_field_text(
                    epic_node, RequirementFieldName.TIME_END
                )
                time_start = _parse_iso_8601(time_start_text)
                time_end = _parse_iso_8601(time_end_text)

                epic_card = WorkPlannerEpicCard(
                    node=epic_node,
                    document=document,
                    title=epic_node.reserved_title or epic_node.get_display_title(),
                    statement=epic_node.reserved_statement or "",
                    status=_get_field_text(
                        epic_node, RequirementFieldName.STATUS
                    )
                    or "",
                    status_css_class=STATUS_TO_CSS_CLASS.get(
                        _get_field_text(epic_node, RequirementFieldName.STATUS)
                        or "",
                        "ready",
                    ),
                    assigned_person=_get_field_text(
                        epic_node, RequirementFieldName.ASSIGNED_PERSON
                    )
                    or "Unassigned person",
                    assigned_team=_get_field_text(
                        epic_node, RequirementFieldName.ASSIGNED_TEAM
                    )
                    or "Unassigned team",
                    time_start=time_start_text,
                    time_end=time_end_text,
                    work_package_uid=(
                        parent_work_package.reserved_uid
                        if parent_work_package is not None
                        else None
                    ),
                    work_package_title=(
                        parent_work_package.reserved_title
                        if parent_work_package is not None
                        else None
                    ),
                    start_month_index=0,
                    end_month_index=0,
                )

                if time_start is not None and time_end is not None:
                    if time_end <= time_start:
                        time_end = time_start + timedelta(minutes=1)
                    scheduled_epics.append(
                        _ScheduledEpic(
                            epic=epic_card,
                            work_package=parent_work_package,
                            start_dt=time_start,
                            end_dt=time_end,
                        )
                    )
                    if parent_work_package is not None:
                        scheduled_epics_by_work_package_mid[
                            parent_work_package.reserved_mid.get_string_value()
                        ].append(epic_card)
                    month_keys.append(_month_key(time_start))
                    month_keys.append(_month_key(time_end))
                else:
                    backlog_epics.append(epic_card)
                    if parent_work_package is not None:
                        backlog_epics_by_work_package_mid[
                            parent_work_package.reserved_mid.get_string_value()
                        ].append(epic_card)

        months: List[WorkPlannerMonth] = []
        month_indexes: Dict[Tuple[int, int], int] = {}
        if len(month_keys) > 0:
            start_key = min(month_keys)
            end_key = max(month_keys)
            month_key_range = _iterate_month_keys(start_key, end_key)
            for month_index, month_key_ in enumerate(month_key_range):
                month_indexes[month_key_] = month_index
                months.append(
                    WorkPlannerMonth(
                        index=month_index,
                        label=_month_label(month_key_),
                    )
                )

        for scheduled_epic in scheduled_epics:
            scheduled_epic.epic.start_month_index = month_indexes[
                _month_key(scheduled_epic.start_dt)
            ]
            scheduled_epic.epic.end_month_index = month_indexes[
                _month_key(scheduled_epic.end_dt)
            ]
            scheduled_epic.epic.start_offset = (
                scheduled_epic.epic.start_month_index
                + _month_fraction(scheduled_epic.start_dt)
            )
            scheduled_epic.epic.end_offset = (
                scheduled_epic.epic.end_month_index
                + _month_fraction(scheduled_epic.end_dt)
            )
            if scheduled_epic.epic.end_offset <= scheduled_epic.epic.start_offset:
                scheduled_epic.epic.end_offset = (
                    scheduled_epic.epic.start_offset + _MIN_VISIBLE_SPAN
                )

        person_groups: DefaultDict[str, List[WorkPlannerEpicCard]] = defaultdict(
            list
        )
        team_groups: DefaultDict[
            str, DefaultDict[str, List[WorkPlannerEpicCard]]
        ] = defaultdict(lambda: defaultdict(list))
        ungrouped_work_package_epics: List[WorkPlannerEpicCard] = []

        for scheduled_epic in scheduled_epics:
            epic_card = scheduled_epic.epic
            person_groups[epic_card.assigned_person].append(epic_card)
            team_groups[epic_card.assigned_team][epic_card.assigned_person].append(
                epic_card
            )
            if scheduled_epic.work_package is None:
                ungrouped_work_package_epics.append(epic_card)

        person_lanes: List[WorkPlannerLane] = []
        for person_title in sorted(person_groups.keys(), key=str.lower):
            lane_epics = person_groups[person_title]
            _assign_stack_levels(lane_epics)
            person_lanes.append(
                WorkPlannerLane(
                    title=person_title,
                    subtitle=f"{len(lane_epics)} epic(s)",
                    epics=lane_epics,
                )
            )

        team_group_objects: List[WorkPlannerTeamGroup] = []
        for team_title in sorted(team_groups.keys(), key=str.lower):
            lanes: List[WorkPlannerLane] = []
            persons = team_groups[team_title]
            for person_title in sorted(persons.keys(), key=str.lower):
                lane_epics = persons[person_title]
                _assign_stack_levels(lane_epics)
                lanes.append(
                    WorkPlannerLane(
                        title=person_title,
                        subtitle=f"{len(lane_epics)} epic(s)",
                        epics=lane_epics,
                    )
                )
            team_group_objects.append(
                WorkPlannerTeamGroup(title=team_title, lanes=lanes)
            )

        work_package_lanes: List[WorkPlannerWorkPackageLane] = []
        for work_package in sorted(
            work_packages,
            key=lambda current: (
                current.reserved_title or "",
                current.reserved_uid or "",
            ),
        ):
            work_package_mid = work_package.reserved_mid.get_string_value()
            epics = scheduled_epics_by_work_package_mid.get(work_package_mid, [])
            if len(epics) == 0:
                continue
            _assign_stack_levels(epics)
            work_package_lanes.append(
                WorkPlannerWorkPackageLane(
                    node=work_package,
                    document=assert_cast(
                        work_package.get_document(), SDocDocument
                    ),
                    title=work_package.reserved_title
                    or work_package.get_display_title(),
                    statement=work_package.reserved_statement or "",
                    start_month_index=min(
                        epic.start_month_index for epic in epics
                    ),
                    end_month_index=max(epic.end_month_index for epic in epics),
                    start_offset=min(epic.start_offset for epic in epics),
                    end_offset=max(epic.end_offset for epic in epics),
                    epics=epics,
                )
            )

        if len(ungrouped_work_package_epics) > 0:
            _assign_stack_levels(ungrouped_work_package_epics)
            work_package_lanes.append(
                WorkPlannerWorkPackageLane(
                    node=None,
                    document=None,
                    title="Ungrouped epics",
                    statement="Scheduled epics without a work package.",
                    start_month_index=min(
                        epic.start_month_index
                        for epic in ungrouped_work_package_epics
                    ),
                    end_month_index=max(
                        epic.end_month_index
                        for epic in ungrouped_work_package_epics
                    ),
                    start_offset=min(
                        epic.start_offset
                        for epic in ungrouped_work_package_epics
                    ),
                    end_offset=max(
                        epic.end_offset
                        for epic in ungrouped_work_package_epics
                    ),
                    epics=ungrouped_work_package_epics,
                )
            )

        backlog_work_packages: List[WorkPlannerBacklogWorkPackage] = []
        for work_package in sorted(
            work_packages,
            key=lambda current: (
                current.reserved_title or "",
                current.reserved_uid or "",
            ),
        ):
            work_package_mid = work_package.reserved_mid.get_string_value()
            scheduled_children = scheduled_epics_by_work_package_mid.get(
                work_package_mid, []
            )
            backlog_children = backlog_epics_by_work_package_mid.get(
                work_package_mid, []
            )
            if len(backlog_children) == 0 and len(scheduled_children) > 0:
                continue
            backlog_work_packages.append(
                WorkPlannerBacklogWorkPackage(
                    node=work_package,
                    document=assert_cast(
                        work_package.get_document(), SDocDocument
                    ),
                    title=work_package.reserved_title
                    or work_package.get_display_title(),
                    statement=work_package.reserved_statement or "",
                    epics=backlog_children,
                )
            )

        backlog_epics_without_work_package = [
            epic
            for epic in backlog_epics
            if epic.work_package_uid is None
        ]

        link_renderer = LinkRenderer(
            root_path="",
            static_path=project_config.dir_for_sdoc_assets,
        )

        return WorkPlannerViewObject(
            traceability_index=traceability_index,
            project_config=project_config,
            link_renderer=link_renderer,
            documents=document_options,
            default_document_mid=(
                document_options[0].mid if len(document_options) > 0 else None
            ),
            months=months,
            person_lanes=person_lanes,
            team_groups=team_group_objects,
            work_package_lanes=work_package_lanes,
            backlog_work_packages=backlog_work_packages,
            backlog_epics=backlog_epics_without_work_package,
        )

    @staticmethod
    def export(
        *,
        project_config: ProjectConfig,
        traceability_index: TraceabilityIndex,
        html_templates: HTMLTemplates,
    ) -> Markup:
        view_object = WorkPlannerHTMLGenerator.create_view_object(
            project_config=project_config,
            traceability_index=traceability_index,
        )
        return view_object.render_screen(html_templates.jinja_environment())
