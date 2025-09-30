from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.node.add_node_menu import AddNode_Menu
from tests.end2end.helpers.components.node.requirement import Requirement
from tests.end2end.helpers.components.node.section import Section
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

            section: Section = screen_document.get_section(node_order=1)

            section_menu: AddNode_Menu = section.do_open_node_menu()
            form_edit_section: Form_EditRequirement = (
                section_menu.do_node_add_requirement_above()
            )

            form_edit_section.do_fill_in_field_title("Requirement title")
            form_edit_section.do_fill_in_field_statement(
                "Requirement statement."
            )

            form_edit_section.do_form_submit()

            requirement: Requirement = screen_document.get_node(2)

            requirement.assert_requirement_title("Requirement title")

            screen_document.assert_toc_contains("Requirement title")

            screen_document.get_root_node().assert_document_title_contains(
                "Document 1"
            )

            #
            # A basic extra test that ensures that the requirement has a right
            # document parent (encountered this regression during implementation).
            #
            form_edit_requirement = requirement.do_open_form_edit_requirement()
            form_edit_requirement.do_form_submit()

            screen_document.assert_toc_contains("Section Foobar")
            screen_document.assert_toc_contains("Requirement title")

        assert test_setup.compare_sandbox_and_expected_output()
