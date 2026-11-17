// Autocomplete list: the options list of an autocompletable form field
// (autocompletable_field.js) and of the link widget (link_widget.js).
// autocomplete.css gives the look.
//
// StrictDoc.autocomplete.listbox(list, field, onChoose) connects a <ul> to
// its field and returns the controller of the list. The aria-controls
// attribute of the field names the id of the list; the end-to-end tests
// find the list of a field this way. The caller decides
// when to request the options, when to show and hide the list, which keys
// reach the list, and what a chosen option writes into the field.
//
// The list has one active option: the option that Enter or Tab chooses.
// The arrow keys and the mouse pointer move it. When new options arrive,
// the option whose value equals the typed value is active, otherwise the
// first option. If the typed value is an option that the field already
// has (aria-disabled), no option is active, so Enter does not replace the
// typed value.

(() => {

  const SEL_OPTION = '[role="option"]:not([aria-disabled])';
  const NO_RESULTS_HTML =
    '<li class="autocomplete_item" role="option" aria-disabled="true">No matches found</li>';

  let uniqueId = 0;

  function listbox(list, field, onChoose) {
    list.setAttribute('role', 'listbox');
    if (!list.id) list.id = `autocomplete-list-${uniqueId++}`;
    field.setAttribute('aria-controls', list.id);

    function options() {
      return [...list.querySelectorAll(SEL_OPTION)];
    }

    function active() {
      return list.querySelector('[aria-selected="true"]');
    }

    // Only a key moves the list to the active option. If the mouse pointer
    // did it, the list would scroll under the pointer.
    function setActive(option, scroll) {
      const previous = active();
      if (previous === option) return;
      previous?.removeAttribute('aria-selected');
      if (option) {
        option.setAttribute('aria-selected', 'true');
        field.setAttribute('aria-activedescendant', option.id);
        if (scroll) option.scrollIntoView({
          block: 'nearest'
        });
      } else {
        field.removeAttribute('aria-activedescendant');
      }
    }

    function render(html, typedValue) {
      list.innerHTML = html.trim() ? html : NO_RESULTS_HTML;
      list.querySelectorAll('[role="option"]').forEach((option) => {
        option.id = `autocomplete-option-${uniqueId++}`;
      });
      const value = typedValue.trim().toLowerCase();
      const match = [...list.querySelectorAll('[data-autocompletable-value]')]
        .find((option) => option.dataset.autocompletableValue.toLowerCase() === value);
      if (match) {
        setActive(match.matches(SEL_OPTION) ? match : null, true);
      } else {
        setActive(options()[0] ?? null, true);
      }
    }

    function move(step) {
      const items = options();
      if (items.length === 0) return;
      const index = items.indexOf(active());
      const next = index === -1 && step < 0 ? items.length - 1 : index + step;
      setActive(items[(next + items.length) % items.length], true);
    }

    function clear() {
      setActive(null);
      list.innerHTML = '';
    }

    // For a list that the caller removes from the page.
    function detach() {
      clear();
      field.removeAttribute('aria-controls');
    }

    // Keep the focus and the caret in the field.
    list.addEventListener('mousedown', (event) => event.preventDefault());

    list.addEventListener('mousemove', (event) => {
      const option = event.target.closest(SEL_OPTION);
      if (option) setActive(option, false);
    });

    list.addEventListener('click', (event) => {
      const option = event.target.closest(SEL_OPTION);
      if (option) onChoose(option);
    });

    return {
      active,
      move,
      render,
      clear,
      detach
    };
  }

  window.StrictDoc.autocomplete = {
    listbox
  };

})();
