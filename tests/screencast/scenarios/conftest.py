from __future__ import annotations

import os
import sys
from typing import Iterator

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

STRICTDOC_ROOT = os.path.abspath(os.path.join(__file__, "../../../.."))
assert os.path.isdir(STRICTDOC_ROOT), STRICTDOC_ROOT
sys.path.insert(0, STRICTDOC_ROOT)


@pytest.fixture
def page() -> Iterator[Page]:
    with sync_playwright() as playwright:
        browser: Browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        browser_page = context.new_page()
        try:
            yield browser_page
        finally:
            context.close()
            browser.close()
