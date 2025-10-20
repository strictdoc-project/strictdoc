"""
@relation(SDOC-SRS-106, scope=file)
"""

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

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

            # Section 1

            root_node = screen_document.get_root_node()
            root_node_menu = root_node.do_open_node_menu()
            form_edit_section_1: Form_EditRequirement = (
                root_node_menu.do_node_add_element_first("SECTION")
            )

            form_edit_section_1.do_fill_in("TITLE", "Section_1")
            form_edit_section_1.do_form_submit()

            section_1 = screen_document.get_node()
            section_1.assert_requirement_title("Section_1", "1")
            screen_document.assert_toc_contains("Section_1")

            # Section 1_1 as child

            section_1_node_menu = section_1.do_open_node_menu()
            form_edit_section_2: Form_EditRequirement = (
                section_1_node_menu.do_node_add_element_child("SECTION")
            )

            form_edit_section_2.do_fill_in("TITLE", "Section_1_1")
            form_edit_section_2.do_form_submit()

            section_2 = screen_document.get_node(2)
            section_2.assert_requirement_title("Section_1_1", "1.1")
            screen_document.assert_toc_contains("Section_1_1")

            # # Section 1_1_1 as child

            section_2_node_menu = section_2.do_open_node_menu()
            form_edit_section_3: Form_EditRequirement = (
                section_2_node_menu.do_node_add_element_child("SECTION")
            )
            form_edit_section_3.do_fill_in("TITLE", "Section_1_1_1")
            form_edit_section_3.do_form_submit()

            section_3 = screen_document.get_node(3)
            section_3.assert_requirement_title("Section_1_1_1", "1.1.1")
            screen_document.assert_toc_contains("Section_1_1_1")

        assert test_setup.compare_sandbox_and_expected_output()
