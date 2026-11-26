"""
@relation(SDOC-SRS-34, SDOC-SRS-141, scope=file)
"""

from string import Template
from typing import ClassVar, Optional

from lark import Lark, ParseTree, UnexpectedToken

from strictdoc.backend.sdoc_source_code.constants import (
    REGEX_REQ,
    RESERVED_KEYWORDS,
)


class GrammarTemplate(Template):
    delimiter = "##"


RELATION_MARKER_START = r"@relation[\(\{]"

NODE_GRAMMAR_EXTENSION = GrammarTemplate("""
node_field: node_name ":" node_multiline_value
node_name: /##CUSTOM_TAGS/
node_multiline_value: (_WS_INLINE? | (_WS_INLINE NODE_STRING_VALUE)) NEWLINE (NODE_STRING_VALUE NEWLINE)*

NODE_STRING_VALUE.2: /(?![ ]*##RELATION_MARKER_START)(?!\\s*(##CUSTOM_TAGS):\\s)(?!\\s*##NODE_FIELD_END_MARKER)[^\\n\\r]+/

_NORMAL_STRING_NO_MARKER_NO_NODE: /(?!\\s*##RELATION_MARKER_START)((?!\\s*(##CUSTOM_TAGS):\\s)|(##RESERVED_KEYWORDS)).+/
""")

GRAMMAR = GrammarTemplate("""
start: ##START

relation_marker: _RELATION_MARKER_START _WS? relation_node_uid (_SEP _WS relation_node_uid)* (_SEP _WS "scope=" relation_scope)? (_SEP _WS "role=" relation_role)? _WS? _BRACE_RIGHT

_RELATION_MARKER_START: /##RELATION_MARKER_START/
relation_node_uid: /##REGEX_REQ/
relation_scope: /file|class|component|function|line|range_start|range_end/
relation_role: ALPHANUMERIC_WORD

##GRAMMAR_EXTENSION

_NORMAL_STRING_NO_MARKER: /(?!\\s*##RELATION_MARKER_START).+/

_BRACE_LEFT: /[\\(\\{{]/
_BRACE_RIGHT: /[\\)\\}}]/

_SEP: ","

_NL : (CR? LF)

_WS : WS
_WS_INLINE : WS_INLINE

ALPHANUMERIC_WORD: /[a-zA-Z0-9_]+/

%import common.WS -> WS
%import common.CR -> CR
%import common.LF -> LF
%import common.WS_INLINE -> WS_INLINE
%import common.NEWLINE -> NEWLINE
""")


class MarkerLexer:
    # Building a Lark parser from a grammar takes about 1.5 ms. Parsing one
    # comment takes about 0.02 ms, and a project can have thousands of
    # comments. As a result, MarkerLexer builds one parser per set of custom
    # tags and keeps the parser for the lifetime of the process.
    #
    # Thread safety: all threads share these parsers. Comments are parsed when
    # the traceability index reads source files:
    # - Export reads source files in its main thread.
    # - The server reads source files when it rebuilds the traceability index:
    #   at startup, in request handlers, and in the file watcher thread. The
    #   global write lock of the server lets only one rebuild run at a time.
    # MarkerLexer does not rely on the callers to parse one comment at a time.
    # The comments in parse() explain why each step is safe without a lock.
    _parsers: ClassVar[dict[Optional[frozenset[str]], Lark]] = {}

    @staticmethod
    def parse(
        source_input: str, custom_tags: Optional[set[str]] = None
    ) -> ParseTree:
        # The key is an immutable copy of the custom tags. If the caller
        # changes its set later, the cache does not change. Equal sets give
        # equal keys and share one parser. None and an empty set give different
        # keys because they give different grammars.
        key: Optional[frozenset[str]] = (
            frozenset(custom_tags) if custom_tags is not None else None
        )

        # A dict read and a dict write are atomic, so the cache needs no lock.
        # Two threads can miss the cache at once and both build a parser for
        # one key. The second parser replaces the first one in the cache. Both
        # parsers are equal, so this costs one extra build and is harmless.
        parser: Optional[Lark] = MarkerLexer._parsers.get(key)
        if parser is None:
            parser = Lark(
                MarkerLexer._build_grammar(key),
                parser="lalr",
                cache=True,
                propagate_positions=True,
            )
            MarkerLexer._parsers[key] = parser

        try:
            # Several threads can parse with this parser at once. Lark does not
            # document thread safety, but the Lark 1.3 source shows that this
            # is safe for an LALR parser:
            # - Lark.parse() creates a new lexer state and a new parser state
            #   for each call.
            # - Parsing only reads the parse table, the lexers, and the tree
            #   callbacks.
            # - A lexer builds its scanner on first use. If two threads build
            #   the scanner at once, both scanners are equal and one of them is
            #   kept.
            #
            # FIXME: Without rstrip, there is an edge case where the parser
            #        breaks when resolving conflicts between multiline node
            #        fields and normal strings.
            #        See also test: test_31_single_node_field.
            tree: ParseTree = parser.parse(source_input.rstrip() + "\n")
        except UnexpectedToken as exception_:  # pragma: no cover
            print(  # noqa: T201
                "error: could not parse source comment:\n" + source_input
            )
            raise exception_
        return tree

    @staticmethod
    def _build_grammar(key: Optional[frozenset[str]]) -> str:
        """
        Build the grammar for a cache key of parse().

        The key is the only input that varies, so a cached parser always
        matches the grammar for its key. All other inputs are module
        constants. The function reads no shared state and is thread-safe.
        """
        if key is not None:
            grammar_extension = NODE_GRAMMAR_EXTENSION.substitute(
                # The tags are sorted, so one key always gives the same
                # grammar text, also in other processes. The order does not
                # change what the grammar matches, because each tag must be
                # followed by ":".
                CUSTOM_TAGS="|".join(f"{tag}(?=:)" for tag in sorted(key)),
                RESERVED_KEYWORDS=RESERVED_KEYWORDS,
                RELATION_MARKER_START=RELATION_MARKER_START,
                NODE_FIELD_END_MARKER="SPDX-Req-End",
            )
            start = "(relation_marker | node_field | _NORMAL_STRING_NO_MARKER_NO_NODE | _WS)*"
        else:
            grammar_extension = ""
            start = "(relation_marker | _NORMAL_STRING_NO_MARKER | _WS)*"

        return GRAMMAR.substitute(
            GRAMMAR_EXTENSION=grammar_extension,
            RELATION_MARKER_START=RELATION_MARKER_START,
            REGEX_REQ=REGEX_REQ,
            START=start,
        )
