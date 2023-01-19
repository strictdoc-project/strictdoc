// To collapse and expand TOC branches

import { Controller } from "/_static/stimulus.js";

const controlSelector = '#toc_control';
const listSelector = '#toc';

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
    this.registerListEvents();
    // console.log(this.element)
  }

  registerListEvents(params) {
    const style = document.createElement('style');
    style.textContent = STYLE;
    this.element.prepend(style);

    //*

    const tocList = processList(listSelector);

    if (tocList.length > 0) {
      const tocControl = document.querySelector(controlSelector);
      tocControl.classList.add("collapsible_list");
      tocControl.style = '';

      const tocExpandAll = document.createElement('div');
      tocExpandAll.dataset.collapsible_list__handler = '＋';
      tocExpandAll.title = 'Expand all lines in TOC';
      tocExpandAll.addEventListener('click', () => {
        expandAllInList(tocList)
      });

      const tocCollapseAll = document.createElement('div');
      tocCollapseAll.dataset.collapsible_list__handler = '－';
      tocCollapseAll.title = 'Collapse all lines in TOC';
      tocCollapseAll.addEventListener('click', () => {
        collapseAllInList(tocList)
      });

      tocControl.append(tocExpandAll, tocCollapseAll);
    }
  }
});

function processList(selector) {

  const tocContainer = document.querySelector(selector);
  const ulList = [...tocContainer.querySelectorAll('ul')];
  const ulHandlerList = ulList.map(
    ul => {
      const parent = ul.parentNode;
      const ulHandler = document.createElement('div');
      ulHandler.dataset.collapsible_list__branch = '0';
      parent.insertBefore(ulHandler, ul);
      // Required:
      parent.style = "position:relative";

      ulHandler.addEventListener('click', () => {
        ulHandler.dataset.collapsible_list__branch = (ulHandler.dataset.collapsible_list__branch === '1') ? '0' : '1';
      });

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
