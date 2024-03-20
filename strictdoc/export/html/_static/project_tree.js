const FRAME_SELECTOR = '#frame_project_tree';
const SWITCH_SELECTOR = '#project_tree_controls';
const FRAGMENT_ATTR = 'included-document';
const FRAGMENT_SELECTOR = `.project_tree-file[${FRAGMENT_ATTR}]`;

// This class Switch was taken
// from strictdoc/export/html/_static/source-code-coverage.js
// and improved a bit:
class Switch {
  constructor({
    callback,
    labelText,
    checked,
    componentClass,
    colorOn,
    colorOff,
    size,
    stroke,
    units,
    position,
    topPosition,
    leftPosition,
    rightPosition,
    bottomPosition,
  }) {
    this.colorOn = colorOn || 'rgb(242, 100, 42)';
    this.colorOff = colorOff || 'rgb(200, 200, 200)';
    this.labelInitialText = labelText || '';
    this.checked = (checked === false) ? false : true;

    this.componentClass = componentClass || 'std-switch-scc';
    this.size = size || 0.75;
    this.stroke = stroke || 0.25;
    this.units = units || 'rem';

    this.topPosition = topPosition || 'unset',
    this.leftPosition = leftPosition || 'unset',
    this.rightPosition = rightPosition || 'unset',
    this.bottomPosition = bottomPosition || 'unset',
    this.position = position || 'static',

    this.controlLabelTextSpan = document.createElement('span');
    this.callback = callback;
  }

  create() {
    const block = document.createElement('div');
    block.classList.add(this.componentClass);
    const label = document.createElement('label');
    label.classList.add(`${this.componentClass}__label`);
    const input = document.createElement('input');
    input.classList.add(`${this.componentClass}__input`);
    input.type = 'checkbox';
    input.checked = this.checked;
    const slider = document.createElement('span');
    slider.classList.add(`${this.componentClass}__slider`);

    label.append(input, slider, this.controlLabelTextSpan);
    block.append(label);

    this.insertStyle();
    this.updateLabelText(this.labelInitialText);
    input.addEventListener('change', () => this.callback(input.checked));

    return block;
  }

  updateLabelText(text) {
    this.controlLabelTextSpan.innerHTML = text;
  }

  insertStyle() {

    const css = `
    .${this.componentClass} {
      display: inline-block;
      line-height: 0;
      position: ${this.position};
      top: ${this.topPosition};
      left: ${this.leftPosition};
      right: ${this.rightPosition};
      bottom: ${this.bottomPosition};
    }
    .${this.componentClass}__label {
      display: inline-flex;
      column-gap: 8px;
      line-height: ${this.size * 1.6}${this.units};
      line-height: 1.25;
      align-items: flex-start;
      justify-content: flex-start;
      user-select: none;
      cursor: pointer;
      font-size: small;
    }
    .${this.componentClass}__input {
      opacity: 0;
      width: 0;
      height: 0;
      position: absolute;
    }
    .${this.componentClass}__slider {
      position: relative;
      cursor: pointer;
      background-color: ${this.colorOff};
      -webkit-transition: .4s;
      transition: .4s;
      display: inline-block;
      width: ${this.size * 2 + this.stroke * 2}${this.units};
      min-width: ${this.size * 2 + this.stroke * 2}${this.units};
      height: ${this.size + this.stroke * 2}${this.units};
      margin-right: ${this.size * 0.5}${this.units};
      border-radius: ${this.size * 0.5 + this.stroke}${this.units};
    }
    .${this.componentClass}__slider::before  {
      position: absolute;
      content: "";
      height: ${this.size}${this.units};
      width: ${this.size}${this.units};
      left: ${this.stroke}${this.units};
      bottom: ${this.stroke}${this.units};
      background-color: white;
      -webkit-transition: .4s;
      transition: .4s;
      border-radius: 50%;
    }
    input:checked + .${this.componentClass}__slider {
      background-color: ${this.colorOn};
    }
    input:focus + .${this.componentClass}__slider {
      box-shadow: 0 0 1px ${this.colorOn};
    }
    input:checked + .${this.componentClass}__slider::before {
      -webkit-transform: translateX(${this.size}${this.units});
      -ms-transform: translateX(${this.size}${this.units});
      transform: translateX(${this.size}${this.units});
    }
    `;

    const head = document.querySelector('head');
    const style = document.createElement('style');
    style.append(document.createTextNode(css));
    style.setAttribute("data-slider-styles", '');
    head.append(style);
  }

}

class ProjectTree {
  constructor({
    mutatingFrame,
    controlTarget
  }) {
    this.mutatingFrame = mutatingFrame;
    this.controlTarget = controlTarget;
    this.fragments = [];

    this.control;
    this.controlElement;
    this.controlElementDisplayInitial;

    this.state = {
      fragmentVisibility: {
        _sessionStorageItemName: 'projectTreeFragmentVisibility',
        initial: 'hide',
        current: null,
      }
    };
  }

  __testStorage() {
    const testStorage = this._getSessionStorageItem();
    console.log(testStorage);
  }

  init() {
    console.log('First time call.');

    console.assert(this.mutatingFrame, `mutatingFrame not found on the page`);
    this._addMutationObserver();

    this._initStateAndStorage();
    this.__testStorage();

    console.assert(this.controlTarget, `controlTarget not found on the page`);
    this.control = this._addControl();

    this.updateFragmentsAndControl();
  }

  getCurrentFragmentVisibilityBool() {
    console.log('getCurrentFragmentVisibilityBool', this.state.fragmentVisibility.current)
    return (this.state.fragmentVisibility.current === 'show') ? true : false;
  }

  updateFragmentsAndControl() {
    this.fragments = this._getFragments();
    this._updateControl(this.fragments.length);
    this._updateFragmentsVisibility(this.getCurrentFragmentVisibilityBool());
  }

  _getFragments() {
    const fragments = [...this.mutatingFrame.querySelectorAll(FRAGMENT_SELECTOR)];
    // this._prepareFragmentsFoldersAndNeighbors(fragments);
    return fragments;
  }

  _prepareFragmentsFoldersAndNeighbors(fragments) {
    // ul > li > .std-tree_row
    // .std-tree_row === fragment
    const folders = new Set();
    this.fragments.forEach(element => {
      element.style.display = display;
    })
  }

  _updateFragmentsVisibility(bool) {
    const display = bool ? '' : 'none';
    this.fragments.forEach(element => {
      element.style.display = display;
    })
  }

  _updateControl(num) {
    this.control.updateLabelText(`<b>Show ${num} fragment${num > 1 ? 's' : ''}</b> included in&nbsp;other documents in the Project document tree.`)

    if (num) {
      console.log('this.fragments.length', num);
      this.controlElement.style.display = this.controlElementDisplayInitial;
    } else {
      this.controlElement.style.display = 'none';
    }
  }

  toggleFragmentsVisibility(checked) {
    this._updateFragmentsVisibility(checked);

    if (checked) {
      this._updateCurrentState('show', 'fragmentVisibility');
      this._setSessionStorageItem('show', 'fragmentVisibility');
      this.__testStorage();
    } else {
      this._updateCurrentState('hide', 'fragmentVisibility');
      this._setSessionStorageItem('hide', 'fragmentVisibility');
      this.__testStorage();
    }
  }

  _initStateAndStorage(option = 'fragmentVisibility') {
    const storage = this._getSessionStorageItem(option);

    if (storage) {
      this._updateCurrentState(storage);
    } else {
      this._updateCurrentState(this.state[option].initial);
      this._setSessionStorageItem(this.state[option].initial);
    }
  }

  _updateCurrentState(value, option = 'fragmentVisibility') {
    this.state[option].current = value;
  }

  _setSessionStorageItem(nextState, option = 'fragmentVisibility') {
    sessionStorage.setItem(this.state[option]._sessionStorageItemName, nextState);
  }

  _getSessionStorageItem(option = 'fragmentVisibility') {
    const storage = sessionStorage.getItem(this.state[option]._sessionStorageItemName);
    return storage;
  }

  _addControl() {
    const control = new Switch(
      {
        labelText: `<b>Show fragments</b>`, // * This text will be updated later.
        size: 0.5,
        stroke: 0.175,
        // position: 'absolute',
        // topPosition: '16px',
        // leftPosition: 0,
        // checked: false,
        checked: this.getCurrentFragmentVisibilityBool(),
        callback: (checked) => this.toggleFragmentsVisibility(checked),
      }
    );

    const controlElement = control.create();
    this.controlTarget.append(controlElement);

    this.controlElement = controlElement;
    this.controlElementDisplayInitial = controlElement.style.display;
    return control
  }

  _addMutationObserver() {
    console.log('Mutation observer added for', this.mutatingFrame);

    new MutationObserver((mutationsList, observer) => {
      for (let mutation of mutationsList) {
        if (mutation.type === 'childList') {
          // When re-rendering the frame content,
          // the array of tracked elements should be updated
          // and their visibility should be set according
          // to the current settings available in the State.
          this.updateFragmentsAndControl();
        }
      }
    }).observe(
      this.mutatingFrame,
      {
        childList: true,
        // subtree: true
      }
    );
  }
}

window.addEventListener("DOMContentLoaded", function(){

  const controlTarget = document.querySelector(SWITCH_SELECTOR);
  if (!controlTarget) {
    console.error(`Selector "${SWITCH_SELECTOR}" not found on the page`);
    return;
  }
  const mutatingFrame = document.querySelector(FRAME_SELECTOR);
  if (!mutatingFrame) {
    console.error(`Selector "${FRAME_SELECTOR}" not found on the page`);
    return;
  }

  const projectTree = new ProjectTree({
    mutatingFrame,
    controlTarget
  });

  projectTree.init();

},false);
