Stimulus.register("diff", class extends Controller {
  initialize() {

    // * fragment collapse control

    const leftColumn = this.element.querySelector('.diff_column[left]');
    const rightColumn = this.element.querySelector('.diff_column[right]');

    const leftOpenBtn = document.getElementById('diff_left_open');
    const leftCloseBtn = document.getElementById('diff_left_close');
    const rightOpenBtn = document.getElementById('diff_right_open');
    const rightCloseBtn = document.getElementById('diff_right_close');

    const detailsLeftAll = [...leftColumn.querySelectorAll('details')];
    const detailsRightAll = [...rightColumn.querySelectorAll('details')];
    const detailsLeft = [...leftColumn.querySelectorAll('details[modified]')];
    const detailsRight = [...rightColumn.querySelectorAll('details[modified]')];

    // Add event listener
    leftOpenBtn.addEventListener("click", (event) => {
      event.preventDefault();
      this._openAll(detailsLeft);
    });
    leftCloseBtn.addEventListener("click", (event) => {
      event.preventDefault();
      this._closeAll(detailsLeftAll);
    });
    rightOpenBtn.addEventListener("click", (event) => {
      event.preventDefault();
      this._openAll(detailsRight);
    });
    rightCloseBtn.addEventListener("click", (event) => {
      event.preventDefault();
      this._closeAll(detailsRightAll);
    });

    // * sync

    const sync = [...this.element.querySelectorAll('button[uid]')]
    .reduce((acc, curr) => {
      const uid = curr.getAttribute('uid');
      const side = curr.getAttribute('side');
      acc[uid] = {
        [side]: curr,
        ...acc[uid]
      }
      return acc
    },{});

    Object.entries(sync)
    .forEach(([uid, obj]) => {
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

        // this._openAll(detailsRightAll);
        this._openAncestors(obj.right)
        this._scroll(obj.right);

        setTimeout(() => {
          // this._openAll(detailsLeftAll);
          this._openAncestors(obj.left)
          this._scroll(obj.left);
        }, 900);
      });

      obj.right.addEventListener("click", (event) => {
        event.preventDefault();

        // this._openAll(detailsLeftAll);
        this._openAncestors(obj.left)
        this._scroll(obj.left);

        setTimeout(() => {
          // this._openAll(detailsRightAll);
          this._openAncestors(obj.right)
          this._scroll(obj.right);
        }, 900);
      });
    })
  }

  _openAncestors(element) {
    let currentElement = element;

    while (currentElement && currentElement !== this.element) {
      currentElement = currentElement.parentElement;

      if (currentElement && currentElement.tagName === 'DETAILS') {
        currentElement.setAttribute('open', '');
      }
    }
  }

  _scroll(target) {
    // We insert a special element into the button ('button[uid]')
    // that compensates by 40 pixels
    // for the height of the sticky header
    // at the top of the scroll container:
    // ***
    // <a-a style="position:absolute;top:-40px;"></a-a>

    const a = target.querySelector('a-a') || target;
    a.scrollIntoView({ behavior: "smooth" });
  }

  _closeAll(details) {
    details.forEach(detail => {
      detail.removeAttribute("open")
    });
  }

  _openAll(details) {
    details.forEach(detail => {
      detail.setAttribute("open", "")
    });
  }
});
