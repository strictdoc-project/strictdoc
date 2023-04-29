from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.collapsible_list import CollapsibleList
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test_UC112_T01_UI_toc(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document title")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document title")
            screen_document.assert_text("Hello world!")

            collapsible_list: CollapsibleList = (
                screen_document.get_collapsible_list()
            )

            collapsible_list.assert_is_expanded("Section 1 title")
            collapsible_list.assert_is_expanded("Section 2 title")
            collapsible_list.assert_visible("Section 1 title")
            collapsible_list.assert_visible("Section 2 title")
            collapsible_list.assert_visible("Nested section 1 title")
            collapsible_list.assert_visible("Nested section 2 title")
            collapsible_list.assert_all_is_expanded()

            # test single item

            collapsible_list.do_toggle_collapsible("Section 1 title")
            collapsible_list.do_toggle_collapsible("Section 2 title")

            collapsible_list.assert_is_collapsed("Section 1 title")
            collapsible_list.assert_is_collapsed("Section 2 title")
            collapsible_list.assert_visible("Section 1 title")
            collapsible_list.assert_visible("Section 2 title")
            collapsible_list.assert_visible_not("Nested section 1 title")
            collapsible_list.assert_visible_not("Nested section 2 title")

            collapsible_list.assert_all_is_collapsed()

            collapsible_list.do_toggle_collapsible("Section 1 title")
            collapsible_list.do_toggle_collapsible("Section 2 title")

            collapsible_list.assert_is_expanded("Section 1 title")
            collapsible_list.assert_is_expanded("Section 2 title")
            collapsible_list.assert_visible("Section 1 title")
            collapsible_list.assert_visible("Section 2 title")
            collapsible_list.assert_visible("Nested section 1 title")
            collapsible_list.assert_visible("Nested section 2 title")

            collapsible_list.assert_all_is_expanded()

            # test bulk operation

            collapsible_list.do_bulk_collapse("Section 1 title")
            collapsible_list.assert_all_is_collapsed()
            collapsible_list.assert_visible_not("Nested section 1 title")
            collapsible_list.assert_visible_not("Nested section 2 title")

            collapsible_list.do_bulk_expand("Section 1 title")
            collapsible_list.assert_all_is_expanded()
            collapsible_list.assert_visible("Nested section 1 title")
            collapsible_list.assert_visible("Nested section 2 title")

            # test session storage

            collapsible_list.assert_all_is_expanded()
            self.refresh()
            collapsible_list.assert_all_is_expanded()

            collapsible_list.do_bulk_collapse("Section 1 title")
            collapsible_list.assert_all_is_collapsed()
            self.refresh()
            collapsible_list.assert_all_is_collapsed()

        assert test_setup.compare_sandbox_and_expected_output()
