from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.constants import NODE_1
from tests.end2end.helpers.screens.document.form_edit_section import (
    Form_EditSection,
)
from tests.end2end.helpers.screens.document_tree.screen_document_tree import (
    Screen_DocumentTree,
)
from tests.end2end.server import SDocTestServer


class Test_UC03_T04_CreateTwoSiblingSections(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        # Run server.
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_DocumentTree(self)

            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_contains_document("Document 1")

            screen_document = screen_document_tree.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")

            screen_document.assert_text("Hello world!")

            # Creating Section 1
            first_added_node_number = NODE_1

            root_node = screen_document.get_root_node()
            root_node_menu = root_node.do_open_node_menu()
            form_edit_section: Form_EditSection = (
                root_node_menu.do_node_add_section_first()
            )

            form_edit_section.do_fill_in_title("First title")
            form_edit_section.do_fill_in_text(
                "This is a free text of the first section."
            )
            form_edit_section.do_form_submit()

            section = screen_document.get_section(first_added_node_number)

            section.assert_section_title(
                "First title", "1", first_added_node_number
            )
            screen_document.assert_toc_contains("First title")

            # Creating Section 2 below
            second_added_node_number = first_added_node_number + 1

            section_node_menu = section.do_open_node_menu(
                first_added_node_number
            )

            form_edit_section2: Form_EditSection = (
                section_node_menu.do_node_add_section_below()
            )
            form_edit_section2.do_fill_in_title("Second title")
            form_edit_section2.do_fill_in_text(
                "This is a free text of the second section."
            )
            form_edit_section2.do_form_submit()

            section2 = screen_document.get_section(second_added_node_number)

            section2.assert_section_title(
                "Second title", "2", second_added_node_number
            )
            screen_document.assert_toc_contains("Second title")

        assert test_setup.compare_sandbox_and_expected_output()
