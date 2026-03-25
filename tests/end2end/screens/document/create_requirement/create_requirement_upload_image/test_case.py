"""
@relation(SDOC-LLR-208, scope=file)
"""

import re
from pathlib import Path

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
    """
    test image upload on newly created node
    """

    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        # Run server.
        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_document_tree = Screen_ProjectIndex(self)

            screen_document_tree.assert_on_screen()
            screen_document_tree.assert_contains_document("Document 1")

            screen_document = screen_document_tree.do_click_on_first_document()

            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Document 1")

            root_node = screen_document.get_root_node()
            root_node_menu = root_node.do_open_node_menu()
            form_edit_requirement: Form_EditRequirement = (
                root_node_menu.do_node_add_requirement_first()
            )

            form_edit_requirement.do_fill_in_field_title("First title")

            screen_document.do_drop_image_to_requirement(
                "STATEMENT",
                "./tests/end2end/screens/document/create_requirement/create_requirement_upload_image/picture.svg",
            )
            form_edit_requirement.do_form_submit()

            screen_document.assert_no_js_errors()

            screen_document.assert_text("picture.svg")

            sandbox_doc_path = (
                Path(test_setup.path_to_sandbox) / "document.sdoc"
            )

            # The requirement mid is dynamic and unpredictable, so we normalize it here
            # to the arbitraty requirement_mid 00112233445566778899AABBCCDDEEFF
            if sandbox_doc_path.exists():
                content = sandbox_doc_path.read_text(encoding="utf-8")
                # This regex looks for the dynamically generated requirement_mid (32 hex characters)
                # and normalized it, so that the comparison works
                sanitized_content = re.sub(
                    r"@assets/[a-f0-9]{32}/",
                    "@assets/00112233445566778899AABBCCDDEEFF/",
                    content,
                )
                sandbox_doc_path.write_text(sanitized_content, encoding="utf-8")

            assets_dir = Path(test_setup.path_to_sandbox) / "_assets"
            if assets_dir.exists() and assets_dir.is_dir():
                for item in assets_dir.iterdir():
                    # If it's a directory and exactly matches 32 hex characters
                    if item.is_dir() and re.fullmatch(
                        r"[a-f0-9]{32}", item.name
                    ):
                        new_path = (
                            assets_dir / "00112233445566778899AABBCCDDEEFF"
                        )
                        item.rename(new_path)

        assert test_setup.compare_sandbox_and_expected_output()
