"""
@relation(SDOC-SRS-24, scope=file)
"""

from html import escape
from typing import Optional, Tuple

from markdown_it import MarkdownIt
from markupsafe import Markup


class MarkdownToHtmlFragmentWriter:
    # Use the default preset to support common Markdown extensions such as
    # pipe tables when rendering HTML fragments.
    markdown_parser = MarkdownIt("default")

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
