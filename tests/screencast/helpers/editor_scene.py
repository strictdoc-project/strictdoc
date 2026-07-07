from __future__ import annotations

from pathlib import Path
from typing import List

from playwright.sync_api import Page
from pygments import highlight
from pygments.formatters import HtmlFormatter

from strictdoc.backend.rst.strictdoc_lexer import StrictDocLexer

# Reuses StrictDoc's own .sdoc syntax highlighter (the same Pygments lexer
# used to highlight `.. code:: strictdoc` blocks in the docs) and the
# product's own token colors, instead of hand-marking up keywords here.
_LEXER = StrictDocLexer()
_FORMATTER = HtmlFormatter(nowrap=True)

_PYGMENTS_CSS_PATH = (
    Path(__file__).resolve().parents[3]
    / "strictdoc"
    / "export"
    / "html"
    / "_static"
    / "pygments.css"
)

_RENDER_ORIGINAL_JS = """
([filename, lines, css]) => {
  document.getElementById('fileTab').textContent = filename;
  if (!document.getElementById('__pygments_css')) {
    const style = document.createElement('style');
    style.id = '__pygments_css';
    style.textContent = css;
    document.head.appendChild(style);
  }
  const code = document.getElementById('code');
  code.innerHTML = '';
  for (const lineHtml of lines) {
    const row = document.createElement('div');
    row.className = 'line';
    const text = document.createElement('span');
    text.className = 'line-text';
    text.innerHTML = lineHtml;
    row.appendChild(text);
    code.appendChild(row);
  }
}
"""

_APPEND_LINE_JS = """
(lineHtml) => {
  const code = document.getElementById('code');
  const previous = code.querySelector('.line.cursor-line');
  if (previous) {
    previous.classList.remove('cursor-line');
  }
  const row = document.createElement('div');
  row.className = 'line added cursor-line';
  const text = document.createElement('span');
  text.className = 'line-text';
  text.innerHTML = lineHtml;
  row.appendChild(text);
  code.appendChild(row);
  row.scrollIntoView({ block: 'end' });
}
"""


def _highlight_lines(text: str) -> List[str]:
    """
    One highlighted HTML fragment per source line (StrictDocLexer's rules
    each match exactly one line, so this lines up 1:1 with `text`'s lines).
    """
    html = highlight(text, _LEXER, _FORMATTER)
    lines = html.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def render_original(page: Page, filename: str, text: str) -> None:
    """Renders the file's pre-existing content instantly, highlighted."""
    css = _PYGMENTS_CSS_PATH.read_text(encoding="utf-8")
    page.evaluate(_RENDER_ORIGINAL_JS, [filename, _highlight_lines(text), css])


def reveal_added_lines(
    page: Page, added_text: str, *, line_delay_ms: int = 350
) -> None:
    """
    Appends the newly written lines one at a time, highlighted, so the
    viewer sees exactly what the UI action just wrote to disk.
    """
    for line_html in _highlight_lines(added_text):
        page.evaluate(_APPEND_LINE_JS, line_html)
        page.wait_for_timeout(line_delay_ms)
