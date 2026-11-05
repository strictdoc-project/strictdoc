"""
Scanner for the classes and component declarations of a Modelica file.

The scanner is tolerant and does not validate. It finds the items that
requirements-to-source traceability needs and skips all other text. The
scanner follows the Modelica Language Specification 3.6: the concrete syntax
in appendix A and the chapters on classes (4) and functions (12).

The scanner recognizes:

- Long class definitions with all class prefixes and kinds, including
  "model extends X ... end X;".
- Short class definitions, for example "type T = Real(unit="K") "desc";".
- Nested classes. Each item has its qualified name, which starts with the
  package name of the "within" clause.
- Component declarations in the public and protected sections of a class.
  "Real a, b;" gives one item for each name.
- The description string of each class and component.

The scanner skips modifications, annotations, imports, extends clauses,
equations and algorithms as balanced text. It returns the comments
separately, so that a caller can read the relation markers in them.

All offsets are byte offsets in the scanned input. All lines are 1-based.

@relation(SDOC-LLR-219, SDOC-LLR-223, scope=file)
"""

import bisect
import re
from enum import Enum
from typing import List, Optional, Tuple

from strictdoc.helpers.auto_described import auto_described

CLASS_KINDS = frozenset(
    (
        b"block",
        b"class",
        b"connector",
        b"function",
        b"model",
        b"operator",
        b"package",
        b"record",
        b"type",
    )
)
CLASS_PREFIXES = frozenset(
    (
        b"encapsulated",
        b"expandable",
        b"final",
        b"impure",
        b"inner",
        b"outer",
        b"partial",
        b"pure",
        b"redeclare",
        b"replaceable",
    )
)
ELEMENT_PREFIXES = frozenset(
    (b"final", b"inner", b"outer", b"redeclare", b"replaceable")
)
TYPE_PREFIXES = frozenset(
    (
        b"constant",
        b"discrete",
        b"flow",
        b"input",
        b"output",
        b"parameter",
        b"stream",
    )
)
SECTION_KEYWORDS = frozenset(
    (b"algorithm", b"equation", b"external", b"protected", b"public")
)

# "end if;", "end for;", "end when;" and "end while;" do not end a class.
_END_OF_BLOCK_KEYWORDS = frozenset((b"for", b"if", b"when", b"while"))

# A string after one of these tokens is a value, not a description string.
# Examples: 'String s = "x";' and 'if c then "a" else "b"'.
_TOKENS_BEFORE_VALUE = frozenset(
    (b"=", b":=", b"then", b"else", b"+", b"(", b",", b"and", b"or", b"not")
)

_OPENING_BRACKETS = (b"(", b"[", b"{")
_CLOSING_BRACKETS = (b")", b"]", b"}")

_TOKEN_REGEX = re.compile(
    rb"""
     (?P<whitespace>\s+)
    |(?P<line_comment>//[^\n]*)
    |(?P<block_comment>/\*.*?\*/)
    |(?P<string>"(?:\\.|[^"\\])*")
    |(?P<quoted_identifier>'(?:\\.|[^'\\])*')
    |(?P<number>\d+(?:\.\d*)?(?:[eE][+-]?\d+)?)
    |(?P<identifier>[A-Za-z_][A-Za-z0-9_]*)
    |(?P<operator>\.\+|\.-|\.\*|\./|\.\^|:=|==|<>|<=|>=|[()\[\]{};,.=:+\-*/^<>])
    |(?P<other>.)
    """,
    re.DOTALL | re.VERBOSE,
)


class ModelicaScanError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"line {line}: {message}")
        self.message: str = message
        self.line: int = line


class ModelicaItemKind(Enum):
    CLASS = "class"
    COMPONENT = "component"


@auto_described
class ModelicaComment:
    def __init__(self, *, line_begin: int, byte_begin: int, byte_end: int):
        self.line_begin: int = line_begin
        self.byte_begin: int = byte_begin
        self.byte_end: int = byte_end


@auto_described
class ModelicaItem:
    def __init__(
        self,
        *,
        kind: ModelicaItemKind,
        name: str,
        line_begin: int,
        line_end: int,
        byte_begin: int,
        byte_end: int,
    ):
        self.kind: ModelicaItemKind = kind
        # The qualified name, for example "Rig.Check.req1Check".
        self.name: str = name
        # From the first prefix of the definition to its closing ";".
        self.line_begin: int = line_begin
        self.line_end: int = line_end
        self.byte_begin: int = byte_begin
        self.byte_end: int = byte_end
        # From the opening quote of the description string to its closing
        # quote. A description string can be a concatenation: "a" + "b".
        self.description_byte_range: Optional[Tuple[int, int]] = None


@auto_described
class ModelicaScanResult:
    def __init__(
        self,
        *,
        within: str,
        items: List[ModelicaItem],
        comments: List[ModelicaComment],
    ):
        # The package name of the "within" clause, or "" if there is none.
        self.within: str = within
        # All classes and components in the order of the source.
        self.items: List[ModelicaItem] = items
        self.comments: List[ModelicaComment] = comments


def scan_modelica(source: bytes) -> ModelicaScanResult:
    """
    Scan the classes, components and comments of a Modelica file.

    Raise ModelicaScanError with the line of the error if the scanner cannot
    follow the file.
    """
    tokens, comments, line_offsets = _tokenize(source)
    return _ModelicaScanner(tokens, line_offsets).scan(comments)


class _Token:
    def __init__(self, kind: str, text: bytes, byte_begin: int, byte_end: int):
        self.kind: str = kind
        self.text: bytes = text
        self.byte_begin: int = byte_begin
        self.byte_end: int = byte_end


def _line_of(line_offsets: List[int], byte_offset: int) -> int:
    return bisect.bisect_right(line_offsets, byte_offset)


def _tokenize(
    source: bytes,
) -> Tuple[List[_Token], List[ModelicaComment], List[int]]:
    line_offsets: List[int] = [0] + [
        match_.end() for match_ in re.finditer(b"\n", source)
    ]
    tokens: List[_Token] = []
    comments: List[ModelicaComment] = []
    position = 0
    while position < len(source):
        match = _TOKEN_REGEX.match(source, position)
        assert match is not None
        kind = match.lastgroup
        assert kind is not None
        text = match.group()
        if (kind == "other" and text in (b'"', b"'")) or (
            kind == "operator" and source.startswith(b"/*", position)
        ):
            raise ModelicaScanError(
                "unterminated string, quoted name or comment",
                _line_of(line_offsets, position),
            )
        if kind in ("line_comment", "block_comment"):
            comments.append(
                ModelicaComment(
                    line_begin=_line_of(line_offsets, match.start()),
                    byte_begin=match.start(),
                    byte_end=match.end(),
                )
            )
        elif kind != "whitespace":
            tokens.append(_Token(kind, text, match.start(), match.end()))
        position = match.end()
    return tokens, comments, line_offsets


class _ModelicaScanner:
    def __init__(self, tokens: List[_Token], line_offsets: List[int]):
        self.tokens: List[_Token] = tokens
        self.index: int = 0
        self.line_offsets: List[int] = line_offsets
        self.items: List[ModelicaItem] = []

    def scan(self, comments: List[ModelicaComment]) -> ModelicaScanResult:
        """
        Scan a stored definition: an optional "within" clause and classes.
        """
        within = ""
        if self._text_at() == b"within":
            self.index += 1
            name_begin = self.index
            semicolon = self._scan_to((b";",))
            within = b"".join(
                token_.text for token_ in self.tokens[name_begin:semicolon]
            ).decode("utf-8")
            self.index = semicolon + 1
        while self.index < len(self.tokens):
            if self._text_at() == b"final" and not self._at_class_start():
                self.index += 1
            if not self._at_class_start():
                raise self._error(
                    "a class definition expected, found "
                    f"{self._describe_token()}"
                )
            self._class_definition(within)
            self._skip_statement()
        return ModelicaScanResult(
            within=within, items=self.items, comments=comments
        )

    def _class_definition(self, owner_name: str) -> None:
        first_token = self.index
        while self._text_at() in CLASS_PREFIXES:
            self.index += 1
        self.index += 1  # The class kind.
        if self.tokens[self.index - 1].text == b"operator" and (
            self._text_at() in (b"record", b"function")
        ):
            self.index += 1
        if self._text_at() == b"extends":
            # "model extends Name ... end Name;"
            self.index += 1
            name = self._expect_name()
            if self._text_at() == b"(":
                self._skip_balanced()
            self._long_class(owner_name, name, first_token)
            return
        name = self._expect_name()
        if self._text_at() == b"=":
            self._short_class(owner_name, name, first_token)
            return
        self._long_class(owner_name, name, first_token)

    def _short_class(
        self, owner_name: str, name: str, first_token: int
    ) -> None:
        declaration_begin = self.index
        semicolon = self._scan_to((b";",))
        item = self._create_item(
            ModelicaItemKind.CLASS,
            _qualified_name(owner_name, name),
            first_token,
            semicolon,
        )
        item.description_byte_range = _description_byte_range(
            self.tokens, declaration_begin, semicolon
        )

    def _long_class(self, owner_name: str, name: str, first_token: int) -> None:
        item = self._create_item(
            ModelicaItemKind.CLASS,
            _qualified_name(owner_name, name),
            first_token,
            first_token,
        )
        description_begin = self.index
        while self._kind_at() == "string":
            self.index += 1
            if self._text_at() == b"+" and self._kind_at(1) == "string":
                self.index += 1
        if self.index > description_begin:
            item.description_byte_range = (
                self.tokens[description_begin].byte_begin,
                self.tokens[self.index - 1].byte_end,
            )
        self._composition(item.name, name)
        self.index += 1  # "end"
        end_name = self._expect_name()
        if end_name != name:
            raise self._error(
                f"'end {end_name};' does not match the class name {name}"
            )
        item.line_end = self._line()
        item.byte_end = self.tokens[self.index].byte_end

    def _composition(self, class_name: str, short_name: str) -> None:
        while True:
            if self.index >= len(self.tokens):
                raise self._error(
                    f"'end {short_name};' expected before the end of the file"
                )
            text = self._text_at()
            if self._at_class_end():
                return
            if text in (b"public", b"protected"):
                self.index += 1
            elif text in (b"equation", b"algorithm"):
                self.index += 1
                self._skip_section()
            elif text == b"initial" and self._text_at(1) in (
                b"equation",
                b"algorithm",
            ):
                self.index += 2
                self._skip_section()
            elif text in (b"external", b"annotation", b"import", b"extends"):
                self._skip_statement()
            else:
                self._element(class_name)

    def _skip_section(self) -> None:
        """
        Skip an equation or algorithm section up to the next section keyword
        or the end of the class.
        """
        depth = 0
        while self.index < len(self.tokens):
            token = self.tokens[self.index]
            if token.kind == "operator" and token.text in _OPENING_BRACKETS:
                depth += 1
            elif token.kind == "operator" and token.text in _CLOSING_BRACKETS:
                depth -= 1
            elif depth == 0:
                if token.text in SECTION_KEYWORDS:
                    return
                if token.text == b"initial" and self._text_at(1) in (
                    b"equation",
                    b"algorithm",
                ):
                    return
                if self._at_class_end():
                    return
            self.index += 1
        raise self._error(
            "the end of the file inside an equation or algorithm section"
        )

    def _element(self, class_name: str) -> None:
        if self._at_class_start():
            self._class_definition(class_name)
            # Skip a "constrainedby" clause up to the ";".
            self._skip_statement()
            return
        first_token = self.index
        while self._text_at() in ELEMENT_PREFIXES:
            self.index += 1
        while self._text_at() in TYPE_PREFIXES:
            self.index += 1
        # The type name, for example ".Modelica.Units.SI.Time".
        if self._text_at() == b".":
            self.index += 1
        self._expect_name()
        while self._text_at() == b"." and self._kind_at(1) in (
            "identifier",
            "quoted_identifier",
        ):
            self.index += 2
        if self._text_at() == b"[":
            self._skip_balanced()
        # The component list: "Real a, b;".
        while True:
            name = self._expect_name()
            declaration_begin = self.index
            separator = self._scan_to((b",", b";"))
            item = self._create_item(
                ModelicaItemKind.COMPONENT,
                _qualified_name(class_name, name),
                first_token,
                separator,
            )
            item.description_byte_range = _description_byte_range(
                self.tokens, declaration_begin, separator
            )
            self.index = separator + 1
            if self.tokens[separator].text == b";":
                return

    def _create_item(
        self,
        kind: ModelicaItemKind,
        name: str,
        first_token: int,
        last_token: int,
    ) -> ModelicaItem:
        item = ModelicaItem(
            kind=kind,
            name=name,
            line_begin=self._line(first_token),
            line_end=self._line(last_token),
            byte_begin=self.tokens[first_token].byte_begin,
            byte_end=self.tokens[last_token].byte_end,
        )
        self.items.append(item)
        return item

    def _at_class_start(self) -> bool:
        offset = 0
        while self._text_at(offset) in CLASS_PREFIXES:
            offset += 1
        return (
            self._kind_at(offset) == "identifier"
            and self._text_at(offset) in CLASS_KINDS
        )

    def _at_class_end(self) -> bool:
        return (
            self._text_at() == b"end"
            and self._kind_at(1) in ("identifier", "quoted_identifier")
            and self._text_at(1) not in _END_OF_BLOCK_KEYWORDS
            and self._text_at(2) == b";"
        )

    def _skip_balanced(self) -> None:
        """
        Skip from an opening bracket past its closing bracket.
        """
        depth = 0
        while self.index < len(self.tokens):
            token = self.tokens[self.index]
            if token.kind == "operator" and token.text in _OPENING_BRACKETS:
                depth += 1
            elif token.kind == "operator" and token.text in _CLOSING_BRACKETS:
                depth -= 1
            self.index += 1
            if depth == 0:
                return
        raise self._error("unbalanced brackets at the end of the file")

    def _scan_to(self, stop_tokens: Tuple[bytes, ...]) -> int:
        """
        Move to the next stop token outside of brackets and return its index.
        """
        depth = 0
        while self.index < len(self.tokens):
            token = self.tokens[self.index]
            if token.kind == "operator" and token.text in _OPENING_BRACKETS:
                depth += 1
            elif token.kind == "operator" and token.text in _CLOSING_BRACKETS:
                depth -= 1
            elif depth == 0 and token.text in stop_tokens:
                return self.index
            self.index += 1
        expected = " or ".join(
            f"'{stop_token_.decode('utf-8')}'" for stop_token_ in stop_tokens
        )
        raise self._error(f"{expected} expected before the end of the file")

    def _skip_statement(self) -> None:
        self._scan_to((b";",))
        self.index += 1

    def _expect_name(self) -> str:
        if self._kind_at() not in ("identifier", "quoted_identifier"):
            raise self._error(
                f"a name expected, found {self._describe_token()}"
            )
        self.index += 1
        return self.tokens[self.index - 1].text.decode("utf-8")

    def _text_at(self, offset: int = 0) -> Optional[bytes]:
        position = self.index + offset
        if position < len(self.tokens):
            return self.tokens[position].text
        return None

    def _kind_at(self, offset: int = 0) -> Optional[str]:
        position = self.index + offset
        if position < len(self.tokens):
            return self.tokens[position].kind
        return None

    def _describe_token(self) -> str:
        text = self._text_at()
        if text is None:
            return "the end of the file"
        return f"'{text.decode('utf-8', errors='replace')}'"

    def _line(self, token_index: Optional[int] = None) -> int:
        if len(self.tokens) == 0:
            return 1
        if token_index is None:
            token_index = self.index
        token_index = min(token_index, len(self.tokens) - 1)
        return _line_of(self.line_offsets, self.tokens[token_index].byte_begin)

    def _error(self, message: str) -> ModelicaScanError:
        return ModelicaScanError(message, self._line())


def _qualified_name(owner_name: str, name: str) -> str:
    if len(owner_name) > 0:
        return f"{owner_name}.{name}"
    return name


def _description_byte_range(
    tokens: List[_Token], begin: int, end: int
) -> Optional[Tuple[int, int]]:
    """
    Find the description string of the declaration tokens[begin:end].

    The description string is the last run of strings, joined by "+", outside
    of brackets and before "annotation". A run of strings that is a value
    ('= "x"') is not a description string. In a component list, each
    declaration has its own description string: in 'Real re, im "parts";',
    "parts" describes im only.
    """
    depth = 0
    stop = end
    for index_ in range(begin, end):
        token_ = tokens[index_]
        if token_.kind == "operator" and token_.text in _OPENING_BRACKETS:
            depth += 1
        elif token_.kind == "operator" and token_.text in _CLOSING_BRACKETS:
            depth -= 1
        elif depth == 0 and token_.text == b"annotation":
            stop = index_
            break
    last = stop - 1
    if last < begin or tokens[last].kind != "string":
        return None
    first = last
    while (
        first - 2 >= begin
        and tokens[first - 1].text == b"+"
        and tokens[first - 2].kind == "string"
    ):
        first -= 2
    if first - 1 >= begin and tokens[first - 1].text in _TOKENS_BEFORE_VALUE:
        return None
    return tokens[first].byte_begin, tokens[last].byte_end
