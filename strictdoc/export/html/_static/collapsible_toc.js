/*
collapsible_toc.js
Adds interactive collapsing/expanding behavior to the TOC.

The script assumes TOC updates are performed as root-level replacement inside the mount container.
On dynamic updates, a new TOC root node ([js-collapsible_list]) is expected to be added
as a direct child of #frame-toc.
Partial in-place updates of nested TOC nodes are not the primary update model for this script.

Required markup:

1) Mount container
   - A container matching MOUNT_SELECTOR must exist (currently: #frame-toc).
   - If it is missing, initialization stops.

2) TOC root inside mount
   - Inside the mount container, there must be an element with [js-collapsible_list].
   - This is the root TOC node processed by the script.
   - If missing at runtime, run() exits safely.

3) TOC tree structure
   - Collapsible branches are detected by nested <ul> elements.
   - Expected branch pattern: <li ...><a ...></a><ul>...</ul></li>.
   - No nested <ul> => no collapse handlers are added.

4) Stable node ids for persisted state
   - Each branch parent (<li> that owns a child <ul>) should have data-nodeid.
   - data-nodeid values should be unique within the TOC.
   - These IDs are used as keys for per-branch collapsed/expanded state.

5) Dynamic TOC replacement behavior
   - MutationObserver watches childList changes on the mount container (subtree: false).
   - For auto-reinit on dynamic updates, a newly added direct child node of mount
     must be the TOC root (or include the [js-collapsible_list] node matched by current check).

6) State re-application on TOC updates
   - Persisted state is keyed by data-nodeid.
   - On re-init, each branch restores state from sessionStorage when nodeid matches.
   - Branches with unknown nodeid use default state (expanded).
   - After processing, sessionStorage is rewritten from the current DOM tree.
*/

/*
Bulk/Undo scenario:
1) If snapshot is empty and user clicks a bulk button:
   - create snapshot,
   - apply bulk action,
   - put undo mode on the clicked bulk button.
2) If snapshot already exists and user clicks a bulk button:
   - keep snapshot unchanged,
   - apply bulk action,
   - move undo mode to the clicked bulk button.
3) If user performs any non-bulk tree action:
   - clear snapshot,
   - return both bulk buttons to normal mode.
4) If user clicks undo:
   - restore snapshot,
   - clear snapshot,
   - return both bulk buttons to normal mode.
*/

// ===== Constants =====

const SS_ITEM = 'collapsibleTOC'; // sessionStorageItem

const MOUNT_SELECTOR = '#frame-toc';
const ROOT_SELECTOR = 'js-collapsible_list'; // js-collapsible_list with any value
const BRANCH_DATA_ATTR = `branch`; // li with a branch inside
const HANDLER_DATA_ATTR = `handler`; // handler
const NODE_ID_DATA_ATTR = `nodeid`; // from sdoc markup
const BULK_DATA_ATTR = `bulk`; // bulk operations button

// panel with global controls (expand all, collapse all, etc):
const CONTROLS_PANEL_ATTR = `${ROOT_SELECTOR}-bulk_controls`;
const CONTROLS_PANEL_CLASS = `toc-control-panel`; // for styling purposes only, not used in JS logic
const CONTROLS_PANEL_HEIGHT = `32px`;

const BULK_MODE = 'bulk';
const UNDO_MODE = 'undo';
let lastBulkSnapshot = null;

const _TRUE = 'collapsed';
const _FALSE = 'expanded';

const SYMBOL_FALSE = '－';
const SYMBOL_TRUE = '＋';
const SYMBOL_SIZE = 16;

const STYLE = `
[data-${BULK_DATA_ATTR}],
[data-${HANDLER_DATA_ATTR}] {
  display: flex;
  align-items: center;
  justify-content: center;
  -webkit-box-align: center;
  -webkit-box-pack: center;
  background-clip: padding-box;
  cursor: pointer;
  user-select: none;
  transition: .3s;
  width: ${SYMBOL_SIZE}px;
  height: ${SYMBOL_SIZE}px;
  font-size: ${SYMBOL_SIZE * 0.875}px;
  font-weight: bold;
  line-height: 0;
  border-radius: 50%;
  color: rgba(0,0,0,0.5);
  box-shadow: rgb(0 0 0 / 10%) 0px 1px 2px 0px;
  position: absolute;
  top: ${SYMBOL_SIZE * 0.5}px;
  left: -${SYMBOL_SIZE * 0.75}px;
}

[data-${BULK_DATA_ATTR}] {
  border: 1px solid rgba(0, 0, 0, 0);
  border-radius: 20%;
  box-shadow: rgb(0 0 0 / 25%) 1px 1px 0px 0px;
  background-color: var(--toc-background, #F2F5F9);
  position: relative;
  inset: 0;
}

[data-${BULK_DATA_ATTR}]:hover {
  background-color: rgb(255 255 255 / 50%);
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: rgba(0,0,0,1);
}

[data-${BULK_DATA_ATTR}]::before {
  content: attr(data-${BULK_DATA_ATTR});
}

[data-${BULK_DATA_ATTR}]::after {
  content: '';
  position: absolute;
  border-radius: 22%;
  inset: 2px -3px -3px 2px;
  box-shadow: rgb(0 0 0 / 20%) 1px 1px 0px 0px;
  pointer-events: none;
}

[data-${BULK_DATA_ATTR}][data-mode="${UNDO_MODE}"] {
  background-color: rgb(255 255 255 / 50%);
  border: 1px solid var(--toc-accent, #ffcc00);
}

[data-${BULK_DATA_ATTR}][data-mode="${UNDO_MODE}"]::before {
  content: '↶';
  font-family: monospace;
  font-size: ${SYMBOL_SIZE}px;
  font-weight: normal;
  color: var(--toc-accent, #ffcc00);
}

[data-${HANDLER_DATA_ATTR}]:hover {
  border: 1px solid rgba(0, 0, 0, 0.15);
  box-shadow: rgb(0 0 0 / 15%) 0px 2px 8px 0px;
  color: rgba(0,0,0,1);
}

[data-${HANDLER_DATA_ATTR}='${_TRUE}']::before {
  content: '${SYMBOL_TRUE}';
}

[data-${HANDLER_DATA_ATTR}='${_FALSE}']::before {
  content: '${SYMBOL_FALSE}';
}

[data-${BRANCH_DATA_ATTR}='${_TRUE}'] > ul {
  display: none;
}

[data-${BRANCH_DATA_ATTR}='${_FALSE}'] > ul {
  display: unset;
}

/* control panel */

[${CONTROLS_PANEL_ATTR}] {
  list-style: none;
  padding: 0 !important;
  margin: 0 !important;
  display: flex;
  align-items: stretch;
  justify-content: flex-start;
  height: ${CONTROLS_PANEL_HEIGHT};
}

[${CONTROLS_PANEL_ATTR}] > div {
  position: fixed;
  z-index: 2;
  display: flex;
  column-gap: ${SYMBOL_SIZE * 0.5}px;
  align-items: center;
  padding: ${SYMBOL_SIZE * 0.5}px;

  background: color-mix(in srgb, var(--toc-background, #F2F5F9) 20%, transparent);
  backdrop-filter: blur(${SYMBOL_SIZE * 0.5}px);
  -webkit-backdrop-filter: blur(${SYMBOL_SIZE * 0.5}px);
}
`;

// ===== Bootstrap =====

// Main entrypoint for TOC collapsing behavior.
// - Observe element `MOUNT_SELECTOR` for dynamic TOC injection and initialize when found.
// - Initialize immediately for the first render.
function main() {

  let mutatingFrame = document.querySelector(MOUNT_SELECTOR);
  if (!mutatingFrame) {
    console.error(MOUNT_SELECTOR + " not found");
    return;
  }

  new MutationObserver(function (mutationsList, observer) {

    for (let mutation of mutationsList) {
      if (mutation.type === 'childList') {
        let addedToc = Array.from(mutation.addedNodes).find(node => isCollapsibleList(node));
        if (addedToc) {
          run(mutatingFrame)
        }
      }
    }

  }).observe(
    mutatingFrame,
    {
      childList: true,
      // subtree: true
    }
  );

  run(mutatingFrame)
}

// Run TOC processing for the collapsible-list root
// (inside mount container).
function run(mount) {
  const toc = mount.querySelector(`[${ROOT_SELECTOR}]`);
  if (!toc) {
    return;
  }
  processToc(toc);
}

// Detect the TOC root node when it is injected into the frame.
function isCollapsibleList(node) {
  return (
    node.nodeType === 1 &&
    node.hasAttribute('js-collapsible_list')
    // node.getAttribute('js-collapsible_list') === 'root'
  );
}

// ===== TOC Processing =====

// Initialize all collapsible controls inside the TOC.
// - Adds expand/collapse controls next to branch items.
// - Restores saved state from sessionStorage.
// - Click toggles one branch.
// - Shift+Click toggles all descendant branches.
// - Double-click toggles all descendant branches.
function processToc(toc) {
  const storage = sessionStorageGet();

  const branchList = toc.querySelectorAll('ul');

  // Do it if that makes sense (if there are branches
  // in the list that could in principle be collapsible):
  if (branchList.length > 0) {
    addStyleElement(toc, STYLE);

    const controls = createControlsPanel(toc);

    branchList.forEach(
      ul => {
        const handler = createHandler();

        const parentNode = ul.parentNode;
        const nodeID = parentNode.dataset[NODE_ID_DATA_ATTR];
        const currentState = storage[nodeID] || _FALSE;

        // * I need the button to come before the link as well
        parentNode.prepend(handler);
        // Required:
        parentNode.style = "position:relative";

        // * run after the items have been added to the DOM
        setBranchState(handler, currentState);

        handler.addEventListener('click', event => {
          if (event.shiftKey) {
            bulkToggleChildBrunches(controls, handler);
            return;
          }
          toggle(controls, handler);
        });
        handler.addEventListener('dblclick', () => {
          bulkToggleChildBrunches(controls, handler);
        });
      }
    );

    updateSessionStorage();
  }
}

// ===== Tree Actions =====

// Toggle one branch between expanded and collapsed.
function toggle(controls, handler) {
  clearBulkUndoMode(controls);
  const newState = (handler.dataset[HANDLER_DATA_ATTR] === _FALSE) ? _TRUE : _FALSE;
  setBranchState(handler, newState);
  updateSessionStorage();
}

// Toggle all nested branches below a node in one action.
function bulkToggleChildBrunches(controls, handler) {
  clearBulkUndoMode(controls);
  const newState = (handler.dataset[HANDLER_DATA_ATTR] === _FALSE) ? _TRUE : _FALSE;
  const list = handler.parentNode.querySelectorAll(`[data-${HANDLER_DATA_ATTR}]`);
  list.forEach(handler => {
    setBranchState(handler, newState);
  });
  updateSessionStorage();
}

// ===== Bulk Controls =====

// Create and insert a panel with buttons for bulk operations (expand/collapse all).
function createControlsPanel(root) {
  const li = document.createElement('li');
  li.setAttribute(CONTROLS_PANEL_ATTR, '');
  li.classList.add(CONTROLS_PANEL_CLASS);
  const container = document.createElement('div');
  li.append(container);
  root.prepend(li);
  root.setAttribute('has-top-panel', '');
  // return li

  const collapseAllHandler = createBulkHandler(SYMBOL_TRUE);
  const expandAllHandler = createBulkHandler(SYMBOL_FALSE);
  container.append(collapseAllHandler, expandAllHandler);
  const controls = { collapseAllHandler, expandAllHandler };

  collapseAllHandler.addEventListener('click', () => {
    if (collapseAllHandler.dataset.mode === UNDO_MODE) {
      runUndoAction(root, controls);
      return;
    }
    runBulkAction(root, collapseAllHandler, expandAllHandler, _TRUE);
  });

  expandAllHandler.addEventListener('click', () => {
    if (expandAllHandler.dataset.mode === UNDO_MODE) {
      runUndoAction(root, controls);
      return;
    }
    runBulkAction(root, expandAllHandler, collapseAllHandler, _FALSE);
  });

  return controls;
}

// Create a handler element for bulk operations.
function createBulkHandler(symbol) {
  const handler = document.createElement('div');
  setBulkHandlerMode(handler, BULK_MODE);
  handler.dataset[BULK_DATA_ATTR] = symbol;
  return handler
}

// Set bulk button mode (`bulk` or `undo`).
function setBulkHandlerMode(handler, mode) {
  if (mode !== BULK_MODE && mode !== UNDO_MODE) {
    throw new Error(`Invalid bulk handler mode: ${mode}`);
  }
  handler.dataset.mode = mode;
}

// Exit undo mode and clear stored bulk snapshot.
function clearBulkUndoMode(controls) {
  if (controls) {
    setBulkHandlerMode(controls.collapseAllHandler, BULK_MODE);
    setBulkHandlerMode(controls.expandAllHandler, BULK_MODE);
  }
  lastBulkSnapshot = null;
}

// Apply bulk state to all branches and manage undo mode on bulk buttons.
function runBulkAction(root, handler, oppositeHandler, state) {
  if (!lastBulkSnapshot) {
    const snapshot = captureBulkSnapshot(root);
    // Skip storing trivial snapshots (all branches have the same state).
    if (!isTrivialSnapshot(snapshot)) {
      lastBulkSnapshot = snapshot;
    }
  }
  const handlerList = root.querySelectorAll(`[data-${HANDLER_DATA_ATTR}]`);
  handlerList.forEach(currentHandler => setBranchState(currentHandler, state));
  updateSessionStorage();
  if (lastBulkSnapshot) {
    setBulkHandlerMode(handler, UNDO_MODE);
  }
  setBulkHandlerMode(oppositeHandler, BULK_MODE);
}

// Restore the last captured bulk snapshot and reset undo mode.
function runUndoAction(root, controls) {
  restoreBulkSnapshot(root, lastBulkSnapshot);
  updateSessionStorage();
  clearBulkUndoMode(controls);
}

// ===== `Undo` Snapshot =====

// Capture current branch states for one-step bulk undo.
function captureBulkSnapshot(root) {
  const snapshot = {};
  root.querySelectorAll(`[data-${HANDLER_DATA_ATTR}]`).forEach(handler => {
    const nodeID = handler.parentNode.dataset[NODE_ID_DATA_ATTR];
    if (nodeID) {
      snapshot[nodeID] = handler.dataset[HANDLER_DATA_ATTR];
    }
  });
  return snapshot;
}

// Restore branch states from a previously captured snapshot.
function restoreBulkSnapshot(root, snapshot) {
  if (!snapshot) {
    return;
  }
  root.querySelectorAll(`[data-${HANDLER_DATA_ATTR}]`).forEach(handler => {
    const nodeID = handler.parentNode.dataset[NODE_ID_DATA_ATTR];
    const state = snapshot[nodeID];
    if (state) {
      setBranchState(handler, state);
    }
  });
}

// A snapshot is trivial when all stored branches have the same state.
function isTrivialSnapshot(snapshot) {
  const states = Object.values(snapshot);
  return states.length === 0 || states.every(state => state === states[0]);
}

// ===== Generic Helpers =====

// Keep handler and branch state in sync (expanded/collapsed).
function setBranchState(handler, state) {
  handler.dataset[HANDLER_DATA_ATTR] = state;
  handler.parentNode.dataset[BRANCH_DATA_ATTR] = state;
}

// Save every branch state currently rendered in the TOC.
function updateSessionStorage() {
  const obj = {};
  document.querySelector(`[${ROOT_SELECTOR}]`)
    .querySelectorAll(`[data-${BRANCH_DATA_ATTR}]`)
    .forEach(
      branch => obj[branch.dataset[NODE_ID_DATA_ATTR]] = branch.dataset[BRANCH_DATA_ATTR]
    );
  sessionStorageSet(obj);
}

// Read persisted branch states for this browser session.
function sessionStorageGet() {
  const item = sessionStorage.getItem(SS_ITEM);
  const res = item ? JSON.parse(item) : {};
  return res
}

// Persist current branch states for this browser session.
function sessionStorageSet(obj) {
  const string = JSON.stringify(obj);
  sessionStorage.setItem(SS_ITEM, string)
}

// Inject the CSS that draws toggle controls and shows/hides child lists.
function addStyleElement(target, styleTextContent, attr = 'style') {
  const style = document.createElement('style');
  style.setAttribute(`collapsible-toc-${attr}`, '');
  style.textContent = styleTextContent;
  target.before(style);
}

// Create a clickable handler element for one TOC branch.
function createHandler(state) {
  const div = document.createElement('div');
  state && setBranchState(item, state);
  return div
}

// ===== Startup =====

// Bootstrapping: run main after page load.
window.addEventListener("load", function() {
  main();
}, false);
