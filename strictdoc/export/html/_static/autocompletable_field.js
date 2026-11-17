// Ported from stimulus-autocomplete (MIT License, Copyright (c) 2021
// Alberto Fernández-Capel, https://github.com/afcapel/stimulus-autocomplete).
//
// A page can have several independent [data-js-autocompletable] elements at
// once (e.g. one per editable table cell), so all per-instance state
// (debounce timer, in-flight AbortController) lives in the closure below,
// created fresh per element by StrictDoc.onInsert - none of it is shared or
// stored on the element itself.
//
// The options list comes from StrictDoc.autocomplete (autocomplete.js).

(() => {

  const SEL_AUTOCOMPLETABLE = '[data-js-autocompletable]';

  function filterSingleLine(text) {
    return text.replace(/\s/g, ' ').replace(/\s\s+/g, ' ');
  }

  const debounce = (fn, delay = 10) => {
    let timeoutId = null;
    return (...args) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => fn(...args), delay);
    };
  };

  function initAutocompletable(autocompletable) {
    const hidden = autocompletable.nextElementSibling;
    const results = hidden.nextElementSibling;
    const readonly = autocompletable.getAttribute('contenteditable') === 'false';

    function resultsShown() {
      return !results.hidden;
    }

    function setResultsShown(value) {
      results.hidden = !value;
    }

    function open() {
      if (resultsShown()) return;
      setResultsShown(true);
      autocompletable.setAttribute('aria-expanded', 'true');
      autocompletable.dispatchEvent(
        new CustomEvent('toggle', {
          detail: {
            action: 'open',
            autocompletable: autocompletable,
            results: results
          }
        })
      );
    }

    function close() {
      if (!resultsShown()) return;
      setResultsShown(false);
      autocompletable.removeAttribute('aria-activedescendant');
      autocompletable.setAttribute('aria-expanded', 'false');
      autocompletable.dispatchEvent(
        new CustomEvent('toggle', {
          detail: {
            action: 'close',
            autocompletable: autocompletable,
            results: results
          }
        })
      );
    }

    close();

    if (!autocompletable.hasAttribute('autocompletable')) autocompletable.setAttribute(
      'autocompletable', 'off');
    autocompletable.setAttribute('spellcheck', 'false');

    if (readonly) {
      autocompletable.setAttribute('aria-readonly', 'true');
      return;
    }

    const urlValue = autocompletable.dataset.autocompletableUrl;
    const minLengthValue = Number(autocompletable.dataset.autocompletableMinLength || 0);
    const delayValue = Number(autocompletable.dataset.autocompletableDelay || 10);
    const queryParamValue = autocompletable.dataset.autocompletableQueryParam || 'q';
    const multipleChoiceValue = autocompletable.hasAttribute(
      'data-autocompletable-multiple-choice');

    let abortController = null;

    const list = window.StrictDoc.autocomplete.listbox(results, autocompletable, commit);

    // The value that the user types: for a MultipleChoice or Tag field, the
    // part after the last comma.
    function typedValue() {
      const text = autocompletable.innerText;
      return multipleChoiceValue ? text.split(',').pop() : text;
    }

    function moveCursorToEnd() {
      autocompletable.focus();
      const range = document.createRange();
      range.selectNodeContents(autocompletable);
      range.collapse(false);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
    }

    function commit(selected) {
      if (readonly) return;
      if (selected.getAttribute('aria-disabled') === 'true') return;

      if (selected instanceof HTMLAnchorElement) {
        selected.click();
        close();
        return;
      }

      const textValue = selected.getAttribute('data-autocompletable-label') || selected
        .textContent.trim();
      let suggestion = selected.getAttribute('data-autocompletable-value') || textValue;

      if (multipleChoiceValue) {
        // Replace the last incomplete token with the suggestion.
        const parts = (autocompletable.innerText || '').split(',');
        parts[parts.length - 1] = ' ' + suggestion;
        suggestion = parts.map((p) => p.trim()).join(', ');
      }

      autocompletable.innerText = suggestion;
      hidden.value = suggestion;

      moveCursorToEnd();

      hidden.dispatchEvent(new Event('input'));
      hidden.dispatchEvent(new Event('change'));

      autocompletable.focus();
      hideAndRemoveOptions();

      autocompletable.dispatchEvent(
        new CustomEvent('autocompletable.change', {
          bubbles: true,
          detail: {
            value: suggestion,
            textValue: textValue,
            selected: selected
          }
        })
      );
    }

    function hideAndRemoveOptions() {
      close();
      list.clear();
    }

    function buildURL(query) {
      const url = new URL(urlValue, window.location.href);
      const params = new URLSearchParams(url.search.slice(1));
      params.append(queryParamValue, query);
      url.search = params.toString();
      return url.toString();
    }

    async function doFetch(url, signal) {
      const response = await fetch(url, {
        signal
      });
      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }
      return response.text();
    }

    function replaceResults(html) {
      list.render(html, typedValue());
      open();
    }

    async function fetchResults(query) {
      if (!urlValue) return;

      // Abort the previous request as we are about to send a new one.
      if (abortController) abortController.abort();
      abortController = new AbortController();
      const signal = abortController.signal;

      const url = buildURL(query);
      try {
        autocompletable.dispatchEvent(new CustomEvent('loadstart'));
        const html = await doFetch(url, signal);
        replaceResults(html);
        autocompletable.dispatchEvent(new CustomEvent('load'));
        autocompletable.dispatchEvent(new CustomEvent('loadend'));
      } catch (error) {
        if (error.name === 'AbortError') return;
        autocompletable.dispatchEvent(new CustomEvent('error'));
        autocompletable.dispatchEvent(new CustomEvent('loadend'));
        throw error;
      }
    }

    function buildClickQuery() {
      // If minLengthValue is greater than 0, narrow-down-as-you-type
      // behavior is in effect: use the current text as the query, same as
      // while typing.
      if (minLengthValue != 0) {
        return autocompletable.innerText.trim();
      }

      if (!multipleChoiceValue) {
        // minLengthValue is 0 and not MultipleChoice/Tag: clicking should
        // act like a drop-down and show all possible options (i.e. for
        // SingleChoice).
        return '';
      }

      const currentText = autocompletable.innerText.trim();
      if (!currentText || currentText.endsWith(',')) {
        // Nothing typed yet, or already mid-way through a new entry.
        return currentText;
      }

      // MultipleChoice/Tag with an already-complete value and no trailing
      // comma: clicking to browse more options is equivalent to the user
      // having just typed a separating comma. We actually insert it (not
      // just send it as the query) so that the values already present are
      // excluded from suggestions *and* so that selecting a suggestion
      // afterwards appends a new value via commit() instead of overwriting
      // the existing one.
      const newText = `${currentText}, `;
      autocompletable.innerText = newText;
      hidden.value = newText;
      moveCursorToEnd();
      hidden.dispatchEvent(new Event('input'));
      hidden.dispatchEvent(new Event('change'));

      return newText.trim();
    }

    const keydownHandlers = {
      Escape: (event) => {
        if (!resultsShown()) return;
        hideAndRemoveOptions();
        event.stopPropagation();
        event.preventDefault();
      },
      ArrowDown: (event) => {
        if (!resultsShown()) return;
        list.move(1);
        event.preventDefault();
      },
      ArrowUp: (event) => {
        if (!resultsShown()) return;
        list.move(-1);
        event.preventDefault();
      },
      Tab: (event) => {
        if (!resultsShown()) return;
        // Without an active option, Tab moves the focus as usual.
        const active = list.active();
        if (!active) return;
        commit(active);
        event.preventDefault();
      },
      Enter: (event) => {
        if (readonly) return;
        const active = list.active();
        if (active && resultsShown()) commit(active);
        // single line, dont allow enter
        event.preventDefault();
      }
    };

    // Loading autocomplete options can wait until the user pauses typing. The
    // delay avoids sending a request for every character.
    const loadOptionsAfterInput = debounce(() => {
      if (readonly) return;

      const query = autocompletable.innerText.trim();
      if (query && query.length >= minLengthValue) {
        fetchResults(query);
      } else {
        hideAndRemoveOptions();
      }
    }, delayValue);

    function onInputChange() {
      if (readonly) return;

      // The visible autocomplete control is contenteditable, so the browser
      // does not include its text when the surrounding form is submitted. The
      // adjacent hidden control holds the value that the browser submits.
      // Update that hidden value during the same input event. If this update
      // were delayed together with loading the options, submitting the form
      // immediately after typing could send the previous value.
      hidden.value = filterSingleLine(autocompletable.innerText);

      loadOptionsAfterInput();
    }

    autocompletable.addEventListener('input', onInputChange);

    autocompletable.addEventListener('keydown', (event) => {
      const handler = keydownHandlers[event.key];
      if (handler) handler(event);
    });

    autocompletable.addEventListener('blur', close);

    autocompletable.addEventListener('click', () => {
      // Toggle between showing / hiding results.
      if (resultsShown()) {
        hideAndRemoveOptions();
      } else {
        fetchResults(buildClickQuery());
      }
    });

    if (autocompletable.hasAttribute('autofocus')) {
      autocompletable.focus();
    }
  }

  window.StrictDoc.onInsert(SEL_AUTOCOMPLETABLE, initAutocompletable);

})();
