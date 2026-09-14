"""
@relation(SDOC-SRS-55, scope=file)
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

            requirement = screen_document.get_node()
            form_edit_requirement: Form_EditRequirement = (
                requirement.do_open_form_edit_requirement()
            )

            # This test checks the submission and server-side validation of an
            # invalid MultipleChoice value.
            #
            # An autocomplete field has two elements. The user enters text in
            # the visible contenteditable element. The browser does not include
            # the content of that element when it submits the HTML form. The
            # adjacent hidden input provides the submitted value, so the input
            # event handler must copy the visible text there immediately.
            #
            # Loading the autocomplete options is delayed. Updating the hidden
            # input must not depend on that delay. Otherwise, the user could
            # submit the form immediately after typing, when the visible field
            # already contains INCORRECT but the hidden input still contains
            # the previous value, A.
            #
            # The test simulates an immediate form submission after typing. It
            # writes INCORRECT to the visible field, dispatches the input event,
            # and checks the hidden input before the browser can run the delayed
            # autocomplete option loading. This reproduces the moment when the
            # user has finished typing but the timer callback has not run yet.
            #
            # The hidden input must already contain INCORRECT. If it still
            # contains A, submitting the form immediately after typing could
            # send the old value, and the test fails.
            #
            # The test then submits the form. The server must receive INCORRECT,
            # reject it as an invalid MultipleChoice value, and return the
            # expected validation error.
            submitted_value = self.execute_script(
                """
                const visibleField = document.querySelector(
                    "[data-testid='form-field-CUSTOM_FIELD']"
                );
                const hiddenField = visibleField.nextElementSibling;
                visibleField.innerText = 'INCORRECT';
                visibleField.dispatchEvent(new InputEvent('input', {
                    bubbles: true,
                    inputType: 'insertText',
                    data: 'INCORRECT',
                }));
                return hiddenField.value;
                """
            )
            assert submitted_value == "INCORRECT"

            form_edit_requirement.do_form_submit_and_catch_error(
                "Node's CUSTOM_FIELD must not contain values other than A, B, C."
            )

        assert test_setup.compare_sandbox_and_expected_output()
