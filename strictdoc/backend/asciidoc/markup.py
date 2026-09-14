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
        bullet_depth: int = 0,
        ordered_depth: int = 0,
    ) -> str:
        if isinstance(node, nodes.paragraph):
            self._check_attributes(node)
            return (
                "".join(self._render_inline(child_) for child_ in node.children)
                + "\n\n"
            )
        if isinstance(node, (nodes.bullet_list, nodes.enumerated_list)):
            return self._render_list(node, bullet_depth, ordered_depth)
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
        if isinstance(node, nodes.table):
            return self._render_table(node)
        if isinstance(node, nodes.target) and "refuri" in node:
            self._check_attributes(node, ("ids", "names", "refuri"))
            return ""
        self._fail(f"unsupported RST construct: {node.tagname}", node)
        raise AssertionError

    def _render_list(
        self,
        node: Union[nodes.bullet_list, nodes.enumerated_list],
        bullet_depth: int,
        ordered_depth: int,
    ) -> str:
        top_level = bullet_depth == 0 and ordered_depth == 0
        if isinstance(node, nodes.bullet_list):
            self._check_attributes(node, ("bullet",))
            bullet_depth += 1
            marker = "*" * bullet_depth
            attributes = ""
        else:
            self._check_attributes(
                node, ("enumtype", "prefix", "suffix", "start")
            )
            if node.get("enumtype") != "arabic":
                self._fail("unsupported non-Arabic ordered list", node)
            ordered_depth += 1
            marker = "." * ordered_depth
            start = node.get("start", 1)
            attributes = f"[start={start}]\n" if start != 1 else ""
        output = ("[]\n" if top_level else "") + attributes
        for item_ in node.children:
            if not isinstance(item_, nodes.list_item):
                self._fail("unsupported list child", item_)
            assert isinstance(item_, nodes.list_item)
            self._check_attributes(item_)
            if len(item_.children) == 0 or not isinstance(
                item_.children[0], nodes.paragraph
            ):
                self._fail("list item must start with a paragraph", item_)
            for position_, child_ in enumerate(item_.children):
                if isinstance(
                    child_, (nodes.bullet_list, nodes.enumerated_list)
                ) and (position_ != 1 or position_ != len(item_.children) - 1):
                    self._fail(
                        "a nested list must immediately follow its item's "
                        "first paragraph and be its last block",
                        child_,
                    )
                rendered = self._render_block(
                    child_, bullet_depth, ordered_depth
                ).rstrip("\n")
                if position_ == 0:
                    output += f"{marker} {rendered}\n"
                elif isinstance(
                    child_, (nodes.bullet_list, nodes.enumerated_list)
                ):
                    output += rendered + "\n"
                else:
                    output += "+\n" + rendered + "\n"
        return output + "\n"

    def _render_table(self, node: nodes.table) -> str:
        self._check_attributes(node, ("classes",))
        if any(
            class_ not in ("colwidths-auto", "colwidths-given")
            for class_ in node.get("classes", [])
        ):
            self._fail("unsupported table classes", node)
        if len(node.children) != 1 or not isinstance(
            node.children[0], nodes.tgroup
        ):
            self._fail("unsupported table structure", node)
        group = node.children[0]
        assert isinstance(group, nodes.tgroup)
        self._check_attributes(group, ("cols",))
        columns = group["cols"]
        widths: List[str] = []
        rows: List[str] = []
        header_count = 0
        for child_ in group.children:
            if isinstance(child_, nodes.colspec):
                self._check_attributes(child_, ("colwidth",))
                widths.append(str(child_["colwidth"]))
                continue
            if not isinstance(child_, (nodes.thead, nodes.tbody)):
                self._fail("unsupported table group", child_)
            assert isinstance(child_, (nodes.thead, nodes.tbody))
            self._check_attributes(child_)
            if isinstance(child_, nodes.thead):
                header_count += len(child_.children)
            for row_ in child_.children:
                if not isinstance(row_, nodes.row):
                    self._fail("unsupported table row", row_)
                assert isinstance(row_, nodes.row)
                self._check_attributes(row_)
                if len(row_.children) != columns:
                    self._fail("unsupported table cell span", row_)
                cells: List[str] = []
                for entry_ in row_.children:
                    if not isinstance(entry_, nodes.entry):
                        self._fail("unsupported table entry", entry_)
                    assert isinstance(entry_, nodes.entry)
                    self._check_attributes(entry_)
                    if len(entry_.children) == 0:
                        cells.append("")
                    elif len(entry_.children) == 1 and isinstance(
                        entry_.children[0], nodes.paragraph
                    ):
                        cells.append(
                            self._render_block(entry_.children[0])
                            .strip("\n")
                            .replace("\n", " ")
                        )
                    else:
                        self._fail("unsupported complex table cell", entry_)
                rows.append("|" + " |".join(cells))
        if header_count > 1 or len(widths) != columns:
            self._fail("unsupported table headers or columns", node)
        attributes = f'cols="{",".join(widths)}"'
        if header_count == 1:
            attributes += ',options="header"'
        return f"[{attributes}]\n|===\n" + "\n".join(rows) + "\n|===\n\n"
