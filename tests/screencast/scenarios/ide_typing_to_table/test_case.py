"""
Screencast scenario: an IDE-style typing scene followed by the StrictDoc UI
table view.

If this test fails, the "ide-to-table" screencast video is stale and must
be re-recorded (see tests/screencast/README.md).
"""

from __future__ import annotations

import os

from playwright.sync_api import Page, expect

from tests.end2end.server import SDocTestServer
from tests.screencast.fixture import (
    FIXTURE_CONFIG,
    FIXTURE_DIR,
    RECORD_SERVER_PORT,
)
from tests.screencast.helpers.viewtype_selector import ViewTypeSelector
from tests.screencast.scenarios.typing import type_text

SCENE_HTML = os.path.abspath(
    os.path.join(__file__, "../../../demo.html")
)

TYPED_TEXT = (
    "[DOCUMENT]\n"
    "TITLE: Requirements\n"
    "\n"
    "[REQUIREMENT]\n"
    "UID: REQ-001\n"
    "TITLE: Export documentation\n"
    "STATEMENT: StrictDoc shall export requirements to HTML.\n"
)


class Test:
    def test(self, page: Page) -> None:
        page.goto(f"file://{SCENE_HTML}")
        demo_text = page.locator("#demoText")
        expect(demo_text).to_be_visible()

        type_text(demo_text, TYPED_TEXT)
        expect(demo_text).to_have_text(TYPED_TEXT)

        with SDocTestServer(
            input_path=str(FIXTURE_DIR),
            config_path=str(FIXTURE_CONFIG),
            port=RECORD_SERVER_PORT,
        ) as server:
            base_url = server.get_host_and_port()

            page.goto(
                f"{base_url}/strictdoc-demo-project/docs/requirements.html"
            )

            viewtype_selector = ViewTypeSelector(page)
            screen_table = viewtype_selector.go_to_table()

            screen_table.assert_header_document_title("StrictDoc")
            screen_table.assert_on_screen("table")
