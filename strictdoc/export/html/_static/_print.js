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
  // We will collect the IDs of the page breaks into the 'pageBreaks' array.
  let pageBreaks = [];

  for (let i = 0; i < offsetHeightsOfPageElemments.length; ++i) {

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
      // mark current element as the beginning of a new page,
      pageBreaks.push({
        id: i,
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

  console.log(pageBreaks);

  // Set breaks for all pages in loop:
  pageBreaks.forEach(({ id, previousPageContentHeight }) => {

    // Close the previous page.
    // In the case of the first page:
    // the end of previous page does not exist.
    const endPage = id ? printable.querySelector(`#printable${id - 1}`) : undefined;
    endPage?.after(runningFooter.cloneNode(true));

    // To compensate for the empty space at the end of the page, add a padding to footer.
    const compensateDiv = document.createElement('div');
    const paddingCompensation = PRINT_HEIGHT - previousPageContentHeight
    console.log('paddingCompensation: ', id, paddingCompensation);
    compensateDiv.style.paddingTop = paddingCompensation + 'px';
    compensateDiv.style.backgroundColor = 'red';
    endPage?.after(compensateDiv);

    // Starting a new page.
    const startPage = printable.querySelector(`#printable${id}`);
    startPage.before(runningHeader.cloneNode(true));

  });

  // // Add runningHeader for last page if it was not added.
  // if (heightAccumulator < PRINT_HEIGHT) {
  //   printable.append(runningFooter.cloneNode(true));
  // }
};