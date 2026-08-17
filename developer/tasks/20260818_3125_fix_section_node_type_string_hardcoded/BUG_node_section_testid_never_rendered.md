# Bug: `data-testid="node-section"` is never rendered

## Summary

No node in StrictDoc's HTML output ever gets `data-testid="node-section"`,
regardless of its grammar tag. Every node, sections included, renders
`data-testid="node-requirement"`. As a result, the e2e page object
`tests/end2end/helpers/components/node/section.py` (`Section` class)
selects nothing: its `node_xpath` is
`(//sdoc-node[@data-testid='node-section'])[{node_order}]`, a selector
that matches zero elements in the current app.

## Root cause

`strictdoc/export/html/templates/components/node/index.jinja:14` sets
`node_type = sdoc_entity.get_type_string()`, and line 33 renders
`data-testid="node-{{ node_type }}"`.

`get_type_string()` is defined in exactly two places in the codebase:

- `SDocDocument.get_type_string()`
  (`strictdoc/backend/sdoc/models/document.py:209`) returns `"document"`.
- `SDocNode.get_type_string()`
  (`strictdoc/backend/sdoc/models/node.py:316`), a `@staticmethod` that
  unconditionally returns `"requirement"`.

`SDocCompositeNode` (`strictdoc/backend/sdoc/models/node.py:885`), the
class used for sections and other composite nodes, subclasses `SDocNode`
and does not override `get_type_string()`. Every node, whether its grammar
tag is REQUIREMENT, SECTION, TEXT, or a custom tag, therefore renders the
same testid: `node-requirement`.

## Evidence

Verified against the repo's own fixture
`tests/end2end/screens/document/clone_node/clone_node/input/document.sdoc`
(one SECTION `S-01`, one REQUIREMENT `REQ-1`) by rendering it through
`TestClient` and counting testid occurrences in the HTML:

- `node-section`: 0 occurrences.
- `node-requirement`: 2 occurrences, one for the section and one for the
  requirement.

## Why this went unnoticed

The only test that references `data-testid='node-section'` is
`tests/end2end/screens/document/clone_node/clone_node/test_case.py`, and
it does so with `assert_element_not_present(...)`, checking that a section
node has no clone button. Since the outer selector (`node-section`) never
matches anything, the assertion passes whether or not sections actually
lack a clone button. The test stays green for the wrong reason.

No other test in the repository instantiates `Section`
(`tests/end2end/helpers/components/node/section.py`) at all, confirmed
with `grep -rl "= Section(" tests/end2end/`, which returned only a new
test written for the current task. The page object is effectively dead
code.

## Impact

- `Section` cannot select, assert on, or act on section nodes in e2e
  tests as currently written; any attempt times out with
  `NoSuchElementException`.
- The `clone_node` test's assertion about sections lacking a clone action
  verifies nothing.
- Any e2e test that needs to interact with a section specifically, not
  just "some node," cannot rely on `Section` and has to fall back to a
  generic `Node`-based selector instead.

## Where this was found

Found while writing the `move_node_subtree_moves_as_whole` e2e scenario
for `20260817_feat_ux_node_moving`, which needed to move a section with
children as one test case.

## Suggested fix (not implemented, out of scope here)

Either:

1. Make `data-testid="node-{{ node_type }}"` in
   `components/node/index.jinja` use the node's actual grammar tag (for
   example `sdoc_entity.node_type|lower`) instead of the hardcoded
   `get_type_string()`, and update whatever code relies on
   `get_type_string()` always returning `"requirement"`; or
2. Remove `get_type_string()`/`node-section` entirely if the distinction
   no longer matters in the current grammar model, and update or remove
   the dead `Section` page object and the vacuous `clone_node` assertion
   to match.

Either direction touches shared rendering code and existing tests, so it
needs its own review rather than being folded into the node-move feature.
