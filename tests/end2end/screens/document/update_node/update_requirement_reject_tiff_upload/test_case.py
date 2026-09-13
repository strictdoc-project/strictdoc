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
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_document = screen_project_index.do_click_on_first_document()
            requirement = screen_document.get_node()
            requirement.do_open_form_edit_requirement()

            screen_document.do_drop_image_to_requirement(
                "STATEMENT",
                "./tests/end2end/screens/document/update_node/update_requirement_reject_tiff_upload/picture.tiff",
                wait_for_upload=False,
            )

            self.assert_text(
                "Unsupported format: picture.tiff.",
                "[data-testid='unsupported-image-format-message']",
            )
            self.assert_text(
                "You can use SVG, PNG, GIF, JPG, JPEG, WebP, AVIF.",
                "[data-testid='unsupported-image-format-message']",
            )
            self.assert_text_not_visible("Uploading picture")
            self.click("[data-testid='unsupported-image-format-close']")
            self.assert_element_not_present(
                "[data-testid='unsupported-image-format-message']"
            )

        assert test_setup.compare_sandbox_and_expected_output()
