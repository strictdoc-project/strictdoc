"""
@relation(SDOC-SRS-24, scope=file)
"""

import re
from html import escape
from typing import Callable, MutableMapping, Optional, Sequence, Tuple, cast

from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml, unescapeAll
from markdown_it.renderer import RendererHTML
from markdown_it.rules_inline import StateInline
from markdown_it.token import Token
from markdown_it.utils import EnvType, OptionsDict
from markupsafe import Markup

_MARKDOWN_PARSER = MarkdownIt("default", {"html": True})
_MARKDOWN_RENDERER = cast(RendererHTML, _MARKDOWN_PARSER.renderer)
_FenceRenderer = Callable[[Sequence[Token], int, OptionsDict, EnvType], str]
_MARKDOWN_RENDERER_RULES = cast(
    MutableMapping[str, _FenceRenderer], _MARKDOWN_RENDERER.rules
)
_DEFAULT_FENCE_RENDERER: _FenceRenderer = _MARKDOWN_RENDERER_RULES["fence"]


def _render_fence(
    tokens: Sequence[Token],
    idx: int,
    options: OptionsDict,
    env: EnvType,
) -> str:
    token = tokens[idx]
    info = unescapeAll(token.info).strip() if token.info else ""
    lang_name = info.split(maxsplit=1)[0] if info else ""

    if lang_name.lower() != "mermaid":
        return _DEFAULT_FENCE_RENDERER(tokens, idx, options, env)

    return f'<pre class="mermaid">{escapeHtml(token.content)}</pre>\n'


def _math_inline_rule(state: StateInline, silent: bool) -> bool:
    pos = state.pos
    max_ = state.posMax
    src = state.src

    if pos >= max_ or src[pos] != "$":
        return False

    is_display = pos + 1 <= max_ and src[pos + 1] == "$"
    marker_len = 2 if is_display else 1
    start = pos + marker_len

    if start >= max_:
        return False

    end = -1
    i = start
    while i <= max_:
        dollar_idx = src.find("$", i)
        if dollar_idx == -1:
            break
        if is_display:
            if dollar_idx + 1 <= max_ and src[dollar_idx + 1] == "$":
                end = dollar_idx
                break
            i = dollar_idx + 1
        else:
            if dollar_idx + 1 <= max_ and src[dollar_idx + 1] == "$":
                i = dollar_idx + 2
            else:
                end = dollar_idx
                break

    if end == -1:
        return False

    content = src[start:end]
    if not content.strip():
        return False

    if not silent:
        token_type = "math_inline_double" if is_display else "math_inline"
        token = state.push(token_type, "math", 0)
        token.markup = "$$" if is_display else "$"
        token.content = content

    state.pos = end + marker_len
    return True


def _render_math_inline(
    tokens: Sequence[Token],
    idx: int,
    _options: OptionsDict,
    _env: EnvType,
) -> str:
    return f'<span class="math notranslate nohighlight">\\( {tokens[idx].content} \\)</span>'


def _render_math_inline_double(
    tokens: Sequence[Token],
    idx: int,
    _options: OptionsDict,
    _env: EnvType,
) -> str:
    return f'<div class="math notranslate nohighlight">\\[ {tokens[idx].content} \\]</div>'


def _strip_dotdot_from_img_src(html: str) -> str:
    def _rebase(m: "re.Match[str]") -> str:
        src = m.group(1)
        while src.startswith("../"):
            src = src[3:]
        return f'src="{src}"'

    return re.sub(r'src="(\.\./[^"]*)"', _rebase, html)


class MarkdownToHtmlFragmentWriter:
    # Use the default preset to support common Markdown extensions such as
    # pipe tables when rendering HTML fragments.
    markdown_parser = _MARKDOWN_PARSER
    _MARKDOWN_RENDERER_RULES["fence"] = _render_fence
    _MARKDOWN_PARSER.inline.ruler.before(
        "backticks", "math_inline", _math_inline_rule
    )
    _MARKDOWN_RENDERER_RULES["math_inline"] = _render_math_inline
    _MARKDOWN_RENDERER_RULES["math_inline_double"] = _render_math_inline_double

    def __init__(self, flat_assets: bool = False) -> None:
        self.flat_assets: bool = flat_assets

    def write(self, markdown_fragment: str) -> Markup:
        assert isinstance(markdown_fragment, str), markdown_fragment
        html = MarkdownToHtmlFragmentWriter.markdown_parser.render(
            markdown_fragment
        )
        if self.flat_assets:
            html = _strip_dotdot_from_img_src(html)
        return Markup(html)

    @staticmethod
    def write_with_validation(
        markdown_fragment: str,
    ) -> Tuple[Optional[str], Optional[str]]:
        assert isinstance(markdown_fragment, str), markdown_fragment
        return (
            MarkdownToHtmlFragmentWriter.markdown_parser.render(
                markdown_fragment
            ),
            None,
        )

    @staticmethod
    def write_anchor_link(title: str, href: str) -> str:
        return (
            f'<a href="{escape(href, quote=True)}">🔗&nbsp;{escape(title)}</a>'
        )
