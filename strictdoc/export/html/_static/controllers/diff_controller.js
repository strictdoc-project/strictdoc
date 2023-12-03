Stimulus.register("diff", class extends Controller {
  initialize() {

    const leftColumn = this.element.querySelector('.diff[left]');
    const rightColumn = this.element.querySelector('.diff[right]');

    const leftOpenBtn = document.getElementById('diff_left_open');
    const leftCloseBtn = document.getElementById('diff_left_close');
    const rightOpenBtn = document.getElementById('diff_right_open');
    const rightCloseBtn = document.getElementById('diff_right_close');

    const detailsLeftAll = [...leftColumn.querySelectorAll('details')];
    const detailsRightAll = [...rightColumn.querySelectorAll('details')];
    const detailsLeft = [...leftColumn.querySelectorAll('details[modified]')];
    const detailsRight = [...rightColumn.querySelectorAll('details[modified]')];

    // Add event listener
    leftOpenBtn.addEventListener("click", function(event){
      event.preventDefault();
      openAll(detailsLeft);
    });
    leftCloseBtn.addEventListener("click", function(event){
      event.preventDefault();
      closeAll(detailsLeftAll);
    });
    rightOpenBtn.addEventListener("click", function(event){
      event.preventDefault();
      openAll(detailsRight);
    });
    rightCloseBtn.addEventListener("click", function(event){
      event.preventDefault();
      closeAll(detailsRightAll);
    });

  }
});

function closeAll(details) {
  details.forEach(detail => {
    detail.removeAttribute("open")
  });
}
function openAll(details) {
  details.forEach(detail => {
    detail.setAttribute("open", "")
  });
}
