"""
@relation(SDOC-LLR-214, scope=file)
@relation(SDOC-LLR-215, scope=file)
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
            screen_document = screen_project_index.do_click_on_first_document()
            requirement = screen_document.get_node()
            form_edit_requirement: Form_EditRequirement = (
                requirement.do_open_form_edit_requirement()
            )

            current_url = self.get_current_url()
            assert screen_document.do_drop_file_outside_editable(
                "./tests/end2end/screens/document/update_node/update_requirement_reject_pdf_upload/document.pdf"
            )
            assert self.get_current_url() == current_url

            screen_document.do_drop_image_to_requirement(
                "STATEMENT",
                [
                    "./tests/end2end/screens/document/update_node/update_requirement_upload_image_webp/picture.webp",
                    "./tests/end2end/screens/document/update_node/update_requirement_upload_image_replace_existing/picture.svg",
                    "./tests/end2end/screens/document/update_node/update_requirement_upload_image_with_spaces/picture with spaces.svg",
                    "./tests/end2end/screens/document/update_node/update_requirement_reject_tiff_upload/picture.tiff",
                    "./tests/end2end/screens/document/update_node/update_requirement_reject_pdf_upload/document.pdf",
                ],
            )
            screen_document.assert_text("picture.*")
            screen_document.assert_text("picture_with_spaces.svg")
            self.assert_text(
                "Unsupported formats: picture.tiff, document.pdf.",
                "[data-testid='unsupported-image-format-message']",
            )
            self.click("[data-testid='unsupported-image-format-close']")

            screen_document.do_drop_image_to_requirement(
                "STATEMENT",
                "./tests/end2end/screens/document/update_node/update_requirement_upload_image_webp/picture.avif",
                uploaded_filenames=["other.avif"],
            )
            screen_document.assert_text("other.avif")
            form_edit_requirement.do_form_submit()

        assert test_setup.compare_sandbox_and_expected_output()
