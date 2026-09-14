import io
import re
import string
from typing import Callable, Dict, List, NoReturn, Optional, Tuple, Union
from urllib.parse import quote, urlsplit

from docutils import nodes
from docutils.core import publish_doctree
from docutils.utils import column_width

from strictdoc.backend.sdoc.constants import SDocMarkup
from strictdoc.backend.sdoc.models.anchor import Anchor
from strictdoc.backend.sdoc.models.inline_link import InlineLink
from strictdoc.backend.sdoc.models.node import SDocNodeField
from strictdoc.helpers.exception import StrictDocException


def escape_text(value: str) -> str:
    return "".join(
        f"&#{ord(character_)};"
        if character_ in string.punctuation
        and not (
            character_ == "-"
            and index_ > 0
            and index_ + 1 < len(value)
            and value[index_ - 1].isalnum()
            and value[index_ + 1].isalnum()
        )
        else character_
        for index_, character_ in enumerate(value)
    )


class MarkupRenderer:
    def __init__(
        self,
        resolve_link: Callable[[InlineLink], Tuple[str, str]],
        resolve_anchor: Callable[[Anchor], str],
        resolve_image: Callable[[str], str],
    ) -> None:
        self.resolve_link: Callable[[InlineLink], Tuple[str, str]] = (
            resolve_link
        )
        self.resolve_anchor: Callable[[Anchor], str] = resolve_anchor
        self.resolve_image: Callable[[str], str] = resolve_image
        self._context: str = ""
        self._parts: Dict[str, Union[InlineLink, Anchor]] = {}
        self._token_pattern: Optional[re.Pattern[str]] = None

    def render(
        self,
        field: SDocNodeField,
        markup: Optional[str],
        context: str,
    ) -> str:
        self._context = context
        self._parts = {}
        if markup not in (None, SDocMarkup.RST, SDocMarkup.TEXT):
            self._fail(f"unsupported source markup: {markup}")

        source_text = "".join(
            part_ for part_ in field.parts if isinstance(part_, str)
        )
        source_parts: List[str] = []
        token_number = 0
        for part_ in field.parts:
            if isinstance(part_, str):
                source_parts.append(part_)
            elif isinstance(part_, (InlineLink, Anchor)):
                width = (
                    column_width(f"[LINK: {part_.link}]")
                    if isinstance(part_, InlineLink)
                    else 12
                )
                while True:
                    token = f"SD{token_number:0{width - 3}x}X"
                    token_number += 1
                    if len(token) > width:
                        self._fail("too many inline references in one field")
                    if token not in source_text and token not in self._parts:
                        break
                self._parts[token] = part_
                source_parts.append(token)
                if isinstance(part_, Anchor):
                    source_parts.append("\n")
            else:
                self._fail("unsupported StrictDoc field part")
        self._token_pattern = re.compile(
            "(" + "|".join(self._parts) + ")"
            if len(self._parts) > 0
            else r"(?!x)x"
        )
        source = "".join(source_parts)
        if len(source.strip()) == 0:
            return ""
        if markup == SDocMarkup.TEXT:
            rendered_text = self._render_text(source)
            return (
                '[verse,subs="specialchars,macros,replacements"]\n'
                f"____\n{rendered_text}\n____\n"
            )

        warning_stream = io.StringIO()
        document = publish_doctree(
            source,
            source_path=context,
            settings_overrides={
                "file_insertion_enabled": False,
                "raw_enabled": False,
                "syntax_highlight": "none",
                "halt_level": 6,
                "report_level": 2,
                "warning_stream": warning_stream,
            },
        )
        if warning_stream.tell() > 0:
            self._fail(
                f"RST parsing failed: {warning_stream.getvalue().strip()}"
            )
        for message_ in list(document.findall(nodes.system_message)):
            if message_["level"] >= 2:
                self._fail(f"RST parsing failed: {message_.astext()}", message_)
            assert message_.parent is not None
            message_.parent.remove(message_)
        output = "".join(
            self._render_block(child_) for child_ in document.children
        )
        return output.rstrip("\n") + "\n"

    def _fail(
        self, message: str, node: Optional[nodes.Node] = None
    ) -> NoReturn:
        location = self._context
        if node is not None and node.line is not None:
            location += f", field line {node.line}"
        raise StrictDocException(f"AsciiDoc export: {location}: {message}")

    def _check_attributes(
        self, node: nodes.Element, allowed: Tuple[str, ...] = ()
    ) -> None:
        for name_, value_ in node.attributes.items():
            if name_ not in allowed and value_ not in (None, [], "", False):
                self._fail(
                    f"unsupported RST {node.tagname} attribute: {name_}", node
                )

    def _render_text(self, value: str) -> str:
        assert self._token_pattern is not None
        output: List[str] = []
        for part_ in self._token_pattern.split(value):
            structural_part = self._parts.get(part_)
            try:
                if isinstance(structural_part, InlineLink):
                    target, label = self.resolve_link(structural_part)
                    output.append(f"xref:{target}[{escape_text(label)}]")
                elif isinstance(structural_part, Anchor):
                    anchor = self.resolve_anchor(structural_part)
                    output.append(f"anchor:{anchor}[]")
                else:
                    output.append(escape_text(part_))
            except StrictDocException as exception:
                self._fail(str(exception))
        return "".join(output)

    def _literal(self, value: str, node: nodes.Node) -> str:
        assert self._token_pattern is not None
        if self._token_pattern.search(value) is not None:
            self._fail(
                "StrictDoc links or anchors inside literal content", node
            )
        return escape_text(value)

    def _render_inline(self, node: nodes.Node) -> str:
        if isinstance(node, nodes.Text):
            return self._render_text(str(node))
        if isinstance(node, (nodes.strong, nodes.emphasis)):
            self._check_attributes(node)
            marker = "**" if isinstance(node, nodes.strong) else "__"
            content = "".join(
                self._render_inline(child_) for child_ in node.children
            )
            return f"{marker}{content}{marker}"
        if isinstance(node, nodes.literal):
            self._check_attributes(node)
            return f"``{self._literal(node.astext(), node)}``"
        if isinstance(node, nodes.reference):
            self._check_attributes(node, ("refuri", "name"))
            target = node.get("refuri")
            if not isinstance(target, str):
                self._fail("unsupported RST internal reference", node)
            assert isinstance(target, str)
            assert self._token_pattern is not None
            if self._token_pattern.search(target) is not None:
                self._fail("StrictDoc link or anchor inside a URL", node)
            if self._token_pattern.search(node.astext()) is not None:
                self._fail("StrictDoc link or anchor inside an RST link", node)
            try:
                scheme = urlsplit(target).scheme
            except ValueError:
                self._fail(f"invalid link URI: {target}", node)
            if scheme not in ("http", "https", "mailto"):
                self._fail(f"unsupported link URI: {target}", node)
            target = quote(target, safe="/:?#@!$&'()*+;=%~-._")
            label = "".join(
                self._render_inline(child_) for child_ in node.children
            )
            return f"link:{target}[{label}]"
        if isinstance(node, nodes.target) and "refuri" in node:
            self._check_attributes(node, ("ids", "names", "refuri"))
            return ""
        self._fail(f"unsupported RST construct: {node.tagname}", node)
        raise AssertionError

    def _render_block(
        self,
        node: nodes.Node,
    ) -> str:
        if isinstance(node, nodes.paragraph):
            self._check_attributes(node)
            return (
                "".join(self._render_inline(child_) for child_ in node.children)
                + "\n\n"
            )
        if isinstance(node, nodes.literal_block):
            self._check_attributes(node, ("classes", "xml:space"))
            classes = node.get("classes", [])
            language = ""
            if len(classes) > 0:
                if (
                    classes[0] != "code"
                    or len(classes) > 2
                    or (
                        len(classes) == 2
                        and re.fullmatch(r"[A-Za-z0-9_+-]+", classes[1]) is None
                    )
                ):
                    self._fail("unsupported code block classes", node)
                if len(classes) == 2:
                    language = "," + classes[1]
            content = self._literal(node.astext(), node)
            return (
                f'[source{language},subs="specialchars,replacements"]\n'
                f"----\n{content}\n----\n\n"
            )
        if isinstance(node, nodes.target) and "refuri" in node:
            self._check_attributes(node, ("ids", "names", "refuri"))
            return ""
        self._fail(f"unsupported RST construct: {node.tagname}", node)
        raise AssertionError
