# Markdown Specification

**Grammar**: Markdown.gra.md

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

### Sections

**MID**: 7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d \
**UID**: MD-7

**STATEMENT**:

An H2–H6 heading that does not qualify as a requirement node (see MD-8, MD-9) becomes a section.

Free-form Markdown prose in a section body is stored as a TEXT node.

### Requirement nodes — default grammar

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

### Requirement nodes — custom grammar

**MID**: 9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f \
**UID**: MD-9

**STATEMENT**:

With a custom grammar, an H2–H6 heading becomes a REQUIREMENT node when the meta block contains at least one field and the heading text is non-empty.

Field validation against the grammar schema is deferred to a later build stage. The heading text is assigned to the `TITLE` field.

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

After the meta block, content fields are written as `**FieldName**: value` lines. A single-line value follows the colon directly; a multi-paragraph value follows a blank line after the field header.

Prose not starting with a `**Key**:` header is accumulated as an implicit `STATEMENT` field.

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

Its value is a bullet list where each item represents one relation. Within an item, attributes are written as `**Key**: \`value\`` pairs; continuation lines are indented by two spaces and end with ` \` except for the last pair.

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

A File relation requires `**Type**: \`File\`` and a mandatory `**Path**` key.

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
