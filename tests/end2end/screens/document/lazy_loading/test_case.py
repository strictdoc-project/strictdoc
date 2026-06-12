from selenium.webdriver.common.by import By

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.screens.document.form_edit_requirement import (
    Form_EditRequirement,
)
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

# The main document has 35 requirements, and the fixture strictdoc_config.py
# sets chunked_documents_threshold = 10, so the document is rendered as four
# chunks: 0, 1, 2, 3. The last chunk sits several thousand pixels below the
# viewport, so it is guaranteed to stay lazy (i.e., not eagerly loaded by
# Turbo) until the page is scrolled down to it.
# The control document has only 5 requirements, which is below the threshold
# of 10, so it proves that the legacy unchunked rendering path is used.
CHUNK_0_XPATH = "//turbo-frame[@id='document-chunk-0']"
LAST_CHUNK_XPATH = "//turbo-frame[@id='document-chunk-3']"
# The TOC entry for the last requirement (Requirement 35), which lives in the
# last chunk.
LAST_TOC_LINK_XPATH = "(//turbo-frame[@id='frame-toc']//a[@anchor])[last()]"


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)

            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document(
                "Lazy Loading Document"
            )
            screen_project_index.assert_contains_document("Control Document")

            #
            # Scenario 1: A document over the chunking threshold renders
            # chunk 0 inline and the remaining chunks as empty lazy
            # placeholders.
            #
            screen_document = (
                screen_project_index.do_click_on_the_document_with_title(
                    "Lazy Loading Document"
                )
            )
            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title(
                "Lazy Loading Document"
            )

            # Chunk 0 is rendered inline and contains nodes.
            self.assert_element_present(
                f"{CHUNK_0_XPATH}//sdoc-node",
                by=By.XPATH,
            )

            # Lazy placeholder frames exist. The last chunk placeholder is
            # far below the viewport, so it must still be empty: Turbo has
            # not lazy-loaded it because it has not been scrolled into view.
            # (Chunks 1-2 may have been loaded eagerly if the viewport is
            # tall enough, so only the last chunk is asserted to be empty.)
            self.assert_element_present(
                f"{LAST_CHUNK_XPATH}"
                "[@data-testid='document-chunk-placeholder']",
                by=By.XPATH,
            )
            self.assert_element_not_present(
                f"{LAST_CHUNK_XPATH}//sdoc-node",
                by=By.XPATH,
            )

            #
            # Scenario 2: Scrolling down to the last chunk makes Turbo load
            # its content, including the very last requirement.
            #
            self.sdoc_do_scroll_to_element_by_xpath(LAST_CHUNK_XPATH)
            # The lazy chunk fetch goes over the test server, which can be
            # slow on CI, so the default timeout is too tight here.
            self.assert_element_present(
                f"{LAST_CHUNK_XPATH}//sdoc-node",
                by=By.XPATH,
                timeout=20,
            )
            screen_document.assert_text(
                "The lazy loading fixture statement LAZYSTMT-035 "
                "must appear exactly once."
            )

            #
            # Scenario 3: Editing a node inside chunk 0 still works: the
            # Turbo stream response updates the node in place.
            #
            requirement = screen_document.get_node(node_order=2)
            requirement.assert_requirement_title("Requirement 2", "2")

            form_edit_requirement: Form_EditRequirement = (
                requirement.do_open_form_edit_requirement()
            )
            form_edit_requirement.assert_on_form()
            form_edit_requirement.do_fill_in_field_statement(
                "The modified statement LAZYSTMT-002-EDITED must appear "
                "exactly once."
            )
            form_edit_requirement.do_form_submit()

            screen_document.assert_text(
                "The modified statement LAZYSTMT-002-EDITED must appear "
                "exactly once."
            )

            #
            # Scenario 5: Clicking a TOC entry whose target is in an
            # unloaded chunk force-loads that chunk and scrolls to it. The
            # document is reopened so the last chunk starts unloaded again.
            #
            self.open(test_server.get_host_and_port())
            screen_project_index.assert_on_screen()
            screen_document = (
                screen_project_index.do_click_on_the_document_with_title(
                    "Lazy Loading Document"
                )
            )
            screen_document.assert_on_screen_document()
            # The last chunk starts empty (not scrolled into view).
            self.assert_element_not_present(
                f"{LAST_CHUNK_XPATH}//sdoc-node",
                by=By.XPATH,
            )
            # Click the TOC entry for the last requirement without scrolling
            # the content. The deep-link script must load the target chunk.
            self.assert_element_present(LAST_TOC_LINK_XPATH, by=By.XPATH)
            self.click(LAST_TOC_LINK_XPATH, by=By.XPATH)
            self.assert_element_present(
                f"{LAST_CHUNK_XPATH}//sdoc-node",
                by=By.XPATH,
                timeout=20,
            )
            screen_document.assert_text(
                "The lazy loading fixture statement LAZYSTMT-035 "
                "must appear exactly once."
            )

            #
            # Scenario 4: A document below the chunking threshold renders
            # the legacy unchunked path: no chunk frames at all.
            #
            self.open(test_server.get_host_and_port())
            screen_project_index.assert_on_screen()

            screen_document = (
                screen_project_index.do_click_on_the_document_with_title(
                    "Control Document"
                )
            )
            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title("Control Document")

            for control_requirement_index in range(1, 6):
                screen_document.assert_text(
                    "The control fixture statement "
                    f"CTRLSTMT-{control_requirement_index:03d} "
                    "must appear exactly once."
                )
            self.assert_element_not_present(
                "//turbo-frame[starts-with(@id, 'document-chunk-')]",
                by=By.XPATH,
            )

        assert test_setup.compare_sandbox_and_expected_output()
