// viewtype_
// https://kittygiraudel.com/2021/03/18/close-on-outside-click/

window.addEventListener("load",function(){

  const toggle = document.getElementById('viewtype_handler');
  const content = document.getElementById('viewtype_menu');

  const show = () => {
    toggle.setAttribute('aria-expanded', true);
    content.setAttribute('aria-hidden', false);
  }

  const hide = () => {
    toggle.setAttribute('aria-expanded', false);
    content.setAttribute('aria-hidden', true);
  }

  toggle.addEventListener('click', event => {
    event.stopPropagation();
    JSON.parse(toggle.getAttribute('aria-expanded')) ? hide() : show();
  })

  const handleClosure = event => !content.contains(event.target) && hide();

  window.addEventListener('click', handleClosure);
  window.addEventListener('focusin', handleClosure);

},false);
