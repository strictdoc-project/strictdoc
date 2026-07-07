from __future__ import annotations

from typing import Union

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

Target = Union[str, Locator]

# Playwright doesn't render a real OS mouse cursor, so clicks are invisible
# in a recorded video unless we fake one. This injects a small dot that
# tracks real `mousemove` events (dispatched by page.mouse.move below), and
# a pulsing outline style used to highlight a click's target just before
# clicking it. Registered via add_init_script so it re-applies on every
# navigation within this page (file:// scenes, the live server, ...).
_INIT_SCRIPT = """
(() => {
  const style = document.createElement('style');
  style.textContent = `
    #__screencast_cursor {
      position: fixed; top: 0; left: 0; width: 18px; height: 18px;
      margin: -9px 0 0 -9px;
      border-radius: 50%; background: rgba(255, 90, 0, 0.85);
      border: 2px solid white; box-shadow: 0 0 6px rgba(0,0,0,0.5);
      pointer-events: none; z-index: 2147483647;
      transition: left 0.05s linear, top 0.05s linear;
    }
    .__screencast_highlight {
      outline: 3px solid rgba(255, 90, 0, 0.9) !important;
      outline-offset: 2px !important;
      animation: __screencast_pulse 0.6s ease-in-out infinite alternate;
    }
    @keyframes __screencast_pulse {
      from { outline-color: rgba(255, 90, 0, 0.9); }
      to   { outline-color: rgba(255, 90, 0, 0.35); }
    }
  `;

  const attach = () => {
    document.head.appendChild(style);
    const cursor = document.createElement('div');
    cursor.id = '__screencast_cursor';
    document.documentElement.appendChild(cursor);
    window.addEventListener('mousemove', (event) => {
      cursor.style.left = event.clientX + 'px';
      cursor.style.top = event.clientY + 'px';
    }, true);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', attach);
  } else {
    attach();
  }
})();
"""


class Pointer:
    """
    Makes Playwright-driven interactions visible in recorded screencasts:
    a fake cursor travels to the target before every click, and the target
    is briefly highlighted so the viewer's eye doesn't miss it.
    """

    def __init__(self, page: Page) -> None:
        self.page = page
        page.add_init_script(script=_INIT_SCRIPT)

    def _locator(self, target: Target) -> Locator:
        if isinstance(target, str):
            return self.page.locator(target).first
        return target

    def move_to(self, target: Target, *, pause_ms: int = 300) -> None:
        locator = self._locator(target)
        locator.scroll_into_view_if_needed()
        box = locator.bounding_box()
        assert box is not None, f"Not visible: {target}"
        self.page.mouse.move(
            box["x"] + box["width"] / 2,
            box["y"] + box["height"] / 2,
            steps=25,
        )
        self.page.wait_for_timeout(pause_ms)

    def click(self, target: Target, *, pause_ms: int = 400) -> None:
        locator = self._locator(target)
        self.move_to(locator)
        locator.evaluate("(el) => el.classList.add('__screencast_highlight')")
        self.page.wait_for_timeout(pause_ms)
        locator.click()
        try:
            # A click that navigates away (e.g. a tree/document link)
            # leaves nothing left to unhighlight on the new page.
            locator.evaluate(
                "(el) => el.classList.remove('__screencast_highlight')",
                timeout=1000,
            )
        except PlaywrightTimeoutError:
            pass

    def type_into(self, target: Target, text: str, *, delay_ms: int = 35) -> None:
        locator = self._locator(target)
        self.click(locator)
        # Some fields (e.g. UID) come pre-filled with a suggested value;
        # replace it rather than typing alongside it.
        locator.evaluate("(el) => { el.textContent = ''; }")
        locator.press_sequentially(text, delay=delay_ms)
