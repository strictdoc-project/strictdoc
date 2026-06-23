# TABLE screen: Add Node

## WHY

TABLE screen is intended to become a real editing surface, not only a read-only
overview of document content. Inline editing of existing fields already reduces
context switching, but the workflow remains incomplete as long as users must go
back to Document view to insert new nodes.

The missing capability is creation of new nodes directly from the TABLE screen.
Users should be able to place a new node where they are already working,
preserve the underlying document hierarchy, and continue editing immediately in
the table.

The feature must reuse the existing node creation and validation pipeline. It
must not introduce a separate SDOC model, a temporary unsaved node state, or a
parallel creation flow that diverges from Document view rules.

## WHAT

Table edit mode gains separator rows that allow creating new nodes directly in
the table.

The separator behavior is:

- separators are rendered before the first content row, between content rows,
  and after the last content row;
- separators are hidden in display mode and visible only in Table edit mode;
- clicking a separator opens a local menu of valid insertion actions;
- each menu action combines:
  - a grammar element type;
  - a structural placement relative to nearby nodes:
    `before next`, `after previous`, or `child of previous`;
- only structurally valid placements are shown for a given separator;
- all grammar elements of the current document grammar are listed and always
  enabled.

Creation lifecycle:

- selecting an action creates and saves the node immediately;
- the backend generates UID and MID the same way as Document view already does;
- required String, SingleChoice, and MultipleChoice fields are prefilled with
  `TBD` (which is accepted as a legal placeholder value by the grammar
  validator for all of these types);
- if no field receives a value through the above steps (no UID prefix, MID
  disabled, no required fields), the first available field is filled with
  `TBD` in priority order: `TITLE` → `STATEMENT` → `RATIONALE` → first
  String field → first SingleChoice field → first MultipleChoice field;
- successful creation refreshes the TABLE screen through Turbo, keeps edit mode
  active, and updates the table body and TOC;
- creation does not open or focus an editable field in the new node;
- after creation, the new node occupies the viewport position of the Add menu
  that initiated creation: the menu area's top-left viewport coordinates are
  preserved for the top-left of the new row, so the page does not jump;
- there is no post-create cancellation path on TABLE screen because the node is
  already persisted.

Scope limits:

- creation from an empty TABLE screen is out of scope;
- hidden columns do not block node creation;
- the active column-visibility state is reapplied after the Table body is
  replaced, so the header and the new body remain aligned;
- Add actions are unavailable while the table is not in original document
  order:
  - if column sorting is active;
  - if any node types are hidden by the rows filter.

## HOW

### Add row rendering

Table body rendering passes explicit adjacent-node context to a feature-local
separator template. Each separator can therefore compute placement options from
its previous and next document nodes without inferring structure from the DOM
at click time.

The menu uses grammar-aware helpers from the TABLE screen object:

- enumerate current grammar elements;
- determine whether an element type can be created immediately;
- return a disable reason when immediate creation is impossible.

The menu remains local to TABLE screen and does not reuse the Document view node
controls component because the Table separator actions are opened between rows
rather than from an existing node card.

### Placement rules

Each separator may expose these actions:

- `before next`: create a sibling immediately before the next node;
- `after previous`: create a sibling immediately after the previous node;
- `child of previous`: create a child of the previous node only when that node
  is composite and can accept children.

The backend never trusts the client-provided action blindly. It revalidates the
reference node, placement direction, and add/insert permissions using the
existing traceability index checks.

### Immediate creation

Table-specific backend endpoints receive:

- `context_document_mid`
- `reference_mid`
- `whereto`
- `element_type`

The endpoint reuses the existing creation flow:

- create a fresh `RequirementFormObject`;
- populate generated UID/MID as already supported;
- fill all required fields (String, SingleChoice, MultipleChoice) with `TBD`,
  which is accepted as a legal placeholder value by the grammar validator for
  all of these types;
- all grammar element types are always available for creation — no type is
  disabled in the Add menu;
- create the node through `CreateOrUpdateNodeCommand`;
- write the document and export the updated HTML.

The current implementation refreshes only the Table body (`table-content-body`)
and the TOC via Turbo Streams. A hidden feedback target carries the created
node MID back to the client so the client can locate and position the new row
after the Turbo update has settled.

### Turbo refresh and viewport position

On success, the server returns a Turbo update for the refreshed document
content and enough information for the client to find the new row. The Table
creation JavaScript then:

- preserves edit mode across the refresh;
- reapplies hidden-column state to the replacement body;
- does not open or focus any field;
- compensates the page scroll after the DOM replacement so the new row's
  top-left viewport coordinates match the top-left coordinates of the Add menu
  from which creation was requested.

Unexpected transport or `5xx` failures are handled generically in JavaScript
and are never inserted into the table as validation markup.

### Restrictions while reordered or filtered

Table insertion is defined against the real document order, not the current
visual order after sorting or node-type filtering. To avoid ambiguous
placements, Add actions are blocked whenever:

- a column sort is active;
- one or more node types are hidden.

The UI exposes a clear disabled state and an explanation so the user can reset
the table to full document order before adding nodes.

When an Add menu is opened while one or both restrictions are active:

- the separator and its Add handler remain visible;
- the regular node-creation actions are hidden;
- every active blocking reason is shown separately;
- each reason has an inline reset action equivalent to the corresponding Table
  toolbar reset;
- clearing one reason leaves the other reason and its reset action visible;
- when all reasons are cleared, the same open menu immediately returns to its
  regular node-creation actions;
- resetting sorting or the rows filter keeps the open menu on screen at the
  same vertical viewport position, even when the reset changes row visibility
  or order.

Sorting also preserves the vertical viewport position of the row that contains
the active Table edit cell when no Add menu is open. The cell remains in edit
mode after sorting. Row filtering does not preserve an active edit cell: the
cell may lose focus and complete its existing blur/outside-click lifecycle.

The JavaScript creation path rechecks sorting and filtering as a safety
mechanism even though the client hides actions while the Table state is
blocked. The server independently revalidates placement and creatability.

### Viewport anchor contract

The Table toolbar script emits feature-local DOM events immediately before and
after sorting or row-visibility changes. Table edit mode uses these events
without importing toolbar internals:

- an open Add menu is the viewport anchor for sorting and row-filter changes;
- otherwise, the row containing the active edit cell is the anchor for sorting
  changes;
- active edit cells are not anchors for row-filter changes.

The anchor records viewport geometry and compensates the Table `.main` scroll
container after layout settles. While Table edit mode is active, CSS disables
browser-native scroll anchoring and smooth scrolling for this container so
explicit position corrections are immediate and deterministic.

## Verification requirements

Automated coverage must verify:

- separator rendering before, between, and after nodes;
- valid action sets for `before next`, `after previous`, and `child of
  previous`;
- creation of multiple supported grammar element types;
- required String, SingleChoice, and MultipleChoice auto-fill with `TBD`;
- generated UID and MID behavior;
- blocking while sorting is active;
- blocking while node-type filtering hides rows;
- simultaneous sorting and node-type-filter blockers, including both reasons
  and both inline reset actions;
- sequential reset of simultaneous blockers while the same menu remains open;
- restoration of regular actions after the final blocker is removed;
- preservation of the open menu's vertical viewport position when sorting or
  the rows filter is reset;
- preservation of the active edit cell's row position and edit state when
  sorting changes;
- confirmation that row-filter changes do not apply active-cell position
  preservation;
- hidden columns remaining hidden and aligned in both header and replacement
  body after creation;
- preservation of edit mode after Turbo refresh;
- preservation of the initiating menu area's top-left viewport coordinates by
  the newly created row;
- confirmation that creation does not focus or open an editable field;
- generic handling of server/network failures;
- confirmation that empty TABLE screen still does not offer creation.

The viewport-position tests must compare element geometry before and after the
operation with a small browser-rendering tolerance. The existing
`project_tree_preserve_scroll` end-to-end test may be used as a reference for
measuring scroll and viewport geometry.

Required checks:

- `pytest -q tests/unit/strictdoc/export/html/test_html_templates.py`
- `invoke test-end2end --focus add_table_node --headless`
- `invoke test-end2end --focus edit_table --headless`
- `git diff --check`
- `invoke lint-ruff`
- `invoke lint-mypy`
