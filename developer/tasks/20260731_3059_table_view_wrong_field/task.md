# TABLE VIEW Relation field for unsupported node types

## WHAT

In TABLE VIEW, a Relation cell must be editable only when the grammar of the
specific node type declares at least one relation type. For a node type without
relations, the cell must be rendered as a dimmed, inactive cell like other
grammar fields that are not declared for that node.

The relation editing form must present diagnostics consistently: the file
relation limitation belongs with form errors, and parent-relation UID
validation must not be reported for file relations.

The change is covered by an end-to-end regression fixture with a minimal
SECTION without relations and a second node with a UID. The test enters TABLE
VIEW edit mode and verifies that the SECTION Relation cell cannot be opened.

## WHY

The TABLE VIEW showed an active Relation editor for a NODE whose grammar did
not support relations. Users could add a UID, but saving produced a 422 error
instead of a meaningful result.

The misleading UID error had a specific cause: when the relation type select
had no options, the browser omitted the value and request parsing defaulted the
relation type to `File`. Validation then checked only that a reference field
existed, regardless of whether it was a Parent/Child relation, and emitted the
parent-relation UID message.

The file-relation warning was rendered as a standalone inline block instead of
through the form error component, so it appeared in the wrong place relative
to validation errors.

## HOW

The TABLE VIEW view object now treats `RELATIONS` as editable only when the
grammar element has declared relations. The table template uses this check and
renders the same dimmed-cell structure used by other unavailable fields.

Requirement form validation now requires a UID only when at least one Parent or
Child reference is present; File references do not trigger that diagnostic.
The unsupported file-relation message is rendered with `sdoc-form-error` so it
is grouped with the form's errors.

The regression test lives under
`tests/end2end/screens/table/view_table_edit/_relations/` and is run headless
through the Invoke end-to-end task. Existing relation-editing and UID-validation
tests remain unchanged and pass.
