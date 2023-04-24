// To collapse and expand TOC branches

import { Controller } from "/_static/stimulus.js";

const ROOT_SELECTOR = '[js-collapsible_list]';
const LIST_SELECTOR = '[js-collapsible_list="list"]';
const LIST_DEFAULT = 0;

const STYLE = `
[data-collapsible_list__branch] {
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

[data-collapsible_list__branch]:hover {
  border: 1px solid rgba(0, 0, 0, 0.15);
  box-shadow: rgb(0 0 0 / 15%) 0px 2px var(--base-rhythm) 0px;
  color: rgba(0,0,0,1);
}

.toc [data-collapsible_list__branch='1']::before {
  content: '＋';
}

.toc [data-collapsible_list__branch='0']::before {
  content: '－';
}

[data-collapsible_list__branch='1'] + ul {
  height: 0;
  overflow: hidden;
}

[data-collapsible_list__branch='0'] + ul {
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
      processList(branchList, probablyHasScroll(listElement));
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

function hasScroll(target) {
  // Check if a fully open list makes a scroll for its container.
  // *
  // The calculation assumes that `target` is a wrapping element with a scroll.
  // This element is added by another script.
  // We cannot guarantee that this item will be ready at the time the script runs.
  // That's why we do another function probablyHasScroll() as a temporary solution.
  return target.scrollHeight > target.clientHeight;
}

function probablyHasScroll(target) {
  // Check if a fully open list makes a scroll for its container.
  // Expect the target to be a content element
  // (unlike the first function hasScroll(target)).
  // The estimated height, which will not generate scrolling, is taken approximately.
  const temporarySolution = document.body.clientHeight - 100;  // 48 - 32 - 16 ...
  return target.scrollHeight > temporarySolution;
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

function processList(list, hasScroll = true) {
  // This defines how a document is opened:
  // with a collapsed or expanded TOC.
  const storage = sessionStorage.getItem('collapsibleToc');
  console.log(storage);

  // If there is no information in the storage,
  // we end up in the default case and use hasScroll.
  // If the fully open list is long enough and creates a scroll,
  // for its container, we collapse all branches (Each one gets '1').
  // Otherwise it is not necessary and we leave branches expanded ('0').
  const initState = storage || (hasScroll ? '1' : '0');

  list.forEach(item => {
    item.dataset.collapsible_list__branch = initState;

    // add event listeners
    item.addEventListener('click', () => {
      const state = item.dataset.collapsible_list__branch;
      const next = (state === '1') ? '0' : '1';
      item.dataset.collapsible_list__branch = next;
    });
    item.addEventListener('dblclick', () => {
      const state = item.dataset.collapsible_list__branch;
      const next = (state === '1') ? '0' : '1';
      // Add last bulk to local storage:
      sessionStorage.setItem('collapsibleToc', next);
      list.forEach(el => el.dataset.collapsible_list__branch = next);
    });
  })
}
