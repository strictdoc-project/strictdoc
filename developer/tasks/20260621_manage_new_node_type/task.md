# Extend "manage new" command with a required "node_type" parameter

## WHAT

Extend the "manage new" command with an optional "node_type" parameter which
specifies which node type the new node should be created with.

If a document has no grammar, not specifying "node_type" should set it to
"REQUIREMENT" by default.

If a document has a custom grammar and "node_type" is not specified by a user:

* If the grammar has an element of type "REQUIREMENT", "node_type" should be set
to "REQUIREMENT".
* If the grammar has no "REQUIREMENT" element, StrictDoc shall raise an error,
prompting the user to provide "node_type".

## WHY

When a document has a custom grammar, a user needs to specify which node they
want to create with "manage new" command. Otherwise, StrictDoc cannot guess
which node should be created.
