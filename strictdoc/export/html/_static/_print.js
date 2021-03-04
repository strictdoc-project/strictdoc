// INIT vars.
let PRINT_HEIGHT;
let offsetHeightsOfPageElemments = [];

window.onload = function () {

  console.log('I am in _print.js',);

  // Get templates.
  const runningHeader = document.querySelector("#runningHeaderTemplate").content;
  const runningFooter = document.querySelector("#runningFooterTemplate").content;

  // Get printable wrapper.
  const printable = document.querySelector("#printable");

  // Get frontpage.
  const frontpage = printable.querySelector('.frontpage');

  // Set constant PRINT_HEIGHT corresponding frontpage offsetHeight.
  PRINT_HEIGHT = frontpage.offsetHeight;

  // Get printable NodeList,
  // for all children that are tags,
  // add IDs and collect their heights to offsetHeightsOfPageElemments.
  if (printable.hasChildNodes()) {
    // So first we check to see if the object is empty, if it has children.

    let children = printable.childNodes;

    // children.forEach()
    for (let i = 0; i < children.length; ++i) {

      // Check that the element is a tag and not '#text'.
      // https://developer.mozilla.org/ru/docs/Web/API/Node/nodeName
      if (children[i].tagName) {

        // Get offsetHeight and push to accumulator,
        offsetHeightsOfPageElemments.push(children[i].offsetHeight);
        // set ID to element, corresponding ID in accumulator.
        children[i].id = `printable${offsetHeightsOfPageElemments.length - 1}`;

      }
    }
  }

  // Calculate from which elements new pages will start.
  // We will accumulate the height of the elements in the heightAccumulator
  // and compare it to the PRINT_HEIGHT - maximum height of the printed area.
  let heightAccumulator = 0;
  // We will collect the IDs of the page breaks and height of contents
  // into the 'pageBreaks' array.
  // Initiate it with a page break after the frontpage.
  let pageBreaks = [
    {
      id: 0,
      previousPageContentHeight: PRINT_HEIGHT
    }
  ];

  // We start the loop with 1 because the frontpage has a fixed height
  // and we've already added a page break after frontpage when initializing 'pageBreaks'.
  for (let i = 1; i < offsetHeightsOfPageElemments.length; ++i) {

    const currentElementHeight = offsetHeightsOfPageElemments[i];

    // TODO the case when the element is larger than the printable area, we will handle later:
    // // if the item fits in the height of the printing area
    // if (offsetHeightsOfPageElemments[i] <= PRINT_HEIGHT) {
    //   // add its height to the accumulator
    //   heightAccumulator = heightAccumulator + currentElementHeight;
    // }

    // Reserve the previous accumulator value.
    const previousPageContentHeight = heightAccumulator;

    // Add elements height to the accumulator.
    heightAccumulator = heightAccumulator + currentElementHeight;

    // If the accumulator is overflowed,
    if (heightAccumulator >= PRINT_HEIGHT) {
      // // NOT: mark current element as the beginning of a new page,
      // mark the PREVIOUS element as a page break,
      pageBreaks.push({
        id: i - 1,
        previousPageContentHeight: previousPageContentHeight
      });
      // reset the accumulator and add current element height.
      heightAccumulator = currentElementHeight;
    }

    // register the last element as a page break
    // and store the resulting content height of the last page.
    if (i === offsetHeightsOfPageElemments.length - 1) {
      pageBreaks.push({
        id: i,
        previousPageContentHeight: heightAccumulator
      });
    }
  }

  // Set the header for the frontpage here,
  // because it cannot be set in the loop.
  frontpage.before(runningHeader.cloneNode(true));

  // Set the header and footer for all pages in loop:
  // // pageBreaks.forEach(({ id, previousPageContentHeight }) => {
  for (let i = 0; i < pageBreaks.length; ++i) {

    const { id, previousPageContentHeight } = pageBreaks[i];

    // Close the current page,
    // which ends with a page break.
    const pageEnd = printable.querySelector(`#printable${id}`);
    const _runningFooter = runningFooter.cloneNode(true);
    // Add page number.
    _runningFooter.querySelector('.page-number').innerHTML = ` ${i + 1} / ${pageBreaks.length}`;
    pageEnd?.after(_runningFooter);


    // To compensate for the empty space at the end of the page, add a padding to footer.
    const compensateDiv = document.createElement('div');
    const paddingCompensation = PRINT_HEIGHT - previousPageContentHeight
    compensateDiv.style.paddingTop = paddingCompensation + 'px';
    pageEnd?.after(compensateDiv);

    // Starting a new page,
    //which begins after a page break.
    const pageStart = printable.querySelector(`#printable${id + 1}`);
    // In the case of the last page we use the optionality.
    pageStart?.before(runningHeader.cloneNode(true));

  };

};