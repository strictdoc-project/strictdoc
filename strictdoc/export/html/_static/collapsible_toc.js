// To collapse and expand TOC branches

const ROOT_ID = 'toc';
const SS_ITEM = 'collapsibleTOC'; // sessionStorageItem
const BRANCH_DATA_ATTR = `branch`; // li with a branch inside
const HANDLER_DATA_ATTR = `handler`; // handler
const NODE_ID_DATA_ATTR = `nodeid`; // from sdoc markup
const _TRUE = 'collapsed';
const _FALSE = 'expanded';

const ROOT_SELECTOR = 'js-collapsible_list'; // is used in tests

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

function sessionStorageGet() {
  const item = sessionStorage.getItem(SS_ITEM);
  const res = item ? JSON.parse(item) : {};
  return res
}

function sessionStorageSet(obj) {
  const string = JSON.stringify(obj);
  sessionStorage.setItem(SS_ITEM, string)
}

function updateSessionStorage() {
  const obj = {};
  document.querySelector(`[${ROOT_SELECTOR}]`)
    .querySelectorAll(`[data-${BRANCH_DATA_ATTR}]`)
    .forEach(
      branch => obj[branch.dataset[NODE_ID_DATA_ATTR]] = branch.dataset[BRANCH_DATA_ATTR]
    );
  sessionStorageSet(obj);
}

function addStyleElement(target, styleTextContent, attr = 'style') {
  const style = document.createElement('style');
  style.setAttribute(`collapsible-toc-${attr}`, '');
  style.textContent = styleTextContent;
  target.before(style);
}

function setBranchState(handler, state) {
  handler.dataset[HANDLER_DATA_ATTR] = state;
  handler.parentNode.dataset[BRANCH_DATA_ATTR] = state;
}

function createHandler(state) {
  const div = document.createElement('div');
  state && setBranchState(item, state);
  return div
}

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

        // parent.insertBefore(handler, ul);
        // * I need the button to come before the link as well
        parentNode.prepend(handler);
        // Required:
        parentNode.style = "position:relative";

        // * run after the items have been added to the DOM
        setBranchState(handler, currentState);

        // * add event listeners
        handler.addEventListener('click', () => {
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

function toggle(handler) {
  const newState = (handler.dataset[HANDLER_DATA_ATTR] === _FALSE) ? _TRUE : _FALSE;
  setBranchState(handler, newState);
  updateSessionStorage();
}

function bulkToggleChildBrunches(handler) {
  const newState = (handler.dataset[HANDLER_DATA_ATTR] === _FALSE) ? _TRUE : _FALSE;
  const list = handler.parentNode.querySelectorAll(`[data-${HANDLER_DATA_ATTR}]`);
  list.forEach(handler => {
    setBranchState(handler, newState);
  });
  updateSessionStorage();
}

// ******

function run() {
  processToc(document.querySelector(`[${ROOT_SELECTOR}]`));
}

function isCollapsibleList(node) {
  return node.nodeType === 1 && node.id === ROOT_ID
}

window.addEventListener("load", function() {

  let mutatingFrame = document.querySelector('#frame-toc');
  if (!mutatingFrame) {
    console.error("#frame-toc not found");
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

  // * Call for the first time.
  run()

},false);
