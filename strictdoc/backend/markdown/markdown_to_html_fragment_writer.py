"""
@relation(SDOC-SRS-24, scope=file)
"""

from html import escape
from typing import Callable, MutableMapping, Optional, Sequence, Tuple, cast

from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml, unescapeAll
from markdown_it.renderer import RendererHTML
from markdown_it.token import Token
from markdown_it.utils import EnvType, OptionsDict
from markupsafe import Markup

_MARKDOWN_PARSER = MarkdownIt("default")
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


class MarkdownToHtmlFragmentWriter:
    # Use the default preset to support common Markdown extensions such as
    # pipe tables when rendering HTML fragments.
    markdown_parser = _MARKDOWN_PARSER
    _MARKDOWN_RENDERER_RULES["fence"] = _render_fence

    @staticmethod
    def write(markdown_fragment: str) -> Markup:
        assert isinstance(markdown_fragment, str), markdown_fragment
        return Markup(
            MarkdownToHtmlFragmentWriter.markdown_parser.render(
                markdown_fragment
            )
        )

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
