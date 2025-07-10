// @relation(SDOC-SRS-36, scope=file)

const __log = (topic, ...payload) => {
  console.log(`%c ${topic} `, 'background:yellow;color:black',
    ...payload
  );
}

class SimpleTabs {
  constructor(tabsContainer, tabContentSelector = "sdoc-tab-content") {
    this.tabsContainer = tabsContainer;
    this.tabContents = document.querySelectorAll(tabContentSelector);
    this.tabs = tabsContainer.querySelectorAll("sdoc-tab");
    this._init();
  }

  _init() {
    this.tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        this.activateTab(tab.innerText.trim());
      });
    });

    // Activate the tab marked as active, or the first one
    const activeTab = [...this.tabs].find((t) => t.hasAttribute("active")) || this.tabs[0];
    this.activateTab(activeTab.innerText.trim());
  }

  activateTab(tabName) {
    this.tabs.forEach((tab) => {
      if (tab.innerText.trim() === tabName) {
        tab.setAttribute("active", "");
      } else {
        tab.removeAttribute("active");
      }
    });

    this.tabContents.forEach((content) => {
      if (content.id === tabName) {
        content.setAttribute("active", "");
      } else {
        content.removeAttribute("active");
      }
    });
  }
}

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
    alignRight,
  }) {
    this.colorOn = colorOn || 'rgb(100, 200, 50)';
    this.colorOff = colorOff || 'rgb(200, 200, 200)';
    this.labelText = labelText || '';
    this.checked = checked || false; // todo: replace true/false with strings

    this.componentClass = componentClass || 'std-switch-scc';
    this.size = size || 0.75;
    this.stroke = stroke || 0.25;
    this.units = units || 'rem';
    this.alignRight = alignRight || true;

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
    const text = document.createElement('span');
    text.innerHTML = this.labelText;

    input.addEventListener('change', () => this.callback(input.checked));

    label.append(input, slider, text);
    block.append(label);
    this.insertStyle();

    return block;
  }

  insertStyle() {

    const css = `
    .${this.componentClass} {
      display: inline-block;
      line-height: 0;
    }
    .${this.componentClass}__label {
      display: inline-flex;
      gap: ${this.size * 0.5}${this.units};
      font-size: ${this.size * 1.5}${this.units}; /* 0.75rem; */
      line-height: ${this.size}${this.units};
      align-items: center;
      justify-content: flex-start;
      user-select: none;
      cursor: pointer;
      flex-direction: ${this.alignRight ? "row-reverse" : "row"};
      text-align: ${this.alignRight ? "right" : "left"};
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
      height: ${this.size + this.stroke * 2}${this.units};
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

class Dom {
  constructor({
    sourceId,
    sourceContainerId,
    referContainerId,
    hashSplitter,
    strictdocPointerSelector,
    strictdocRequirementSelector,
    strictdocRangeBannerSelector,
    strictdocRangeBannerHeaderSelector,
    strictdocRangeHandlerSelector,
    strictdocRangeCloserSelector,
    strictdocLineSelector,
    strictdocLineNumberSelector,
    strictdocLineContentSelector,
    strictdocLineRangeSelector,
    strictdocSourceFilterClass,
    filteredClass,
    coveredClass,
    activeClass,
    collapsedClass,
    expandedClass,
    coverageClass,
    highlightClass,
    focusClass,
  }) {

    // CONSTANTS
    this.sourceId = sourceId || 'source';
    this.sourceContainerId = sourceContainerId || 'sourceContainer';
    this.referContainerId = referContainerId || 'referContainer';
    this.hashSplitter = hashSplitter || '#';

    // STRICTDOC SPECIFIC
    this.strictdocPointerSelector = strictdocPointerSelector || '.source__range-pointer';
    this.strictdocRequirementSelector = strictdocRequirementSelector || '.source-file__requirement';
    this.strictdocRangeBannerSelector = strictdocRangeBannerSelector || '.source__range';
    this.strictdocRangeBannerHeaderSelector = strictdocRangeBannerHeaderSelector || '.source__range-header';
    this.strictdocRangeHandlerSelector = strictdocRangeHandlerSelector || '.source__range-handler';
    this.strictdocRangeCloserSelector = strictdocRangeCloserSelector || '.source__range-closer';
    this.strictdocLineSelector = strictdocLineSelector || '.source__line';
    this.strictdocLineNumberSelector = strictdocLineNumberSelector || '.source__line-number';
    this.strictdocLineContentSelector = strictdocLineContentSelector || '.source__line-content';
    this.strictdocLineRangeSelector = strictdocLineRangeSelector || '.source__line-ranges';
    this.strictdocSourceFilterClass = strictdocSourceFilterClass || 'source__filter';
    this.filteredClass = filteredClass || 'filtered';
    this.activeClass = activeClass || 'active';
    this.coveredClass = coveredClass || 'covered';
    this.coverageClass = coverageClass || 'coverage';
    this.collapsedClass = collapsedClass || 'collapsed';
    this.expandedClass = expandedClass || 'expanded';
    this.highlightClass = highlightClass || 'highlighted';
    this.focusClass = focusClass || 'focus';

    // elements
    this.sourceContainer;
    this.referContainer;
    this.source;
    this.lines = {};
    this.requirements = {};
    this.ranges = {};
    this.closers = {};

    // state
    this.active = {
      range: null,
      // requirement: null,
      pointers: [],
      labels: [],
      focus: false,
    };
  }

  prepare() {

    // rgb: '75,255,0',
    // alpha: '0.2',
    // rgb: '255,255,155',
    // alpha: '1',

    this._prepareSourceContainer();
    this._prepareReferContainer();
    this._prepareSource();

    this._prepareLines();
    this._prepareRanges();
    this._updateLinesWithRanges();
    this._updateRangesWithRequirements();
    this._updateRangesWithHandlers();
    this._updateRangesWithBanners();
    this._updateRangesWithClosers();

    // console.log('this.lines', this.lines);
    // console.log('this.ranges', this.ranges);
    // console.log('this.closers', this.closers);
    // console.log('this.requirements', this.requirements);
    // console.log('this.active', this.active);

  }

  useLocationHash() {
    const [_, reqId, rangeBegin, rangeEnd] = window.location.hash.split(this.hashSplitter);
    const rangeAlias = rangeBegin ? this._generateRangeAlias(rangeBegin, rangeEnd) : undefined;

    this.changeActive({
      // requirement: this.requirements[reqId],
      rangeBegin,
      rangeEnd,
      rangeAlias,
      pointers: rangeAlias ? this.ranges[rangeAlias].pointers : null,
      // range: rangeAlias ? this.ranges[rangeAlias].highlighter : null,
      labels: (reqId && rangeAlias) ? this.ranges[rangeAlias][reqId] : null,
    });

    this.highlightRange();
  }

  changeActive = ({
    rangeBegin,
    rangeEnd,
    rangeAlias,
    //// range,
    // handler,
    // banner,
    //// requirement,
    pointers,
    labels,
  }) => {

    // remove old 'active'
    // this.active.requirement?.classList.remove(this.activeClass);
    this.active.pointers?.forEach(pointer => pointer?.classList.remove(this.activeClass));
    this.active.labels?.forEach(label => label?.classList.remove(this.activeClass));
    if (this.active.rangeAlias) {
      this.ranges[this.active.rangeAlias].banner.classList.remove(this.activeClass);
      this.closers[this.active.rangeEnd].classList.remove(this.activeClass);
    }

    // make changes to state
    //// this.active.range = range;
    //// this.active.requirement = requirement;
    this.active.pointers = pointers;
    this.active.labels = labels;
    this.active.rangeBegin = rangeBegin;
    this.active.rangeEnd = rangeEnd;
    this.active.rangeAlias = rangeAlias;

    // add new 'active'
    // this.active.requirement?.classList.add(this.activeClass);
    this.active.pointers?.forEach(pointer => pointer.classList.add(this.activeClass));
    this.active.labels?.forEach(label => label.classList.add(this.activeClass));
    this.ranges[rangeAlias]?.banner.classList.add(this.activeClass);
    this.closers[this.active.rangeEnd]?.classList.add(this.activeClass);
  }

  toggleRangeBannerVisibility(handler) {
    const banner = handler.closest(this.strictdocRangeBannerSelector);

    if (banner.classList.contains(this.expandedClass)) {
      banner.classList.remove(this.expandedClass);
      banner.classList.add(this.collapsedClass);
    } else {
      banner.classList.add(this.expandedClass);
      banner.classList.remove(this.collapsedClass);
    }
  }

  toggleCoverageVisibility(toggler) {
    if (toggler) {
      this.source.classList.add(this.coverageClass);
    } else {
      this.source.classList.remove(this.coverageClass);
    }
  }

  highlightRange() {
    this.scrollToActiveRangeIfNeeded();

    const begin = parseInt(this.active.rangeBegin, 10);
    const end = parseInt(this.active.rangeEnd, 10);

    for (var key in this.lines) {
      this.lines[key].line.classList.remove(this.highlightClass);
      if (key >= begin && key <= end) {
        this.lines[key].line.classList.add(this.highlightClass);
      }
    }
  }

  scrollToActiveRangeIfNeeded() {
    // scroll to highlighted, do not scroll to top when unset highlighting:
    if (this.active.rangeAlias) {
      const activeRange = this.ranges[this.active.rangeAlias]?.bannerHeader || 0;
      requestAnimationFrame(() => {
        this.scrollTo(activeRange);
      });
    }
  }

  scrollTo(element) {
    const top = element.offsetTop || 0;
    this.sourceContainer.scrollTo({
      top: top,
      behavior: 'smooth',
    });
  }

  _prepareSource() {
    this.source = document.getElementById(this.sourceId);
    this.source.style.position = 'relative';
    this.source.style.zIndex = '1';
  }

  _prepareSourceContainer() {
    this.sourceContainer = document.getElementById('sourceContainer');

    // this.sourceContainer.style.position = 'absolute';
    // this.sourceContainer.style.top = 0;
    // this.sourceContainer.style.bottom = 0;
    // this.sourceContainer.style.right = 0;
    // this.sourceContainer.style.left = 0;
    // this.sourceContainer.style.overflow = 'auto';
  }

  _prepareReferContainer() {
    this.referContainer = document.getElementById('referContainer');
  }

  _prepareLines() {
    this.lines = [...document.querySelectorAll(this.strictdocLineSelector)]
      .reduce((acc, line) => {
        const lineNumber = line.querySelector(this.strictdocLineNumberSelector);
        const lineContent = line.querySelector(this.strictdocLineContentSelector);
        acc[line.dataset.line] = {
          line: line,
          lineNumber: lineNumber,
          lineContent: lineContent,
          ranges: []
        };
        return acc
      }, {});
  }

  _getRangePart(hash) {
    const parts = hash.split(this.hashSplitter);
    return `${this.hashSplitter}${parts[parts.length - 2]}${this.hashSplitter}${parts[parts.length - 1]}`;
  };

  _prepareRanges() {
    [...document.querySelectorAll(this.strictdocPointerSelector)]
      .map(pointer => {
        const thisFileOrOther = pointer.dataset.traceabilityFileType;
        // consider only references to the current file:
        if (thisFileOrOther === "other_file") {
          return;
        }

        const rangeBegin = pointer.dataset.begin;
        const rangeEnd = pointer.dataset.end;
        const rangeReq = pointer.dataset.reqid;

        const range = this._generateRangeAlias(rangeBegin, rangeEnd);

        if (!this.ranges[range]) {
          // add new range
          this.ranges[range] = {};
          this.ranges[range].pointers = [];

          this.ranges[range].beginLine = this.lines[rangeBegin].lineNumber;
          this.ranges[range].endLine = this.lines[rangeEnd].lineNumber;
          this.ranges[range].begin = rangeBegin;
          this.ranges[range].end = rangeEnd;
        }

        // todo pointers?
        if (rangeReq) {

          // add pointer from code
          (this.ranges[range][rangeReq] ??= []).push(pointer);

        } else {

          // add pointer from menu
          this.ranges[range].pointers.push(pointer);
        }

        pointer.addEventListener("click", (event) => {
          const targetHash = `#${rangeReq || ""}${this.hashSplitter}${rangeBegin}${this.hashSplitter}${rangeEnd}`;
          const currentHash = window.location.hash;

          const isSameHash = currentHash === targetHash;
          // Buttons linked to requirements include an ID in the hash,
          // while buttons in the source code do not.
          // Therefore, only the range part of the hash (e.g., #3#10)
          // should be compared to identify the currently active range.
          const isSameRange = this._getRangePart(currentHash) === `${this.hashSplitter}${rangeBegin}${this.hashSplitter}${rangeEnd}`;

          const isModifierPressed = event.metaKey || event.ctrlKey;

          const targetBannerHeader = this.ranges[range]?.bannerHeader;
          const topBefore = targetBannerHeader?.getBoundingClientRect().top;

          // Modifier click
          if (isModifierPressed) {
            event.preventDefault(); // cancel opening a new browser tab

            if (isSameRange) {
              this._toggleFocus();
              this._compensateSourceContainerScrollPosition(targetBannerHeader, topBefore);
            } else {
              // Sets the URL hash to activate a specific range without reloading the page:
              window.location.hash = targetHash;
              this.useLocationHash();
              this._activateFocus();
              this._compensateSourceContainerScrollPosition(targetBannerHeader, topBefore);
            }
            return;
          }

          // Normal click
          if (isSameRange) {
            // active → reset
            event.preventDefault();
            // Removes hash from URL without reloading or adding history entry:
            history.replaceState(null, '', window.location.pathname);
            this.useLocationHash();
            this._clearFocus();
            this._compensateSourceContainerScrollPosition(targetBannerHeader, topBefore);
          } else {
            // inactive → just reset the focus,
            // the basic functionality via URL will work itself out
            this._clearFocus();
            this._compensateSourceContainerScrollPosition(targetBannerHeader, topBefore);
          }
        });

      });
  }

  _compensateSourceContainerScrollPosition(element, topBefore) {
    // Compensates scroll to keep the given element in the same viewport position.
    // Expects the element and its initial .getBoundingClientRect().top value as input.
    // Measures element's top offset relative to the viewport before and after DOM changes.
    // Uses requestAnimationFrame to wait for DOM/layout updates before measuring again.
    // Calculates delta = after - before, i.e. how much the element moved visually.
    // Scrolls by that delta to restore the element's original viewport position.
    requestAnimationFrame(() => {
      const topAfter = element?.getBoundingClientRect().top;
      const delta = topAfter - topBefore;
      this.sourceContainer.scrollBy({ top: delta });
    });
  }

  _toggleFocus() {
    if (this.active.focus) {
      this.sourceContainer.classList.remove(this.focusClass);
      this.referContainer.classList.remove(this.focusClass);
    } else {
      this.sourceContainer.classList.add(this.focusClass);
      this.referContainer.classList.add(this.focusClass);
    }
    this.active.focus = !this.active.focus;
  }

  _activateFocus() {
    if (!this.active.focus) {
      this.active.focus = true;
      this.sourceContainer.classList.add(this.focusClass);
      this.referContainer.classList.add(this.focusClass);
    }
  }

  _clearFocus() {
    if (this.active.focus) {
      this.active.focus = false;
      this.sourceContainer.classList.remove(this.focusClass);
      this.referContainer.classList.remove(this.focusClass);
    }
  }

  _updateRangesWithRequirements() {
    const requirements = [...document.querySelectorAll(this.strictdocRequirementSelector)];
    requirements.forEach(requirement => {

      const rangeBegin = requirement.dataset.begin;
      const rangeEnd = requirement.dataset.end;
      const rangeReq = requirement.dataset.reqid;

      if (rangeEnd && rangeBegin) {
        const range = this._generateRangeAlias(rangeBegin, rangeEnd);
        console.assert(this.ranges[range], "The range must be registered:", range);

        (this.ranges[range].requirements ??= {})[rangeReq] = {};
        this.ranges[range].requirements[rangeReq].begin = rangeBegin;
        this.ranges[range].requirements[rangeReq].end = rangeEnd;
        this.ranges[range].requirements[rangeReq].element = requirement;
      } else {
        this.requirements[rangeReq] = requirement;
      }


    })
  }

  _updateRangesWithHandlers() {
    const handlers = [...document.querySelectorAll(this.strictdocRangeHandlerSelector)];
    handlers.forEach(handler => {

      const rangeBegin = handler.dataset.begin;
      const rangeEnd = handler.dataset.end;
      const range = this._generateRangeAlias(rangeBegin, rangeEnd);

      console.assert(this.ranges[range], "The range must be registered:", range);

      this.ranges[range].handler = handler;
      handler.addEventListener("click", event => this.toggleRangeBannerVisibility(event.currentTarget));
    })
  }

  _updateRangesWithBanners() {
    const banners = [...document.querySelectorAll(this.strictdocRangeBannerSelector)];
    banners.forEach(banner => {

      const rangeBegin = banner.dataset.begin;
      const rangeEnd = banner.dataset.end;

      if (rangeBegin && rangeEnd) {
        const range = this._generateRangeAlias(rangeBegin, rangeEnd);
        console.assert(this.ranges[range], "The range must be registered:", range);
        this.ranges[range].banner = banner;
        this.ranges[range].bannerHeader = banner.querySelector(this.strictdocRangeBannerHeaderSelector); // 'source__range-header'
      }
    })
  }

  _updateRangesWithClosers() {
    const closers = [...document.querySelectorAll(this.strictdocRangeCloserSelector)];
    closers.forEach(closer => {

      const rangeEnd = closer.dataset.end;

      if (rangeEnd) {
        this.closers[rangeEnd] = closer;
      }
    })
  }

  _updateLinesWithRanges() {
    Object.entries(this.ranges).forEach(([key, value]) => {
      // console.log(value);

      const begin = parseInt(value.begin, 10);
      const end = parseInt(value.end, 10);

      for (let i = begin; i <= end; i++) {
        (this.lines[i].ranges ??= []).push(key);
        (this.lines[i].pointers ??= []).push(...value.pointers);

        console.assert(this.lines[i].lineNumber, `The line ${i} must be registered.`);
        this.lines[i].lineNumber.classList.add(this.strictdocSourceFilterClass);
        this.lines[i].line.classList.add(this.coveredClass);
      }

      // const rangeNumContainer = this.lines[begin].line.querySelector(this.strictdocLineRangeSelector);
      // rangeNumContainer.innerHTML = this.lines[begin].pointers.length;
    });
  }

  _generateRangeAlias(begin, end) { return `${begin}${this.hashSplitter}${end}` };
}

const dom = new Dom({
  // sourceId: 'source',
  // sourceContainerId: 'sourceContainer',
  // hashSplitter: '#',
});

window.addEventListener("load", function () {
  dom.prepare();
  dom.useLocationHash();

  const switcher = new Switch(
    {
      labelText: 'Show coverage',
      size: 0.5,
      stroke: 0.2,
      checked: false,
      callback: (checked) => dom.toggleCoverageVisibility(checked),
    }
  );
  document.getElementById('sourceCodeCoverageSwitch').append(switcher.create());

  const tabsContainer = document.querySelector("sdoc-tabs");
  if (tabsContainer) {
    new SimpleTabs(tabsContainer);
  }

});

window.addEventListener("hashchange", () => dom.useLocationHash());
