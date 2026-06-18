# Extend the Markdown specification to support node TYPE

## WHAT

Extend the Markdown specification to support node TYPE.

If a TYPE is specified explicitly for a node, this node type shall be preserved across all operations, such as UI editing, running `format` or `manage auto-uid` commands, etc.

This rules extends to the SECTION element as well as to all other elements, such as the default REQUIREMENT or other custom elements, such as ASSUMPTION, TEST_CASE, etc.

The TYPE-related rules do not extend/cover the TEXT nodes whose Markdown rules are not affected by this node TYPE feature.

To define whether or not a node shall have an explicit node type, StrictDoc shall derive it from the document grammar using the following rules:

- If a document grammar has elements outside of the default set {"SECTION", "TEXT", "REQUIREMENT"}, the REQUIREMENT and nodes other than SECTION and TEXT shall have their TYPE specified explicitly.

The SECTION node must not have a STATEMENT field defined for its grammar element. This is to ensure there is no conflict possible with TEXT nodes that are children nodes to a SECTION node.

If a TEXT grammar element defines an MID field, all TEXT nodes must appear in the document along with their `TYPE` and `MID` values explicitly specified. If a text node in such a grammar is missing in the Markdown file initially, StrictDoc shall parse the document without raising a validation error. However, when writing a document back, the written file shall contain explicit `TYPE`/`MID` fields.

### Updates to Markdown specification

The following cases shall be reflected explicitly:

- In the Markdown specification.
- In the unit tests.
- In the integration tests.
- In the end-to-end tests.

#### SECTION with TYPE/MID + TEXT without meta information

```markdown
# Document title

**Grammar**: requirements.gra.md

## Introduction

**TYPE**: SECTION \
**MID**: 11111111111111111111111111111111

**STATEMENT**: This is a TEXT node statement, not a SECTION node statement.
```

#### SECTION with TYPE/MID + TEXT with TYPE/MID

```markdown
# Document title

**Grammar**: requirements.gra.md

## Introduction

**TYPE**: SECTION \
**MID**: 11111111111111111111111111111111

**TYPE**: TEXT \
**MID**: 22222222222222222222222222222222

**STATEMENT**: This is a text statement.
```

## WHY

This allows StrictDoc to distinguish between different node types when it parses Markdown nodes.

## HOW

### Implementation details

- Update the Markdown specification to reflect the formality of the node TYPE.

**Reader** (`strictdoc/backend/markdown/reader.py`):

- `ParsedMarkdownNode` gains two new fields: `explicit_node_type` (the value from `**TYPE**:`) and `processed_body` (body after the meta block, used when `TYPE=SECTION` to prevent the raw `**TYPE**:` line from becoming a TEXT child).
- `_parse_markdown_node` strips the `TYPE` field from the parsed fields before validation. If `TYPE=SECTION` the node is forced to become a section; any other explicit TYPE value bypasses the UID/MID and STATEMENT requirements so the node is always accepted as a typed node.
- `_create_requirement_node` gains a `node_type` parameter (default `"REQUIREMENT"`) so non-REQUIREMENT custom types are constructed directly.

**Writer** (`strictdoc/backend/markdown/writer.py`):

- `_serialize_node_fields` calls `Grammar.has_custom_elements()` to decide whether to prepend `**TYPE**: <name>` to the meta block. TYPE is emitted for every non-TEXT node (including SECTION) when the grammar has custom elements. SECTION must be included because the reader treats any heading that has a meta block as a typed node under a custom grammar, so omitting TYPE: SECTION would cause the reader to mis-classify the SECTION as a REQUIREMENT on the next read.

**Grammar** (`strictdoc/backend/sdoc/models/document_grammar.py`):

- `DocumentGrammar.has_custom_elements()` encapsulates the detection logic: returns `True` when `elements_by_type` contains any element type outside `{"SECTION", "TEXT", "REQUIREMENT"}`. When the grammar is not yet resolved (empty `elements_by_type` but `import_from_file` set) it returns `True` as a safe fallback.

**Markdown specification** (`spec/Markdown.md`):

- MD-25 documents the reader behaviour for the TYPE field.
- MD-26 documents the writer emission rule and its grammar-based condition.

### Valid examples as per this task

```markdown
# Document example

**Grammar**: @DO-178C-MD

## Test Section

**TYPE**: SECTION

### Requirement nested in a section

**TYPE**: REQUIREMENT \
**MID**: 6758694447fe418ba1ca94dc1080acf0 \
**UID**: REQ-3 \
**DERIVED**: No \
**SAFETY**: No \
**SECURITY**: No

Some statement text.

### Assumption nested in a section

**TYPE**: ASSUMPTION \
**MID**: 123456744357418ba17a94dc1080a865 \
**UID**: REQ-3 \

Some statement text.
```
