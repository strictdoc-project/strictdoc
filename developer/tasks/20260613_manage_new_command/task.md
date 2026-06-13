# Add "manage new" command

## WHAT

Add a new CLI command `manage new` that creates a new node with unique MID/UID and required fields set to TBD and non-required fields empty.

Additional details:

- This command should work for both SDoc and Markdown files.
- The first required positional argument `project_root_path` shall be a path to a document tree root.
- StrictDoc shall read the project documents in the same way like it does for `export` and `server` commands to ensure that creating new nodes will not introduce any collisions in UID/MID spaces.
- The optional named argument `parent_uid_or_mid` shall indicate an existing parent node UID/MID in the chosen document. The new node shall be added as a child node to this parent node.
- The optional named argument `document_path` should point to a specific document where the new node should be added.
- In case both `document_path` and `parent_uid_or_mid` are provided, the parent UID/MID must be present in the target document otherwise an error shall be printed.
- The `manage new` command shall validate that the parent node is either a document node or a composite node that can hold child nodes.

## WHY

Simplifies the CLI workflow of creating new nodes.

## HOW

New files: `manage_new_config.py`, `manage_new_command.py` (following the pattern of `manage_autouid_command.py`). Modified: `project_config.py` (new loader method), `cli/main.py` (register the sub-command).

`run()` flow:
1. Call `DocumentFinder.find_sdoc_content` to parse documents.
2. If neither `--document-path` nor `--parent-uid-or-mid` is given, validate the document count early (before building the graph).
3. Call `TraceabilityIndexBuilder.create_from_document_tree` to build the traceability graph.
4. Resolve the parent node from `--parent-uid-or-mid` (UID or MID lookup) or `--document-path` (match by absolute path), or fall back to the single document. When both are given, validate the parent is in the specified document.
5. Determine node type from the grammar (first non-SECTION, non-TEXT element).
6. Generate a collision-free UID using `DocumentUIDAnalyzer` + `get_prefix_for_new_node`.
7. Create an `SDocNode` with the UID set and all `required=True` grammar fields set to `TBD`.
8. Append to `parent.section_contents` and write back via `SDWriter` (`.sdoc`) or `SDMarkdownWriter` (`.md`).

Seven integration tests cover: add to document root, add to section, required fields → TBD, UID collision avoidance across documents, `--document-path` selection, both args valid, both args mismatched → error.
