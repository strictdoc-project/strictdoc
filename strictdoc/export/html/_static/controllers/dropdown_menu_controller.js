const __log = (topic, ...payload) => {
  console.log(`%c ${topic} `, 'background:yellow;color:black',
    ...payload
  );
};
// __log('000',???)

const MENU_SELECTOR = '[js-dropdown-menu]';
const HANDLER_SELECTOR = '[js-dropdown-menu-handler]';
const LIST_SELECTOR = '[js-dropdown-menu-list]';

let menuList = [];
// menuList = [...document.querySelectorAll(MENU_SELECTOR)];
// menuList.forEach

Stimulus.register("dropdown_menu", class extends Controller {
  static targets = ["name"];

  connect() {
    this.registerListEvents();
  }

  registerListEvents(params) {
    const toggle = this.element.querySelector(HANDLER_SELECTOR);
    const content = this.element.querySelector(LIST_SELECTOR);

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

    const buttonList = [...content.querySelectorAll('a')];
    buttonList.forEach(button => {
      button.addEventListener('click', event => hide());
    })

    const handleClosure = event => !content.contains(event.target) && hide();

    window.addEventListener('click', handleClosure);
    window.addEventListener('focusin', handleClosure);
  }
});
