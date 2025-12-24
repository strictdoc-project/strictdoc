from pygments.lexer import RegexLexer, bygroups
from pygments.lexers import _mapping
from pygments.token import (
    Error,
    Keyword,
    Name,
    Punctuation,
    String,
    Text,
)

from strictdoc.backend.sdoc.grammar.grammar import REGEX_FIELD_NAME
from strictdoc.backend.sdoc.grammar.type_system import REGEX_NODE_NAME


class SDocPygmentsToken:
    TAG = Keyword
    FIELD_NAME = Name.Attribute


class StrictDocLexer(RegexLexer):  # type: ignore[misc]
    """
    A Pygments lexer for StrictDoc syntax.
    """

    name = "StrictDocLexer"
    aliases = ["strictdoc"]
    filenames = ["*.sdoc"]

    tokens = {
        "root": [
            (r"^\[DOCUMENT\]\n", SDocPygmentsToken.TAG, "document"),
            (r"^\[GRAMMAR\]\n", SDocPygmentsToken.TAG, "grammar"),
            (
                rf"^(\[{REGEX_NODE_NAME}\]|\[\[{REGEX_NODE_NAME}\]\])\n",
                SDocPygmentsToken.TAG,
                "requirement",
            ),
            # Keeping all closing tags under the same rule.
            (
                rf"^\[\[/{REGEX_NODE_NAME}\]\]\n",
                SDocPygmentsToken.TAG,
            ),
            (r".+\n", Error),
        ],
        # This is rather basic but should be sufficient for now.
        "grammar": [
            (
                r"(ELEMENTS:\n)",
                bygroups(SDocPygmentsToken.FIELD_NAME),
            ),
            (
                rf"({REGEX_FIELD_NAME})(:)( .*\n)",
                bygroups(SDocPygmentsToken.FIELD_NAME, Punctuation, Text),
            ),
            (
                rf"(\- {REGEX_FIELD_NAME})(:)( .*\n)",
                bygroups(SDocPygmentsToken.FIELD_NAME, Punctuation, Text),
            ),
            (
                rf"(  {REGEX_FIELD_NAME}:\n)",
                bygroups(SDocPygmentsToken.FIELD_NAME),
            ),
            (
                rf"(  - {REGEX_FIELD_NAME})(:)( .*\n)",
                bygroups(SDocPygmentsToken.FIELD_NAME, Punctuation, Text),
            ),
            (
                rf"(    {REGEX_FIELD_NAME})(:)( .*\n)",
                bygroups(SDocPygmentsToken.FIELD_NAME, Punctuation, Text),
            ),
            (r"^\s*\n", Text, "#pop"),
            (r".+\n", Error),
        ],
        "document": [
            (
                r"((OPTIONS|METADATA):\n)",
                bygroups(SDocPygmentsToken.FIELD_NAME),
                "document_options",
            ),
            (
                rf"({REGEX_FIELD_NAME})(:)( .*\n)",
                bygroups(SDocPygmentsToken.FIELD_NAME, Punctuation, Text),
            ),
            (r"^\s*\n", Text, "#pop"),
            (r".+\n", Error),
        ],
        "document_options": [
            (
                rf"(  {REGEX_FIELD_NAME})(:)( .*\n)",
                bygroups(SDocPygmentsToken.FIELD_NAME, Punctuation, Text),
            ),
            # Non-indented line -> exit OPTIONS. Important: ?! does not consume.
            (r"^(?!  )", Text, "#pop"),
            (r".+\n", Error),
        ],
        "requirement": [
            (
                r"(RELATIONS:\n)",
                bygroups(SDocPygmentsToken.FIELD_NAME),
                "requirement_relations",
            ),
            # Multiline attribute start
            (
                rf"({REGEX_FIELD_NAME})(:)(\s*>>>\n)",
                bygroups(SDocPygmentsToken.FIELD_NAME, Punctuation, String),
                "multiline_value",
            ),
            # Single-line attribute
            (
                rf"({REGEX_FIELD_NAME})(:)([^\n]*\n)",
                bygroups(SDocPygmentsToken.FIELD_NAME, Punctuation, Text),
            ),
            # End of requirement block
            (r"^\n", Text, "#pop"),
            # Anything else is an error
            (r".+\n", Error),
        ],
        "requirement_relations": [
            (
                rf"(\- {REGEX_FIELD_NAME})(:)( .*\n)",
                bygroups(SDocPygmentsToken.FIELD_NAME, Punctuation, Text),
            ),
            (
                rf"(  {REGEX_FIELD_NAME})(:)( .*\n)",
                bygroups(SDocPygmentsToken.FIELD_NAME, Punctuation, Text),
            ),
            # Empty line -> exit RELATIONS. Important: ?! does not consume.
            (r"^(?!\n)", Text, "#pop"),
            (r".+\n", Error),
        ],
        "multiline_value": [
            # End marker
            (r"^<<<\n", String, "#pop"),
            # Multiline content
            (r".*\n", Text),
        ],
    }


# Register the lexer
_mapping.LEXERS["StrictDocLexer"] = (
    "strictdoc.export.rst.strictdoc_lexer",  # module path
    "StrictDocLexer",  # class name
    ("strictdoc",),  # aliases
    ("*.sdoc",),  # filename patterns
    (),  # mimetypes
)

__all__ = ["StrictDocLexer"]
