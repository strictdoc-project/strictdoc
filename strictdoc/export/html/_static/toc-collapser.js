// To collapse and expand TOC branches

import { Controller } from "/_static/stimulus.js";

Stimulus.register("tocCollapser", class extends Controller {
  static targets = ["name"];

  connect() {
    // this.element equal my element
    this.registerTOCEvents();
  }

  registerTOCEvents(params) {

    const tocHandlerList = processTOC('#toc');

    if(tocHandlerList.length > 0) {
      const tocControlDiv = document.getElementById('toc_control');
      tocControlDiv.style = '';

      const tocExpandAll = document.getElementById('toc_expand_all');
      const tocCollapseAll = document.getElementById('toc_collapse_all');

      tocCollapseAll.addEventListener('click', () => {
        collapseAllInList(tocHandlerList)
      });
      tocExpandAll.addEventListener('click', () => {
        expandAllInList(tocHandlerList)
      });
    } else {
      const tocControlDiv = document.getElementById('toc_control');
      tocControlDiv.style = 'display:none';
    }
  }
});

function processTOC(selector) {

  const tocContainer = document.querySelector(selector);
  const ulList = [...tocContainer.querySelectorAll('ul')];
  const ulHandlerList = ulList.map(
    ul => {
      const parent = ul.parentNode;
      const ulHandler = document.createElement('div');
      ulHandler.dataset.collapse = '0';
      parent.insertBefore(ulHandler, ul);

      ulHandler.addEventListener('click', () => {
        ulHandler.dataset.collapse = (ulHandler.dataset.collapse === '1') ? '0' : '1';
      });

      return ulHandler;
    }
  )
  return ulHandlerList;
}

function collapseAllInList(list) {
  list.forEach(el => el.dataset.collapse = 1)
}

function expandAllInList(list) {
  list.forEach(el => el.dataset.collapse = 0)
}
