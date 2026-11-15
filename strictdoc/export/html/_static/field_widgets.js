// @relation(SDOC-SRS-208, scope=file)
//
// Field widgets for the multiline fields of the node form and of the table
// view cell form.
//
// A widget inserts or edits one kind of markup element, for example a
// table. Each widget is a separate script that registers itself with
// StrictDoc.fieldWidgets.register(). This script owns what the widgets
// share:
// - the field text, its lines, and the mapping of text positions to the DOM
// - the button in the field's left margin
// - the insert menu of the button
// - writing new text back into the field.
//
// While the caret is in a field, the button shows next to a block that a
// widget can edit ("edit"), or next to a blank caret line ("insert"). It
// hides while the user types.
//
// The insert menu has one item per widget that supports the field markup
// (the form's "document_markup" input). It opens at the caret when the
// user clicks the insert button or types "/" anywhere in the field. The
// text typed after "/" filters the items. The arrow keys move the active
// item, Enter or Tab chooses it. While the menu is open, a
// placeholder marks the caret position. The placeholder is not part of the
// field text. Escape or the last item of the menu closes the menu and keeps
// the typed text. When the user chooses a widget, the menu removes the "/"
// and the filter text, and the widget inserts its element:
// - an inline widget at the caret position, with spaces around it. On a
// blank line, the element forms a new paragraph (see
// inlineFormsParagraph());
// - a block widget as a new paragraph after the block of non-blank lines
// that holds the caret. On a blank line, the element takes its place.
//
// Widget contract. Every widget has:
// - id: the widget name. It names the insert menu item, its test ID
// "field-widgets-insert-<id>", and its icon in the
// #template-field-widgets-icons template
// (components/field_widgets/icons.jinja).
// - label: the text of the insert menu item.
// - supports(markup): returns true if the widget works with the markup.
// - insert(field, at, rect): inserts a new element. For an inline widget,
// `at` is the text offset of the caret, for a block widget, the caret
// line. `rect` is the viewport rectangle of the caret position, for a
// widget that shows its own popup there.
// - inline: true for an inline widget (see insertInline()), false or
// absent for a block widget (see insertBlock()).
// Any widget can also have these optional hooks:
// - scan(field, lines, markup): called after every change of the text of
// a field with a supported markup.
// - forget(field): called when the field is no longer in the DOM, so the
// widget can drop its data about the field.
// - capturesInput(field): returns true if the text at the caret belongs to
// the widget, for example, the query of an unfinished tag. Then a typed "/"
// is part of that text and does not open the insert menu.
// A widget that recognizes its own blocks in the field text (for example,
// tables) also has:
// - blockAt(field, line): returns the block {start, end, ...} that holds
// the line, or null. The edit button shows next to the block.
// - editTitle: the title of the edit button.
// - edit(field, block): edits a block returned by blockAt().
// - activate(field, block): called on every caret move with the block
// that holds the caret, or with null.
//
// Helpers for the widgets:
// - hasWidget(field, id): returns true if the widget works in the field.
// - lineRange(field, start, end): a DOM range for the lines [start, end],
// or null if the field DOM cannot be mapped to its text.
// - textBeforeCaret(field): the field text before the caret, or null if
// the caret is not in the field or the field DOM cannot be mapped to its
// text.
// - insertInline(field, offset, text): writes the text at the offset, with
// spaces around it, or as a new paragraph (see inlineFormsParagraph()), and
// puts the caret after the text.
// - insertBlock(field, line, blockLines): writes the lines as a new
// paragraph after the block that holds the line, or in place of the line
// if it is blank.
// - replaceLines(field, start, end, newLines): writes the lines in place of
// the lines [start, end].
// - replaceText(field, from, to, text): writes the text in place of the
// characters [from, to) and puts the caret after it.
// - placeFixed(element, rect): puts a fixed element under the rect, or
// above it if there is no room below, inside the viewport.
//
// A widget popup that must not be cut by the form goes into <body> with a
// fixed position (see placeFixed()). Inside the form, the overflow of
// sdoc-form-grid would cut it: sdoc-node is a CSS container, and a
// container is the containing block of its fixed descendants. In the table
// view, a click or a key outside the edited cell saves or cancels the
// cell, so such a popup stops the propagation of its clicks and keys.

(() => {

  const SEL_FIELD =
    'sdoc-contenteditable[data-js-editable-field]' +
    '[data-field-type="multiline"][contenteditable="true"]';

  // Insert menu DOM contract:
  // - js-field_widgets-insert marks an item of the insert menu. Its value is
  // the widget id.
  const ATTR_INSERT = 'js-field_widgets-insert';
  // - js-field_widgets-close marks the last item, which closes the menu.
  const ATTR_CLOSE = 'js-field_widgets-close';
  // - the class "active" marks the item that Enter chooses. It is styled by
  // .dropdown_menu_item.active in element.css.
  const CLASS_ACTIVE = 'active';
  // - js-field_widgets-icon marks an icon in the
  // #template-field-widgets-icons template. Its value is the widget id.
  const ATTR_ICON = 'js-field_widgets-icon';
  const ICON_TEMPLATE_ID = 'template-field-widgets-icons';

  // The distance in pixels between a fixed popup and its rect or the
  // viewport edge.
  const POPUP_GAP = 4;

  const widgets = [];

  //
  // Field text and DOM positions.
  //
  // The field usually holds a single text node, but typing can add more text
  // nodes and <br> elements. To find a text position in the DOM, each text
  // node is mapped to its characters and each <br> to a line break. If the
  // field holds other elements, this mapping no longer matches innerText
  // (the text that is saved). Then positions in the field cannot be computed
  // reliably: the field gets no button, and lineRange() and
  // textBeforeCaret() return null, so the widgets cannot highlight or
  // write anything there.
  //

  function textSegments(root) {
    const segments = [];
    const walker = document.createTreeWalker(
      root,
      NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
    );
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (node.nodeType === Node.TEXT_NODE) {
        segments.push({
          node,
          text: node.nodeValue
        });
      } else if (node.nodeName === 'BR') {
        segments.push({
          node,
          text: '\n'
        });
      }
    }
    return segments;
  }

  function segmentsText(segments) {
    return segments.map((segment) => segment.text).join('');
  }

  // Returns a DOM position {node, offset} for a character offset.
  function domPosition(field, segments, charOffset) {
    let start = 0;
    for (const segment of segments) {
      const end = start + segment.text.length;
      if (charOffset <= end) {
        if (segment.node.nodeType === Node.TEXT_NODE) {
          return {
            node: segment.node,
            offset: charOffset - start
          };
        }
        const parent = segment.node.parentNode;
        const index = Array.prototype.indexOf.call(parent.childNodes, segment.node);
        return {
          node: parent,
          offset: charOffset === start ? index : index + 1
        };
      }
      start = end;
    }
    return {
      node: field,
      offset: field.childNodes.length
    };
  }

  // Returns a DOM range for the characters [from, to) of the field text.
  function textRange(field, segments, from, to) {
    const start = domPosition(field, segments, from);
    const end = domPosition(field, segments, to);
    const range = document.createRange();
    range.setStart(start.node, start.offset);
    range.setEnd(end.node, end.offset);
    return range;
  }

  function lineOffsets(lines) {
    const offsets = [];
    let offset = 0;
    for (const line of lines) {
      offsets.push(offset);
      offset += line.length + 1;
    }
    return offsets;
  }

  function caretRange() {
    const selection = window.getSelection();
    return selection?.rangeCount ? selection.getRangeAt(0) : null;
  }

  //
  // Per-field state.
  //

  // field -> { markup, button, typing, lines, offsets, segments, mapped }
  // typing: the caret position after the last input, or false.
  // lines, offsets, segments, and mapped describe the current field text;
  // scanField() sets them after every change.
  const fieldStates = new Map();
  let activeField = null;

  // The open insert menu: { field, element, placeholder, start, offset,
  // query }, or null.
  // start: the text offset of the "/" that opened the menu, or null if the
  // insert button opened it.
  // offset: the text offset of the caret when the menu opened.
  // query: the text typed after "/".
  let menu = null;

  // Returns the widgets that support the markup of the field.
  function widgetsFor(field) {
    const {
      markup
    } = fieldStates.get(field);
    return widgets.filter((widget) => widget.supports(markup));
  }

  function hasWidget(field, id) {
    return fieldStates.has(field) &&
      widgetsFor(field).some((widget) => widget.id === id);
  }

  function isBlankLine(state, line) {
    return state.lines[line].trim() === '';
  }

  // Drops the fields of closed forms. Nothing watches for their removal, so
  // every scan checks the known fields.
  function forgetRemovedFields() {
    for (const known of fieldStates.keys()) {
      if (known.isConnected) continue;
      if (menu?.field === known) closeInsertMenu();
      fieldStates.delete(known);
      widgets.forEach((widget) => widget.forget?.(known));
    }
  }

  function scanField(field) {
    forgetRemovedFields();
    const state = fieldStates.get(field);
    const text = field.innerText;
    state.lines = text.split('\n');
    state.offsets = lineOffsets(state.lines);
    state.segments = textSegments(field);
    state.mapped = segmentsText(state.segments) === text;
    widgetsFor(field).forEach(
      (widget) => widget.scan?.(field, state.lines, state.markup),
    );
  }

  // See the helpers in the file comment.
  function textBeforeCaret(field) {
    if (!fieldStates.get(field)?.mapped) return null;
    const range = caretRange();
    if (!range || !field.contains(range.startContainer)) return null;

    const before = document.createRange();
    before.selectNodeContents(field);
    before.setEnd(range.startContainer, range.startOffset);
    return segmentsText(textSegments(before.cloneContents()));
  }

  // Returns the line index of the caret, or null (see textBeforeCaret()).
  function caretLine(field) {
    const text = textBeforeCaret(field);
    return text === null ? null : text.split('\n').length - 1;
  }

  // Returns the text offset of the caret, or null (see textBeforeCaret()).
  function caretOffset(field) {
    return textBeforeCaret(field)?.length ?? null;
  }

  // Returns {widget, block} for the widget block that holds the line, or
  // null.
  function blockAtLine(field, line) {
    if (line === null) return null;
    for (const widget of widgetsFor(field)) {
      const block = widget.blockAt?.(field, line);
      if (block) return {
        widget,
        block
      };
    }
    return null;
  }

  function lineRange(field, start, end) {
    const state = fieldStates.get(field);
    if (!state?.mapped) return null;
    return textRange(
      field,
      state.segments,
      state.offsets[start],
      state.offsets[end] + state.lines[end].length,
    );
  }

  // Returns the viewport top of a text line.
  // Uses the caret position when available; otherwise calculates the position
  // from the closest non-empty line at or above it, or from the field's top,
  // using line-height to account for empty lines.
  function lineTop(field, state, line, caret) {
    const caretRect = caret?.getClientRects()[0];
    if (caretRect?.height) return caretRect.top;

    const style = getComputedStyle(field);
    const lineHeight = parseFloat(style.lineHeight);
    for (let above = line; above >= 0; above--) {
      const length = state.lines[above].length;
      if (length === 0) continue;
      const from = state.offsets[above] + (above === line ? 0 : length - 1);
      const rect = textRange(field, state.segments, from, from + 1)
        .getClientRects()[0];
      if (rect) return rect.top + (line - above) * (lineHeight || rect.height);
    }
    return field.getBoundingClientRect().top + parseFloat(style.paddingTop) +
      line * (lineHeight || parseFloat(style.fontSize) * 1.2);
  }

  function caretField() {
    const node = caretRange()?.startContainer;
    const element = node?.nodeType === Node.ELEMENT_NODE ? node : node?.parentElement;
    const field = element?.closest(SEL_FIELD) ?? null;
    return fieldStates.has(field) && field === document.activeElement ? field : null;
  }

  //
  // Field button.
  //

  function hideButton(field) {
    const state = fieldStates.get(field);
    if (state) state.button.hidden = true;
  }

  // Shows the button in the left margin of the field: next to the first line
  // of the block that holds the caret ("edit"), or next to a blank caret line
  // ("insert"). Returns {widget, block} for the block that holds the caret,
  // or null.
  function placeButton(field) {
    const state = fieldStates.get(field);
    const line = caretLine(field);
    const found = blockAtLine(field, line);
    const {
      button
    } = state;
    // The button hides while the user types, so it does not flicker next to
    // the text the user writes. It shows up again when the caret moves away
    // from the position where the last input left it.
    const caret = caretRange();
    if (state.typing && (caret?.startContainer !== state.typing.node ||
        caret?.startOffset !== state.typing.offset)) {
      state.typing = false;
    }
    const canInsert = line !== null && isBlankLine(state, line) &&
      widgetsFor(field).length > 0;
    if (line === null || state.typing || (!found && !canInsert)) {
      hideButton(field);
      return found;
    }

    button.dataset.mode = found ? 'edit' : 'insert';
    button.textContent = found ? '✎' : '+';
    button.title = found ? found.widget.editTitle : 'Insert';
    button.setAttribute('aria-label', button.title);
    const top = found ?
      lineTop(field, state, found.block.start, null) :
      lineTop(field, state, line, caret);
    button.hidden = false;
    button.style.top = `${top - button.offsetParent.getBoundingClientRect().top}px`;
    return found;
  }

  // Updates the button for the field that holds the caret and tells every
  // widget which of its blocks holds the caret. The insert menu closes when
  // the caret leaves the position where the menu expects it.
  function updateActiveField() {
    if (menu && caretOffset(menu.field) !== menu.offset + menu.query.length) {
      closeInsertMenu();
    }
    const field = caretField();
    if (activeField && activeField !== field) hideButton(activeField);
    activeField = field;

    const found = activeField ? placeButton(activeField) : null;
    widgets.forEach((widget) => widget.activate?.(
      activeField,
      found?.widget === widget ? found.block : null,
    ));
  }

  //
  // Insert menu.
  //

  function closeInsertMenu() {
    if (!menu) return;
    menu.element.remove();
    menu.placeholder.remove();
    menu = null;
  }

  function menuItems() {
    return [...menu.element.querySelectorAll(`[${ATTR_INSERT}]`)];
  }

  function setActive(item) {
    menuItems().forEach((each) => each.classList.toggle(CLASS_ACTIVE, each === item));
  }

  function moveActive(step) {
    const items = menuItems().filter((item) => !item.hidden);
    const index = items.findIndex((item) => item.classList.contains(CLASS_ACTIVE));
    setActive(items[(index + step + items.length) % items.length]);
  }

  // Shows the items with a word of the label that starts with the query.
  // The menu closes when no item matches.
  function filterInsertMenu() {
    const query = menu.query.toLowerCase();
    const items = menuItems();
    for (const item of items) {
      const id = item.getAttribute(ATTR_INSERT);
      const words = widgets.find((widget) => widget.id === id)
        .label.toLowerCase().split(/\s+/);
      item.hidden = !words.some((word) => word.startsWith(query));
    }
    const first = items.find((item) => !item.hidden);
    if (first) setActive(first);
    else closeInsertMenu();
  }

  function placeInsertMenu() {
    placeFixed(menu.element, menu.placeholder.getBoundingClientRect());
  }

  // Removes the "/" and the query, and lets the widget insert its element
  // at the caret position.
  function chooseWidget(id) {
    const {
      field,
      placeholder,
      start
    } = menu;
    const rect = placeholder.getBoundingClientRect();
    let at = menu.offset + menu.query.length;
    closeInsertMenu();
    if (start !== null) {
      replaceText(field, start, at, '');
      at = start;
    }
    const widget = widgets.find((each) => each.id === id);
    if (widget.inline) {
      widget.insert(field, at, rect);
    } else {
      widget.insert(field, field.innerText.slice(0, at).split('\n').length - 1, rect);
    }
  }

  // Opens the insert menu under the caret, or above it if there is no room
  // below. The menu is a fixed popup in <body> (see placeFixed()). The menu
  // keeps the caret in the field, so the caret position is still known when
  // an item is chosen. `start` is the text offset of the "/" that opens the
  // menu, or null.
  //
  // The placeholder at the caret is an empty element: its text comes from
  // CSS, so the field text (innerText) does not include it.
  function openInsertMenu(field, start) {
    closeInsertMenu();
    const caret = caretRange();
    const placeholder = document.createElement('sdoc-field-widgets-placeholder');
    placeholder.contentEditable = 'false';
    placeholder.dataset.testid = 'field-widgets-placeholder';
    caret.insertNode(placeholder);
    window.getSelection().collapse(caret.startContainer, caret.startOffset);

    const element = document.createElement('sdoc-field-widgets-insert-menu');
    element.className = 'dropdown_menu';
    element.dataset.testid = 'field-widgets-insert-menu';
    element.setAttribute('role', 'menu');
    for (const widget of widgetsFor(field)) {
      const item = document.createElement('button');
      item.type = 'button';
      item.className = 'dropdown_menu_item';
      item.textContent = widget.label;
      item.dataset.testid = `field-widgets-insert-${widget.id}`;
      item.setAttribute('role', 'menuitem');
      item.setAttribute(ATTR_INSERT, widget.id);
      const icon = document.getElementById(ICON_TEMPLATE_ID)
        ?.content.querySelector(`[${ATTR_ICON}="${widget.id}"] svg`);
      if (icon) item.prepend(icon.cloneNode(true));
      item.addEventListener('pointerenter', () => setActive(item));
      element.appendChild(item);
    }
    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'dropdown_menu_item field-widgets-menu-close';
    close.textContent = 'Close menu';
    close.dataset.testid = 'field-widgets-menu-close';
    close.setAttribute(ATTR_CLOSE, '');
    const key = document.createElement('span');
    key.className = 'field-widgets-menu-key';
    key.textContent = 'Esc';
    close.appendChild(key);
    element.appendChild(close);

    element.addEventListener('mousedown', (event) => event.preventDefault());
    element.addEventListener('click', (event) => {
      // The table view must not see this click (see placeFixed()).
      event.stopPropagation();
      const item = event.target.closest(`[${ATTR_INSERT}]`);
      if (item) chooseWidget(item.getAttribute(ATTR_INSERT));
      else if (event.target.closest(`[${ATTR_CLOSE}]`)) closeInsertMenu();
    });
    document.body.appendChild(element);
    menu = {
      field,
      element,
      placeholder,
      start,
      offset: caretOffset(field),
      query: ''
    };
    filterInsertMenu();
    placeInsertMenu();
  }

  //
  // Writing back to the field.
  //

  // Replaces the field content with one text node, so the caret can be set
  // by a text offset.
  function writeText(field, text, caret) {
    field.replaceChildren(document.createTextNode(text));

    field.focus();
    window.getSelection().collapse(field.firstChild, caret);

    field.dispatchEvent(new Event('input', {
      bubbles: true
    }));
    // The input event above makes the input listener treat this rewrite as
    // typing, which would hide the button. The widget wrote the text, not
    // the user, so the button stays.
    fieldStates.get(field).typing = false;
    updateActiveField();
  }

  function writeLines(field, lines, caretAfterLine) {
    writeText(
      field,
      lines.join('\n'),
      lineOffsets(lines)[caretAfterLine] + lines[caretAfterLine].length,
    );
  }

  function replaceText(field, from, to, text) {
    const current = field.innerText;
    writeText(
      field,
      current.slice(0, from) + text + current.slice(to),
      from + text.length,
    );
  }

  function replaceLines(field, start, end, newLines) {
    const {
      lines
    } = fieldStates.get(field);
    const updated = [
      ...lines.slice(0, start),
      ...newLines,
      ...lines.slice(end + 1),
    ];
    writeLines(field, updated, start + newLines.length - 1);
  }

  // The rule for an inline element on a blank line. Alone on a blank line
  // between two paragraphs, the element would join them into one, so it
  // forms its own paragraph, as a block does. To insert the element into a
  // blank line as is, return false.
  function inlineFormsParagraph(lines, line) {
    return lines[line].trim() === '';
  }

  // See the helpers in the file comment.
  function insertInline(field, offset, text) {
    const current = field.innerText;
    const lines = current.split('\n');
    const line = current.slice(0, offset).split('\n').length - 1;
    if (inlineFormsParagraph(lines, line)) {
      insertBlock(field, line, [text]);
      return;
    }
    const spaceBefore = offset > 0 && /\S/.test(current[offset - 1]) ? ' ' : '';
    const spaceAfter = offset < current.length && /\S/.test(current[offset]) ? ' ' : '';
    writeText(
      field,
      current.slice(0, offset) + spaceBefore + text + spaceAfter + current.slice(offset),
      offset + spaceBefore.length + text.length,
    );
  }

  // See the helpers in the file comment. Blank lines separate the block
  // from the surrounding text.
  function insertBlock(field, line, blockLines) {
    scanField(field);
    const {
      lines
    } = fieldStates.get(field);

    if (lines.join('').trim() === '') {
      writeLines(field, blockLines, blockLines.length - 1);
      return;
    }

    // A blank line is replaced. Otherwise, the block goes after the last
    // non-blank line of the block that holds the line.
    let [before, after] = [lines.slice(0, line), lines.slice(line + 1)];
    if (lines[line].trim() !== '') {
      let end = line;
      while (end + 1 < lines.length && lines[end + 1].trim() !== '') end++;
      [before, after] = [lines.slice(0, end + 1), lines.slice(end + 1)];
    }
    const blankBefore = before.length === 0 ||
      before[before.length - 1].trim() === '' ? [] : [''];
    const blankAfter = after.length > 0 && after[0].trim() !== '' ? [''] : [];

    const updated = [...before, ...blankBefore, ...blockLines, ...blankAfter, ...after];
    writeLines(
      field,
      updated,
      before.length + blankBefore.length + blockLines.length - 1,
    );
  }

  // See the helpers in the file comment.
  function placeFixed(element, rect) {
    const width = element.offsetWidth;
    const height = element.offsetHeight;

    const maxLeft = window.innerWidth - width - POPUP_GAP;
    const left = Math.max(POPUP_GAP, Math.min(rect.left, maxLeft));
    const below = rect.bottom + POPUP_GAP;
    const above = rect.top - POPUP_GAP - height;
    const fitsBelow = below + height <= window.innerHeight - POPUP_GAP;
    const top = fitsBelow || above < POPUP_GAP ? below : above;

    element.style.left = `${left}px`;
    element.style.top = `${top}px`;
  }

  //
  // Fields and listeners.
  //

  function initField(field) {
    if (fieldStates.has(field)) return;

    const markup = field.closest('form')
      ?.querySelector('[name="document_markup"]')?.value;
    if (!markup) return;

    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'field-widgets-button';
    button.dataset.testid = 'field-widgets-button';
    button.hidden = true;

    // Keep the caret in the field: the click handler reads its position.
    button.addEventListener('mousedown', (event) => event.preventDefault());

    button.addEventListener('click', () => {
      scanField(field);
      const state = fieldStates.get(field);
      const line = caretLine(field);
      const found = blockAtLine(field, line);
      if (found) {
        found.widget.edit(field, found.block);
      } else if (menu?.field === field) {
        closeInsertMenu();
      } else if (line !== null && isBlankLine(state, line)) {
        openInsertMenu(field, null);
      }
    });

    // The hidden textarea must stay the field's next sibling:
    // editable_field.js finds it with nextElementSibling.
    (field.nextElementSibling ?? field).after(button);

    fieldStates.set(field, {
      markup,
      button,
      typing: false
    });
    scanField(field);
  }

  // A widget script can load after the fields are initialized, so a new
  // widget scans the fields that already exist.
  function register(widget) {
    widgets.push(widget);
    for (const [field, state] of fieldStates) {
      if (field.isConnected && widget.supports(state.markup)) {
        widget.scan?.(field, state.lines, state.markup);
      }
    }
  }

  window.StrictDoc.fieldWidgets = {
    register,
    hasWidget,
    lineRange,
    textBeforeCaret,
    insertInline,
    insertBlock,
    replaceLines,
    replaceText,
    placeFixed,
  };

  window.StrictDoc.onInsert(SEL_FIELD, initField);

  document.addEventListener('input', (event) => {
    const field = event.target.closest?.(SEL_FIELD);
    if (!fieldStates.has(field)) return;
    const range = caretRange();
    fieldStates.get(field).typing = range && {
      node: range.startContainer,
      offset: range.startOffset
    };
    scanField(field);
    updateInsertMenu(field, event);
    updateActiveField();
  });

  // Typing closes the menu of the insert button. In the menu of "/", the
  // typed text is the query. A "/" typed into the field opens the menu,
  // unless a widget captures the input (see capturesInput() in the file
  // comment).
  function updateInsertMenu(field, event) {
    if (menu?.field === field) {
      const before = menu.start === null ? null : textBeforeCaret(field);
      const query = before !== null && before.length > menu.start &&
        before[menu.start] === '/' ? before.slice(menu.start + 1) : null;
      if (query === null || /\s/.test(query)) {
        closeInsertMenu();
      } else {
        menu.query = query;
        filterInsertMenu();
      }
    }
    const available = widgetsFor(field);
    if (!menu && event.inputType === 'insertText' && event.data === '/' &&
      available.length > 0 && !available.some((widget) => widget.capturesInput?.(field))) {
      const offset = caretOffset(field);
      if (offset !== null) openInsertMenu(field, offset - 1);
    }
  }

  // After typing, the button comes back when the caret moves (see
  // placeButton()). A click at the position where typing stopped does not
  // move the caret, so no selectionchange event fires. The click itself then
  // brings the button back.
  document.addEventListener('pointerup', (event) => {
    const state = fieldStates.get(event.target.closest?.(SEL_FIELD));
    if (!state?.typing) return;
    state.typing = false;
    updateActiveField();
  });

  document.addEventListener('pointerdown', (event) => {
    if (menu && !menu.element.contains(event.target) &&
      !fieldStates.get(menu.field).button.contains(event.target)) closeInsertMenu();
  });

  // The menu keys must not reach the field or the table view, which cancels
  // the edited cell on Escape. The arrow keys left and right close the menu,
  // so the caret does not move past the placeholder.
  document.addEventListener('keydown', (event) => {
    if (!menu || event.target !== menu.field) return;
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      moveActive(event.key === 'ArrowDown' ? 1 : -1);
    } else if (event.key === 'Enter' || event.key === 'Tab') {
      const active = menu.element.querySelector(`.${CLASS_ACTIVE}`);
      chooseWidget(active.getAttribute(ATTR_INSERT));
    } else if (event.key === 'Escape') {
      closeInsertMenu();
    } else {
      if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') closeInsertMenu();
      return;
    }
    event.preventDefault();
    event.stopPropagation();
  }, true);

  document.addEventListener('focusout', (event) => {
    if (!fieldStates.has(event.target)) return;
    if (menu?.field === event.target) closeInsertMenu();
    hideButton(event.target);
  });

  // The insert menu has a fixed position, so it follows the placeholder
  // when the page or a container scrolls, and when the window size changes.
  function replaceInsertMenu() {
    if (menu) placeInsertMenu();
  }
  document.addEventListener('scroll', replaceInsertMenu, true);
  window.addEventListener('resize', replaceInsertMenu);

  document.addEventListener('selectionchange', updateActiveField);

})();
