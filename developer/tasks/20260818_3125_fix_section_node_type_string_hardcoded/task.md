# Fix section nodes getting the wrong node-controls behavior

## WHAT

`get_type_string()` shall report a node's actual grammar tag (for
example `section`, `requirement`, or a custom tag), not a fixed value
regardless of the node's real type.

Once this is fixed, the following shall hold:

- A section node shall not render a Clone action. Only requirement nodes
  are cloneable.
- A section node shall present the section-specific "Add node" menu
  (its own `whereto` options), not the requirement-specific one.
- The `data-testid` attribute rendered for a node
  (`data-testid="node-{{ node_type }}"`) shall match the node's real
  type, so a section renders `data-testid="node-section"`.
- The e2e page object `Section`
  (`tests/end2end/helpers/components/node/section.py`) shall be able to
  select, assert on, and act on section nodes; selecting a section node
  by its testid shall not time out.
- The `clone_node` e2e test's assertion that a section has no clone
  button shall pass because the application is actually correct, not
  because its selector matches nothing.

Before choosing an implementation, verify whether any other code path
relies on the current, incorrect behavior of `get_type_string()` always
returning `"requirement"` for every `SDocNode`/`SDocCompositeNode`
instance. Two candidate approaches, not yet decided between:

1. Make `get_type_string()` (or the `node_type` value derived from it in
   `components/node/index.jinja`) reflect the node's actual grammar tag,
   and update whatever code currently depends on the old, incorrect,
   always-`"requirement"` behavior.
2. Leave `get_type_string()` alone and instead fix the two affected
   template branches directly (the Clone-button guard and the "Add node"
   menu's section branch) with an explicit check that does not go
   through `get_type_string()`.

## WHY

`SDocNode.get_type_string()`
(`strictdoc/backend/sdoc/models/node.py:316`) is a `@staticmethod` that
unconditionally returns `"requirement"`, regardless of a node's actual
grammar tag. `SDocCompositeNode`
(`strictdoc/backend/sdoc/models/node.py:885`), the class used for
sections and other composite nodes, subclasses `SDocNode` and does not
override this method. As a result, every node in the application,
sections included, reports itself as `"requirement"`.

This is a functional bug, not just a test-tooling gap. It has two
concrete effects on the running application, both caused by
`strictdoc/export/html/templates/components/node/node_controls/index.jinja`
branching its rendered controls on `sdoc_entity.get_type_string()`:

1. **Clone button renders on sections.** The template's CLONE block is
   guarded by `{%- if sdoc_entity.get_type_string() == 'requirement' -%}`,
   with a comment stating clone applies to requirements only, not
   sections. Since a section evaluates as `"requirement"`, it renders a
   Clone action it should not have.
2. **Wrong "Add node" menu for sections.** The ADD NODES dropdown has
   separate branches for `'document'`, `'section'`, and `'requirement'`.
   A section always falls into the `'requirement'` branch instead of
   the `'section'` branch, so it presents the requirement-shaped
   add-node menu (different layout, different `whereto` options)
   instead of the section-shaped one.

The same root cause also affects
`data-testid="node-{{ node_type }}"` in
`components/node/index.jinja:33` (`node_type` is set from
`sdoc_entity.get_type_string()` on line 14), so no node in StrictDoc's
HTML output ever gets `data-testid="node-section"`; every node,
sections included, renders `data-testid="node-requirement"`.

Verified against the repository's own fixture
`tests/end2end/screens/document/clone_node/clone_node/input/document.sdoc`
(one SECTION `S-01`, one REQUIREMENT `REQ-1`) by rendering it through a
`TestClient` and counting testid occurrences in the HTML:

- `node-section`: 0 occurrences.
- `node-requirement`: 2 occurrences, one for the section and one for the
  requirement.

This went unnoticed because the only test referencing
`data-testid='node-section'`,
`tests/end2end/screens/document/clone_node/clone_node/test_case.py`,
does so with `assert_element_not_present(...)`, checking that a section
node has no clone button. Since the outer selector (`node-section`)
never matches anything, that assertion passes whether or not sections
actually lack a clone button; the test stays green for the wrong
reason. No other test in the repository instantiates `Section`
(confirmed with `grep -rl "= Section(" tests/end2end/`, which returned
only a test written for an unrelated task), so the page object is
effectively dead code: any attempt to use it times out with
`NoSuchElementException`.

Consequences of leaving this unfixed:

- Sections keep showing a Clone action they should not have, and the
  wrong "Add node" menu.
- `Section` cannot select, assert on, or act on section nodes in e2e
  tests as currently written.
- The `clone_node` test's assertion about sections lacking a clone
  action continues to verify nothing.
- Any future e2e test that needs to interact with a section
  specifically, not just "some node," cannot rely on `Section` and has
  to fall back to a generic `Node`-based selector instead.

Found while writing the `move_node_subtree_moves_as_whole` e2e scenario
for task `20260817_feat_ux_node_moving`, which needed to move a section
with children as one test case. Full original write-up, including the
exact verification steps: `BUG_node_section_testid_never_rendered.md`
in this same directory.

## HOW

<!--
The HOW section should start with a top-down (bottom line up front) summary of
the implemented solution.

Describe the chosen technical approach, architecture, design decisions, implementation details, and trade-offs.
-->
