# mypy: disable-error-code="no-untyped-def"
# ruff: noqa: ARG001
# pylint: disable-all
from docutils import nodes


def raw_html_role(
    name,
    rawtext,
    text,
    lineno,
    inliner,
    options={},  # noqa: B006
    content=[],  # noqa: B006
):
    html = nodes.raw(text, text, format="html")
    return [html], []
