"""
@relation(SDOC-SRS-205, scope=file)
"""

import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.helpers.screens.work_planner.work_planner import (
    Screen_WorkPlanner,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    def test_view_work_planner(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()
            screen_project_index.assert_link_to_work_planner_present()

            work_planner_screen: Screen_WorkPlanner = (
                screen_project_index.do_click_on_work_planner_link()
            )
            work_planner_screen.assert_on_screen()
            work_planner_screen.assert_contains_text("Work planner")
            work_planner_screen.assert_visible_text_present(
                "Buildrolloutboardupdated"
            )
            work_planner_screen.assert_visible_text_present(
                "Prepare telemetry checks"
            )
            work_planner_screen.assert_visible_text_not_present("Jane Doe")
            work_planner_screen.assert_visible_text_not_present(
                "Flight software"
            )
            work_planner_screen.assert_visible_text_not_present("Beta package")

    def test_create_backlog_epic_from_work_planner(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            work_planner_screen: Screen_WorkPlanner = (
                screen_project_index.do_click_on_work_planner_link()
            )
            work_planner_screen.assert_on_screen()

            form_edit_requirement = work_planner_screen.do_open_add_epic_form()
            form_edit_requirement.do_fill_in_field_title("PlannerEpicFromWorkPlanner")
            form_edit_requirement.do_fill_in_field_statement(
                "PlannerEpicCreatedViaPlanner."
            )
            form_edit_requirement.do_form_submit()

            self.open(f"{test_server.get_host_and_port()}/work_planner.html")
            work_planner_screen.assert_on_screen()
            work_planner_screen.assert_contains_text(
                "PlannerEpicFromWorkPlanner"
            )

    def test_pan_work_planner_canvas_horizontally(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            work_planner_screen: Screen_WorkPlanner = (
                screen_project_index.do_click_on_work_planner_link()
            )
            work_planner_screen.assert_on_screen()

            initial_scroll_left = work_planner_screen.get_canvas_scroll_left()
            work_planner_screen.do_pan_canvas_to_the_right()
            updated_scroll_left = work_planner_screen.get_canvas_scroll_left()

            assert updated_scroll_left > initial_scroll_left, (
                initial_scroll_left,
                updated_scroll_left,
            )

    def test_pan_work_planner_canvas_vertically(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            work_planner_screen: Screen_WorkPlanner = (
                screen_project_index.do_click_on_work_planner_link()
            )
            work_planner_screen.assert_on_screen()
            for _ in range(6):
                work_planner_screen.do_click_zoom_in()

            initial_scroll_top = work_planner_screen.get_canvas_scroll_top()
            work_planner_screen.do_pan_canvas_down()
            updated_scroll_top = work_planner_screen.get_canvas_scroll_top()

            assert updated_scroll_top > initial_scroll_top, (
                initial_scroll_top,
                updated_scroll_top,
            )

    def test_pan_work_planner_canvas_after_edit(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            work_planner_screen: Screen_WorkPlanner = (
                screen_project_index.do_click_on_work_planner_link()
            )
            work_planner_screen.assert_on_screen()

            form_edit_requirement = work_planner_screen.do_open_edit_epic_form()
            form_edit_requirement.do_clear_field("TITLE")
            form_edit_requirement.do_fill_in_field_title(
                "Build rollout board updated"
            )
            form_edit_requirement.do_form_submit()

            work_planner_screen.assert_on_screen()

            initial_scroll_left = work_planner_screen.get_canvas_scroll_left()
            work_planner_screen.do_pan_canvas_to_the_right()
            updated_scroll_left = work_planner_screen.get_canvas_scroll_left()

            assert updated_scroll_left > initial_scroll_left, (
                initial_scroll_left,
                updated_scroll_left,
            )

    def test_all_epics_do_not_overlap(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            work_planner_screen: Screen_WorkPlanner = (
                screen_project_index.do_click_on_work_planner_link()
            )
            work_planner_screen.assert_on_screen()
            work_planner_screen.assert_lane_epics_do_not_overlap("All epics")

    def test_zoom_work_planner_canvas_with_buttons(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            work_planner_screen: Screen_WorkPlanner = (
                screen_project_index.do_click_on_work_planner_link()
            )
            work_planner_screen.assert_on_screen()
            work_planner_screen.do_click_zoom_reset()

            initial_scale = work_planner_screen.get_zoom_scale()
            work_planner_screen.do_click_zoom_in()
            zoomed_in_scale = work_planner_screen.get_zoom_scale()
            work_planner_screen.do_click_zoom_out()
            zoomed_out_scale = work_planner_screen.get_zoom_scale()

            assert zoomed_in_scale > initial_scale, (
                initial_scale,
                zoomed_in_scale,
            )
            assert zoomed_out_scale < zoomed_in_scale, (
                zoomed_in_scale,
                zoomed_out_scale,
            )

    def test_zoom_work_planner_canvas_with_ctrl_wheel(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            work_planner_screen: Screen_WorkPlanner = (
                screen_project_index.do_click_on_work_planner_link()
            )
            work_planner_screen.assert_on_screen()
            work_planner_screen.do_click_zoom_reset()

            initial_scale = work_planner_screen.get_zoom_scale()
            work_planner_screen.do_zoom_canvas_with_ctrl_wheel(-120)
            zoomed_in_scale = work_planner_screen.get_zoom_scale()
            work_planner_screen.do_zoom_canvas_with_ctrl_wheel(120)
            zoomed_out_scale = work_planner_screen.get_zoom_scale()

            assert zoomed_in_scale > initial_scale, (
                initial_scale,
                zoomed_in_scale,
            )
            assert zoomed_out_scale < zoomed_in_scale, (
                zoomed_in_scale,
                zoomed_out_scale,
            )

    def test_zoom_work_planner_canvas_limits(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            work_planner_screen: Screen_WorkPlanner = (
                screen_project_index.do_click_on_work_planner_link()
            )
            work_planner_screen.assert_on_screen()
            work_planner_screen.do_click_zoom_reset()

            for _ in range(20):
                work_planner_screen.do_click_zoom_in()

            zoomed_in_state = work_planner_screen.get_zoom_state()
            assert abs(
                zoomed_in_state["scale"] - zoomed_in_state["maxScale"]
            ) < 0.02, zoomed_in_state

            for _ in range(30):
                work_planner_screen.do_click_zoom_out()

            zoomed_out_state = work_planner_screen.get_zoom_state()
            assert abs(
                zoomed_out_state["scale"] - zoomed_out_state["minScale"]
            ) < 0.02, zoomed_out_state
            assert (
                zoomed_out_state["scrollWidth"]
                <= zoomed_out_state["clientWidth"] + 1
            ), zoomed_out_state
            assert (
                zoomed_out_state["scrollHeight"]
                <= zoomed_out_state["clientHeight"] + 1
            ), zoomed_out_state
            assert abs(zoomed_out_state["monthWidth"] - 160) < 0.1, (
                zoomed_out_state
            )

    def test_zoom_work_planner_canvas_after_edit_with_ctrl_wheel(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            work_planner_screen: Screen_WorkPlanner = (
                screen_project_index.do_click_on_work_planner_link()
            )
            work_planner_screen.assert_on_screen()
            work_planner_screen.do_click_zoom_reset()

            form_edit_requirement = work_planner_screen.do_open_edit_epic_form()
            form_edit_requirement.do_clear_field("TITLE")
            form_edit_requirement.do_fill_in_field_title(
                "Build rollout board updated"
            )
            form_edit_requirement.do_form_submit()

            work_planner_screen.assert_on_screen()

            initial_scale = work_planner_screen.get_zoom_scale()
            work_planner_screen.do_zoom_canvas_with_ctrl_wheel(-120)
            updated_scale = work_planner_screen.get_zoom_scale()

            assert updated_scale > initial_scale, (
                initial_scale,
                updated_scale,
            )
