// To collapse and expand TOC branches

import { Controller } from "/_static/stimulus.js";

const ROOT_SELECTOR = 'js-collapsible_list';
const LIST_SELECTOR = `[${ROOT_SELECTOR}="list"]`;
const BRANCH_SELECTOR = `collapsible_list__branch`;
const LIST_DEFAULT = 'open';
const SYMBOL_MINUS = '－';
const SYMBOL_PLUS = '＋';

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
  width: 16px;
  height: 16px;
  font-size: 14px;
  font-weight: bold;
  line-height: 0;
  border-radius: 50%;
  color: rgba(0,0,0,0.5);
  box-shadow: rgb(0 0 0 / 10%) 0px 1px 2px 0px;
  position: absolute;
  top: 0;
  left: -8px;
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

[data-${BRANCH_SELECTOR}='closed'] + ul {
  height: 0;
  overflow: hidden;
}

[data-${BRANCH_SELECTOR}='open'] + ul {
  height: auto;
}
`;

Stimulus.register("collapsible_list", class extends Controller {
  static targets = ["name"];

  initialize() {
    const listElement = document.querySelector(LIST_SELECTOR);
    this.render(listElement)
  }

  render(listElement) {
    // Processes the list and makes it collapse, if that makes sense
    // (if the expanded list was long and would cause scrolling).
    // Returns the processed list.
    const branchList = prepareList(listElement);

    // Do it if that makes sense (if there are branches
    // in the list that could in principle be collapsible):
    if (branchList.length > 0) {
      processList(branchList);
      addStyleElement(this.element, STYLE);
    }
  }

});

function addStyleElement(target, styleTextContent) {
  const style = document.createElement('style');
  style.setAttribute("collapsible-list-style", '');
  style.textContent = styleTextContent;
  target.prepend(style);
}

function prepareList(target) {
  const ulList = [...target.querySelectorAll('ul')];
  const ulHandlerList = ulList.map(
    ul => {
      const parent = ul.parentNode;
      const ulHandler = document.createElement('div');

      parent.insertBefore(ulHandler, ul);
      // Required:
      parent.style = "position:relative";
      return ulHandler;
    }
  )
  return ulHandlerList;
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
      const state = item.dataset[BRANCH_SELECTOR];
      const next = (state === 'closed') ? 'open' : 'closed';
      item.dataset[BRANCH_SELECTOR] = next;
    });
    item.addEventListener('dblclick', () => {
      const state = item.dataset[BRANCH_SELECTOR];
      const next = (state === 'closed') ? 'open' : 'closed';
      // Add last bulk to local storage:
      sessionStorage.setItem('collapsibleToc', next);
      list.forEach(el => el.dataset[BRANCH_SELECTOR] = next);
    });
  })
}
