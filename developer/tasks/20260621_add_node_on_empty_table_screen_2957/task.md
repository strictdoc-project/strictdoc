# Implement adding nodes from the table screen if the document is empty

## WHY

The TABLE screen is intended to become a complete document editing surface.
Users can already modify existing nodes without switching to Document view,
but newly created documents still require a context switch because the first
node cannot be created from the TABLE screen.

This limitation prevents users from completing the entire document creation
workflow in one place and makes the TABLE screen inconsistent with its editing
goals.

## WHAT

Implement the creation of the first document node directly from the TABLE screen
when the document is empty, and preserve the existing ability to edit an empty
ROOT node.

For the view types menu (id=“viewtype_handler”), for the TABLE screen item
(data-viewtype_link=“table”), disable the `(empty)` suffix and the
`.dropdown_menu_item.empty` class. (Just as this option is not used for the
Document screen.)

### Test cases

are verified for the minimal fixture without nodes, on the table screen.

- We are in display mode
- In display mode, we see an empty root node with the Title,
- In display mode, we see a table with a text placeholder.
- We switch to edit mode.
- The root placeholder shows block with meta fields (currently empty; we’re checking for integrity).
- In the table, the placeholder is replaced by a handler for the “Add Node” menu.
- Add the first node. Verify that it was successful (the node exists, and there are menu rows before and after the node).
- Add something to the meta fields and save.
- Exit edit mode.
- Verify that there is the content we entered in the meta fields in the root.
- Verify that there is no placeholder in the table, and that the single node we added is present.
- Switch to edit mode.
- Delete everything in the meta field(s).
- Delete the single node from the table.
- Check the single menu item for adding nodes.
- Exit edit mode.
- Check there is no meta in the root (only Title).
- Check for a placeholder in the table.

## HOW

Now on the empty TABLE screen we can see placeholder "This view is empty because
the document has no content." only.

At the same time, on the document page, we see the ROOT node, along with
a header and buttons that allow us to edit the ROOT and add new nodes relative
to it.

The idea is to reuse what has already been implemented; this does not involve
creating a separate “empty document” mode, but rather removing the special
“empty” table mode that contains only a placeholder.

The TABLE screen in **display mode** should show:

- The ROOT node, exactly as it appears alongside a non-empty table:
title, and meta is optional (no placeholder, that is on DOCUMENT screen).
- An empty table with a single row `colspan=“100%”`, containing the placeholder
text: “This table is empty because the document has no content.”

When **edit mode** is enabled:

- The ROOT node gains all the capabilities that have already been implemented
(editing title, meta, and custom meta).
- In the table, instead of the placeholder row `colspan=“100%”`, display a row
to open the menu for adding nodes.

For technical details on this feature, see the files in
`developer/tasks/20260606_table_view_edit_mode/` (excluding _draft).
