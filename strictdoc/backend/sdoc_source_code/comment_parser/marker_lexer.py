from lark import Lark, ParseTree, UnexpectedToken

from strictdoc.backend.sdoc_source_code.constants import (
    REGEX_REQ,
    RESERVED_KEYWORDS,
)

GRAMMAR = f"""
start: (relation_marker | node_field | _NORMAL_STRING | _WS)*

relation_marker: "@relation" _BRACE_LEFT _WS? (relation_node_uid _SEP _WS)+ "scope=" relation_scope ("," _WS "role=" relation_role)? _WS? _BRACE_RIGHT

relation_node_uid: /{REGEX_REQ}/
relation_scope: /file|class|function|line|range_start|range_end/
relation_role: ALPHANUMERIC_WORD

node_field: node_name ":" _WS_INLINE node_multiline_value
node_name: /(?!({RESERVED_KEYWORDS}))[A-Z_]+/
node_multiline_value: (NORMAL_STRING_VALUE _NL)+
NORMAL_STRING_VALUE.2: /[ ]*(?!\\s*@relation)(?![A-Z_]+:)[^\n\r]+/x

NORMAL_STRING: /(?!\\s*@relation)((?![A-Z_]+:)|({RESERVED_KEYWORDS})).+/
_NORMAL_STRING: NORMAL_STRING

_BRACE_LEFT: /[\\(\\{{]/
_BRACE_RIGHT: /[\\)\\}}]/

_SEP: ","
_NL : NL
_WS : WS
_WS_INLINE : WS_INLINE

ALPHANUMERIC_WORD: /[a-zA-Z0-9_]+/
NL: /\\r?\\n/

%import common.WS -> WS
%import common.WS_INLINE -> WS_INLINE
"""


class MarkerLexer:
    @staticmethod
    def parse(source_input: str) -> ParseTree:
        parser: Lark = Lark(
            GRAMMAR, parser="lalr", cache=True, propagate_positions=True
        )

        try:
            # FIXME: Without rstrip, there is an edge case where the parser
            #        breaks when resolving conflicts between multiline node
            #        fields and normal strings.
            #        See also test: test_31_single_node_field.
            tree: ParseTree = parser.parse(source_input.rstrip() + "\n")
        except UnexpectedToken as exception_:
            print(  # noqa: T201
                "error: could not parse source comment:\n" + source_input
            )
            raise exception_
        return tree
