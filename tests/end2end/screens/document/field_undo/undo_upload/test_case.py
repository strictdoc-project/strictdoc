"""
@relation(SDOC-SRS-211, scope=file)
"""

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.field_widgets import FieldWidgets
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

TEXT = "First position.\nSecond position.\nThird position.\n"


class Test(E2ECase):
    def test(self) -> None:
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document = Screen_ProjectIndex(
                self
            ).do_click_on_first_document()
            requirement = screen_document.get_node()
            form = requirement.do_open_form_edit_requirement()
            image_path = (
                "./tests/end2end/screens/document/update_node/"
                "update_requirement_upload_image_replace_existing/picture.svg"
            )

            statement = FieldWidgets(self, "STATEMENT")
            statement.assert_field_text(TEXT)
            screen_document.set_editable_caret_after_text(
                "STATEMENT", "First position."
            )
            screen_document.do_drop_image_to_requirement(
                "STATEMENT", image_path, uploaded_filenames=["first.svg"]
            )
            uploaded = statement.get_field_text()
            assert "first.svg" in uploaded, uploaded

            # The image reference is one undo step.
            statement.do_undo()
            statement.wait_for_field_text(TEXT)
            statement.do_redo()
            statement.wait_for_field_text(uploaded)

            form.do_form_submit()

        assert test_setup.compare_sandbox_and_expected_output()
