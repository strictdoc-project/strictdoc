# Add an option to enable fixed-width content formatting for SDoc and Markdown documents

## WHAT

Add optional fixed-width content formatting for SDoc and Markdown documents.

Introduce a config option `document_line_width` to the project configuration.
When enabled, this option should make the SDoc and Markdown writers format
document content to the given line width limit.

In particular, when the `document_line_width` is set, editing of all nodes in
the web interface and writing them back to file system, shall respect the given
line width limit.

Introduce `strictdoc format` command that acts like `black` or `ruff`, reading
the input documents and outputting the line width-formatted content back
(in-place editing for now).

The formatting rules specification shall be followed as defined here:
`spec/Formatting.md`.

The minimal acceptable limit shall be `80`.

The user manual shall be updated to reflect the new `format` command.

The formatters for Markdown and RST shall be implemented in separate dedicated Python files. Rationale: Easier maintainance of two similar but different markups.

Add a dedicated integration smoke test that runs the `format` against the
StrictDoc documentation in `docs/` twice. This is to ensure that the
formatting always works against StrictDoc's own documentation.


## WHY

The automatic formatting helps to avoid the manual effort of re-formatting
documents when a user wants to have their content to have fixed line width.

## HOW

### Implementation details

When running `format`, StrictDoc shall only build a traceability index for
documents and avoid reading source files. This is to run the command faster
because the source file information is not required for correct formatting
of documents.
