//
// @relation(SDOC-SRS-53, scope=file)
//

(function () {
const FRAME_SELECTOR = '#frame_project_tree';
const SWITCH_SELECTOR = '#project_tree_controls';
const FRAGMENT_ATTR = 'included-document';
const FRAGMENT_SELECTOR = `.project_tree-file[${FRAGMENT_ATTR}]`;
const FILE_SELECTOR = `.project_tree-file`;
const FOLDER_SELECTOR = `.project_tree-folder`;

function createSwitch({ labelText, checked, dataTestID, callback }) {
  const template = document.getElementById('template-switch');
  const label = template.content.cloneNode(true).querySelector('label');
  const input = label.querySelector('input[type=checkbox]');
  const text = label.querySelector('.switch__label-text');

  text.innerHTML = labelText;
  input.checked = checked;
  input.addEventListener('change', () => callback(input.checked));
  label.setAttribute('data-testid', dataTestID);

  return { element: label, textElement: text };
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

    this.state = {
      fragmentVisibility: {
        _sessionStorageItemName: 'projectTreeFragmentVisibility',
        initial: 'hide',
        current: null,
      }
    };
  }

  init() {
    // console.log('First time call.');

    console.assert(this.mutatingFrame, `mutatingFrame not found on the page`);
    this._addMutationObserver();

    this._initStateAndStorage();

    // * this.controlTarget may not be present on the page, for example, in the case of static export.
    // console.assert(this.controlTarget, `controlTarget not found on the page`);

    this._createControl();
    this._addControl();

    this.updateFragmentsAndControl();
  }

  getCurrentFragmentVisibilityBool() {
    return (this.state.fragmentVisibility.current === 'show') ? true : false;
  }

  updateFragmentsAndControl() {
    // Update list of fragment elements (files + folders) and toggle visibility
    const fileFragments = this._getFileFragments();
    const folderFragments = this._getFoldersWithOnlyFragments();

    // Store both individual file fragments and folders that contain only fragments
    this.fragments = [...fileFragments, ...folderFragments];

    // Only show number of file fragments (folders are excluded from count)
    this._updateControl(fileFragments.length);
    this._updateFragmentsVisibility(this.getCurrentFragmentVisibilityBool());
  }

  _getFileFragments() {
    // Find all file elements that are marked as included fragments
    return [...this.mutatingFrame.querySelectorAll(FRAGMENT_SELECTOR)];
  }

  _getFoldersWithOnlyFragments() {
    // Find folders that contain only fragment files and no other files
    const folders = [...this.mutatingFrame.querySelectorAll(FOLDER_SELECTOR)];
    return folders.filter(folder => {
      // Consider only those folders if it contains only fragment files
      const fragCount = folder.querySelectorAll(FRAGMENT_SELECTOR).length;
      const fileCount = folder.querySelectorAll(FILE_SELECTOR).length;
      return fragCount > 0 && fragCount === fileCount;
    });
  }

  _getFragments() {
    let fragments = [...this.mutatingFrame.querySelectorAll(FRAGMENT_SELECTOR)];
    const folders = this._prepareFragmentsFolders(fragments);
    return fragments.concat(folders);
  }

  _prepareFragmentsFolders(fragments) {
    // Temporary solution.
    // It is possible to optimize the search to reduce the number of runs.

    const result = [];
    // .project_tree-folder > .project_tree-folder-content > .project_tree-file === fragment
    const folders = [...this.mutatingFrame.querySelectorAll(FOLDER_SELECTOR)];
    folders.forEach(folder => {
      const frag = folder.querySelectorAll(FRAGMENT_SELECTOR);
      const file = folder.querySelectorAll(FILE_SELECTOR);
      if (frag.length === file.length) {
        result.push(folder);
      }
    });
    return result
  }

  _updateFragmentsVisibility(bool) {
    const display = bool ? '' : 'none';
    this.fragments.forEach(element => {
      element.style.display = display;
    })
  }

  _updateControl(num) {
    this.control.textElement.innerHTML = `<b>Show ${num} fragment${num > 1 ? 's' : ''}</b> included in&nbsp;other documents in the Project document tree.`;

    if (num) {
      this._addControl();
    } else {
      this._removeControl();
    }
  }

  toggleFragmentsVisibility(checked) {
    this._updateFragmentsVisibility(checked);

    if (checked) {
      this._updateCurrentState('show', 'fragmentVisibility');
      this._setSessionStorageItem('show', 'fragmentVisibility');
    } else {
      this._updateCurrentState('hide', 'fragmentVisibility');
      this._setSessionStorageItem('hide', 'fragmentVisibility');
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

  _createControl() {
    this.control = createSwitch({
      labelText: `<b>Show fragments</b>`, // * This text will be updated later.
      dataTestID: 'show-hide-fragments-toggler',
      checked: this.getCurrentFragmentVisibilityBool(),
      callback: (checked) => this.toggleFragmentsVisibility(checked),
    });
    this.controlElement = this.control.element;
  }

  _addControl() {
    // * this.controlTarget may not be present on the page, for example, in the case of static export.
    this.controlTarget && this.controlTarget.append(this.controlElement);
  }

  _removeControl() {
    this.controlElement.remove();
  }

  _addMutationObserver() {
    // console.log('Mutation observer added for', this.mutatingFrame);

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
  // * This element may not be present on the page, for example, in the case of static export.
  // if (!controlTarget) {
  //   console.error(`Selector "${SWITCH_SELECTOR}" not found on the page`);
  //   return;
  // }

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

  document.addEventListener('click', function (event) {
    const trigger = event.target.closest('.dashboard-path-external');
    if (!trigger) {
      return;
    }
    trigger.closest('.dashboard-path').classList.toggle('revealed');
  });

  document.addEventListener('keydown', function (event) {
    if (event.key !== 'Enter' && event.key !== ' ') {
      return;
    }
    const trigger = event.target.closest('.dashboard-path-external');
    if (!trigger) {
      return;
    }
    event.preventDefault();
    trigger.closest('.dashboard-path').classList.toggle('revealed');
  });

},false);
})();
