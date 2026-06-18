"""
Regression test for https://github.com/strictdoc-project/strictdoc/issues/2923

When a Markdown document uses a custom grammar that declares a MID field, the
web editor must pre-populate the MID form field with a generated UUID when the
user opens the "create requirement" form.

Before the fix the MID field was left empty. With MID declared as Required:
True, submitting the empty form would fail server-side validation with
"Node's MID must not be empty." — confirming the field was not pre-populated.

After the fix the form receives a pre-generated UUID, the submission succeeds,
and the saved requirement carries a MID.
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

            # Open the create-requirement form and submit without manually
            # entering a MID value. The grammar declares MID as Required: True,
            # so if the form did NOT pre-populate MID the server would reject
            # the submission with a validation error. Success here proves that
            # the MID field was pre-populated by the server.
            root_node = screen_document.get_root_node()
            root_node_menu = root_node.do_open_node_menu()
            form_edit_requirement: Form_EditRequirement = (
                root_node_menu.do_node_add_requirement_first()
            )

            form_edit_requirement.do_fill_in_field_title("Requirement title #1")
            form_edit_requirement.do_fill_in_field_statement(
                "Requirement statement #1."
            )
            form_edit_requirement.do_form_submit()

            requirement_1 = screen_document.get_node()
            requirement_1.assert_requirement_has_mid()

        # MID is always a freshly generated UUID so we cannot compare files.
