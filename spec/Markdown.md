# Markdown Specification

**Grammar**: Markdown.gra.md \
**PREFIX**: MD-

This specification defines a Markdown-based format for writing traceable documentation, including requirements. It covers two file formats: the Markdown document format (`.md`) for content and the Markdown grammar format (`.gra.md`) for schemas. Both are valid CommonMark files.

## Markdown Document Format

### File naming

**MID**: 1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d \
**UID**: MD-1

**STATEMENT**: Markdown documents use the `.md` file extension.

### CommonMark standard

**MID**: c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8 \
**UID**: MD-23

**STATEMENT**:

Both the Markdown document format and the Markdown grammar format are valid CommonMark files conforming to CommonMark core syntax v0.31.2.

Extended Markdown features outside the CommonMark core are passed through verbatim and not interpreted as document nodes.

### Document structure

**MID**: 2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e \
**UID**: MD-2

**STATEMENT**:

A document must begin with an H1 heading (`# Title`). No non-blank content may precede it.

The H1 heading text becomes the document title. Exactly one H1 heading is allowed per file.

Body text following the H1 heading and its optional metadata block accumulates as a TEXT node until the next heading.

### Heading levels

**MID**: 3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f \
**UID**: MD-3

**STATEMENT**:

Heading levels must not skip forward: following an H_N heading, the next heading may not be at level M where M > N + 1.

Level decreases and same-level headings are permitted.

### Blank lines

**MID**: 4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a \
**UID**: MD-4

**STATEMENT**:

At most one consecutive blank line is allowed. Two or more consecutive blank lines are invalid, except inside fenced code blocks and blockquotes.

Whitespace-only lines are treated as blank lines.

### Document metadata

**MID**: 5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b \
**UID**: MD-5

**STATEMENT**:

Immediately after the H1 heading, an optional metadata block may appear, separated from the heading by one blank line and ending at the next blank line. Each line has the form `**Key**: value`.

Recognized document-level keys are `Grammar`, `UID`, `VERSION`, `DATE`, `CLASSIFICATION`, and `PREFIX`. Any other key is stored as custom metadata.

Duplicate key names are not allowed. Values may optionally be enclosed in backticks.

### Document PREFIX field

**MID**: f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6 \
**UID**: MD-31

**STATEMENT**:

The `PREFIX` metadata key controls the prefix used when auto-generating UIDs for nodes in the document or section. It may be set at the document level or at the section level.

**1. Document-level PREFIX**

A `PREFIX` key in the H1 metadata block sets the default UID prefix for the entire document.

```markdown
# Requirements specification

**PREFIX**: MYDOC-

## Section

### Requirement

**UID**: MYDOC-001

System A shall do B.
```

**2. Section-level PREFIX**

A section may declare its own prefix by using the `**PREFIX**` meta field together with `**TYPE**: SECTION`. The section-level prefix overrides the document-level prefix for all nodes within that section.

```markdown
# Requirements specification

## Chapter 2

**TYPE**: SECTION \
**PREFIX**: LEVEL2-REQ-

### Requirement

**UID**: LEVEL2-REQ-001

System A shall do B.
```

The section-level `PREFIX` is parsed out of the meta block and is not forwarded as a regular node field.

### Grammar attachment

**MID**: 6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c \
**UID**: MD-6

**STATEMENT**:

The `Grammar` metadata key attaches an external grammar to the document. Its value is either a relative path to a `.gra.md` file or a named alias prefixed with `@`.

Named aliases are resolved from the project configuration. Without a `Grammar` declaration, the built-in default grammar applies.

### Node structure

**MID**: a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6 \
**UID**: MD-21

**STATEMENT**:

An H2–H6 heading forms a node. The heading text is the node TITLE. There is no limit on heading depth: nodes may be at H2, H3, H4, etc.

The node body consists of three consecutive regions:

1. The meta-field block — a contiguous run of `**Key**: value` lines beginning after the first blank line and ending at the next blank line.
2. An optional RELATIONS list — immediately following the meta block without an intervening blank line.
3. Content fields — named or implicit, following the first blank line after the meta/RELATIONS block.

A node terminates at the next heading or end of file.

### Node without title

**MID**: b0294b7fcb4343f19fbab31c399849fb \
**UID**: MD-29

**STATEMENT**:

A node without a title is a special case of the node defined by [LINK: MD-21].

Compared to a node with a title, a node without a title starts directly with a node body.

The resulting node shall have no `TITLE` (as opposed to a node where the title is an empty string).

**RATIONALE**:

No-title nodes are a valid use-case in scenarios where a title is automatically derived and merged from related source code.
They rely on empty headings, which is uncommon but valid syntax in CommonMark.

### SECTION node

**MID**: 7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d \
**UID**: MD-7

**STATEMENT**:

An H2–H6 heading that does not qualify as a requirement node (see [LINK: MD-8], [LINK: MD-9]) becomes a section.

Free-form Markdown prose in a section body is stored as a TEXT node.

### TEXT node

**MID**: 1a8b12341e2f3a4b5c6d7e8f9a0b1c2d \
**UID**: MD-30

**STATEMENT**: TEXT nodes are always nodes without a title. Parsing a TEXT element with a TITLE shall raise a validation error.

### Default grammar

**MID**: 8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e \
**UID**: MD-8

**STATEMENT**:

Without a custom grammar, an H2–H6 heading becomes a REQUIREMENT node when all of the following hold:

1. The meta block contains a `UID` or `MID` field.
2. A `STATEMENT` is present (named or implicit).
3. All field names belong to `{MID, UID, LEVEL, STATUS, TAGS, TITLE, STATEMENT, RATIONALE, COMMENT, RELATIONS}`.
4. No field name is duplicated.
5. No field value is empty.

The heading text is assigned to the `TITLE` field.

### Custom grammar

**MID**: 9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f \
**UID**: MD-9

**STATEMENT**:

With a custom grammar, an H2–H6 heading becomes a node when the meta block contains at least one field and the heading text is non-empty.

Field validation against the grammar schema is deferred to a later build stage. The heading text is assigned to the `TITLE` field.

### MID auto-generation

**MID**: 00fc24ee2f5c44f08c1d7f543a3677b0 \
**UID**: MD-24

**STATEMENT**:

When a custom grammar declares a `MID` field for an element type, the writer automatically inserts the node's auto-generated machine identifier into the output for any node of that type that does not already carry a `MID` field.

This is the Markdown equivalent of SDoc's document-level `ENABLE_MID` option. The presence of the `MID` field in the custom grammar is the activation signal — no explicit document-level option is required.

On the first write-back, every node without a `MID` receives a freshly generated UUID. On subsequent reads, the persisted value is loaded and the node's machine identifier is treated as permanent.

This behavior applies only to custom (user-defined) grammars. The built-in default grammar also declares `MID` for the `REQUIREMENT` element, but the default grammar does not trigger auto-generation.

For SECTION nodes, MID auto-generation is triggered only when the grammar's `SECTION` element declares a `MID` field. When MID is written to a SECTION node, the writer also emits `**TYPE**: SECTION` as the first meta field to prevent the reader from misidentifying the section as a requirement node on the next read.

### Node TYPE field — reader behaviour

**MID**: a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8 \
**UID**: MD-25

**STATEMENT**:

The `**TYPE**: <name>` meta field specifies the element type of a node explicitly and takes precedence over the automatic node-type determination rules of [LINK: MD-7], [LINK: MD-8], and [LINK: MD-9].

- `**TYPE**: SECTION` forces the heading to become a SECTION regardless of other fields. Any content following the meta block (after the TYPE line) forms a TEXT child as usual; the TYPE line itself is not included in the TEXT body.
- Any other `**TYPE**: <name>` value forces the heading to become a node of type `<name>`, bypassing the UID/MID and STATEMENT requirements of [LINK: MD-8]. Grammar field validation is deferred to the build stage as per [LINK: MD-9].

The TYPE field is parsed out of the meta block and is not forwarded as a regular node field.

### Node TYPE field — writer behaviour

**MID**: b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9 \
**UID**: MD-26

**STATEMENT**:

When a document's grammar defines element types outside the built-in set `{SECTION, TEXT, REQUIREMENT}`, the writer emits `**TYPE**: <name>` as the first field in the meta block of every non-TEXT node (including SECTION). This ensures the element type is preserved across `format`, `manage auto-uid`, and UI-edit operations.

SECTION is included because the reader treats any heading with a valid meta block as a typed node when a custom grammar is active; without `**TYPE**: SECTION` the reader would mis-classify a SECTION node as a REQUIREMENT on the next read.

When the grammar only contains built-in element types the TYPE field is not emitted. The determination is performed by `Grammar.has_custom_elements()`.

### SECTION MID with TEXT child — no TEXT meta

**MID**: c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0 \
**UID**: MD-27

**STATEMENT**:

When a SECTION heading carries both `**TYPE**: SECTION` and a `**MID**` field in its meta block, the MID is preserved as the section's machine identifier across all read-write cycles.

Any content following the section meta block (after the next blank line) forms a TEXT child node whose statement is the verbatim body text. The `**TYPE**:` line from the meta block is not included in the TEXT body.

The behavior of the TEXT child on a subsequent format pass depends on whether the document grammar declares a `MID` field for the `TEXT` element.

**Subcase A: Grammar does NOT declare MID for TEXT**

The writer emits the TEXT statement as plain verbatim content — no `**TYPE**:` or `**MID**:` prefix is added. The SECTION MID is still preserved.

Example (input and output are identical after a format pass):

```markdown
## Introduction

**TYPE**: SECTION \
**MID**: 11111111111111111111111111111111

**STATEMENT**: This is a TEXT node statement, not a SECTION node statement.
```

**Subcase B: Grammar declares MID for TEXT**

The writer automatically emits a `**TYPE**: TEXT \` / `**MID**: <mid>` prefix before the TEXT statement body, auto-generating the MID if not already present. This ensures every TEXT node has a tracked machine identifier.

Example input (TEXT child without explicit MID):

```markdown
## Introduction

**TYPE**: SECTION \
**MID**: 11111111111111111111111111111111

**STATEMENT**: This is a TEXT node statement, not a SECTION node statement.
```

After a format pass with a grammar that declares `MID` for `TEXT`, the output becomes:

```markdown
## Introduction

**TYPE**: SECTION \
**MID**: 11111111111111111111111111111111

**TYPE**: TEXT \
**MID**: <auto-generated-mid>

**STATEMENT**: This is a TEXT node statement, not a SECTION node statement.
```

### SECTION MID with TEXT child — TEXT TYPE and MID present

**MID**: d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1 \
**UID**: MD-28

**STATEMENT**:

When the section body begins with a `**TYPE**: TEXT \` / `**MID**: <value>` prefix block (separated by a blank line from the following content), the reader extracts the `MID` value as the TEXT child node's machine identifier. The remaining body text becomes the TEXT statement.

The writer re-emits this prefix whenever the grammar's `TEXT` element declares a `MID` field, preserving the TEXT MID across format passes.

Example:

```markdown
## Introduction

**TYPE**: SECTION \
**MID**: 11111111111111111111111111111111

**TYPE**: TEXT \
**MID**: 22222222222222222222222222222222

**STATEMENT**: This is a text statement.
```

After a format pass the SECTION MID (11111111111111111111111111111111) is preserved in the section meta block, and the TEXT MID (22222222222222222222222222222222) is preserved in the TEXT prefix block.

### Meta-field styles

**MID**: 0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a \
**UID**: MD-10

**STATEMENT**:

The meta block is a contiguous group of `**Key**: value` lines following the first blank line after the heading. It ends at the next blank line. Field names match `[A-Za-z0-9][A-Za-z0-9 _-]*` and are stored uppercase. Values may optionally be enclosed in backticks.

The meta block uses backslash style: each field except the last ends with ` \`.

### Content fields

**MID**: 1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b \
**UID**: MD-11

**STATEMENT**:

After the meta block, content fields are written as `**FieldName**: value` lines.

- If the value contains only one paragraph (no blank line within the value), the value follows the field name on the same line: `**FieldName**: value`.
- If the value contains two or more paragraphs (separated by a blank line), or if the value begins with a Markdown structural element (list, code block, blockquote, table, etc.), the value follows a blank line after the field name alone on its line: `**FieldName**:\n\nvalue`.

Prose not starting with a `**Key**:` header is accumulated as an implicit `STATEMENT` field.

### LINK tag

**MID**: e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3 \
**UID**: MD-32

**STATEMENT**:

A `[LINK: <uid>]` token may appear anywhere in a content field value (e.g. STATEMENT, RATIONALE, COMMENT). It creates a traceable inline reference to the node or anchor identified by `<uid>`. The UID must match the `REGEX_UID` pattern: `[\w]+[\w()\-\/.: ]*`.

A `[LINK: ...]` token that appears inside an inline code span (`` `[LINK: uid]` ``) or inside a fenced code block is treated as plain text and is **not** resolved as a traceable reference. This allows documentation to describe the LINK syntax itself without triggering UID resolution errors.

Example: a STATEMENT referencing another requirement:

```markdown
## Requirement A

**UID**: REQ-1

System shall do X. See also [LINK: REQ-2].
```

### ANCHOR tag

**MID**: f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4 \
**UID**: MD-33

**STATEMENT**:

An `[ANCHOR: <uid>]` or `[ANCHOR: <uid>, <title>]` token places a named anchor in a content field value. The anchor must appear at the start of a line and occupy the entire line (no other text on the same line). The UID follows the `REGEX_UID` pattern. The optional title is a human-readable label.

An `[ANCHOR: ...]` token that appears inside an inline code span or a fenced code block is treated as plain text and is **not** registered as a named anchor.

Example:

```markdown
## Section

[ANCHOR: SEC-INTRO]
This section describes the introduction.

[ANCHOR: SEC-INTRO-ALT, Introduction alternative anchor]
Additional content.
```

### Dictionary format

**MID**: b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7 \
**UID**: MD-22

**STATEMENT**:

Attribute dictionaries use bold-key notation: each key-value pair is written as `**Key**: value`. Values may optionally be enclosed in backticks; if present, the backtick delimiters are stripped when parsed.

When a dictionary spans multiple key-value pairs, all pairs except the last end with ` \` (a space followed by a backslash).

When a dictionary appears as an item in a bullet list (as in RELATIONS), continuation attribute lines must be indented by at least one space relative to the enclosing `- ` marker.

### RELATIONS field

**MID**: 2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c \
**UID**: MD-12

**STATEMENT**:

The `RELATIONS` field is a list-valued meta field. It must immediately follow the rest of the meta block without an intervening blank line.

Its value is a bullet list where each item represents one relation. Within an item, attributes are written as `**<Key>**: <Value>` pairs; continuation lines are indented by two spaces and end with ` \` except for the last pair.

A `RELATIONS` list must contain at least one item.

### Parent and Child relations

**MID**: 3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d \
**UID**: MD-13

**STATEMENT**:

A Parent or Child relation requires `**Type**` (`Parent` or `Child`) and a mandatory `**ID**` key holding the UID of the related node.

An optional `**Role**` key names the relation role. No other keys are allowed.

### File relations

**MID**: 4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e \
**UID**: MD-14

**STATEMENT**:

A File relation requires `**Type**: File` and a mandatory `**Path**` key.

Optional keys are `**Lines**` (line range), `**Element**` (language element type), `**ID**` (element identifier), and `**Hash**` (content hash).

`Element` and `ID` are mutually exclusive with `Lines`. No other keys are allowed.

## Markdown Grammar Format

### Grammar file naming

**MID**: 5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f \
**UID**: MD-15

**STATEMENT**: Markdown grammar files use the `.gra.md` file extension.

### Grammar document structure

**MID**: 6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a \
**UID**: MD-16

**STATEMENT**:

A grammar file must start with an H1 heading with no content before it.

The body uses a fixed heading hierarchy: H2 for element declarations, H3 for field declarations and the Relations section, H4 for relation declarations. Other heading levels are not allowed.

### Element declaration

**MID**: 7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b \
**UID**: MD-17

**STATEMENT**:

Each grammar element is declared as `## Element: <NAME>`. Element names must be unique within the file. At least one element is required.

Optional element properties:

- `**Composite**: True|False` — whether the element may contain child elements.
- `**Prefix**: <string>` — default UID prefix.
- `**View Style**: <string>` — display style hint.

### Field declaration

**MID**: 8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c \
**UID**: MD-18

**STATEMENT**:

Each field is declared as `### Field: <NAME>`. Field names must be unique within the element.

Required properties: `**Type**: <type>` and `**Required**: True|False`. Optional property: `**Human Title**: <string>`.

Field properties are written as plain `**Key**: value` lines with no continuation marker.

### Field types

**MID**: 9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d \
**UID**: MD-19

**STATEMENT**:

Supported field types:

- `String` — free-form text.
- `Tag` — space-separated tag list.
- `SingleChoice(<option>, ...)` — exactly one value from a fixed set.
- `MultipleChoice(<option>, ...)` — one or more values from a fixed set.

`SingleChoice` and `MultipleChoice` must declare at least one option.

### Relation declarations

**MID**: 0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e \
**UID**: MD-20

**STATEMENT**:

Within an element, `### Relations` opens the relations section. Each permitted relation type is declared as `#### Relation: <TYPE>` where `<TYPE>` is `Parent`, `Child`, or `File`.

An optional `**Role**: <role>` property names the relation role.
