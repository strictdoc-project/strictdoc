# Create Markdown grammar following the schema of SDoc grammar

## WHAT

StrictDoc shall support grammars/schemas for constraining Markdown files.

There is a schema proposal in the `spec/Markdown.md`.

Iterate on the proposal to make it 100% identical model-wise to the existing SDoc grammar.

With this change in place, the expected behavior is as follows:

- The MarkdownReader shall remove any assumptions about being constrained to only the default elements: REQUIREMENT, SECTION and TEXT.
- A user shall be able to create Markdown with arbitrary elements as configured by the user in the grammar: reading Markdown is permissive with respect to element types but is checked by the TraceabilityIndexBuilder via `SDocValidator.validate_document(document)` just like it is done for the SDoc documents.

## WHY

The users of Markdown need a mechanism for constraining Markdown files according to a given schema.

## HOW

- Create a pair of dedicated `MarkdownGrammarReader`/`MarkdownGrammarWriter` classes.
- These classes shall validate the schema of the grammar.
- The StrictDoc document finding algorithm shall recognize files `*.gra.md` as Markdown grammar files and parse them into `DocumentGrammar` just like the SDoc grammar reader does it.
- The grammar shall be attachable to Markdown files if their document meta information specifies a grammar alias or a path to a grammar file.

Examples:

```
# Document example

**Grammar**: `requirements.gra.md`
```

```
# Document example

**Grammar**: `@requirements`
```

The `@requirements` grammar has to be registered in `strictdoc_config.py`.

- The Markdown grammar shall be attached to documents in the same way like it is done for SDoc documents and grammar from file nodes.

- The Markdown grammar reader shall provide validations equivalent to what is done by SDoc grammar reader based on a textX grammar.

### Second round

The likely remaining item is that MarkdownReader is still hardcoded to the default StrictDoc grammar. We want to relax it, postponing the validation to the TracebilityIndexBuilder.

### Third round: Markdown specification

Check the current branch and its task in developer/tasks

I am looking to create a separate document:

`spec/Markdown.md` that will contain a terse but complete summary of:

1) StrictDoc's Markdown format as implemented in the MarkdownReader/Writer.

2) StrictDoc's Markdown Grammar format as implemented in this branch by MarkdownGrammarReader.

The following requirements apply to this spec:

1) The spec shall be very terse.
2) The spec shall be complete, i.e., all existing markup details shall be covered as they are currently implemented in StrictDoc.
3) The spec shall be compatible with SDoc schema.
4) The spec shall be free from StrictDoc's Python implementation details. Any other tool shall be able to implement this format.
5) The spec shall be written using itself, both the `.md` and `.gra.md` files.
6) The spec shall have MID/UID identifiers similar to how that is done for all other StrictDoc documentation in `docs/`:
- The MID is an auto-generated identifier.
- The UID shall be based on a prefix `MD-` growing incrementally starting from the value `MD-1`.
