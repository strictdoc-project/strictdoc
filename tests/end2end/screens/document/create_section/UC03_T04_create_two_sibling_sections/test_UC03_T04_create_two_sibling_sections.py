from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_section import (
    Form_EditSection,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test_UC03_T04_CreateTwoSiblingSections(BaseCase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        # Run server.
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document("Document 1")

            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")

            screen_document.assert_text("Hello world!")

            # Creating Section 1

            root_node = screen_document.get_root_node()
            root_node_menu = root_node.do_open_node_menu()
            form_edit_section_1: Form_EditSection = (
                root_node_menu.do_node_add_section_first()
            )

            form_edit_section_1.do_fill_in_title("First title")
            form_edit_section_1.do_fill_in_text(
                "This is a free text of the first section."
            )
            form_edit_section_1.do_form_submit()

            section_1 = screen_document.get_section()

            section_1.assert_section_title("First title", "1")
            screen_document.assert_toc_contains("First title")

            # Creating Section 2 below

            section_1_node_menu = section_1.do_open_node_menu()

            form_edit_section2: Form_EditSection = (
                section_1_node_menu.do_node_add_section_below()
            )
            form_edit_section2.do_fill_in_title("Second title")
            form_edit_section2.do_fill_in_text(
                "This is a free text of the second section."
            )
            form_edit_section2.do_form_submit()

            section2 = screen_document.get_section(2)

            section2.assert_section_title("Second title", "2")
            screen_document.assert_toc_contains("Second title")

        assert test_setup.compare_sandbox_and_expected_output()
