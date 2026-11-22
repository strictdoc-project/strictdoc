"""
YAML front matter for Markdown documents.

A front matter block starts on the first line of a document with a line
that contains only ``---``. The block ends with the next line that
contains only ``---``. The lines in between are YAML.

The markdown-it-py block rule ``front_matter`` turns the block into a
``front_matter`` token. The token content is the YAML text, and the
token map covers both delimiter lines.

StrictDoc reads the YAML as a flat mapping of string keys to string
values. The loader and the dumper do not resolve implicit YAML types:
``Version: 1.10`` stays the string ``"1.10"``, and the writer emits it
without quotes.
"""

import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml
from markdown_it import MarkdownIt
from markdown_it.rules_block.state_block import StateBlock
from markdown_it.token import Token

FRONT_MATTER_TOKEN_TYPE = "front_matter"
FRONT_MATTER_DELIMITER = "---"


class FrontMatterError(Exception):
    def __init__(self, message: str, line: int) -> None:
        super().__init__(message)
        self.message: str = message
        # 1-based line number in the Markdown document.
        self.line: int = line


def add_front_matter_rule(markdown_parser: MarkdownIt) -> MarkdownIt:
    """Register the front matter rule before all other block rules."""
    first_rule_name = markdown_parser.block.ruler.get_all_rules()[0]
    markdown_parser.block.ruler.before(
        first_rule_name, FRONT_MATTER_TOKEN_TYPE, front_matter_rule
    )
    return markdown_parser


def front_matter_rule(
    state: StateBlock,
    startLine: int,
    endLine: int,
    silent: bool,
) -> bool:
    """Recognize a YAML front matter block at the start of a document."""
    if startLine != 0 or state.blkIndent != 0:
        return False
    if _get_line(state, startLine) != FRONT_MATTER_DELIMITER:
        return False

    closing_line: Optional[int] = None
    for line_index_ in range(startLine + 1, endLine):
        if _get_line(state, line_index_) == FRONT_MATTER_DELIMITER:
            closing_line = line_index_
            break
    if closing_line is None:
        return False

    if silent:
        return True

    token = state.push(FRONT_MATTER_TOKEN_TYPE, "", 0)
    token.hidden = True
    token.markup = FRONT_MATTER_DELIMITER
    token.block = True
    token.content = state.getLines(startLine + 1, closing_line, 0, False)
    token.map = [startLine, closing_line + 1]

    state.line = closing_line + 1
    return True


def find_front_matter_token(
    markdown_tokens: Sequence[Token],
) -> Optional[Token]:
    if (
        len(markdown_tokens) > 0
        and markdown_tokens[0].type == FRONT_MATTER_TOKEN_TYPE
    ):
        return markdown_tokens[0]
    return None


def parse_front_matter(
    front_matter_token: Token,
) -> List[Tuple[str, str, int]]:
    """
    Parse the YAML of a front matter token.

    Return (key, value, line) tuples in document order. The line is the
    1-based line of the key in the Markdown document. Raise
    FrontMatterError if the YAML is not a flat mapping of scalar values.
    """
    assert front_matter_token.map is not None
    # The first YAML line is the line after the opening delimiter.
    first_yaml_line = front_matter_token.map[0] + 2

    try:
        root_node = yaml.compose(
            front_matter_token.content, Loader=yaml.BaseLoader
        )
    except yaml.MarkedYAMLError as exception_:
        line = first_yaml_line
        if exception_.problem_mark is not None:
            line += exception_.problem_mark.line
        raise FrontMatterError(
            f"invalid YAML: {exception_.problem}", line
        ) from exception_

    if root_node is None:
        return []
    if not isinstance(root_node, yaml.MappingNode):
        raise FrontMatterError(
            "the YAML must be a mapping of keys to values.",
            first_yaml_line + root_node.start_mark.line,
        )

    entries: List[Tuple[str, str, int]] = []
    seen_keys = set()
    for key_node_, value_node_ in root_node.value:
        key_line_ = first_yaml_line + key_node_.start_mark.line
        if not isinstance(key_node_, yaml.ScalarNode):
            raise FrontMatterError("a key must be a string.", key_line_)
        key_ = str(key_node_.value)
        if len(key_) == 0:
            raise FrontMatterError("a key must not be empty.", key_line_)
        if key_ in seen_keys:
            raise FrontMatterError(
                f"duplicate key '{key_}' is not allowed.", key_line_
            )
        if not isinstance(value_node_, yaml.ScalarNode):
            raise FrontMatterError(
                f"the value of key '{key_}' must be a single value, "
                "not a list or a mapping.",
                key_line_,
            )
        seen_keys.add(key_)
        entries.append((key_, str(value_node_.value), key_line_))
    return entries


def serialize_front_matter(entries: Sequence[Tuple[str, str]]) -> str:
    """Serialize key-value pairs into a front matter block."""
    front_matter_mapping: Dict[str, str] = dict(entries)
    yaml_text = yaml.dump(
        front_matter_mapping,
        Dumper=_FrontMatterDumper,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
        width=math.inf,
    )
    return f"{FRONT_MATTER_DELIMITER}\n{yaml_text}{FRONT_MATTER_DELIMITER}"


class _FrontMatterDumper(yaml.SafeDumper):
    """
    Dump all values as YAML strings without implicit type resolution.

    Without implicit resolvers, a string such as "1.10" or "true" does
    not look like a number or a boolean to the dumper. The dumper then
    emits the string without quotes, the same way the user wrote it.
    """

    yaml_implicit_resolvers: Dict[Any, Any] = {}


def _represent_string(dumper: yaml.SafeDumper, value: str) -> yaml.Node:
    if "\n" in value:
        return dumper.represent_scalar(
            "tag:yaml.org,2002:str", value, style="|"
        )
    return dumper.represent_scalar("tag:yaml.org,2002:str", value)


_FrontMatterDumper.add_representer(str, _represent_string)


def _get_line(state: StateBlock, line: int) -> str:
    return state.src[state.bMarks[line] : state.eMarks[line]].rstrip()
