


// Expected:
// js-resizable_bar="tree"
// data-state="open"
// data-position="left"

// ! Right now, the code only considers one possibility for the panels
// ! to the left of the main part.

class ResizableBar {
  constructor({
    barAttribute,
    barGravity,
    barMaxWidthVW,
    // styles
    barMinWidth,
    barClosedWidth,
    barHandlerWidth,
    barColorMain,
    barColorBackground,
    barColorActive,
    barColorBorder,
  }) {
    this.barAttribute = barAttribute || 'js-resizable_bar';
    this.barMaxWidthVW = barMaxWidthVW || '25vw';
    this.barGravity = barGravity || 100;
    // styles
    this.barMinWidth = barMinWidth || 100;
    this.barClosedWidth = barClosedWidth || 12;
    this.barHandlerWidth = barHandlerWidth || 8;
    this.barColorMain = barColorMain || 'var(--color-fg-main, Black)';
    this.barColorBackground = barColorBackground || 'var(--color-bg-main, White)';
    this.barColorActive = barColorActive || 'var(--color-fg-accent, currentColor)';
    this.barColorBorder = barColorBorder || 'var(--color-border, rgba(0,0,0,0.1))';

    // state
    this.state = [];

    // current
    this.activeID = null;
    this.pageX = null;

    // subscribe
    const _this = this;
    this._mouseDownHandler = (e) => {_this._onMouseDown(e)};
    this._mouseMoveHandler = (e) => {_this._onMouseMove(e)};
    this._mouseUpHandler = (e) => {_this._onMouseUp(e)};
    this._toggleHandler = (e) => {_this._toggle(e)};
  }

  init() {
    this._insertStyle();
    this._renderBars();
  }

  _setState({
    id,
    element,
    state,
    position,
    width,
  }) {
    this.state[id] = {
      element: element,
      state: state,
      position: position,
      width: width,
    };
  }

  _updateState({
    id,
    element,
    state,
    position,
    width,
  }) {
    console.assert(id, '_updateState(): ID must be provided');
    if (!this.state[id]) { this.state[id] = {} }

    if(element) { this.state[id].element = element; }
    if(state) { this.state[id].state = state; }
    if(position) { this.state[id].position = position; }
    if(width) { this.state[id].width = width; }
  }

  _updateBar(id) {
    const bar = this.state[id].element;
    const barState = this.state[id];
    bar.style.width = barState.width + 'px';
    bar.dataset.position = barState.position;
    bar.dataset.state = barState.state;
  }

  _renderBars() {
    [...document.querySelectorAll(`[${this.barAttribute}]`)]
    .forEach((bar) => {
      const id = bar.getAttribute(this.barAttribute);

      // READ DATA FROM STORAGE
      // AND SET TO STATE:

      this._setState({
        id: id,
        element: bar,
        state: bar.dataset.state,
        position: bar.dataset.position,
        width: bar.offsetWidth,
      })

      // TODO AND UPDATE BAR WITH DATA FROM STORAGE
      // this._updateState({ id: id, width: 123 });
      // this._updateBar(id);

      // Check if there is a scrollable element
      let wrapper = bar.querySelector(`${this.barAttribute}-scroll`);
      if(wrapper) {
        console.log('wrapper is here')
      } else {
        wrapper = this._createScrollableWrapper(id);
        [ ...bar.childNodes ].forEach(child => wrapper.appendChild(child));
        bar.appendChild(wrapper);
      }

      bar.append(this._createHandler(id));
    });
  }

  _createHandler(id) {
    const handler = document.createElement('div');
    handler.setAttribute(`${this.barAttribute}-handler`, '');
    handler.dataset.content = id;
    handler.style[this.state[id].position] = 'unset'; // 'left | right'

    const border = document.createElement('div');
    border.setAttribute(`${this.barAttribute}-border`, '');
    border.dataset.content = id;
    border.title = `Resize ${id}`;
    border.addEventListener('mousedown', this._mouseDownHandler);

    const button = document.createElement('div');
    button.setAttribute(`${this.barAttribute}-button`, '');
    button.dataset.content = id;
    button.title = `Toggle ${id}`;
    button.addEventListener('mousedown', this._toggleHandler);

    handler.append(border, button);
    return handler;
  }

  _createScrollableWrapper(id, direction = 'y') {
    const wrapper = document.createElement('div');
    wrapper.setAttribute(`${this.barAttribute}-scroll`, direction);
    wrapper.dataset.content = id;
    return wrapper;
  }

  _insertStyle() {
    const style = document.createElement('style');
    style.setAttribute(`${this.barAttribute}-style`, '');
    style.textContent = this._style();
    document.head.append(style);
  }

  _style() {
    return `
[${this.barAttribute}]::after {
  opacity: 0;
  transition: .3s;
  pointer-events: none;
}

[${this.barAttribute}] {
  position: relative;
  height: 100%;
  max-width: ${this.barMaxWidthVW};
}

[${this.barAttribute}]:hover {
  z-index: 22;
}

[${this.barAttribute}][data-state="open"] {
  min-width: ${this.barMinWidth}px;
  pointer-events: auto;
}
[${this.barAttribute}][data-state="closed"] {
  max-width: ${this.barClosedWidth}px;
  min-width: ${this.barClosedWidth}px;
  pointer-events: none;
  transition: .5s;
}

[${this.barAttribute}][data-position="left"] {
  border-left: none;
}
[${this.barAttribute}][data-position="right"] {
  border-right: none;
}

[${this.barAttribute}-handler] {
  pointer-events: auto;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 10;
  width: ${this.barHandlerWidth}px;
  color: ${this.barColorActive};
}

[${this.barAttribute}-border] {
  pointer-events: auto;
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  width: ${this.barHandlerWidth}px;
  background: transparent;
  transition: .3s;
  cursor: col-resize;
}

[${this.barAttribute}][data-state="closed"] [${this.barAttribute}-border] {
  cursor: e-resize;
}

[${this.barAttribute}-border]::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  width: 1px;
  background: ${this.barColorBorder};
  transition: .3s;
}

[${this.barAttribute}-border]::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  width: ${0.5 * this.barHandlerWidth}px;
  background: transparent;
  transition: .3s;
}

[${this.barAttribute}][data-position="left"] [${this.barAttribute}-border]::before {
  right: 0;
  left: unset;
}
[${this.barAttribute}][data-position="left"] [${this.barAttribute}-border]::after {
  right: ${-0.25 * this.barHandlerWidth}px;
  left: unset;
}

[${this.barAttribute}][data-position="right"] [${this.barAttribute}-border]::before {
  right: unset;
  left: 0;
}
[${this.barAttribute}][data-position="right"] [${this.barAttribute}-border]::after {
  right: unset;
  left: ${-0.25 * this.barHandlerWidth}px;
}

[${this.barAttribute}-border]:hover::after {
  background: ${this.barColorActive};
}

[${this.barAttribute}-button] {
  cursor: pointer;
  position: absolute;
  z-index: 2;
  left: 0;
  top: ${-1 * this.barHandlerWidth}px;
  box-sizing: border-box;
  width: ${2 * this.barHandlerWidth}px;
  height: ${2 * this.barHandlerWidth}px;
  font-size: ${1.5 * this.barHandlerWidth}px;
  font-weight: bold;
  border-radius: 50%;
  border-width: 1px;
  border-style: solid;
  border-color: ${this.barColorBackground};
  background: ${this.barColorBackground};
  color: ${this.barColorActive};
  transition: .3s;
}

[${this.barAttribute}-button]:hover {
  color: ${this.barColorMain};
  border-color: ${this.barColorMain};
}

/* ❮❯ */
[${this.barAttribute}-button]::after {
  content: '❮';
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  left: 0;
  right: 0;
  top: ${-1 * this.barHandlerWidth}px;
  bottom: ${-1 * this.barHandlerWidth}px;
}
[${this.barAttribute}][data-state="open"] [${this.barAttribute}-button]::after {
  content: '❮';
}
[${this.barAttribute}][data-state="closed"] [${this.barAttribute}-button]::after {
  content: '❯';
}

[${this.barAttribute}-scroll] {
  height: 100%;
  overflow-x: hidden;
  overflow-y: scroll;
  padding: calc(var(--base-rhythm)*2);
  padding-bottom: calc(var(--base-rhythm)*8);
  scrollbar-color: transparent var(--scrollbarBG);
  /* scrollbar-width: thin; */
}
[${this.barAttribute}-scroll='y'] {
  overflow-x: hidden;
  overflow-y: scroll;
}
[${this.barAttribute}-scroll]:hover {
  scrollbar-color: var(--thumbBG) var(--scrollbarBG);
}
[${this.barAttribute}-scroll]::-webkit-scrollbar {
  /* width: var(--base-rhythm); */
}
[${this.barAttribute}-scroll]::-webkit-scrollbar-thumb {
  background-color: transparent;
}
[${this.barAttribute}-scroll]:hover::-webkit-scrollbar-thumb {
  background-color: var(--thumbBG)
}

[data-state="closed"] [${this.barAttribute}-scroll] {
  display: none;
}
    `;
  }

  _updateCurrents(e) {
    if (e.type == "mousedown") {
      // When we start a new resize, we update the currents:
      this.activeID = e.target.dataset.content;
      this.pageX = e.pageX;
      // When we start a new resize, we take the current width of the element:
      this.state[this.activeID].width = this.state[this.activeID].element.offsetWidth;
    } else {
      // e.type == "mouseup"
      // At the end of the resize:
      this.activeID = null;
      this.pageX = null;
      // We leave the last adjusted width,
      // * this.state[this.activeID].width
      // and if the panel is opened/closed with a button,
      // this adjusted width will be used.
    }
  }

  _onMouseDown(e) {
    // Init resizing
    if(e.button == 0) {
      e.preventDefault();
      this._updateCurrents(e);
      window.addEventListener('mousemove', this._mouseMoveHandler);
      window.addEventListener('mouseup', this._mouseUpHandler);
    }
  }

  _toggle(e) {
    if(e.button == 0) {
      const id = e.target.dataset.content;
      this.state[id].state = this.state[id].state === 'open'
        ? 'closed'
        : 'open';
      this._updateBar(id);
    }
  }

  _open(id) {
    this.state[id].state = 'open';
    this._updateBar(id);
  }

  _close(id) {
    this.state[id].state = 'closed';
    this._updateBar(id);
  }

  _onMouseMove(e) {
    // Resizing
    requestAnimationFrame(() => {
      if(this.activeID) {
        const delta = e.pageX - this.pageX;
        const w = this.state[this.activeID].width + delta;

        this.state[this.activeID].element.style.width = w + 'px';

        if(w < this.barGravity) {
          if(this.state[this.activeID].state == 'open') {
            this._close(this.activeID);
          }
        } else {
          if(this.state[this.activeID].state == 'closed') {
            this._open(this.activeID);
          }
        }

      }
    })
  }

  _onMouseUp(e) {
    // Clean up after work
    window.removeEventListener('mousemove', this._mouseMoveHandler);
    window.removeEventListener('mouseup', this._mouseUpHandler);

    const currentWidth = this.state[this.activeID].element.offsetWidth;
    this._updateState({ id: this.activeID, width: currentWidth });
    this._updateBar(this.activeID);
    this._updateCurrents(e);

    // WRITE DATA TO STORAGE!
  }
}

const resizableBar = new ResizableBar({});

window.addEventListener("load", function () {
  resizableBar.init();
});
