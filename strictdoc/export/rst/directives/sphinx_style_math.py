from typing import Any, Dict, List, Optional, Tuple

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.states import Inliner


def eq_role(
    _role: str,
    _rawtext: str,
    text: str,
    _lineno: int,
    _inliner: Inliner,
    _options: Optional[Dict[str, Any]] = None,
    _content: Optional[List[str]] = None,
) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
    """Handle rst :eq: role, producing a link to an equation."""
    eqref = f"\\( \\eqref{{{text}}} \\)"
    node = nodes.raw(
        "",
        f'<span class="math notranslate nohighlight">{eqref}</span>',
        format="html",
    )
    return [node], []


def eq_role_for_server(
    _role: str,
    _rawtext: str,
    text: str,
    _lineno: int,
    _inliner: Inliner,
    _options: Optional[Dict[str, Any]] = None,
    _content: Optional[List[str]] = None,
) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
    """Handle rst :eq: role, producing a link to an equation. (server edition)."""
    eqref = f"\\( \\eqref{{{text}}} \\)"

    node = nodes.raw(
        "",
        f'<span class="math notranslate nohighlight" original-math="{eqref}">{eqref}</span>',
        format="html",
    )
    return [node], []


def math_role(
    _role: str,
    rawtext: str,
    text: str,
    _lineno: int,
    _inliner: Inliner,
    _options: Optional[Dict[str, Any]] = None,
    _content: Optional[List[str]] = None,
) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
    """Handle rst :math: role, rendering a formula inline with text."""
    if rawtext.startswith(":math:`") and rawtext.endswith("`"):
        extracted = rawtext[len(":math:`") : -1]
    else:
        extracted = text

    extracted = f"\\( {extracted} \\)"

    node = nodes.raw(
        "",
        f'<span class="math notranslate nohighlight">{extracted}</span>',
        format="html",
    )
    return [node], []


def math_role_for_server(
    _role: str,
    rawtext: str,
    text: str,
    _lineno: int,
    _inliner: Inliner,
    _options: Optional[Dict[str, Any]] = None,
    _content: Optional[List[str]] = None,
) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
    """Handle rst :math: role, rendering a formula inline with text. (server edition)."""
    if rawtext.startswith(":math:`") and rawtext.endswith("`"):
        extracted = rawtext[len(":math:`") : -1]
    else:
        extracted = text

    extracted = f"\\( {extracted} \\)"

    node = nodes.raw(
        "",
        f'<span class="math notranslate nohighlight" original-math="{extracted}">{extracted}</span>',
        format="html",
    )
    return [node], []


class MathDirective(Directive):  # type: ignore[misc]
    """Docutils directive emulating Sphinx-style math syntax."""

    is_running_in_server: bool = False
    has_content = True
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "nowrap": directives.flag,
        "no-wrap": directives.flag,
        "label": directives.unchanged,
        "number": directives.flag,
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Constuct a MathDirective."""
        self.is_running_in_server = False
        super().__init__(*args, **kwargs)

    def run(self) -> List[nodes.Node]:
        """Handle ..math :: directive, rendering a formula centered, optionally with eq number."""

        nowrap = "no-wrap" in self.options or "nowrap" in self.options
        label = self.options.get("label")

        math_content = "\n".join(self.content).strip()
        html_parts = []

        if nowrap:
            mathjax_content = math_content
        else:
            parts = [p.strip() for p in math_content.split("\n\n") if p.strip()]
            if len(parts) > 1:
                wrapped = []
                for part in parts:
                    if r"\\" in part:
                        wrapped.append(r"\begin{split}" + part + r"\end{split}")
                    else:
                        wrapped.append(part)

                if label:
                    mathjax_content = (
                        f"\\begin{{equation}}\\label{{{label}}}"
                        r"\begin{aligned}"
                        + r" \\ ".join(wrapped)
                        + r"\end{aligned}\end{equation}"
                    )
                else:
                    mathjax_content = (
                        r"\begin{align*}\begin{aligned}"
                        + r" \\ ".join(wrapped)
                        + r"\end{aligned}\end{align*}"
                    )
            else:
                if label:
                    mathjax_content = f"\\begin{{equation}}\\label{{{label}}}\\begin{{aligned}} {math_content} \\end{{aligned}}\\end{{equation}}"
                else:
                    mathjax_content = (
                        f" \\begin{{align*}}  {math_content} \\end{{align*}}"
                    )

        mathjax_content = f"\\[ {mathjax_content} \\]"

        if self.is_running_in_server:
            html_parts.append(
                f'<div class="math notranslate nohighlight" original-math="{mathjax_content}">'
            )
        else:
            html_parts.append('<div class="math notranslate nohighlight">')
        html_parts.append(mathjax_content)
        html_parts.append("</div>")

        html = "".join(html_parts)
        return [nodes.raw("", html, format="html")]


class MathDirectiveForServer(MathDirective):
    """Docutils directive emulating Sphinx-style math syntax. (server edition)"""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Constuct a MathDirective, and set flag for running in server-mode."""
        super().__init__(*args, **kwargs)
        self.is_running_in_server = True
