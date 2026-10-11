# Investigation: node categories and section Clone behavior

## Outcome

The investigation started from a valid test failure but reached an incorrect
initial diagnosis. A regular `SECTION` node does not render as
`data-testid="node-section"`. The original e2e assertion therefore verified no
node.

The investigation also found that StrictDoc currently clones sections. The UI
shows Clone for sections, and the server accepts a section through the Clone
route. The current task changes that product behavior. Clone will support only
regular, non-composite document nodes.

## Trigger

The `move_node_subtree_moves_as_whole` scenario needed to select and move a
regular section with child nodes. The existing `Section` e2e page object used
this selector:

```text
//sdoc-node[@data-testid='node-section']
```

The selector found no regular `SECTION` node. The first report assumed that
`get_type_string()` should return the grammar tag and that a section should
therefore render as `node-section`.

The report also assumed that section Clone and the Add node menu were broken.
The initial assumptions required a review of the model, templates, routes, and
test history.

## Confirmed behavior

### `get_type_string()` returns UI categories

The method has three possible results:

- `document` for a top-level `SDocDocument`
- `section` for an included `SDocDocument`
- `requirement` for every `SDocNode`.

The `requirement` category includes:

- `REQUIREMENT`
- `SECTION`
- `TEXT`
- custom grammar nodes
- composite custom grammar nodes.

Templates use the category for route names, controls, CSS roles, anchors, and
test IDs. The value is not a grammar tag.

### A regular section is an `SDocNode`

The current model represents `[[SECTION]]` as a composite `SDocNode` with
`node_type == "SECTION"`. A regular section follows the content-node render
path and uses `<sdoc-node-content>`. The section does not use
`<sdoc-section>`.

### `<sdoc-section>` represents an included-document root

An included document remains an `SDocDocument`. The UI exposes the document as
the category `section` and renders it through `components/section/*` and
`<sdoc-section>`.

The `section` category came from the legacy model. StrictDoc previously had a
separate `SDocSection` class. The e2e `Section` helper originally selected that
model. After StrictDoc migrated sections to composite `SDocNode` instances,
the old `node-section` selector continued to match included-document roots
only.

### The negative Clone assertion was vacuous

The clone fixture contains one regular section and one requirement. Both nodes
render as `data-testid="node-requirement"`. The old test checked for a Clone
control below `data-testid="node-section"`. The parent selector matched no
node, so the negative assertion always passed.

The test must first select an existing node with grammar type `SECTION`. Only
then can the test make a valid assertion about its controls.

### Section Clone currently works

The node-controls template shows Clone when `get_type_string()` returns
`requirement`. A section returns that category.

`can_clone_node()` accepts every deletable `SDocNode`. The Clone route uses the
source node's grammar element to create the form. The combined behavior lets a
user clone a section successfully.

### The Add node menu has no confirmed defect

A regular section enters the `requirement` branch of the Add node template.
The section is composite, so the branch renders `above`, `child`, and `below`.
The dedicated `section` branch renders the same positions. The investigation
found no user-visible difference for the section fixture.

## Problems found during the investigation

### Test defect

The e2e test made a negative descendant assertion before it established that
the parent section existed. The test stayed green while the application showed
a Clone control on the section.

### No server restriction

The server uses deletion permission as the Clone permission. The check does
not distinguish regular nodes from composite nodes. A direct request can clone
a section.

### No stable grammar-type selector

The HTML exposes the UI category through `data-testid`. The markup does not
provide a stable, dedicated attribute for the grammar type. Tests therefore
mix UI categories with grammar types.

### Ambiguous names

Several names preserve assumptions from the legacy section model:

- `get_type_string()` sounds like a grammar-type method
- `section` means an included-document root in the current UI category
- `requirement` means any `SDocNode`
- the `Section` page object selects included-document roots
- `clone_requirement` handles regular nodes beyond `REQUIREMENT`.

The names make code and tests easy to misread. A future refactoring should
separate these concepts:

- document kind
- grammar node type
- UI category
- operation support
- operation permission.

## Decision for the implementation task

The current task will:

- define Clone support for non-composite `SDocNode` instances
- hide Clone for sections and other composite nodes
- reject unsupported nodes in the Clone route
- preserve disabled Clone controls for protected regular nodes
- add a stable grammar-type attribute for tests
- replace the vacuous section assertion
- update the requirement documentation and release notes.

The current task will not rename the shared category APIs. The rename affects
templates, routes, CSS, tests, and page objects. A separate refactoring can
change those names while keeping terminology cleanup separate from the behavior
fix.

## Verification performed during the investigation

- `invoke test-end2end --focus clone_node --headless`: 4 passed with the old
  vacuous assertion.
- `invoke test-end2end --focus update_included_document_title --headless`:
  1 passed. The test proves that `Section` selects an included-document root.
- The rendered clone fixture contained two `node-requirement` elements, no
  `node-section` element, and a Clone control on both regular nodes.
