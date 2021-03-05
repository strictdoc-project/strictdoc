window.onload = function () {

  console.log('I am in _print.js',);

  // Preparing the DOM elements.
  const {
    printableFlow,
    frontpage,
    runningHeaderTemplate,
    runningFooterTemplate,
  } = prepareDomElements({
    printableFlow: '#printable',
    frontpage: '.frontpage',
    runningHeaderTemplate: '#runningHeaderTemplate',
    runningFooterTemplate: '#runningFooterTemplate',
  });

  // Defining the constant printAreaHeight corresponding frontpage offsetHeight.
  const printAreaHeight = frontpage.offsetHeight;

  // The height compensator is taken into account
  // in the calculation of page breaks in calculatePageBreaks().
  // It is used for Spacer that is added after each printable element
  // in makePreview().
  const heightCompensator = 16;

  // Adding IDs to nodes that we don't want to break,
  // and collecting their IDs and heights
  // in processedPrintable
  // to then break down the content into pages.
  const processedPrintable = processPrintable({
    // use any selector:
    printable: '.printable',
    // use class selector:
    breakable: '.breakable',
  });

  // Calculate page breaks
  // and add flags to processedPrintable.
  calculatePageBreaks({
    processedPrintable,
    printAreaHeight,
    heightCompensator,
  });

  // Splitting content into virtual pages
  // and generating previews that look like PDF.
  makePreview({
    printableFlow,
    runningFooterTemplate,
    runningHeaderTemplate,
    processedPrintable,
    printAreaHeight,
    heightCompensator,
  });
};

// USED FUNCTIONS

function prepareDomElements({
  printableFlow,
  frontpage,
  runningHeaderTemplate,
  runningFooterTemplate,
}) {

  // Get printable wrapper.
  const _printableFlow = document.querySelector(printableFlow);

  // Get frontpage.
  const _frontpage = _printableFlow.querySelector(frontpage);

  // Get templates.
  const _runningHeaderTemplate = document.querySelector(runningHeaderTemplate).content;
  const _runningFooterTemplate = document.querySelector(runningFooterTemplate).content;

  return {
    printableFlow: _printableFlow,
    frontpage: _frontpage,
    runningHeaderTemplate: _runningHeaderTemplate,
    runningFooterTemplate: _runningFooterTemplate,
  }
}



function processPrintable({
  printable,
  breakable,
}) {

  // Checking for variable format.
  // breakable should be suitable for classList.contains
  if (breakable.charAt(0) === '.') {
    breakable = breakable.substring(1);
  }
  if (breakable.charAt(0) === '#') {
    console.error('"breakable" var in processPrintable() should be suitable for classList.contains and contain only the class name!');
  }

  // let accumulator
  let processedPrintable = [];

  // What we are going to do with the element:
  const processElement = (element) => {
    const elementId = processedPrintable.length;
    const elementHeight = element.offsetHeight;

    // Get offsetHeight and push to accumulator 'processedPrintable',
    processedPrintable.push({
      id: elementId, // is equal to id in array
      height: elementHeight,
    });
    // set ID to element, corresponding ID in accumulator 'processedPrintable'.
    element.id = `printable${elementId}`;

    // Add styles, compensate for visibility over the virtual page.
    element.style.position = 'relative';
  }

  // Get printable NodeList,
  // from all .selectors elements.
  const sections = [...document.querySelectorAll(printable)];
  sections.map((element, id) => {

    // If the item is breakable, process ONLY its child elements.
    if (element.classList.contains(breakable) && element.hasChildNodes()) {

      const children = makeArrayOfNotTextChildNodes(element);

      children.forEach((element) => {
        if (element.classList.contains('document')) {
          // The condition is specific to STRICTDOC:
          // '.document' is generated inside requirement statement.
          const documentChildren = makeArrayOfNotTextChildNodes(element);

          documentChildren.forEach((element) => {
            processElement(element);
          })
        } else {
          processElement(element);
        }
      })
    } else {
      // Else process the elements.
      processElement(element);
    }
  })

  console.log('processedPrintable: \n', processedPrintable);
  return processedPrintable;
}

function calculatePageBreaks({
  processedPrintable,
  printAreaHeight,
  // We take the height compensator into account in this function in the calculation of the page breaks:
  // via compensatedCurrentElementHeight.
  // It is used for Spacer and is added after each printable element.
  heightCompensator = 16
}) {

  // Calculate from which elements new pages will start.
  // We will accumulate the height of the elements in the heightAccumulator
  // and compare it to the printAreaHeight - maximum height of the printed area.
  let heightAccumulator = 0;

  // We will collect the IDs of the page breaks and height of contents
  // into the 'processedPrintable' array.
  processedPrintable.map((item, id) => {

    const currentElementHeight = item.height;
    const compensatedCurrentElementHeight = currentElementHeight + heightCompensator;

    // TODO the case when the element is larger than the printable area, we will handle later:

    // Reserve the previous accumulator value.
    const pageContentHeight = heightAccumulator;

    // Add element height to the accumulator.
    heightAccumulator = heightAccumulator + compensatedCurrentElementHeight;

    // If the accumulator is overflowed,
    if (heightAccumulator > printAreaHeight) {
      // // NOT: mark current element as the beginning of a new page,
      // mark the PREVIOUS element as a page break,
      // and set page content height,
      // TODO front?
      // TODO вынести все темплейты на фронт и брать оттуда, а тут обрабатывать поток без фронта!
      if (id === 0) {
        console.log("000");
      }
      processedPrintable[id - 1] = {
        ...processedPrintable[id - 1],
        pageBreak: pageContentHeight
      };
      // mark the CURRENT element as a page start,
      processedPrintable[id] = {
        ...processedPrintable[id],
        pageStart: true,
      };
      // reset the accumulator and add current element height.
      heightAccumulator = compensatedCurrentElementHeight;
    }

    // register the last element as a page break
    // and store the resulting content height of the last page.
    if (id === processedPrintable.length - 1) {
      processedPrintable[id] = {
        ...processedPrintable[id],
        pageBreak: heightAccumulator
      };
    }
  })
}

function makePreview({
  // elements
  printableFlow,
  runningFooterTemplate,
  runningHeaderTemplate,
  // data
  processedPrintable,
  printAreaHeight,
  // Consider the height compensator.
  // It is taken into account in the calculation of page breaks.
  // It is used for Spacer and is added after each printable element.
  heightCompensator = 16
}) {

  // Set the header and footer for all pages:

  processedPrintable.map((item) => {

    const { id, height, pageStart, pageBreak } = item;
    const element = printableFlow.querySelector(`#printable${id}`);

    if (pageStart) {
      // Starting a new virtual page.
      const runningHeader = runningHeaderTemplate.cloneNode(true);
      element.before(runningHeader);
    }

    if (pageBreak) {
      // Closing the current virtual page,
      // which ends with a page break.
      const runningFooter = runningFooterTemplate.cloneNode(true);
      // Add page number.
      // TODO
      // runningFooter.querySelector('.page-number').innerHTML = ` ${i + 1} / ${pageBreaks.length}`;
      element.after(runningFooter);

      // To compensate for the empty space at the end of the page, add a padding to footer.
      const pageHeightCompensator = document.createElement('div');
      const paddingCompensation = printAreaHeight - pageBreak;
      pageHeightCompensator.style.paddingTop = paddingCompensation + 'px';
      element.after(pageHeightCompensator);
    }

    // Add elementsPaddingCompensator after each printable element.
    const elementsPaddingCompensator = document.createElement('div');
    elementsPaddingCompensator.style.paddingTop = heightCompensator + 'px';
    elementsPaddingCompensator.style.position = 'relative';

    element.after(elementsPaddingCompensator);
  })
}

function makeArrayOfNotTextChildNodes(element) {
  // Check that the element is a tag and not '#text'.
  // https://developer.mozilla.org/ru/docs/Web/API/Node/nodeName
  let children = element.childNodes;
  return [...children].filter(item => item.tagName);
}
