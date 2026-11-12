// @relation(SDOC-SRS-208, scope=file)
//
// Anchor widget: the "anchor" widget of field_widgets.js. It writes an
// [ANCHOR: <UID>, <title>] tag on the blank caret line of an RST or
// Markdown field. The tag is block-level: it starts a line and ends it, and
// the insert button shows only on a blank line.
//
// The Anchor item of the insert menu opens a form under the field button
// with two inputs: UID (required) and title (optional). The form checks the
// UID while the user types:
// - The UID must match the UID syntax of the SDoc grammar.
// - The UID must not be used in the project. The form asks
// /autocomplete/link, which lists the target with the same UID first.
// - The UID must not be used by an anchor in the field text. The server
// does not know the anchors that are not saved yet.
// The title must be writable in the tag syntax (see titleSource()).
// Insert works only for a valid, free UID and a valid title. The server
// checks the anchors again when the node form is saved.
//
// Enter in an input inserts the anchor, Escape or Cancel closes the form.
// Both give the focus back to the field. A click outside the form closes
// it. The form is a child of <body> with a fixed position, see placeFixed()
// in field_widgets.js.

(() => {

  const fieldWidgets = window.StrictDoc.fieldWidgets;

  const AUTOCOMPLETE_URL = '/autocomplete/link';
  // The delay in milliseconds between the last keystroke and the request.
  const REQUEST_DELAY = 150;

  //
  // ANCHOR syntax.
  //

  // The UID syntax of the SDoc grammar (REGEX_UID in grammar.py). Python's
  // \w also matches non-Latin letters and digits, hence \p{L} and \p{N}.
  // @relation(SDOC-SRS-150, scope=line)
  const UID_PATTERN = /^[\p{L}\p{N}_][\p{L}\p{N}_()\-/.: ]*$/u;

  // Returns the UIDs of the anchors in the field text.
  // @relation(SDOC-SRS-150, scope=function)
  function fieldAnchorUids(text) {
    return new Set(
      [...text.matchAll(/^\[ANCHOR: ([^,\]\n]+)/gm)].map((match) => match[1].trim()),
    );
  }

  // Returns the title as the tag writes it, or null if the tag syntax
  // cannot hold it. A title with "," or "]" goes in double quotes, the same
  // as Anchor.get_source_title() writes it. A quoted title cannot contain a
  // double quote. An unquoted title cannot start or end with one: the
  // parser removes the quotes at the ends.
  // @relation(SDOC-SRS-150, scope=function)
  function titleSource(title) {
    if (/[,\]]/.test(title)) return title.includes('"') ? null : `"${title}"`;
    if (title.startsWith('"') || title.endsWith('"')) return null;
    return title;
  }

  // @relation(SDOC-SRS-150, scope=function)
  function anchorTag(uid, title) {
    return title ? `[ANCHOR: ${uid}, ${titleSource(title)}]` : `[ANCHOR: ${uid}]`;
  }

  //
  // Form.
  //

  // The open form: { field, line, element, uidInput, titleInput,
  // uidMessage, titleMessage, insertButton, offset, timer, controller,
  // uidIsFree }, or null.
  // offset: the position of the form relative to the field, so the form
  // follows the field on scroll.
  // uidIsFree: true only after the server confirmed the current UID.
  let form = null;

  function closeForm(focusField) {
    if (!form) return;
    clearTimeout(form.timer);
    form.controller?.abort();
    form.element.remove();
    const {
      field
    } = form;
    form = null;
    if (focusField && field.isConnected) field.focus();
  }

  function setMessage(element, text) {
    element.textContent = text;
    element.hidden = text === '';
  }

  // Returns the UID error that the browser can find without the server, or
  // an empty string.
  function localUidError(uid) {
    if (uid === '') return '';
    if (!UID_PATTERN.test(uid)) {
      return 'A UID starts with a letter, a digit, or "_". ' +
        'It can also contain spaces and the characters - ( ) / . :';
    }
    if (fieldAnchorUids(form.field.innerText).has(uid)) {
      return 'This field already has an anchor with this UID.';
    }
    return '';
  }

  function titleError(title) {
    if (title === '' || titleSource(title) !== null) return '';
    return /[,\]]/.test(title) ?
      'A title with "," or "]" cannot contain double quotes.' :
      'A title cannot start or end with a double quote.';
  }

  function updateInsertButton() {
    const uid = form.uidInput.value.trim();
    const title = form.titleInput.value.trim();
    form.insertButton.disabled = !(uid !== '' && form.uidIsFree &&
      localUidError(uid) === '' && titleError(title) === '');
  }

  // Asks the server if the UID is used. /autocomplete/link lists the target
  // with the same UID first.
  function checkUidOnServer(uid) {
    clearTimeout(form.timer);
    form.timer = setTimeout(async () => {
      form.controller?.abort();
      const controller = new AbortController();
      form.controller = controller;
      const params = new URLSearchParams({
        q: uid
      });
      try {
        const response = await fetch(`${AUTOCOMPLETE_URL}?${params}`, {
          signal: controller.signal
        });
        const html = await response.text();
        if (form?.controller !== controller) return;
        const results = document.createElement('template');
        results.innerHTML = html;
        const first = results.content.querySelector('[data-autocompletable-value]');
        if (first?.dataset.autocompletableValue === uid) {
          const kind = first.querySelector('.field-widgets-link-kind')?.textContent;
          setMessage(form.uidMessage,
            `This UID is already used${kind ? ` by ${kind}` : ''}.`);
        } else {
          form.uidIsFree = true;
        }
        updateInsertButton();
      } catch (error) {
        if (error.name !== 'AbortError') throw error;
      }
    }, REQUEST_DELAY);
  }

  function onUidInput() {
    const uid = form.uidInput.value.trim();
    form.uidIsFree = false;
    clearTimeout(form.timer);
    form.controller?.abort();
    const error = localUidError(uid);
    setMessage(form.uidMessage, error);
    if (uid !== '' && error === '') checkUidOnServer(uid);
    updateInsertButton();
  }

  function onTitleInput() {
    setMessage(form.titleMessage, titleError(form.titleInput.value.trim()));
    updateInsertButton();
  }

  function insertAnchor() {
    if (form.insertButton.disabled) return;
    const {
      field,
      line
    } = form;
    const tag = anchorTag(form.uidInput.value.trim(), form.titleInput.value.trim());
    closeForm(false);
    if (field.isConnected) fieldWidgets.insertBlock(field, line, [tag]);
  }

  function placeForm() {
    const fieldRect = form.field.getBoundingClientRect();
    fieldWidgets.placeFixed(form.element, {
      left: fieldRect.left + form.offset.left,
      top: fieldRect.top + form.offset.top,
      bottom: fieldRect.top + form.offset.bottom,
    });
  }

  function createInput(label, testId) {
    const wrapper = document.createElement('label');
    wrapper.className = 'field-widgets-anchor-label';
    wrapper.textContent = label;
    const input = document.createElement('input');
    input.type = 'text';
    input.autocomplete = 'off';
    input.spellcheck = false;
    input.dataset.testid = testId;
    const message = document.createElement('div');
    message.className = 'field-widgets-anchor-message';
    message.dataset.testid = `${testId}-message`;
    message.hidden = true;
    wrapper.append(input, message);
    return {
      wrapper,
      input,
      message
    };
  }

  function createButton(text, actionType, testId) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'action_button';
    button.textContent = text;
    button.dataset.actionType = actionType;
    button.dataset.testid = testId;
    return button;
  }

  function openForm(field, line, buttonRect) {
    closeForm(false);

    const element = document.createElement('sdoc-field-widgets-anchor-form');
    element.setAttribute('role', 'dialog');
    element.setAttribute('aria-label', 'Anchor');
    element.dataset.testid = 'field-widgets-anchor-form';

    const uid = createInput('UID', 'field-widgets-anchor-uid');
    const title = createInput('Title (optional)', 'field-widgets-anchor-title');
    const actions = document.createElement('div');
    actions.className = 'field-widgets-anchor-actions';
    const cancelButton = createButton('Cancel', 'cancel', 'field-widgets-anchor-cancel');
    const insertButton = createButton('Insert', 'submit', 'field-widgets-anchor-insert');
    insertButton.disabled = true;
    actions.append(cancelButton, insertButton);
    element.append(uid.wrapper, title.wrapper, actions);

    uid.input.addEventListener('input', onUidInput);
    title.input.addEventListener('input', onTitleInput);
    cancelButton.addEventListener('click', () => closeForm(true));
    insertButton.addEventListener('click', insertAnchor);

    // The table view must not see the clicks and keys of the form (see
    // field_widgets.js): a click would save the edited cell, and Escape
    // would cancel it.
    element.addEventListener('click', (event) => event.stopPropagation());
    element.addEventListener('keydown', (event) => {
      event.stopPropagation();
      if (event.key === 'Escape') {
        event.preventDefault();
        closeForm(true);
      } else if (event.key === 'Enter' && event.target.tagName === 'INPUT') {
        event.preventDefault();
        insertAnchor();
      }
    });

    document.body.appendChild(element);
    const fieldRect = field.getBoundingClientRect();
    form = {
      field,
      line,
      element,
      uidInput: uid.input,
      titleInput: title.input,
      uidMessage: uid.message,
      titleMessage: title.message,
      insertButton,
      offset: {
        left: buttonRect.left - fieldRect.left,
        top: buttonRect.top - fieldRect.top,
        bottom: buttonRect.bottom - fieldRect.top,
      },
      timer: null,
      controller: null,
      uidIsFree: false
    };
    placeForm();
    uid.input.focus();
  }

  //
  // Listeners.
  //

  document.addEventListener('pointerdown', (event) => {
    if (form && !form.element.contains(event.target)) closeForm(false);
  });

  // The form has a fixed position, so it follows the field when the page or
  // a container scrolls, and when the window size changes.
  function replaceForm() {
    if (form) placeForm();
  }
  document.addEventListener('scroll', replaceForm, true);
  window.addEventListener('resize', replaceForm);

  fieldWidgets.register({
    id: 'anchor',
    label: 'Anchor',
    supports: (markup) => markup === 'RST' || markup === 'Markdown',

    insert(field, line, rect) {
      openForm(field, line, rect);
    },
  });

})();
