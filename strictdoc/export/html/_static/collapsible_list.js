// To collapse and expand TOC branches

const ROOT_SELECTOR = 'js-collapsible_list';

const BRANCH_SELECTOR = `collapsible_list__branch`;
const LIST_DEFAULT = 'open';
const SYMBOL_MINUS = '－';
const SYMBOL_PLUS = '＋';
const SYMBOL_SIZE = 16;

const STYLE = `
[data-${BRANCH_SELECTOR}] {
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

[data-${BRANCH_SELECTOR}]:hover {
  border: 1px solid rgba(0, 0, 0, 0.15);
  box-shadow: rgb(0 0 0 / 15%) 0px 2px 8px 0px;
  color: rgba(0,0,0,1);
}

[data-${BRANCH_SELECTOR}='closed']::before {
  content: '${SYMBOL_PLUS}';
}

[data-${BRANCH_SELECTOR}='open']::before {
  content: '${SYMBOL_MINUS}';
}

[data-${BRANCH_SELECTOR}='closed'] ~ ul { /* Subsequent-sibling */
  display: none;
}

[data-${BRANCH_SELECTOR}='open'] ~ ul { /* Subsequent-sibling */
  display: unset;
}

[${ROOT_SELECTOR}-bulk] {
  display: flex;
  gap: 8px;
  z-index: 2;
  position: fixed;
  margin-left: ${SYMBOL_SIZE * 0.5}px;
  pointer-events: none;
  padding: 8px;
  background: #F2F5F9;
  box-shadow: #F2F5F9 0px 8px 8px 0px;
}

[${ROOT_SELECTOR}-bulk] > div {
  cursor: pointer;
  user-select: none;
  transition: .3s;
  width: ${SYMBOL_SIZE}px;
  height: ${SYMBOL_SIZE}px;
  position: relative;
  pointer-events: auto;
}

[${ROOT_SELECTOR}-bulk] > div::before {
  content: attr(data-action);
  display: flex;
  align-items: center;
  justify-content: center;
  -webkit-box-align: center;
  -webkit-box-pack: center;
  background-clip: padding-box;
  width: ${SYMBOL_SIZE}px;
  height: ${SYMBOL_SIZE}px;
  font-size: ${SYMBOL_SIZE * 0.875}px;
  font-weight: bold;
  line-height: 0;
  border-radius: 50%;
  background: #F2F5F9;
  box-shadow: rgb(0 0 0 / 10%) 0 0px 0px 1px, rgb(0 0 0 / 10%) 2px 1px 1px 0px;
  position: absolute;
  top: 0;
  left: 0;
  z-index: 2;
}

[${ROOT_SELECTOR}-bulk] > div:hover::before {
  background: #FFF;
}

[${ROOT_SELECTOR}-bulk] > div::after {
  content: '';
  width: ${SYMBOL_SIZE}px;
  height: ${SYMBOL_SIZE}px;
  border-radius: 50%;
  position: absolute;
  box-shadow: rgb(0 0 0 / 15%) 0px 0px 0px 1px;
  top: -${SYMBOL_SIZE * 0.25}px;
  left: ${SYMBOL_SIZE * 0.25}px;
  z-index: 1;
}

[${ROOT_SELECTOR}-has-bulk] {
  margin-top: 32px;
}
`;

function addStyleElement(target, styleTextContent, attr = 'style') {
  const style = document.createElement('style');
  style.setAttribute(`${ROOT_SELECTOR}-${attr}`, '');
  style.textContent = styleTextContent;
  target.before(style);
}

function prepareList(target) {
  const ulList = [...target.querySelectorAll('ul')];
  const ulHandlerList = ulList.map(
    ul => {
      const parent = ul.parentNode;
      const ulHandler = document.createElement('div');

      // parent.insertBefore(ulHandler, ul);
      // * I need the button to come before the link as well
      parent.prepend(ulHandler);
      // Required:
      parent.style = "position:relative";
      return ulHandler;
    }
  )
  return ulHandlerList;
}

function addBulkHandler(target, handler) {
  target.before(handler);
  target.setAttribute(`${ROOT_SELECTOR}-has-bulk`, '');
}

function createBulkHandler(list) {
  const bulk = document.createElement('div');
  bulk.setAttribute(`${ROOT_SELECTOR}-bulk`, '');

  const bulkPlus = document.createElement('div');
  bulkPlus.dataset.action = SYMBOL_PLUS;
  const bulkMinus = document.createElement('div');
  bulkMinus.dataset.action = SYMBOL_MINUS;

  // add event listeners
  bulkPlus.addEventListener('click', () => {
    bulkToggle(list, 'closed');
  });
  bulkMinus.addEventListener('click', () => {
    bulkToggle(list, 'open');
  });

  bulk.append(bulkPlus, bulkMinus);
  return bulk;
}

function processList(list) {
  // This defines how a document is opened:
  // with a collapsed or expanded TOC.
  const storage = sessionStorage.getItem('collapsibleToc');

  // If there is no information in the storage, we set the default list state.
  const initState = storage || LIST_DEFAULT;

  list.forEach(item => {
    item.dataset[BRANCH_SELECTOR] = initState;

    // add event listeners
    item.addEventListener('click', () => {
      toggle(item);
    });
    item.addEventListener('dblclick', () => {
      bulkToggle(list, item.dataset[BRANCH_SELECTOR]);
    });
  })
}

function toggle(item) {
  const oldState = item.dataset[BRANCH_SELECTOR];
  const nextState = (oldState === 'closed') ? 'open' : 'closed';
  item.dataset[BRANCH_SELECTOR] = nextState;
}

function bulkToggle(list, oldState) {
  const nextState = (oldState === 'closed') ? 'open' : 'closed';
  // Add last bulk to local storage:
  sessionStorage.setItem('collapsibleToc', nextState);
  // Update list:
  list.forEach(el => el.dataset[BRANCH_SELECTOR] = nextState);
}

// ******

function run() {
  const toc = document.querySelector(`[${ROOT_SELECTOR}]`);

  // Processes the list and makes it collapse, if that makes sense
  // (if the expanded list was long and would cause scrolling).
  // Returns the processed list.
  const branchList = prepareList(toc);

  // Do it if that makes sense (if there are branches
  // in the list that could in principle be collapsible):
  if (branchList.length > 0) {
    processList(branchList);
    addStyleElement(toc, STYLE);

    // Uncomment to add buttons for bulk operations:
    // addBulkHandler(listElement, createBulkHandler(branchList));
  }
}

function isCollapsibleList(node) {
  return node.nodeType === 1 && node.hasAttribute(ROOT_SELECTOR)
}

window.addEventListener("load",function(){

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
