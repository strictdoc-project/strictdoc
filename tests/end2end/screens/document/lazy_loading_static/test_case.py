import os

from selenium.webdriver.common.by import By

from tests.end2end.e2e_case import E2ECase
from tests.end2end.exporter import SDocTestHTMLExporter
from tests.end2end.helpers.components.toc import TOC
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))

# The main document has 35 requirements, and strictdoc_config.py sets
# lazy_document_loading_threshold = 10, so the document is rendered as four
# chunks: 0, 1, 2, 3. Static export has no FastAPI server, so chunks 1-3 are
# delivered as generated .js files (see
# DocumentHTMLGenerator._export_static_chunks) instead of Turbo fragment
# fetches - toc_chunk_navigation.js's static delivery path
# (loadStaticChunk()) is what is under test here, mirroring
# tests/end2end/screens/document/lazy_loading/test_case.py for server mode.
# The control document has only 5 requirements, below the threshold, so it
# proves the legacy unchunked path is used for both modes.
CHUNK_0_XPATH = "//turbo-frame[@id='document-chunk-0']"
LAST_CHUNK_XPATH = "//turbo-frame[@id='document-chunk-3']"
LAST_CHUNK_ID = "document-chunk-3"
LAST_TOC_LINK_XPATH = "(//turbo-frame[@id='frame-toc']//a[@anchor])[last()]"


class Test(E2ECase):
    def test(self):
        with SDocTestHTMLExporter(
            input_path=path_to_this_test_file_folder
        ) as exporter:
            output_uri = exporter.get_output_path_as_uri()

            self.open(output_uri + "index.html")

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()
            screen_project_index.assert_contains_document(
                "Lazy Loading Static Document"
            )
            screen_project_index.assert_contains_document("Control Document")

            #
            # Scenario 1: A document over the chunking threshold renders
            # chunk 0 inline and the remaining chunks as empty static
            # placeholders (no "src"/"loading" Turbo attributes - see
            # document_chunk_lazy_placeholder_static.jinja.html).
            #
            screen_document = (
                screen_project_index.do_click_on_the_document_with_title(
                    "Lazy Loading Static Document"
                )
            )
            screen_document.assert_on_screen_document()
            screen_document.assert_header_document_title(
                "Lazy Loading Static Document"
            )

            self.assert_element_present(
                f"{CHUNK_0_XPATH}//sdoc-node",
                by=By.XPATH,
            )
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
            # Scenario 2: Scrolling down to the last chunk triggers
            # loadStaticChunk() to inject the generated .js file and splice
            # its content into the placeholder.
            #
            self.sdoc_do_scroll_to_element_by_xpath(LAST_CHUNK_XPATH)
            self.assert_element_present(
                f"{LAST_CHUNK_XPATH}//sdoc-node",
                by=By.XPATH,
                timeout=20,
            )
            screen_document.assert_chunk_frame_placeholder_cleared(
                LAST_CHUNK_ID
            )
            screen_document.assert_text(
                "The lazy loading fixture statement LAZYSTMT-035 "
                "must appear exactly once."
            )

            #
            # Scenario 3: Clicking a TOC entry whose target is in an
            # unloaded chunk force-loads that chunk (via loadStaticChunk())
            # and scrolls to it. The document is reopened so the last chunk
            # starts unloaded again.
            #
            self.open(output_uri + "index.html")
            screen_project_index.assert_on_screen()
            screen_document = (
                screen_project_index.do_click_on_the_document_with_title(
                    "Lazy Loading Static Document"
                )
            )
            screen_document.assert_on_screen_document()
            self.assert_element_not_present(
                f"{LAST_CHUNK_XPATH}//sdoc-node",
                by=By.XPATH,
            )
            self.assert_element_present(LAST_TOC_LINK_XPATH, by=By.XPATH)
            self.click(LAST_TOC_LINK_XPATH, by=By.XPATH)
            self.assert_element_present(
                f"{LAST_CHUNK_XPATH}//sdoc-node",
                by=By.XPATH,
                timeout=20,
            )
            screen_document.assert_target_by_anchor("REQ-035")
            screen_document.assert_node_in_viewport_by_anchor("REQ-035")
            toc: TOC = screen_document.get_toc()
            toc.assert_toc_link_has_attribute("REQ-035", "intersected")
            screen_document.assert_text(
                "The lazy loading fixture statement LAZYSTMT-035 "
                "must appear exactly once."
            )

            #
            # Scenario 4: A document below the chunking threshold renders
            # the legacy unchunked path in static export too: no chunk
            # frames at all.
            #
            self.open(output_uri + "index.html")
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
