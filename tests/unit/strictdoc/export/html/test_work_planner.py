from strictdoc.export.html.generators.view_objects.work_planner_view_object import (
    WorkPlannerEpicCard,
)
from strictdoc.export.html.generators.work_planner import _assign_stack_levels


def _create_epic(
    *, title: str, start_offset: float, end_offset: float
) -> WorkPlannerEpicCard:
    return WorkPlannerEpicCard(
        node=None,
        document=None,
        title=title,
        statement="",
        status="Ready",
        status_css_class="ready",
        time_start=None,
        time_end=None,
        work_package_uid=None,
        start_month_index=int(start_offset),
        end_month_index=int(end_offset),
        start_offset=start_offset,
        end_offset=end_offset,
    )


def test_assign_stack_levels_reuses_level_when_epics_only_touch():
    epic_a = _create_epic(title="A", start_offset=0.0, end_offset=1.0)
    epic_b = _create_epic(title="B", start_offset=1.0, end_offset=2.0)
    epic_c = _create_epic(title="C", start_offset=2.0, end_offset=3.0)

    _assign_stack_levels([epic_b, epic_c, epic_a])

    assert epic_a.stack_level == 0
    assert epic_b.stack_level == 0
    assert epic_c.stack_level == 0


def test_assign_stack_levels_minimizes_levels_for_chain_overlap():
    epic_a = _create_epic(title="A", start_offset=0.0, end_offset=2.0)
    epic_b = _create_epic(title="B", start_offset=1.0, end_offset=3.0)
    epic_c = _create_epic(title="C", start_offset=2.0, end_offset=4.0)

    _assign_stack_levels([epic_c, epic_a, epic_b])

    assert epic_a.stack_level == 0
    assert epic_b.stack_level == 1
    assert epic_c.stack_level == 0
