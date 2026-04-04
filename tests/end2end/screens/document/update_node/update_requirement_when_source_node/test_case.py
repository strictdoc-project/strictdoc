from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


class MergedNodeUpdateAndNormalizationE2ECase(E2ECase):
    """
    E2E Test: Verifies that for a merged node (which exists in .sdoc but fields
    are populated from source code) we can still edit the fields that are in the .sdoc document.
    When such a node is saved, we verify that any non-required fields are removed (normalized)
    as the source of truth for these fields is not the source code.
    """

    def test_merged_node_update(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            screen_project_index.assert_contains_document("Hybrid Document")
            screen_document = screen_project_index.do_click_on_first_document()

            screen_document.assert_on_screen_document()

            node = screen_document.get_node()

            form_edit_requirement: Form_EditRequirement = (
                node.do_open_form_edit_requirement()
            )

            form_edit_requirement.do_fill_in_field_rationale(
                "This is a rationale."
            )
            form_edit_requirement.do_form_submit()

        test_setup.compare_sandbox_and_expected_output()
