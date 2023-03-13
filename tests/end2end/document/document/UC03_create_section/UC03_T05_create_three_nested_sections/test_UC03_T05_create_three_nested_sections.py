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


class Test_UC03_T05_CreateThreeNestedSections(BaseCase):
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

            # Section 1
            added_node_1_order = NODE_1
            added_node_1_level = "1"

            form_edit_section: Form_EditSection = (
                screen_document.do_node_add_section_first()
            )
            form_edit_section.do_fill_in_title("Section_1")
            form_edit_section.do_fill_in_text(
                "This is a free text of the section 1."
            )
            form_edit_section.do_form_submit()

            screen_document.assert_node_title_contains(
                "Section_1", added_node_1_level, added_node_1_order
            )
            screen_document.assert_toc_contains_string("Section_1")

            # Section 1_1 as child
            added_node_2_order = added_node_1_order + 1
            added_node_2_level = "1.1"

            form_edit_section: Form_EditSection = (
                screen_document.do_node_add_section_child(added_node_1_order)
            )
            form_edit_section.do_fill_in_title("Section_1_1")
            form_edit_section.do_fill_in_text(
                "This is a free text of the section 1_1."
            )
            form_edit_section.do_form_submit()

            screen_document.assert_node_title_contains(
                "Section_1_1", added_node_2_level, added_node_2_order
            )
            screen_document.assert_toc_contains_string("Section_1_1")

            # # Section 1_1_1 as child
            added_node_3_order = added_node_2_order + 1
            added_node_3_level = "1.1.1"

            form_edit_section: Form_EditSection = (
                screen_document.do_node_add_section_child(added_node_2_order)
            )
            form_edit_section.do_fill_in_title("Section_1_1_1")
            form_edit_section.do_fill_in_text(
                "This is a free text of the section 1_1_1."
            )
            form_edit_section.do_form_submit()

            screen_document.assert_node_title_contains(
                "Section_1_1_1", added_node_3_level, added_node_3_order
            )
            screen_document.assert_toc_contains_string("Section_1_1_1")

        assert test_setup.compare_sandbox_and_expected_output()
