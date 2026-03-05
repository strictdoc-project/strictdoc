// Adds interactive collapsing/expanding behavior to the TOC.

const SS_ITEM = 'collapsibleTOC'; // sessionStorageItem

const MOUNT_SELECTOR = '#frame-toc';
const ROOT_SELECTOR = 'js-collapsible_list'; // js-collapsible_list with any value
const BRANCH_DATA_ATTR = `branch`; // li with a branch inside
const HANDLER_DATA_ATTR = `handler`; // handler
const NODE_ID_DATA_ATTR = `nodeid`; // from sdoc markup

const _TRUE = 'collapsed';
const _FALSE = 'expanded';

const SYMBOL_FALSE = '－';
const SYMBOL_TRUE = '＋';
const SYMBOL_SIZE = 16;

const STYLE = `
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

`;

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
          run()
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

  run()
}

// Run TOC processing for the collapsible-list root.
function run() {
  processToc(document.querySelector(`[${ROOT_SELECTOR}]`));
}

// Detect the TOC root node when it is injected into the frame.
function isCollapsibleList(node) {
  return (
    node.nodeType === 1 &&
    node.hasAttribute('js-collapsible_list')
    // node.getAttribute('js-collapsible_list') === 'root'
  );
}

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
            bulkToggleChildBrunches(handler);
            return;
          }
          toggle(handler);
        });
        handler.addEventListener('dblclick', () => {
          bulkToggleChildBrunches(handler);
        });
      }
    );

    updateSessionStorage();
  }
}

// Toggle one branch between expanded and collapsed.
function toggle(handler) {
  const newState = (handler.dataset[HANDLER_DATA_ATTR] === _FALSE) ? _TRUE : _FALSE;
  setBranchState(handler, newState);
  updateSessionStorage();
}

// Toggle all nested branches below a node in one action.
function bulkToggleChildBrunches(handler) {
  const newState = (handler.dataset[HANDLER_DATA_ATTR] === _FALSE) ? _TRUE : _FALSE;
  const list = handler.parentNode.querySelectorAll(`[data-${HANDLER_DATA_ATTR}]`);
  list.forEach(handler => {
    setBranchState(handler, newState);
  });
  updateSessionStorage();
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

// Inject the CSS that draws toggle controls and shows/hides child lists.
function addStyleElement(target, styleTextContent, attr = 'style') {
  const style = document.createElement('style');
  style.setAttribute(`collapsible-toc-${attr}`, '');
  style.textContent = styleTextContent;
  target.before(style);
}

// Keep handler and branch state in sync (expanded/collapsed).
function setBranchState(handler, state) {
  handler.dataset[HANDLER_DATA_ATTR] = state;
  handler.parentNode.dataset[BRANCH_DATA_ATTR] = state;
}

// Create a clickable handler element for one TOC branch.
function createHandler(state) {
  const div = document.createElement('div');
  state && setBranchState(item, state);
  return div
}

// Bootstrapping: run main after page load.
window.addEventListener("load", function() {
  main();
}, false);
