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


class Test_UC03_T02_CreateBeforeSection(BaseCase):
    def test_01(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_DocumentTree(self)

            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_contains_document("Document 1")

            screen_document = screen_document_tree.do_click_on_first_document()

            screen_document.assert_on_screen()
            screen_document.assert_is_document_title("Document 1")

            screen_document.assert_text("Hello world!")

            existing_node_number = NODE_1

            screen_document.assert_node_title_contains(
                "Section B", "1", existing_node_number
            )

            form_edit_section: Form_EditSection = (
                screen_document.do_node_add_section_above(existing_node_number)
            )

            form_edit_section.do_fill_in_title("Section A")
            form_edit_section.do_fill_in_text("Section A text.")
            form_edit_section.do_form_submit()

            screen_document.assert_node_title_contains(
                "Section A", "1", existing_node_number
            )
            screen_document.assert_node_title_contains(
                "Section B", "2", existing_node_number + 1
            )

            screen_document.assert_toc_contains_string("Section A")
            screen_document.assert_toc_contains_string("Section B")

        assert test_setup.compare_sandbox_and_expected_output()
