"""
@relation(SDOC-SRS-34, SDOC-SRS-141, scope=file)
"""

from string import Template
from typing import Optional

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

relation_marker: _RELATION_MARKER_START _WS? (relation_node_uid _SEP _WS)+ "scope=" relation_scope ("," _WS "role=" relation_role)? _WS? _BRACE_RIGHT

_RELATION_MARKER_START: /##RELATION_MARKER_START/
relation_node_uid: /##REGEX_REQ/
relation_scope: /file|class|function|line|range_start|range_end/
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
    @staticmethod
    def parse(
        source_input: str, custom_tags: Optional[set[str]] = None
    ) -> ParseTree:
        if custom_tags is not None:
            grammar_extension = NODE_GRAMMAR_EXTENSION.substitute(
                CUSTOM_TAGS="|".join(f"{tag}(?=:)" for tag in custom_tags),
                RESERVED_KEYWORDS=RESERVED_KEYWORDS,
                RELATION_MARKER_START=RELATION_MARKER_START,
                NODE_FIELD_END_MARKER="SPDX-Req-End",
            )
            start = "(relation_marker | node_field | _NORMAL_STRING_NO_MARKER_NO_NODE | _WS)*"
        else:
            grammar_extension = ""
            start = "(relation_marker | _NORMAL_STRING_NO_MARKER | _WS)*"

        grammar = GRAMMAR.substitute(
            GRAMMAR_EXTENSION=grammar_extension,
            RELATION_MARKER_START=RELATION_MARKER_START,
            REGEX_REQ=REGEX_REQ,
            START=start,
        )
        parser: Lark = Lark(
            grammar, parser="lalr", cache=True, propagate_positions=True
        )

        try:
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
