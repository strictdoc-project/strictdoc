from selenium.webdriver.common.by import By

from tests.end2end.e2e_case import E2ECase
from tests.end2end.end2end_test_setup import End2EndTestSetup
from tests.end2end.helpers.components.toc import TOC
from tests.end2end.helpers.screens.project_index.screen_project_index import (
    Screen_ProjectIndex,
)
from tests.end2end.server import SDocTestServer

# The document has 35 requirements, and strictdoc_config.py sets
# chunked_documents_threshold = 10, so the document is rendered as four
# chunks: 0, 1, 2, 3. The last chunk sits several thousand pixels below the
# viewport, so it is guaranteed to stay lazy (not eagerly loaded by Turbo)
# until the page is scrolled down to it - see
# tests/end2end/screens/document/lazy_loading/test_case.py, which relies on
# the same guarantee.
LAST_CHUNK_XPATH = "//turbo-frame[@id='document-chunk-3']"


class Test(E2ECase):
    def test(self):
        test_setup = End2EndTestSetup(path_to_test_file=__file__)

        with SDocTestServer(
            input_path=test_setup.path_to_sandbox
        ) as test_server:
            self.open(test_server.get_host_and_port())

            screen_project_index = Screen_ProjectIndex(self)
            screen_project_index.assert_on_screen()

            screen_document = (
                screen_project_index.do_click_on_the_document_with_title(
                    "TOC Highlighting Lazy Chunks Document"
                )
            )
            screen_document.assert_on_screen_document()

            toc: TOC = screen_document.get_toc()

            # The last chunk (and TOCLZ-035, its only requirement's anchor)
            # is not loaded yet: its content must not be in the DOM.
            self.assert_element_not_present(
                f"{LAST_CHUNK_XPATH}//sdoc-node",
                by=By.XPATH,
            )

            # Scrolling the last chunk's placeholder into view makes Turbo
            # lazily load it - this is the scenario where content appears
            # in the DOM without any corresponding mutation of the TOC
            # frame (see developer/tasks/20260726_toc_highlight_improvement/
            # task.md for why this matters for TOC highlighting).
            self.sdoc_do_scroll_to_element_by_xpath(LAST_CHUNK_XPATH)
            self.assert_element_present(
                f"{LAST_CHUNK_XPATH}//sdoc-node",
                by=By.XPATH,
                timeout=20,
            )

            # Scroll the now-loaded last requirement into the center of the
            # viewport so it is unambiguously the "current" section.
            self.execute_script(
                "document.getElementById('TOCLZ-035')"
                ".scrollIntoView({block: 'center'});"
            )
            self.sleep(1)

            # The TOC entry for the newly-loaded requirement must be marked
            # as the current section.
            toc.assert_toc_link_has_attribute("TOCLZ-035", "intersected")

            # The TOC entry for the first requirement, now scrolled far out
            # of view, must not be marked as current.
            toc.assert_toc_link_has_not_attribute("TOCLZ-001", "intersected")
