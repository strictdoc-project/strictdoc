# Implement ENABLE_MID in Markdown

## WHAT

Enable the `ENABLE_MID` behavior in Markdown similar how it is done by the SDoc machinery.

Implement in the following way:

- DO NOT introduce a document level `ENABLE_MID` option.
- Instead, make the `ENABLE_MID` behavior be activated if a user grammar contains the MID field.

## WHY

- The `ENABLE_MID` feature is very important for many users. We want to have it enabled for Markdown.
- At the same time, we would like to avoid adding a yet another document-level option to active it.

The automatic recognition based on the grammar field should be enough to do the job.

## HOW

### Trigger condition

ENABLE_MID behavior is activated when **all three** conditions are met:

1. The document uses a custom (non-default) grammar (`document_grammar.is_default == False`).
2. The grammar element (e.g. `REQUIREMENT`) declares a `MID` field in its `fields_map`.
3. The node being written does not already have a `MID` field in its `ordered_fields_lookup`.

The default Markdown grammar also carries a `MID` field (for backward compatibility), so guarding with `is_default` prevents MID injection into plain Markdown documents that do not reference any custom grammar.

### Changes

**`strictdoc/backend/markdown/writer.py` — `_serialize_node_fields`**

Before iterating the node's own fields, check the trigger condition. If met, prepend `("MID", node.reserved_mid)` to `meta_fields`. This causes the auto-generated UUID to be written to the document on the next save, making it permanent on the subsequent read (because `SDocNode.__init__` sets `mid_permanent = True` whenever a MID value is present in the parsed fields).

**`strictdoc/core/transforms/update_requirement.py`**

When the web UI creates a new requirement node, `mid_permanent = True` is set if `document.config.enable_mid` is True (SDoc path) **or** if the grammar element has a `MID` field (Markdown custom grammar path).

**`strictdoc/core/file_traceability_index.py`**

Same extension: when a MID field is updated via the server merge path, `mid_permanent = True` is set if the grammar element has a `MID` field (in addition to the existing `enable_mid` check).

### Tests

Three new unit tests were added to
`tests/unit/strictdoc/backend/markdown/test_markdown_grammar.py`:

- `test_007` — writer auto-writes MID when grammar has MID but node has none.
- `test_008` — writer preserves an existing MID (no duplicate injection).
- `test_009` — writer does NOT inject MID when grammar has no MID field.
