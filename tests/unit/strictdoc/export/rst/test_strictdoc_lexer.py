from pygments import highlight
from pygments.formatters import (
    HtmlFormatter,
    RawTokenFormatter,
    TestcaseFormatter,
)
from pygments.token import Token

from strictdoc.export.rst.strictdoc_lexer import (
    SDocPygmentsToken,
    StrictDocLexer,
)


def dump_lexed_code(lexer, code) -> None:
    print(highlight(code, lexer, RawTokenFormatter()))  # noqa: T201
    print(highlight(code, lexer, HtmlFormatter()))  # noqa: T201
    print(highlight(code, lexer, TestcaseFormatter()))  # noqa: T201


def test_01_document_tag_only():
    code = """\
[DOCUMENT]
"""

    lexer = StrictDocLexer()
    tokens = [
        (SDocPygmentsToken.TAG, "[DOCUMENT]\n"),
    ]
    assert list(lexer.get_tokens(code)) == tokens


def test_02_document_with_title():
    code = """\
[DOCUMENT]
TITLE: Test
"""

    lexer = StrictDocLexer()

    tokens = [
        (SDocPygmentsToken.TAG, "[DOCUMENT]\n"),
        (SDocPygmentsToken.FIELD_NAME, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Test\n"),
    ]
    assert list(lexer.get_tokens(code)) == tokens


def test_03_basic_requirement():
    code = """\
[DOCUMENT]
TITLE: Test

[REQUIREMENT]
TITLE: Foo
STATEMENT: Bar
RELATIONS:
- TYPE: Parent
  VALUE: STANDARD-001
- TYPE: Child
  VALUE: PROJECT-001

[REQUIREMENT]
TITLE: Second requirement.
STATEMENT: Baz
"""

    lexer = StrictDocLexer()

    tokens = [
        (SDocPygmentsToken.TAG, "[DOCUMENT]\n"),
        (SDocPygmentsToken.FIELD_NAME, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Test\n"),
        (Token.Text, "\n"),
        (SDocPygmentsToken.TAG, "[REQUIREMENT]\n"),
        (SDocPygmentsToken.FIELD_NAME, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Foo\n"),
        (SDocPygmentsToken.FIELD_NAME, "STATEMENT"),
        (Token.Punctuation, ":"),
        (Token.Text, " Bar\n"),
        (SDocPygmentsToken.FIELD_NAME, "RELATIONS:\n"),
        (SDocPygmentsToken.FIELD_NAME, "- TYPE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Parent\n"),
        (SDocPygmentsToken.FIELD_NAME, "  VALUE"),
        (Token.Punctuation, ":"),
        (Token.Text, " STANDARD-001\n"),
        (SDocPygmentsToken.FIELD_NAME, "- TYPE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Child\n"),
        (SDocPygmentsToken.FIELD_NAME, "  VALUE"),
        (Token.Punctuation, ":"),
        (Token.Text, " PROJECT-001\n"),
        (Token.Text.Whitespace, "\n"),
        (Token.Keyword, "[REQUIREMENT]\n"),
        (Token.Name.Attribute, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Second requirement.\n"),
        (Token.Name.Attribute, "STATEMENT"),
        (Token.Punctuation, ":"),
        (Token.Text, " Baz\n"),
    ]
    assert list(lexer.get_tokens(code)) == tokens


def test_04_multiline_value():
    code = """\
[DOCUMENT]
TITLE: Test

[REQUIREMENT]
TITLE: Foo1
STATEMENT: >>>
Bar1
<<<

[REQUIREMENT]
TITLE: Foo2
STATEMENT: >>>
Bar2
<<<
"""

    lexer = StrictDocLexer()

    tokens = [
        (Token.Keyword, "[DOCUMENT]\n"),
        (Token.Name.Attribute, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Test\n"),
        (Token.Text, "\n"),
        (Token.Keyword, "[REQUIREMENT]\n"),
        (Token.Name.Attribute, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Foo1\n"),
        (Token.Name.Attribute, "STATEMENT"),
        (Token.Punctuation, ":"),
        (Token.Literal.String, " >>>\n"),
        (Token.Text, "Bar1\n"),
        (Token.Literal.String, "<<<\n"),
        (Token.Text, "\n"),
        (Token.Keyword, "[REQUIREMENT]\n"),
        (Token.Name.Attribute, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Foo2\n"),
        (Token.Name.Attribute, "STATEMENT"),
        (Token.Punctuation, ":"),
        (Token.Literal.String, " >>>\n"),
        (Token.Text, "Bar2\n"),
        (Token.Literal.String, "<<<\n"),
    ]
    assert list(lexer.get_tokens(code)) == tokens


def test_05_text_node():
    code = """\
[DOCUMENT]
TITLE: Test

[TEXT]
TITLE: Foo
STATEMENT: >>>
Bar
<<<
COMMENT: >>>
String 1.

String 3.

String 5.
<<<
"""

    lexer = StrictDocLexer()

    tokens = [
        (SDocPygmentsToken.TAG, "[DOCUMENT]\n"),
        (SDocPygmentsToken.FIELD_NAME, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Test\n"),
        (Token.Text, "\n"),
        (SDocPygmentsToken.TAG, "[TEXT]\n"),
        (SDocPygmentsToken.FIELD_NAME, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Foo\n"),
        (SDocPygmentsToken.FIELD_NAME, "STATEMENT"),
        (Token.Punctuation, ":"),
        (Token.Literal.String, " >>>\n"),
        (Token.Text, "Bar\n"),
        (Token.Literal.String, "<<<\n"),
        (Token.Name.Attribute, "COMMENT"),
        (Token.Punctuation, ":"),
        (Token.Literal.String, " >>>\n"),
        (Token.Text, "String 1.\n"),
        (Token.Text, "\n"),
        (Token.Text, "String 3.\n"),
        (Token.Text, "\n"),
        (Token.Text, "String 5.\n"),
        (Token.Literal.String, "<<<\n"),
    ]
    assert list(lexer.get_tokens(code)) == tokens


def test_06_section():
    code = """\
[DOCUMENT]
TITLE: Test

[[SECTION]]
UID: S123
TITLE: Foo

[[/SECTION]]
"""

    lexer = StrictDocLexer()

    tokens = [
        (SDocPygmentsToken.TAG, "[DOCUMENT]\n"),
        (Token.Name.Attribute, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Test\n"),
        (Token.Text, "\n"),
        (SDocPygmentsToken.TAG, "[[SECTION]]\n"),
        (Token.Name.Attribute, "UID"),
        (Token.Punctuation, ":"),
        (Token.Text, " S123\n"),
        (SDocPygmentsToken.FIELD_NAME, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Foo\n"),
        (Token.Text, "\n"),
        (SDocPygmentsToken.TAG, "[[/SECTION]]\n"),
    ]
    assert list(lexer.get_tokens(code)) == tokens


def test_07_mix_of_leaf_and_composite_nodes():
    code = """\
[DOCUMENT]
TITLE: Test

[NODE]
TITLE: Leaf node 1

[[COMPOSITE_NODE]]
TITLE: Composite node

[[/COMPOSITE_NODE]]

[NODE]
TITLE: Leaf node 2
"""

    lexer = StrictDocLexer()

    tokens = [
        (Token.Keyword, "[DOCUMENT]\n"),
        (Token.Name.Attribute, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Test\n"),
        (Token.Text, "\n"),
        (Token.Keyword, "[NODE]\n"),
        (Token.Name.Attribute, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Leaf node 1\n"),
        (Token.Text, "\n"),
        (Token.Keyword, "[[COMPOSITE_NODE]]\n"),
        (Token.Name.Attribute, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Composite node\n"),
        (Token.Text, "\n"),
        (Token.Keyword, "[[/COMPOSITE_NODE]]\n"),
        (Token.Text.Whitespace, "\n"),
        (Token.Keyword, "[NODE]\n"),
        (Token.Name.Attribute, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Leaf node 2\n"),
    ]
    assert list(lexer.get_tokens(code)) == tokens


def test_20_document_options():
    code = """\
[DOCUMENT]
TITLE: Test
OPTIONS:
  ENABLE_MID: True
  VIEW_STYLE: Inline
  NODE_IN_TOC: True
"""

    lexer = StrictDocLexer()

    tokens = [
        (SDocPygmentsToken.TAG, "[DOCUMENT]\n"),
        (SDocPygmentsToken.FIELD_NAME, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Test\n"),
        (SDocPygmentsToken.FIELD_NAME, "OPTIONS:\n"),
        (SDocPygmentsToken.FIELD_NAME, "  ENABLE_MID"),
        (Token.Punctuation, ":"),
        (Token.Text, " True\n"),
        (SDocPygmentsToken.FIELD_NAME, "  VIEW_STYLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Inline\n"),
        (SDocPygmentsToken.FIELD_NAME, "  NODE_IN_TOC"),
        (Token.Punctuation, ":"),
        (Token.Text, " True\n"),
        (Token.Text, ""),
    ]
    assert list(lexer.get_tokens(code)) == tokens


def test_23_document_metadata():
    code = """\
[DOCUMENT]
TITLE: Test
METADATA:
  AUTHOR: Wile E. Coyote
"""

    lexer = StrictDocLexer()

    tokens = [
        (SDocPygmentsToken.TAG, "[DOCUMENT]\n"),
        (SDocPygmentsToken.FIELD_NAME, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Test\n"),
        (SDocPygmentsToken.FIELD_NAME, "METADATA:\n"),
        (SDocPygmentsToken.FIELD_NAME, "  AUTHOR"),
        (Token.Punctuation, ":"),
        (Token.Text, " Wile E. Coyote\n"),
        (Token.Text, ""),
    ]
    assert list(lexer.get_tokens(code)) == tokens


def test_24_document_options_and_metadata():
    code = """\
[DOCUMENT]
TITLE: Hello world
OPTIONS:
  NODE_IN_TOC: True
METADATA:
  AUTHOR: John Doe
  APPROVED_BY: Jane Smith
"""

    lexer = StrictDocLexer()

    tokens = [
        (Token.Keyword, "[DOCUMENT]\n"),
        (Token.Name.Attribute, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " Hello world\n"),
        (Token.Name.Attribute, "OPTIONS:\n"),
        (Token.Name.Attribute, "  NODE_IN_TOC"),
        (Token.Punctuation, ":"),
        (Token.Text, " True\n"),
        (Token.Text, ""),
        (Token.Name.Attribute, "METADATA:\n"),
        (Token.Name.Attribute, "  AUTHOR"),
        (Token.Punctuation, ":"),
        (Token.Text, " John Doe\n"),
        (Token.Name.Attribute, "  APPROVED_BY"),
        (Token.Punctuation, ":"),
        (Token.Text, " Jane Smith\n"),
        (Token.Text, ""),
    ]
    assert list(lexer.get_tokens(code)) == tokens


def test_30_grammar_block():
    code = """\
[DOCUMENT]
TITLE: How to declare a grammar with different field types

[GRAMMAR]
ELEMENTS:
- TAG: TEXT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: False
  - TITLE: STATEMENT
    TYPE: String
    REQUIRED: True
- TAG: REQUIREMENT
  FIELDS:
  - TITLE: UID
    TYPE: String
    REQUIRED: True
  - TITLE: VERIFICATION
    TYPE: MultipleChoice(Review, Analysis, Inspection, Test)
    REQUIRED: True
  RELATIONS:
  - Type: Parent
  - Type: File
"""

    lexer = StrictDocLexer()

    tokens = [
        (Token.Keyword, "[DOCUMENT]\n"),
        (Token.Name.Attribute, "TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " How to declare a grammar with different field types\n"),
        (Token.Text, "\n"),
        (Token.Keyword, "[GRAMMAR]\n"),
        (Token.Name.Attribute, "ELEMENTS:\n"),
        (Token.Name.Attribute, "- TAG"),
        (Token.Punctuation, ":"),
        (Token.Text, " TEXT\n"),
        (Token.Name.Attribute, "  FIELDS:\n"),
        (Token.Name.Attribute, "  - TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " UID\n"),
        (Token.Name.Attribute, "    TYPE"),
        (Token.Punctuation, ":"),
        (Token.Text, " String\n"),
        (Token.Name.Attribute, "    REQUIRED"),
        (Token.Punctuation, ":"),
        (Token.Text, " False\n"),
        (Token.Name.Attribute, "  - TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " STATEMENT\n"),
        (Token.Name.Attribute, "    TYPE"),
        (Token.Punctuation, ":"),
        (Token.Text, " String\n"),
        (Token.Name.Attribute, "    REQUIRED"),
        (Token.Punctuation, ":"),
        (Token.Text, " True\n"),
        (Token.Name.Attribute, "- TAG"),
        (Token.Punctuation, ":"),
        (Token.Text, " REQUIREMENT\n"),
        (Token.Name.Attribute, "  FIELDS:\n"),
        (Token.Name.Attribute, "  - TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " UID\n"),
        (Token.Name.Attribute, "    TYPE"),
        (Token.Punctuation, ":"),
        (Token.Text, " String\n"),
        (Token.Name.Attribute, "    REQUIRED"),
        (Token.Punctuation, ":"),
        (Token.Text, " True\n"),
        (Token.Name.Attribute, "  - TITLE"),
        (Token.Punctuation, ":"),
        (Token.Text, " VERIFICATION\n"),
        (Token.Name.Attribute, "    TYPE"),
        (Token.Punctuation, ":"),
        (Token.Text, " MultipleChoice(Review, Analysis, Inspection, Test)\n"),
        (Token.Name.Attribute, "    REQUIRED"),
        (Token.Punctuation, ":"),
        (Token.Text, " True\n"),
        (Token.Name.Attribute, "  RELATIONS:\n"),
        (Token.Name.Attribute, "  - Type"),
        (Token.Punctuation, ":"),
        (Token.Text, " Parent\n"),
        (Token.Name.Attribute, "  - Type"),
        (Token.Punctuation, ":"),
        (Token.Text, " File\n"),
    ]
    assert list(lexer.get_tokens(code)) == tokens
