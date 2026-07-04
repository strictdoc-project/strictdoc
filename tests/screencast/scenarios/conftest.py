from __future__ import annotations

import os
import sys
from typing import Iterator

import pytest
from playwright.sync_api import Browser, Page, sync_playwright

STRICTDOC_ROOT = os.path.abspath(os.path.join(__file__, "../../../.."))
assert os.path.isdir(STRICTDOC_ROOT), STRICTDOC_ROOT
sys.path.insert(0, STRICTDOC_ROOT)

from tests.screencast.fixture import OUTPUT_DIR  # noqa: E402

VIEWPORT_SIZE = {"width": 1280, "height": 720}


def pytest_addoption(parser):
    parser.addoption(
        "--strictdoc-record-video",
        action="store_true",
        default=False,
        help=(
            "Record each screencast scenario's .webm video into "
            "tests/screencast/output/ (named after the scenario's "
            "directory)."
        ),
    )


@pytest.fixture
def page(request) -> Iterator[Page]:
    record_video = request.config.getoption("--strictdoc-record-video")

    with sync_playwright() as playwright:
        browser: Browser = playwright.chromium.launch(headless=True)

        context_kwargs = {"viewport": VIEWPORT_SIZE}
        if record_video:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            context_kwargs["record_video_dir"] = str(OUTPUT_DIR)
            context_kwargs["record_video_size"] = VIEWPORT_SIZE

        context = browser.new_context(**context_kwargs)
        browser_page = context.new_page()

        try:
            yield browser_page
        finally:
            video = browser_page.video
            context.close()

            if record_video and video is not None:
                scenario_name = request.node.path.parent.name
                output_video = OUTPUT_DIR / f"{scenario_name}.webm"
                if output_video.exists():
                    output_video.unlink()
                video.save_as(output_video)
                video.delete()

            browser.close()
