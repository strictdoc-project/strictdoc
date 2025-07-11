from typing import Any, Dict, List, Optional, Tuple

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.states import Inliner


def eq_role(
    _role: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: Inliner,
    _options: Optional[Dict[str, Any]] = None,
    _content: Optional[List[str]] = None,
) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
    """Handle rst :eq: role, producing a link to an equation."""
    doc = inliner.document

    if (
        not hasattr(doc, "math_equation_labels")
        or text not in doc.math_equation_labels
    ):
        msg = inliner.reporter.error(
            f"Unknown equation label: {text}", line=lineno
        )
        return [inliner.problematic(rawtext, rawtext, msg)], [msg]

    eq_number = doc.math_equation_labels[text]
    ref = nodes.raw("", f'<a href="#{text}">({eq_number})</a>', format="html")
    return [ref], []


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

    node = nodes.raw(
        "",
        f'<span class="math notranslate nohighlight">\\( {extracted} \\)</span>',
        format="html",
    )
    return [node], []


class MathDirective(Directive):
    """Docutils directive emulating Sphinx-style math syntax."""

    has_content = True
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "nowrap": directives.flag,
        "label": directives.unchanged,
        "number": directives.flag,
    }

    def run(self) -> List[nodes.Node]:
        """Handle ..math :: directive, rendering a formula centered, optionally with eq number."""
        doc = self.state.document
        if not hasattr(doc, "math_equation_counter"):
            doc.math_equation_counter = 0
            doc.math_equation_labels = {}

        nowrap = "nowrap" in self.options
        label = self.options.get("label")
        numbered = "number" in self.options or label is not None

        math_content = "\n".join(self.content).strip()
        html_parts = []

        if numbered:
            doc.math_equation_counter += 1
            eq_number = doc.math_equation_counter
            if label:
                doc.math_equation_labels[label] = eq_number
            number_html = f'<span class="eqno">({eq_number})</span>'
        else:
            number_html = ""

        if nowrap:
            html_parts.append('<div class="math notranslate nohighlight">')
            html_parts.append(math_content)
            html_parts.append(number_html)
            html_parts.append("</div>")
        else:
            parts = [p.strip() for p in math_content.split("\n\n") if p.strip()]
            if len(parts) > 1:
                wrapped = []
                for part in parts:
                    if r"\\" in part:
                        wrapped.append(r"\begin{split}" + part + r"\end{split}")
                    else:
                        wrapped.append(part)
                mathjax_content = (
                    r"\begin{align}\begin{aligned}"
                    + r" \\ ".join(wrapped)
                    + r"\end{aligned}\end{align}"
                )
            else:
                mathjax_content = math_content

            html_parts.append('<div class="math notranslate nohighlight">')
            html_parts.append(number_html)
            html_parts.append(f"\\[{mathjax_content}\\]")
            html_parts.append("</div>")

        if label:
            html_parts.insert(0, f'<a id="{label}"></a>')

        html = "".join(html_parts)
        return [nodes.raw("", html, format="html")]
