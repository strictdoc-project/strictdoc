// To collapse and expand TOC branches

import { Controller } from "/_static/stimulus.js";

const ROOT_SELECTOR = '[js-collapsible_list]';
const CONTROLS_SELECTOR = '[js-collapsible_list-control]';
const LIST_SELECTOR = '[js-collapsible_list-list]';
const CONTAINER_SELECTOR = '[js-collapsible_list-container]';

const STYLE = `
.collapsible_list {
  display: flex;
  align-items: center;
  column-gap: 8px;
}

[data-collapsible_list__handler] {
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  cursor: pointer;
  user-select: none;
  width: 24px;
  height: 24px;
  font-size: 14px;
  font-weight: bold;
  color: rgba(0,0,0,0.5);
  transition: .3s;
}

[data-collapsible_list__handler]::before {
  content: attr(data-collapsible_list__handler);
}

[data-collapsible_list__handler]::after {
  content: attr(data-collapsible_list__handler);
  position: absolute;
  transform: translate(8px, 4px);
  opacity: .5;
}

[data-collapsible_list__handler]:hover {
  color: rgba(0,0,0,1);
}

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

  connect() {
    this.render()
  }

  render() {
    // `this` element is the same as what we get on ROOT_SELECTOR
    const controlsElement = document.querySelector(CONTROLS_SELECTOR);
    const containerElement = document.querySelector(CONTAINER_SELECTOR);
    const listElement = document.querySelector(LIST_SELECTOR);

    // Processes the list and makes it collapse, if that makes sense
    // (if the expanded list was long and would cause scrolling).
    // Returns the processed list.
    const tocList = processList(
      listElement,
      hasScroll(containerElement)
      );

    // Add controls and styles, if that makes sense (if there are branches
    // in the list that could in principle be collapsible):
    if (tocList.length > 0) {
      addBulkControls(controlsElement, tocList)
      addStyleElement(this, STYLE);
    }
  }

});

function addStyleElement(target, styleTextContent) {
  const style = document.createElement('style');
  style.textContent = styleTextContent;
  target.element.prepend(style);
}

function addBulkControls(target, tocList) {
  // Prepare container
  target.classList.add("collapsible_list");

  // Create expand all control
  const tocExpandAll = document.createElement('div');
  tocExpandAll.dataset.collapsible_list__handler = '＋';
  tocExpandAll.title = 'Expand all lines in TOC';
  tocExpandAll.addEventListener('click', () => {
    expandAllInList(tocList)
  });

  // Create collapse all control
  const tocCollapseAll = document.createElement('div');
  tocCollapseAll.dataset.collapsible_list__handler = '－';
  tocCollapseAll.title = 'Collapse all lines in TOC';
  tocCollapseAll.addEventListener('click', () => {
    collapseAllInList(tocList)
  });

  // Append controls
  target.append(tocExpandAll, tocCollapseAll);
}

function hasScroll(target) {
  // Check if a fully open list makes a scroll for its container.
  return target.scrollHeight > target.clientHeight;
}

function processList(target, hasScroll = true) {
  const ulList = [...target.querySelectorAll('ul')];
  const ulHandlerList = ulList.map(
    ul => {
      const parent = ul.parentNode;
      const ulHandler = document.createElement('div');

      parent.insertBefore(ulHandler, ul);
      // Required:
      parent.style = "position:relative";

      ulHandler.addEventListener('click', () => {
        ulHandler.dataset.collapsible_list__branch = (ulHandler.dataset.collapsible_list__branch === '1') ? '0' : '1';
      });

      // This defines how a document is opened:
      // with a collapsed or expanded TOC.
      // TODO: We may want to read/write this from/to a session at some point.

      // If the fully open list is long enough and creates a scroll,
      // for its container, we collapse all branches (Each one gets '1').
      // Otherwise it is not necessary and we leave branches expanded ('0').

      // This modification should be done at the end, so that the element
      // is sure to be re-rendered and catch the styles.
      // Otherwise, because of the strange behavior of Chrome
      // (this is not the case in Firefox and Safari):
      // the CSS added in addStyleElement(),
      // which sets `height: 0;` for the collapsed branch,
      // are present and visible in the inspector,
      // but don't affect the display of elements in the DOM.
      // We also call addStyleElement() in connect() after the rest
      // of the DOM manipulation, which provides the additional ensure
      // that the block styles will be re-rendered in Chrome
      // with these styles enabled.
      ulHandler.dataset.collapsible_list__branch = hasScroll ? '1' : '0';

      return ulHandler;
    }
  )
  return ulHandlerList;
}

function collapseAllInList(list) {
  list.forEach(el => el.dataset.collapsible_list__branch = 1)
}

function expandAllInList(list) {
  list.forEach(el => el.dataset.collapsible_list__branch = 0)
}
