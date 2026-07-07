from __future__ import annotations

from typing import List

from playwright.sync_api import Page

_RENDER_ORIGINAL_JS = """
([filename, lines]) => {
  document.getElementById('fileTab').textContent = filename;
  const code = document.getElementById('code');
  code.innerHTML = '';
  for (const line of lines) {
    const row = document.createElement('div');
    row.className = 'line';
    const text = document.createElement('span');
    text.className = 'line-text';
    text.textContent = line;
    row.appendChild(text);
    code.appendChild(row);
  }
}
"""

_APPEND_LINE_JS = """
(line) => {
  const code = document.getElementById('code');
  const previous = code.querySelector('.line.cursor-line');
  if (previous) {
    previous.classList.remove('cursor-line');
  }
  const row = document.createElement('div');
  row.className = 'line added cursor-line';
  const text = document.createElement('span');
  text.className = 'line-text';
  text.textContent = line;
  row.appendChild(text);
  code.appendChild(row);
  row.scrollIntoView({ block: 'end' });
}
"""


def render_original(page: Page, filename: str, text: str) -> None:
    """Renders the file's pre-existing content instantly, unhighlighted."""
    lines = text.splitlines()
    page.evaluate(_RENDER_ORIGINAL_JS, [filename, lines])


def reveal_added_lines(
    page: Page, added_text: str, *, line_delay_ms: int = 350
) -> None:
    """
    Appends the newly written lines one at a time, highlighted, so the
    viewer sees exactly what the UI action just wrote to disk.
    """
    lines: List[str] = added_text.splitlines()
    for line in lines:
        page.evaluate(_APPEND_LINE_JS, line)
        page.wait_for_timeout(line_delay_ms)
