from __future__ import annotations

from playwright.sync_api import Page


def pause(page: Page, seconds: float = 1.0) -> None:
    """A deliberate beat, for viewers to register what just happened."""
    page.wait_for_timeout(int(seconds * 1000))
