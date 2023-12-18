window.addEventListener("load",function(){

    const root = document.querySelector('#diff_result');
    console.log([root]);

    var observer = new MutationObserver(function (mutationsList, observer) {
      console.log([root], 'updated');

      prepareBulkButtons(root);
      syncDiff(root);

      // Disable the observer after the first trigger
      // because the functions modify the elements inside the #diff_result.
      observer.disconnect();
    });

    observer.observe(
      root,
      {
        childList: true,
        subtree: true
      }
    );

},false);

function prepareBulkButtons(root) {
  console.log('prepareBulkButtons');

  const leftColumn = document.querySelector('.diff_column[left]');
  const rightColumn = document.querySelector('.diff_column[right]');

  const leftOpenBtn = document.getElementById('diff_left_open');
  const leftCloseBtn = document.getElementById('diff_left_close');
  const rightOpenBtn = document.getElementById('diff_right_open');
  const rightCloseBtn = document.getElementById('diff_right_close');

  const detailsLeftAll = [...leftColumn.querySelectorAll('details')];
  const detailsRightAll = [...rightColumn.querySelectorAll('details')];
  const detailsLeft = [...leftColumn.querySelectorAll('details[modified]')];
  const detailsRight = [...rightColumn.querySelectorAll('details[modified]')];

  leftOpenBtn.addEventListener("click", (event) => {
    event.preventDefault();
    _openAll(detailsLeft);
  });
  leftCloseBtn.addEventListener("click", (event) => {
    event.preventDefault();
    _closeAll(detailsLeftAll);
  });
  rightOpenBtn.addEventListener("click", (event) => {
    event.preventDefault();
    _openAll(detailsRight);
  });
  rightCloseBtn.addEventListener("click", (event) => {
    event.preventDefault();
    _closeAll(detailsRightAll);
  });
}

function syncDiff(root) {
  console.log('syncDiff');

  const sync = [...root.querySelectorAll('button[uid]')]
  .reduce((acc, curr) => {
    const uid = curr.getAttribute('uid');
    const side = curr.getAttribute('side');
    acc[uid] = {
      [side]: curr,
      ...acc[uid]
    }
    return acc
  },{});

  Object.entries(sync).forEach(([uid, obj]) => {
    if (!obj.left) {
      obj.right.remove()
      return
    };

    if (!obj.right) {
      obj.left.remove()
      return
    };

    obj.left.addEventListener("click", (event) => {
      event.preventDefault();

      // _openAll(detailsLeftAll);
      _openAncestors(obj.left, root);
      _scrollTo(obj.left);

      setTimeout(() => {
        // _openAll(detailsRightAll);
        _openAncestors(obj.right, root);
        _scrollTo(obj.right);
      }, 900);
    });

    obj.right.addEventListener("click", (event) => {
      event.preventDefault();

      // _openAll(detailsRightAll);
      _openAncestors(obj.right, root);
      _scrollTo(obj.right);

      setTimeout(() => {
        // _openAll(detailsLeftAll);
        _openAncestors(obj.left, root);
        _scrollTo(obj.left);
      }, 900);
    });
  })
};

function _openAncestors(element, root) {

  let currentElement = element;

  while (currentElement && currentElement !== root) {
    currentElement = currentElement.parentElement;

    if (currentElement && currentElement.tagName === 'DETAILS') {
      currentElement.setAttribute('open', '');
    }
  }
};

function _scrollTo(target) {
  // We insert a special element into the button ('button[uid]')
  // that compensates by 40 pixels
  // for the height of the sticky header
  // at the top of the scroll container:
  // ***
  // <a-a style="position:absolute;top:-40px;"></a-a>

  const a = target.querySelector('a-a') || target;
  a.scrollIntoView({ behavior: "smooth" });
};

function _closeAll(details) {
  details.forEach(detail => {
    detail.removeAttribute("open")
  });
};

function _openAll(details) {
  details.forEach(detail => {
    detail.setAttribute("open", "")
  });
};
