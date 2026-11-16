from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.field_widgets import FieldWidgets
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

# The form shows a multiline field with a line break at the end.
TEXT = "Line one.\nLine two.\n"
TYPED = "Line one.\nLine two. Typed text.\n"


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_document = screen_project_index.do_click_on_first_document()
            screen_document.assert_on_screen_document()
            form = screen_document.get_node().do_open_form_edit_requirement()
            form.assert_on_form()

            # Ctrl+Z undoes the typed text in one step, not one character at
            # a time, and Ctrl+Shift+Z redoes it in one step.
            statement = FieldWidgets(self, "STATEMENT")
            statement.do_place_caret_after("Line two.")
            statement.do_type_at_caret(" Typed text.")
            statement.assert_field_text(TYPED)

            statement.do_undo()
            statement.assert_field_text(TEXT)
            statement.do_redo()
            statement.assert_field_text(TYPED)

            # The form sends the text after undo and redo.
            form.do_form_submit()
            screen_document.assert_text("Typed text.")

        assert test_setup.compare_sandbox_and_expected_output()
