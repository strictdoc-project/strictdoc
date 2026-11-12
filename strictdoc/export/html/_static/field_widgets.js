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
// hides while the user types. The insert button opens a menu with one item
// per widget that supports the field markup (the form's "document_markup"
// input).
//
// Widget contract. Every widget has:
// - id: the widget name. It names the insert menu item, its test ID
// "field-widgets-insert-<id>", and its icon in the
// #template-field-widgets-icons template
// (components/field_widgets/icons.jinja).
// - label: the text of the insert menu item.
// - supports(markup): returns true if the widget works with the markup.
// - insert(field, line, rect): inserts a new element at the blank caret
// line. `rect` is the viewport rectangle of the field button, for a widget
// that shows its own popup there.
// Any widget can also have these optional hooks:
// - scan(field, lines, markup): called after every change of the text of
// a field with a supported markup.
// - forget(field): called when the field is no longer in the DOM, so the
// widget can drop its data about the field.
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
// - insertBlock(field, line, blockLines): writes the lines in place of the
// blank caret line.
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

  // field -> { markup, button, menu, typing, lines, offsets, segments,
  // mapped }
  // menu: the open insert menu as { element, line }, or null.
  // typing: the caret position after the last input, or false.
  // lines, offsets, segments, and mapped describe the current field text;
  // scanField() sets them after every change.
  const fieldStates = new Map();
  let activeField = null;

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

  // Returns the viewport top of a text line. A collapsed range on an empty
  // line has no rect, so the top is then derived from the closest non-empty
  // line above.
  function lineTop(field, state, line, caret) {
    const caretRect = caret?.getClientRects()[0];
    if (caretRect?.height) return caretRect.top;

    for (let above = line; above >= 0; above--) {
      const length = state.lines[above].length;
      if (length === 0) continue;
      const from = state.offsets[above] + (above === line ? 0 : length - 1);
      const rect = textRange(field, state.segments, from, from + 1)
        .getClientRects()[0];
      if (rect) return rect.top + (line - above) * rect.height;
    }
    const style = getComputedStyle(field);
    const lineHeight = parseFloat(style.lineHeight) ||
      parseFloat(style.fontSize) * 1.2;
    return field.getBoundingClientRect().top + parseFloat(style.paddingTop) +
      line * lineHeight;
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

  function closeInsertMenu(state) {
    state.menu?.element.remove();
    state.menu = null;
  }

  function hideButton(field) {
    const state = fieldStates.get(field);
    if (!state) return;
    closeInsertMenu(state);
    state.button.hidden = true;
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
    if (state.menu?.line !== line) closeInsertMenu(state);

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
  // widget which of its blocks holds the caret.
  function updateActiveField() {
    const field = caretField();
    if (activeField && activeField !== field) hideButton(activeField);
    activeField = field;

    const found = activeField ? placeButton(activeField) : null;
    widgets.forEach((widget) => widget.activate?.(
      activeField,
      found?.widget === widget ? found.block : null,
    ));
  }

  // Opens the insert menu under the button, or above it if there is no
  // room below. The menu is a fixed popup in <body> (see placeFixed()). The
  // menu keeps the caret in the field, so the caret line is still known when
  // an item is chosen.
  function openInsertMenu(field, line) {
    const state = fieldStates.get(field);
    const {
      button
    } = state;
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
      element.appendChild(item);
    }
    element.addEventListener('mousedown', (event) => event.preventDefault());
    element.addEventListener('click', (event) => {
      // The table view must not see this click (see placeFixed()).
      event.stopPropagation();
      const item = event.target.closest(`[${ATTR_INSERT}]`);
      if (!item) return;
      const rect = button.getBoundingClientRect();
      closeInsertMenu(state);
      const id = item.getAttribute(ATTR_INSERT);
      widgets.find((widget) => widget.id === id).insert(field, line, rect);
    });
    document.body.appendChild(element);
    placeFixed(element, button.getBoundingClientRect());
    state.menu = {
      element,
      line
    };
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

  // Writes the block in place of the blank caret line. Blank lines separate
  // the block from the surrounding text.
  function insertBlock(field, line, blockLines) {
    scanField(field);
    const {
      lines
    } = fieldStates.get(field);

    if (lines.join('').trim() === '') {
      writeLines(field, blockLines, blockLines.length - 1);
      return;
    }

    const before = lines.slice(0, line);
    const after = lines.slice(line + 1);
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
      } else if (state.menu) {
        closeInsertMenu(state);
      } else if (line !== null && isBlankLine(state, line)) {
        openInsertMenu(field, line);
      }
    });

    // The hidden textarea must stay the field's next sibling:
    // editable_field.js finds it with nextElementSibling.
    (field.nextElementSibling ?? field).after(button);

    fieldStates.set(field, {
      markup,
      button,
      menu: null,
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
    updateActiveField();
  });

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
    for (const state of fieldStates.values()) {
      if (state.menu && !state.menu.element.contains(event.target) &&
        !state.button.contains(event.target)) closeInsertMenu(state);
    }
  });

  // Escape closes only the insert menu. The table view cancels the edited
  // cell on Escape from its listener on the document, so the event must not
  // get there.
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    const state = fieldStates.get(event.target.closest?.(SEL_FIELD));
    if (!state?.menu) return;
    event.stopPropagation();
    closeInsertMenu(state);
  }, true);

  document.addEventListener('focusout', (event) => {
    if (fieldStates.has(event.target)) hideButton(event.target);
  });

  // The insert menu has a fixed position, so it follows the button when the
  // page or a container scrolls, and when the window size changes.
  function replaceInsertMenus() {
    for (const state of fieldStates.values()) {
      if (state.menu) placeFixed(state.menu.element, state.button.getBoundingClientRect());
    }
  }
  document.addEventListener('scroll', replaceInsertMenus, true);
  window.addEventListener('resize', replaceInsertMenus);

  document.addEventListener('selectionchange', updateActiveField);

})();
