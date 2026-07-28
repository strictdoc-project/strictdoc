import os

from selenium.webdriver.common.by import By

from tests.end2end.e2e_case import E2ECase
from tests.end2end.helpers.components.toc import TOC
from tests.end2end.helpers.screens.document.screen_document import (
    Screen_Document,
)
from tests.end2end.server import SDocTestServer

path_to_this_test_file_folder = os.path.dirname(os.path.abspath(__file__))

# The fixture has 35 requirements and chunked_documents_threshold = 10 (see
# strictdoc_config.py), so REQ-035 (the target) is the last node of chunk 3,
# and chunk 1 is neither the initially-loaded chunk (0) nor the target chunk
# (3) nor adjacent to it - it has no reason to load as part of this test.
CHUNK_1_XPATH = "//turbo-frame[@id='document-chunk-1']"


class Test(E2ECase):
    """
    Regression test: a stable UID/MID link that resolves (via
    stable_uri_forwarder.js and the server's /UID/{uid_or_mid} redirect) to
    an anchor whose chunk is not loaded at initial page load must still end
    up with the anchor marked as CSS :target, its TOC entry marked
    "targeted", and actually scrolled into view - the same as
    tests/end2end/stable_url_links/02_web_server, but
    with chunked_documents_threshold forced low enough (see
    strictdoc_config.py) to guarantee the target sits outside the
    initially-loaded chunk 0, rather than only accidentally so depending on
    the project's ambient default threshold.

    This is a distinct entry point from TOC-click navigation
    (tests/end2end/navigation/toc/toc_click_navigation_chunked) and
    scroll-triggered lazy loading (tests/end2end/screens/document/
    lazy_loading): here, the very first thing the browser does is a full
    top-level page load/redirect landing directly on a URL with the
    fragment already set, before any of toc_chunk_navigation.js's own code
    has run - it is the window "load" handler path.

    Both test methods also assert that chunk 1 (unrelated to the target)
    stays unloaded, to prove this is actually exercising the force-load
    code path rather than a document/chunk-size combination small enough
    that everything ends up preloaded regardless (see
    strictdoc_config.py for why chunk size matters here).
    """

    def test_uid(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            target = "REQ-035"

            self.open(test_server.get_host_and_port() + "#" + target)

            screen_document = Screen_Document(self)
            screen_document.assert_target_by_anchor(target)
            screen_document.assert_node_in_viewport_by_anchor(target)
            toc: TOC = screen_document.get_toc()
            toc.assert_toc_link_has_attribute(target, "targeted")
            self.assert_element_not_present(
                f"{CHUNK_1_XPATH}//sdoc-node", by=By.XPATH
            )

    def test_mid(self):
        with SDocTestServer(
            input_path=path_to_this_test_file_folder
        ) as test_server:
            target = "REQ-035"
            mid = "3e06d65b527d4cab87680232880a3430"

            self.open(test_server.get_host_and_port() + "#" + mid)

            screen_document = Screen_Document(self)
            screen_document.assert_target_by_anchor(target)
            screen_document.assert_node_in_viewport_by_anchor(target)
            toc: TOC = screen_document.get_toc()
            toc.assert_toc_link_has_attribute(target, "targeted")
            self.assert_element_not_present(
                f"{CHUNK_1_XPATH}//sdoc-node", by=By.XPATH
            )
