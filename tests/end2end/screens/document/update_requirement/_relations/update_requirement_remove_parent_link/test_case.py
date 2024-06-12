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

            requirement1 = screen_document.get_requirement(1)
            requirement2 = screen_document.get_requirement(2)

            # Make sure there is the reference to the child in Requirement 1:
            requirement1.assert_requirement_uid_contains("REQ-001")
            requirement1.assert_requirement_has_child_relation("REQ-002")
            # Make sure there is the reference to the parent in Requirement 2:
            requirement2.assert_requirement_uid_contains("REQ-002")
            requirement2.assert_requirement_has_parent_relation("REQ-001")

            # edit the second requirement

            form_edit_requirement: Form_EditRequirement = (
                requirement2.do_open_form_edit_requirement()
            )
            form_edit_requirement.do_open_tab("Relations")
            form_edit_requirement.assert_form_has_relations()
            form_edit_requirement.do_delete_relation()
            # Make sure that the field is removed from the form:
            form_edit_requirement.assert_form_has_no_relations()
            form_edit_requirement.do_form_submit()

            # Make sure there is no reference to the child in Requirement 1:
            requirement1.assert_requirement_uid_contains("REQ-001")
            requirement1.assert_requirement_has_not_child_relation("REQ-002")
            # Make sure there is no reference to the parent in Requirement 2:
            requirement2.assert_requirement_uid_contains("REQ-002")
            requirement2.assert_requirement_has_not_parent_relation("REQ-001")

        assert test_setup.compare_sandbox_and_expected_output()
