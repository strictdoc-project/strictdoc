import os

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))


class Test(E2ECase):
    """
    Ensures that this does no longer happen:
    AssertionError when updating the relation for a requirement #1856,
    https://github.com/strictdoc-project/strictdoc/issues/1856
    """

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
            screen_document.assert_not_empty_document()

            requirement = screen_document.get_node(3)
            form_edit_requirement: Form_EditRequirement = (
                requirement.do_open_form_edit_requirement()
            )
            form_edit_requirement.do_open_tab("Relations")

            node_mid = form_edit_requirement.get_node_relation_form_mid(1)
            form_edit_requirement.do_fill_in_field_relation(node_mid, "REQ-2")

            form_edit_requirement.do_form_submit()

        assert test_setup.compare_sandbox_and_expected_output()
