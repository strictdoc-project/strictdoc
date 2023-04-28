from seleniumbase import BaseCase

from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_section import (
    Form_EditSection,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test_UC03_T11_CreateSectionWithNonExistingRSTWildcardImage(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        # Run server.
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_ProjectIndex(self)

            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_contains_document("Document 1")

            screen_document = screen_document_tree.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")

            screen_document.assert_text("Hello world!")

            root_node = screen_document.get_root_node()
            root_node_menu = root_node.do_open_node_menu()
            form_edit_section: Form_EditSection = (
                root_node_menu.do_node_add_section_first()
            )

            form_edit_section.do_fill_in_title("First title")
            form_edit_section.do_fill_in_text(".. image:: _assets/picture.*")
            form_edit_section.do_form_submit_and_catch_error(
                "RST markup syntax error on line 1: "
                "No image could be found to match the wildcard: "
                "_assets/picture.*"
            )

        assert test_setup.compare_sandbox_and_expected_output()
