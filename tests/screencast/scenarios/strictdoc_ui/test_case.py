"""
Screencast scenario: browsing a StrictDoc document and switching to the
table view.

If this test fails, the "strictdoc-ui" screencast video is stale and must
be re-recorded (see tests/screencast/README.md).
"""

from __future__ import annotations

from playwright.sync_api import Page, expect

from tests.end2end.server import SDocTestServer
from tests.screencast.fixture import (
    FIXTURE_CONFIG,
    FIXTURE_DIR,
    RECORD_SERVER_PORT,
)


class Test:
    def test(self, page: Page) -> None:
        with SDocTestServer(
            input_path=str(FIXTURE_DIR),
            config_path=str(FIXTURE_CONFIG),
            port=RECORD_SERVER_PORT,
        ) as server:
            base_url = server.get_host_and_port()

            page.goto(f"{base_url}/")
            expect(page.locator("body")).to_be_visible()

            page.goto(
                f"{base_url}/strictdoc-demo-project/docs/requirements.html"
            )
            expect(page.locator(".header__document_title")).to_contain_text(
                "StrictDoc"
            )

            page.click("#viewtype_handler")
            table_link = page.locator('[data-viewtype_link="table"]')
            expect(table_link).to_be_visible()
            table_link.click()

            expect(page.locator("body")).to_have_attribute(
                "data-viewtype", "table"
            )
            expect(
                page.locator('[data-testid="document-main-placeholder"]')
            ).not_to_be_visible()
