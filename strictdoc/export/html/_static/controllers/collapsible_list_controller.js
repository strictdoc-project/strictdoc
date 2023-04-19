// To collapse and expand TOC branches

import { Controller } from "/_static/stimulus.js";

const ROOT_SELECTOR = '[js-collapsible_list]';
const LIST_SELECTOR = '[js-collapsible_list="list"]';
const CONTAINER_SELECTOR = '[js-collapsible_list="container"]';

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

  constructor(...args) {
    super(...args);
    this.firstRun = false
  }

  connect() {
    // Stimulus watches the page for changes asynchronously using
    // the DOM MutationObserver API.
    // **
    // We need to know if the target will have scrolling.
    // The necessary calculations must be done when the DOM elements
    // are already loaded.
    // However, Stimulus loads too early and for our target its height
    // is calculated incorrectly, as the styles are not yet in effect,
    // even though the target already exists in the DOM.
    // **
    // There has also been a problem with lagged styles:
    // (this is not the case in Firefox and Safari):
    // the CSS added in addStyleElement(),
    // which sets `height: 0;` for the collapsed branch,
    // are present and visible in the inspector,
    // but don't affect the display of elements in the DOM.
    // We also call addStyleElement() in connect() after the rest
    // of the DOM manipulation, which provides the additional ensure
    // that the block styles will be re-rendered in Chrome
    // with these styles enabled.
    // **
    // This is eliminated by a timeout of 100 milliseconds.
    // Also by forcing a delay in triggering Stimulus before the LOAD event.
    // ** This prevents operation in regular asynchronous mode.
    // ** That is why there is also a hack with a flag 'firstRun'.

    const renderCall = (event) => {
      this.render();
      this.firstRun = true;
      window.removeEventListener("load", renderCall);
    };
    window.addEventListener("load", renderCall);

    !this.firstRun && this.render();

  }

  render() {
    // `this` element is the same as what we get on ROOT_SELECTOR
    const containerElement = document.querySelector(CONTAINER_SELECTOR);
    const listElement = document.querySelector(LIST_SELECTOR);

    // Processes the list and makes it collapse, if that makes sense
    // (if the expanded list was long and would cause scrolling).
    // Returns the processed list.
    const branchList = prepareList(listElement);

    // Do it if that makes sense (if there are branches
    // in the list that could in principle be collapsible):
    if (branchList.length > 0) {
      processList(branchList, hasScroll(containerElement));
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
  return target.scrollHeight > target.clientHeight;
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
  list.forEach(item => {
    item.addEventListener('click', () => {
      const state = item.dataset.collapsible_list__branch;
      item.dataset.collapsible_list__branch = (state === '1') ? '0' : '1';
    });
    item.addEventListener('dblclick', () => {
      const state = item.dataset.collapsible_list__branch;
      // TODO: ADD last bulk to local storage
      list.forEach(
        el => el.dataset.collapsible_list__branch = (state === '1') ? '0' : '1'
      );
    });

      // This defines how a document is opened:
      // with a collapsed or expanded TOC.
      // TODO: We may want to read/write this from/to a session at some point.
      // TODO: READ last bulk FROM local storage

      // If the fully open list is long enough and creates a scroll,
      // for its container, we collapse all branches (Each one gets '1').
      // Otherwise it is not necessary and we leave branches expanded ('0').
      item.dataset.collapsible_list__branch = hasScroll ? '1' : '0';
  })
}
