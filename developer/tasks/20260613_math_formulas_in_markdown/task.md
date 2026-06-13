# Support mathematical formulas in Markdown

## WHAT

A user asked:

> in-line equation in strictdoc? Delimited with one $. Is it expected to be implemented?

It would be great if the $-syntax was rendered into mathematical formulas, for example:

- The spacecraft dry mass is $m_d = 120\,kg$ and the propellant mass is $m_p = 30\,kg$.

- The total mass shall satisfy $m_t = m_d + m_p \le 160\,kg$.

## HOW

StrictDoc already had MathJax infrastructure in place for RST (via `.. math::` directive and `:math:` role). The task was to extend the Markdown rendering path to also produce MathJax-compatible HTML from `$...$` and `$$...$$` syntax.

### Existing infrastructure

- `markdown-it-py` is the Markdown parser (already a dependency).
- MathJax assets are copied to the output and injected into HTML templates when `--enable-mathjax` is passed. This is controlled by `project_config.is_activated_mathjax()`.
- The RST path produces `<span class="math notranslate nohighlight">\( ... \)</span>` for inline math and `<div class="math notranslate nohighlight">\[ ... \]</div>` for display math — MathJax picks up these delimiters.

### Implementation

No new dependencies were added. `markdown-it-py` exposes a plugin API that allows registering custom inline rules and renderers.

A custom inline rule `_math_inline_rule` was added to `markdown_to_html_fragment_writer.py`:

- Detects `$...$` (inline math) and `$$...$$` (display math).
- Skips `$$` when scanning for the closing `$` of an inline formula, so `$$...$$` is not misread as two adjacent empty inline formulas.
- Pushes a `math_inline` or `math_inline_double` token with the raw LaTeX content.

Two renderer functions output the HTML in the same format as the RST path:

- `_render_math_inline` → `<span class="math notranslate nohighlight">\( ... \)</span>`
- `_render_math_inline_double` → `<div class="math notranslate nohighlight">\[ ... \]</div>`

The rule and renderers are registered at class-definition time on the shared `_MARKDOWN_PARSER` instance, alongside the existing Mermaid fence renderer.

### Files changed

- `strictdoc/backend/markdown/markdown_to_html_fragment_writer.py` — added the inline rule and two renderers.
- `tests/unit/strictdoc/export/markdown/test_markdown_to_html_fragment_writer.py` — added unit tests 08–10 covering inline math, display math, and two formulas in one paragraph.
- `tests/integration/features/html/markdown_markup_to_html/20_math_formulas/` — integration test that exports a Markdown document with `--enable-mathjax`, verifies MathJax script is injected, and checks the generated HTML contains the expected `<span>`/`<div>` math elements.
