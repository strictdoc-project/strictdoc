window.onload = function () {

  // TODO fire this as eventHandler -- conflict on the window.onload

  console.log('I am in _print.js',);

  // The elementsPaddingCompensator is taken into account
  // in the calculation of page breaks
  // in calculatePages().
  // It is used for Spacer that is added after each printable element
  // in makePreview().
  // This is done to make the page height predictable.
  const elementsPaddingCompensator = 16;

  // Preparing templates.
  const {
    printableFlow,
    runningHeaderTemplate,
    runningFooterTemplate,
    printAreaHeight,
  } = prepareTemplates({
    printableFlowSelector: '#printableFlow',
    pageTemplateSelector: '#pageTemplate',
    printAreaTemplateSelector: '#printAreaTemplate',
    runningHeaderTemplateSelector: '#runningHeaderTemplate .running',
    runningFooterTemplateSelector: '#runningFooterTemplate .running',
  });

  // Collects nodes with the corresponding selectors,
  // adding IDs to nodes that we don't want to break,
  // and collecting their data in printableElements
  // to then break down the content into pages.
  const printableElements = processPrintable({
    // where we're looking for:
    printableFlow,
    // use any selector:
    printableSelector: '.printable',
    // use class selector (is intended for use in classList.contains):
    breakableSelector: 'breakable',
    pagebreakSelector: 'pagebreak',
  });

  // Calculate page breaks
  // and add flags to printableElements.
  // Returns printablePages.
  const printablePages = calculatePages({
    // from the templates
    printAreaHeight,
    // from the processed data
    printableElements,
    // constant
    elementsPaddingCompensator,
  });

  // Splitting content into virtual pages
  // and generating previews that look like PDF.
  makePreview({
    // from the templates
    printableFlow,
    runningFooterTemplate,
    runningHeaderTemplate,
    printAreaHeight,
    // from the processed data
    printableElements,
    printablePages,
    // constant
    elementsPaddingCompensator,
  });
};

// USED FUNCTIONS

function prepareTemplates({
  printableFlowSelector,
  pageTemplateSelector,
  printAreaTemplateSelector,
  runningHeaderTemplateSelector,
  runningFooterTemplateSelector,
}) {

  // Get printable wrapper.
  const _printableFlow = document.querySelector(printableFlowSelector);

  // Get page templates container.
  const _pageTemplate = document.querySelector(pageTemplateSelector);

  // Get templates for cloning.
  const _printAreaTemplate = _pageTemplate.querySelector(printAreaTemplateSelector);
  const _runningHeaderTemplate = _pageTemplate.querySelector(runningHeaderTemplateSelector);
  const _runningFooterTemplate = _pageTemplate.querySelector(runningFooterTemplateSelector);

  // Get print area height for calculating pages.
  const _printAreaHeight = _printAreaTemplate.offsetHeight;
  // To print frontage correctly, fix the height of the printable area,
  // otherwise it changes after processing the CSS virtual elements.
  _printAreaTemplate.style.height = _printAreaHeight + 'px';

  console.log('print area height: ', _printAreaHeight);

  return {
    printableFlow: _printableFlow,
    runningHeaderTemplate: _runningHeaderTemplate,
    runningFooterTemplate: _runningFooterTemplate,
    printAreaHeight: _printAreaHeight,
  }
}

function processPrintable({
  printableFlow,
  printableSelector,
  breakableSelector,
  pagebreakSelector,
}) {

  // Checking for variable format.
  // Selector in 'breakable' and 'pagebreak' should be suitable for classList.contains
  if (breakableSelector.charAt(0) === '.') {
    breakableSelector = breakableSelector.substring(1);
  }
  if (pagebreakSelector.charAt(0) === '.') {
    pagebreakSelector = pagebreakSelector.substring(1);
  }
  if (breakableSelector.charAt(0) === '#') {
    console.error(` "breakableSelector" var in processPrintable() should be suitable for classList.contains and contain only the class name!`);
  }
  if (pagebreakSelector.charAt(0) === '#') {
    console.error(` "pagebreakSelector" var in processPrintable() should be suitable for classList.contains and contain only the class name!`);
  }

  // let accumulator of printable elements data
  const printableElements = [];

  // What we are going to do with the element:
  const processElement = (element) => {

    const elementId = printableElements.length;
    const elementHeight = element.offsetHeight;

    // Get offsetHeight and push to accumulator 'printableElements',
    printableElements.push({
      id: elementId, // is equal to id in array
      height: elementHeight,
    });

    // register a forced page break
    if (element.classList.contains(pagebreakSelector)) {
      printableElements[elementId] = {
        ...printableElements[elementId],
        pageBreak: true,
      };
    }

    // set ID to element, corresponding ID in accumulator 'printableElements'.
    element.id = `printable_${elementId}`;

    // Add styles, compensate for visibility over the virtual page.
    element.style.position = 'relative';
  }

  // Get printable NodeList,
  // from all elements with selectors in 'printable'.
  [...printableFlow.querySelectorAll(printableSelector)]
    .map((printableElement, id) => {

      // If the printable Element is breakable, process ONLY its child elements.
      if (printableElement.classList.contains(breakableSelector) && printableElement.hasChildNodes()) {

        const breakableElement = printableElement;
        makeArrayOfNotTextChildNodes(breakableElement)
          .forEach((breakableElementChild) => {

            // The condition is specific to STRICTDOC:
            // '.document' is generated inside requirement statement,
            // so we have to process his children.
            if (breakableElementChild.classList.contains('document')) {

              const strictddocElement = breakableElementChild;
              makeArrayOfNotTextChildNodes(strictddocElement)

                .forEach((strictddocElementChild) => {
                  processElement(strictddocElementChild);
                })

            } else {
              // Else process other childs of breakable Element.
              processElement(breakableElementChild);
            }
          })

      } else {
        // Else process the printable Element.
        processElement(printableElement);
      }
    })

  console.log('printableElements: \n', printableElements);
  return printableElements;
}

function calculatePages({
  printAreaHeight,
  printableElements,
  // We take the padding compensator into account in this function in the calculation of the page breaks:
  // via compensatedCurrentElementHeight.
  // It is used for Spacer and is added after each printable element.
  elementsPaddingCompensator = 16
}) {

  // Calculate from which elements new pages will start.
  // We will accumulate the height of the elements in the heightAccumulator
  // and compare it to the printAreaHeight - maximum height of the printed area.
  let heightAccumulator = 0;

  // Init with flagged front page.
  // From this variable we only use the length of the array,
  // so we can use 'frontpage' here, and then IDs.
  const printablePages = ['frontpage'];

  function registerPageStart(id, printablePages) {
    // mark the element as a page start,
    printableElements[id] = {
      ...printableElements[id],
      //We register the beginning of the page
      // based on the registration of the end of the previous page.
      // So we force its number by 1 beforehand:
      pageStart: printablePages.length + 1,
    };
  }

  function registerPageEnd(id, printablePages, memorizedPageContentHeight) {
    registerPage(id, printablePages);

    // mark the element as a page break,
    // write the memorized pageContentHeight down,
    // write the page number down,
    printableElements[id] = {
      ...printableElements[id],
      pageEnd: printablePages.length,
      pageBreak: memorizedPageContentHeight,
    };
  }

  function registerPage(id, printablePages) {
    // register the page,
    printablePages.push(id);
  }

  // We will collect the IDs of the page breaks and height of contents
  // into the 'printableElements' array.

  // Register the first element of the 'printableElements' as a page start.
  registerPageStart(0, printablePages);

  // process content flow
  printableElements.map((element, id) => {

    const compensatedCurrentElementHeight = element.height + elementsPaddingCompensator;

    // TODO the case when the element is larger than the printable area, we will handle later:

    // Memorize the previous accumulator value.
    const pageContentHeight = heightAccumulator;

    // Add element height to the accumulator.
    heightAccumulator = heightAccumulator + compensatedCurrentElementHeight;

    // If the element has pagebreak attribute,
    if (element.pageBreak) {
      // mark the CURRENT element as a page break
      // with pageBreak equal to the accumulated height at this moment,
      registerPageEnd(id, printablePages, heightAccumulator);
      // mark the NEXT element as a page start,
      registerPageStart(id + 1, printablePages);
      // reset the accumulator
      heightAccumulator = 0;
      // go to next element
      return;
    }

    // If the accumulator is overflowed,
    if (heightAccumulator > printAreaHeight) {
      // mark the PREVIOUS element as a page break.
      registerPageEnd(id - 1, printablePages, pageContentHeight);
      // mark the CURRENT element as a page start,
      registerPageStart(id, printablePages);
      // reset the accumulator
      // and add to it the height of the current element,
      // which will be the start of the new page.
      heightAccumulator = compensatedCurrentElementHeight;
    }
  })

  // Register the last element as a page break
  // and assign the last heightAccumulator value
  // as the height of the last page.
  // We need it to generate the footer on the last page correctly.
  const lastPrintableElementId = printableElements.length - 1;
  registerPageEnd(lastPrintableElementId, printablePages, heightAccumulator);

  console.log('printablePages:\n', printablePages);
  return printablePages;
}

function makePreview({
  // elements
  printableFlow,
  runningFooterTemplate,
  runningHeaderTemplate,
  // data
  printAreaHeight,
  printableElements,
  printablePages,
  // Consider the height compensator.
  // It is taken into account in the calculation of page breaks.
  // It is used for Spacer and is added after each printable element.
  elementsPaddingCompensator = 16
}) {

  // Set the page number for Frontpage, if possible.
  // runningHeaderTemplate & runningFooterTemplate are frontpage children.
  setPageNumber(runningHeaderTemplate, 1, printablePages.length);
  setPageNumber(runningFooterTemplate, 1, printablePages.length);

  // Set the header and footer for all pages.

  printableElements.map((item) => {

    const { id, height, pageStart, pageEnd, pageBreak } = item;
    const element = printableFlow.querySelector(`#printable_${id}`);

    if (pageStart) {
      // Starting a new virtual page.
      const runningHeader = runningHeaderTemplate.cloneNode(true);
      // Add page number, if possible.
      setPageNumber(runningHeader, pageStart, printablePages.length);
      // Put the element into DOM.
      element.before(runningHeader);
    }

    if (pageEnd) {
      // Closing the current virtual page,
      // which ends with a page break.
      const runningFooter = runningFooterTemplate.cloneNode(true);
      // Add page number, if possible.
      setPageNumber(runningFooter, pageEnd, printablePages.length);
      // Put the element into DOM.
      element.after(runningFooter);

      // To compensate for the empty space at the end of the page, add a padding to footer.
      const pageHeightCompensatorDIV = document.createElement('div');
      pageHeightCompensatorDIV.style.paddingTop = printAreaHeight - pageBreak + 'px';
      element.after(pageHeightCompensatorDIV);
    }

    // Add elementPaddingCompensatorDIV after each printable element.
    const elementPaddingCompensatorDIV = document.createElement('div');
    elementPaddingCompensatorDIV.style.paddingTop = elementsPaddingCompensator + 'px';
    elementPaddingCompensatorDIV.style.position = 'relative';
    element.after(elementPaddingCompensatorDIV);
  })
}

function makeArrayOfNotTextChildNodes(element) {
  // Check that the element is a tag and not '#text'.
  // https://developer.mozilla.org/ru/docs/Web/API/Node/nodeName
  let children = element.childNodes;
  return [...children].filter(item => item.tagName);
}

function setPageNumber(target, current, total) {
  const contaiter = target.querySelector(`.page-number`);
  if (contaiter) {
    contaiter.querySelector('.current').innerHTML = current;
    contaiter.querySelector('.total').innerHTML = total;
  }
}
