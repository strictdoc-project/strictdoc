"""
@relation(SDOC-SRS-205, scope=file)
"""

import os

from selenium.webdriver.common.by import By

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
            work_planner_screen.assert_contains_text("Beta package")

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

    def test_pan_work_planner_canvas(self):
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
