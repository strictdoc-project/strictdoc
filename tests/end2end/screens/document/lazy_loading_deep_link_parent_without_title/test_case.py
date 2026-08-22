from selenium.webdriver.common.by import By

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

# The document has 35 requirements, and the fixture strictdoc_config.py sets
# lazy_document_loading_threshold = 10, so it is rendered as four chunks:
# 0, 1, 2, 3. REQ-001 (chunk 0) has a Parent relation to REQ-035, which has
# no TITLE field and lives in the last chunk, several thousand pixels below
# the viewport, so that chunk stays lazy until scrolled to or deep-linked.
LAST_CHUNK_XPATH = "//turbo-frame[@id='document-chunk-3']"
LAST_CHUNK_ID = "document-chunk-3"


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            screen_document: Screen_Document = (
                screen_project_index.do_click_on_the_document_with_title(
                    "Deep Link Parent Without Title Document"
                )
            )
            screen_document.assert_on_screen_document()

            # The last chunk, which holds the titleless parent requirement,
            # starts unloaded.
            self.assert_element_not_present(
                f"{LAST_CHUNK_XPATH}//sdoc-node",
                by=By.XPATH,
            )

            requirement = screen_document.get_node(node_order=1)
            requirement.assert_requirement_title("Requirement 1", "1")
            requirement.assert_requirement_has_parent_relation("REQ-035")

            # The parent link renders the UID, but no title text, because
            # REQ-035 has no TITLE field.
            parent_link_text = self.get_text(
                "(//sdoc-node-field[@data-field-label='parent relations']"
                "//a[contains(@class, 'requirement__link-parent')])[1]",
                by=By.XPATH,
            )
            assert parent_link_text.strip() == "REQ-035"

            # Clicking the parent link must force-load the chunk holding the
            # titleless target and scroll to it, exactly like a TOC deep-link
            # would.
            requirement.do_click_on_parent_relation_link("REQ-035")

            self.assert_element_present(
                f"{LAST_CHUNK_XPATH}//sdoc-node",
                by=By.XPATH,
                timeout=20,
            )
            screen_document.assert_chunk_frame_placeholder_cleared(
                LAST_CHUNK_ID
            )

            # CSS :target must match the newly force-loaded, titleless node.
            screen_document.assert_target_by_anchor("REQ-035")
            # DOM presence and :target do not by themselves prove the scroll
            # actually reached the target on screen.
            screen_document.assert_node_in_viewport_by_anchor("REQ-035")

            # The scroll landed on the correct node: its own statement, not
            # some other requirement's, is now visible.
            screen_document.assert_text(
                "The lazy loading fixture statement LAZYSTMT-035 "
                "must appear exactly once."
            )

            target_requirement = screen_document.get_node_by_anchor("REQ-035")
            target_requirement.assert_requirement_uid_contains("REQ-035")
