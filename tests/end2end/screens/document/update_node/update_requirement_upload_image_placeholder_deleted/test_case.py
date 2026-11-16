"""
@relation(SDOC-LLR-214, scope=file)
"""

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer


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

            screen_document.hold_asset_upload_responses()

            screen_document.set_editable_caret_after_text(
                "STATEMENT", "First position."
            )
            screen_document.do_drop_image_to_requirement(
                "STATEMENT",
                image_path,
                wait_for_upload=False,
                uploaded_filenames=["first.svg"],
            )

            # The user deletes the placeholder and then types before its
            # place. The image reference still goes where the placeholder
            # was.
            screen_document.do_delete_image_upload_placeholder("STATEMENT")
            self.assert_element_not_present(
                "[data-testid='image-upload-placeholder']"
            )
            screen_document.do_type_in_editable_after_text(
                "STATEMENT", "First", " typed"
            )

            screen_document.release_asset_upload_response(0)
            self.assert_text("first.svg")
            screen_document.restore_asset_upload_responses()

            form.do_form_submit()

        assert test_setup.compare_sandbox_and_expected_output()
