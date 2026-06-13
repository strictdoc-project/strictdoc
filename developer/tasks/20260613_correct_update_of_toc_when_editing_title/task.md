# Ensure correct update of TOC when editing node TITLE in web interface

## WHAT

https://github.com/strictdoc-project/strictdoc/issues/1278

When a node's TITLE is edited in the web interface, saving the node shall result in the TOC updated correctly.

Two cases are identified:

1) When a node does not have a TITLE and a user adds a TITLE.
2) When a node does have a TITLE and the user removes the TITLE.

## WHY

Suspecting that in some cases the TOC updates will not re-render the updated title levels correctly when a node's TITLE is edited in the web interface.

## HOW

- Check the existing logic of main_router.py and ensure that the TOC is updated correctly with respect to new levels.

Example:

If TOC has levels:

1. Requirement #1
2. Requirement #2
3. Requirement #3

If the TITLE is removed from the Requirement #2, the TOC shall become:

1. Requirement #1
2. Requirement #3
