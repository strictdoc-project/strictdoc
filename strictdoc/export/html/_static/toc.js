
// **
// Place this code right after the opening BODY tag:

// <script>document.body.dataset.toc_state = sessionStorage.getItem('tocState') || 'open';</script>

// This ensures that the status of the sidebar is preserved when the page is reloaded.
// **

let setTocState = sessionStorage.getItem('tocState');
sessionStorage.setItem('tocState', (setTocState ? setTocState : 'open'));

function switchTOC() {
  sessionStorage.setItem('tocState', (
    sessionStorage.getItem('tocState') === 'open'
      ? 'close'
      : 'open'
  ));
  document.body.dataset.toc_state = sessionStorage.getItem('tocState');
}

// To collapse and expand TOC branches:

function processTOC(selector) {

  const tocContainer = document.querySelector(selector);
  const ulList = [...tocContainer.querySelectorAll('ul')];

  console.log(ulList);

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

window.addEventListener("load",function(){
  document.body.dataset.toc_state = sessionStorage.getItem('tocState');
  document.getElementById('toc_handler').addEventListener('click', () => {
    switchTOC();
  });

  const tocHandlerList = processTOC('.toc');
  document.getElementById('toc_collapse_all').addEventListener('click', () => {
    collapseAllInList(tocHandlerList)
  });
  document.getElementById('toc_expand_all').addEventListener('click', () => {
    expandAllInList(tocHandlerList)
  });

},false);
