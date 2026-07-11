from __future__ import annotations

import difflib
from pathlib import Path

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

_INSERT_LINE_JS = """
([index, lineHtml]) => {
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
  const reference = code.children[index] || null;
  code.insertBefore(row, reference);
  row.scrollIntoView({ block: 'center' });
}
"""


def _highlight_lines(text: str) -> list[str]:
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


def reveal_change(
    page: Page, original_text: str, final_text: str, *, line_delay_ms: int = 350
) -> None:
    """
    Reveals whatever changed between `original_text` (already rendered by
    `render_original`) and `final_text`, one new line at a time, inserted
    at its real position (not just appended) — so an edit in the middle
    of the file (e.g. a field added to an existing node) reveals in
    place, not as a trailing block.

    Only insertions are supported: this is for scenarios that add
    content (a new field, a new node), not ones that remove or rewrite
    existing lines. `strictdoc`'s save-and-reformat is assumed not to
    have touched any line outside the inserted ones; the assertion below
    catches it loudly if that assumption ever breaks.
    """
    original_lines = original_text.splitlines()
    final_lines = final_text.splitlines()
    highlighted_final = _highlight_lines(final_text)

    matcher = difflib.SequenceMatcher(a=original_lines, b=final_lines, autojunk=False)
    dom_offset = 0
    for tag, a1, _a2, b1, b2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        assert tag == "insert", (
            f"reveal_change only supports pure insertions, got {tag!r}: "
            "the edit changed or removed existing lines, not just added "
            "new ones."
        )
        for offset, line_index in enumerate(range(b1, b2)):
            dom_index = a1 + dom_offset + offset
            page.evaluate(
                _INSERT_LINE_JS, [dom_index, highlighted_final[line_index]]
            )
            page.wait_for_timeout(line_delay_ms)
        dom_offset += b2 - b1
