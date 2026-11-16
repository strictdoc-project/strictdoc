// Delegated document-level listeners for every contenteditable field.
// The event types bubble, so no per-element registration (StrictDoc.onInsert)
// is needed - unlike the click-only controls, these only ever need to know
// about the element an event already fired on.

(() => {

  const SEL_EDITABLE = '[data-js-editable-field]';
  // Source of truth: strictdoc/core/image_formats.py (ImageFormat).
  const SUPPORTED_IMAGE_FORMATS = new Map([
    ['.svg', 'image/svg+xml'],
    ['.png', 'image/png'],
    ['.gif', 'image/gif'],
    ['.jpg', 'image/jpeg'],
    ['.jpeg', 'image/jpeg'],
    ['.webp', 'image/webp'],
    ['.avif', 'image/avif'],
  ]);
  const SUPPORTED_IMAGE_FORMAT_NAMES = 'SVG, PNG, GIF, JPG, JPEG, WebP, AVIF';

  function filterSingleLine(text) {
    return text.replace(/\s/g, ' ').replace(/\s\s+/g, ' ');
  }

  // @relation(SDOC-LLR-225, scope=range_start)
  //
  // Field text and writing into a field.
  //
  // A script that changes the text of a field writes through writeText(), so
  // that the browser records the change in its undo history: Ctrl+Z undoes
  // the write, and the undo of the edits before it keeps working. The browser
  // does not record a DOM change made by a script (insertNode(), nodeValue,
  // replaceChildren()), and its history then refers to nodes that are gone.
  //
  // writeText() selects the range and writes HTML-escaped text with
  // execCommand('insertHTML'). The field stays plain text in both Chrome and
  // Firefox. writeText() does not use execCommand('insertText'): in Chrome, a
  // multi-line text written at the end of a field gets an extra line break
  // after it.
  //

  // Text nodes and <br> elements make up the field text, as in innerText.
  // `root` is a field or a fragment of it.
  function walkFieldText(root, visit) {
    const walker = document.createTreeWalker(
      root,
      NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT,
    );
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (node.nodeType === Node.TEXT_NODE) {
        if (visit(node, node.nodeValue) === false) return;
      } else if (visit(node, node.nodeName === 'BR' ? '\n' : '') === false) {
        return;
      }
    }
  }

  function fieldText(root) {
    let text = '';
    walkFieldText(root, (node, nodeText) => {
      text += nodeText;
    });
    return text;
  }

  // The DOM position of a text offset in the field.
  function domPosition(editable, offset) {
    let rest = offset;
    let position = null;
    walkFieldText(editable, (node, nodeText) => {
      if (node.nodeType === Node.TEXT_NODE && rest <= nodeText.length) {
        position = [node, rest];
      } else if (node.nodeName === 'BR' && rest === 0) {
        position = [node.parentNode, [...node.parentNode.childNodes].indexOf(node)];
      } else {
        rest -= nodeText.length;
        return true;
      }
      return false;
    });
    return position ?? [editable, editable.childNodes.length];
  }

  function textOffset(editable, container, offset) {
    const range = document.createRange();
    range.setStart(editable, 0);
    range.setEnd(container, offset);
    return fieldText(range.cloneContents()).length;
  }

  // The selection in the field as text offsets { from, to }, or null if the
  // selection is not in the field.
  function textSelection(editable) {
    const selection = window.getSelection();
    if (!selection.rangeCount) return null;
    const range = selection.getRangeAt(0);
    if (!editable.contains(range.startContainer) ||
      !editable.contains(range.endContainer)) return null;
    return {
      from: textOffset(editable, range.startContainer, range.startOffset),
      to: textOffset(editable, range.endContainer, range.endOffset),
    };
  }

  // Replaces the text in [from, to) of the field with `text` and puts the
  // caret after it. The browser fires the 'input' event.
  //
  // The browser writes only into the focused field. If another element has
  // the focus, the field gets the focus for the write, and the other element
  // gets it back with its selection, so the caret stays where the user is.
  //
  // A write that reaches the end of the field starts right after a character
  // that is not a line break, and the line breaks it moves over are written
  // again. Firefox otherwise moves the line break before the range to the end
  // of the field.
  function writeText(editable, from, to, text) {
    const active = document.activeElement;
    const selection = window.getSelection();
    const saved = active !== editable && selection.rangeCount ?
      selection.getRangeAt(0).cloneRange() :
      null;
    if (active !== editable) {
      editable.focus({
        preventScroll: true
      });
    }

    const current = fieldText(editable);
    let start = from;
    let written = text;
    if (to === current.length) {
      while (start > 0 && current[start - 1] === '\n') {
        start--;
        written = `\n${written}`;
      }
    }
    const range = document.createRange();
    range.setStart(...domPosition(editable, start));
    range.setEnd(...domPosition(editable, to));
    selection.removeAllRanges();
    selection.addRange(range);
    const escaped = document.createElement('div');
    escaped.textContent = written;
    document.execCommand('insertHTML', false, escaped.innerHTML);

    if (active === editable) return;
    if (active && active !== document.body) {
      active.focus({
        preventScroll: true
      });
    } else {
      editable.blur();
    }
    if (saved) {
      selection.removeAllRanges();
      selection.addRange(saved);
    }
  }

  // Changes the text of the field to `text` with one write of the changed
  // part only: the parts that the old and the new text share at the start
  // and at the end stay. Returns false if the text is the same.
  //
  // The shared end is cut first, so a line break at the end of both texts
  // stays out of the write: Chrome cannot delete the last line break of a
  // field.
  function setText(editable, text) {
    const current = fieldText(editable);
    let end = 0;
    while (
      end < current.length &&
      end < text.length &&
      current[current.length - 1 - end] === text[text.length - 1 - end]
    ) {
      end++;
    }
    let start = 0;
    while (
      start < current.length - end &&
      start < text.length - end &&
      current[start] === text[start]
    ) {
      start++;
    }
    if (start === current.length - end && start === text.length - end) return false;
    writeText(editable, start, current.length - end, text.slice(start, text.length - end));
    return true;
  }

  window.StrictDoc.editableField = {
    setText,
    textSelection,
    writeText,
  };
  // @relation(SDOC-LLR-225, scope=range_end)

  // @relation(SDOC-LLR-214, scope=range_start)
  function getImageStem(path) {
    return getImageFilename(path).replace(/\.[^/.]+$/, '');
  }

  function getImageFilename(path) {
    return path.split('/').pop().replace(/ /g, '_');
  }

  function getDirectImageUri(wildcardUri, filename) {
    if (!wildcardUri.endsWith('.*')) return wildcardUri;
    const extension = filename.match(/\.[^.]+$/)?.[0] || '';
    return `${wildcardUri.slice(0, -1)}${extension.slice(1)}`;
  }

  function replaceDirectImageUris(editable, wildcardUri) {
    if (!wildcardUri.endsWith('.*')) return false;

    const uriPrefix = wildcardUri.slice(0, -1);
    const directUris = [...SUPPORTED_IMAGE_FORMATS.keys()].map(
      (extension) => `${uriPrefix}${extension.slice(1)}`
    );
    const textNodes = [];
    const walker = document.createTreeWalker(
      editable,
      NodeFilter.SHOW_TEXT,
    );
    while (walker.nextNode()) textNodes.push(walker.currentNode);

    let replaced = false;
    for (const textNode of textNodes) {
      let text = textNode.nodeValue;
      for (const directUri of directUris) {
        if (!text.includes(directUri)) continue;
        text = text.replaceAll(directUri, wildcardUri);
        replaced = true;
      }
      textNode.nodeValue = text;
    }
    return replaced;
  }

  function isSupportedImageFile(file) {
    const extensionMatch = file.name.toLowerCase().match(/\.[^.]+$/);
    if (!extensionMatch) return false;
    return SUPPORTED_IMAGE_FORMATS.get(extensionMatch[0]) === file.type;
  }

  function showImageUploadToast(testId, lines, closeTestId = `${testId}-close`) {
    const toast = document.createElement('sdoc-toast');
    // toast.className = 'toast';
    toast.dataset.testid = testId;

    const message = document.createElement('div');
    for (const line of lines) {
      const lineElement = document.createElement('div');
      lineElement.append(line);
      message.appendChild(lineElement);
    }

    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'toast-close';
    closeButton.dataset.testid = closeTestId;
    closeButton.setAttribute('aria-label', 'Close');
    closeButton.textContent = '×';

    toast.append(message, closeButton);
    document.querySelector('.mars')?.appendChild(toast);

    const onOutsideClick = (event) => {
      if (!toast.contains(event.target)) removeToast();
    };
    const removeToast = () => {
      toast.remove();
      document.removeEventListener('click', onOutsideClick);
    };

    closeButton.addEventListener('click', (event) => {
      event.stopPropagation();
      removeToast();
    });
    document.addEventListener('click', onOutsideClick);
  }

  function createHighlightedText(prefix, text, className) {
    const fragment = document.createDocumentFragment();
    fragment.append(prefix);
    const highlight = document.createElement('code');
    highlight.className = className;
    highlight.textContent = text;
    fragment.append(highlight);
    return fragment;
  }

  function showUnsupportedFormatToast(files) {
    const filenames = files.map((file) => file.name).join(', ');
    const label = files.length === 1 ?
      'Unsupported format: ' :
      'Unsupported formats: ';
    showImageUploadToast(
      'unsupported-image-format-message',
      [
        createHighlightedText(label, `${filenames}.`, 'toast-warn'),
        createHighlightedText(
          'You can use ',
          `${SUPPORTED_IMAGE_FORMAT_NAMES}.`,
          'toast-loud',
        ),
      ],
      'unsupported-image-format-close',
    );
  }

  function showUploadFailedToast(files, errorMessage) {
    const filenames = files.map((file) => file.name).join(', ');
    showImageUploadToast('image-upload-failed-message', [
      createHighlightedText(
        'Image upload failed: ',
        `${filenames}.`,
        'toast-warn',
      ),
      errorMessage,
    ]);
  }

  function showImagesUpdatedToast(files) {
    const filenames = files.map((file) => file.name).join(', ');
    const label = files.length === 1 ?
      'Previously added image updated: ' :
      'Previously added images updated: ';
    showImageUploadToast('image-upload-updated-message', [
      createHighlightedText(label, `${filenames}.`, 'toast-loud'),
    ]);
  }

  async function uploadSupportedImages(editable, files) {
    const supportedFiles = files.filter(isSupportedImageFile);
    const unsupportedFiles = files.filter((file) => !isSupportedImageFile(file));

    if (unsupportedFiles.length > 0) {
      showUnsupportedFormatToast(unsupportedFiles);
    }
    if (supportedFiles.length > 0) {
      await handleAssetUpload(editable, supportedFiles);
    }
  }

  async function handleImagePaste(editable, event) {
    const clipboardItems = (event.clipboardData ||
      event.originalEvent.clipboardData).items;
    const pastedFiles = [];

    for (const clipboardItem of clipboardItems) {
      let file = clipboardItem.getAsFile();
      if (!file) continue;

      // Give generic clipboard filenames a unique name.
      if (file.name === 'image.png' || file.name === 'image.jpg') {
        const extension = file.type === 'image/jpeg' ? '.jpg' : '.png';
        const randomId = typeof crypto !== 'undefined' && crypto.randomUUID ?
          crypto.randomUUID().substring(0, 8) :
          Date.now().toString(36);
        const newName = `pasted_${randomId}${extension}`;
        file = new File([file], newName, {
          type: file.type
        });
      }
      pastedFiles.push(file);
    }

    if (pastedFiles.length === 0) return false;

    // If the clipboard contains files, validate and handle them here.
    await uploadSupportedImages(editable, pastedFiles);
    return true;
  }

  // An upload placeholder is an empty element with a label from CSS. The
  // field text, which the form sends, does not include it, and the user can
  // only delete it as a whole. When the upload ends, the script writes the
  // image reference in place of the placeholder. If the user deletes the
  // placeholder before that, the script writes the reference where the
  // placeholder was.
  //
  // For each field with running uploads: { text, placeholders }. `text` is
  // the field text at the last update, and each placeholder keeps its text
  // offset in the field. The offset of a deleted placeholder moves with the
  // text changes before it.
  const uploadPlaceholders = new Map();

  function createUploadPlaceholder(stem) {
    const element = document.createElement('sdoc-image-upload-placeholder');
    element.contentEditable = 'false';
    element.dataset.label = `Uploading ${stem}...`;
    element.dataset.testid = 'image-upload-placeholder';
    return element;
  }

  function textOffsetBefore(editable, element) {
    let offset = 0;
    walkFieldText(editable, (node, nodeText) => {
      if (node === element) return false;
      offset += nodeText.length;
    });
    return offset;
  }

  function insertTextAt(editable, offset, text) {
    let rest = offset;
    let inserted = false;
    walkFieldText(editable, (node, nodeText) => {
      if (node.nodeType === Node.TEXT_NODE && rest <= nodeText.length) {
        node.insertData(rest, text);
      } else if (node.nodeName === 'BR' && rest === 0) {
        node.before(text);
      } else {
        rest -= nodeText.length;
        return true;
      }
      inserted = true;
      return false;
    });
    if (!inserted) editable.append(text);
  }

  function trackUploadPlaceholders(editable, placeholders) {
    if (!uploadPlaceholders.has(editable)) {
      uploadPlaceholders.set(editable, {
        text: fieldText(editable),
        placeholders: new Set(),
      });
    }
    const tracked = uploadPlaceholders.get(editable);
    for (const placeholder of placeholders) tracked.placeholders.add(placeholder);
    updateUploadPlaceholderOffsets(editable);
  }

  function updateUploadPlaceholderOffsets(editable) {
    const tracked = uploadPlaceholders.get(editable);
    if (!tracked) return;
    const text = fieldText(editable);
    const previous = tracked.text;
    let commonPrefix = 0;
    while (
      commonPrefix < previous.length &&
      commonPrefix < text.length &&
      previous[commonPrefix] === text[commonPrefix]
    ) {
      commonPrefix++;
    }
    for (const placeholder of tracked.placeholders) {
      if (editable.contains(placeholder.element)) {
        placeholder.offset = textOffsetBefore(editable, placeholder.element);
      } else if (commonPrefix < placeholder.offset) {
        placeholder.offset = Math.max(
          commonPrefix,
          placeholder.offset + text.length - previous.length,
        );
      }
    }
    tracked.text = text;
  }

  // Adds the line breaks that put an empty line between the reference and
  // the text before and after it, so that the markup reads the reference as
  // a block of its own. A line with spaces only counts as empty. At the start
  // or the end of the field, the reference needs no empty line.
  function separateBlock(text, offset, reference) {
    const before = text.slice(0, offset);
    const after = text.slice(offset);
    const breaksBefore = before.match(/(\n[ \t]*)*$/)[0].split('\n').length - 1;
    const breaksAfter = after.match(/^([ \t]*\n)*/)[0].split('\n').length - 1;
    const needBefore = before.trim() ? Math.max(0, 2 - breaksBefore) : 0;
    const needAfter = after.trim() ? Math.max(0, 2 - breaksAfter) : 0;
    return '\n'.repeat(needBefore) + reference + '\n'.repeat(needAfter);
  }

  // Writes the reference in place of the placeholder, or only removes the
  // placeholder if the reference is null. Does nothing for a placeholder
  // that is already replaced.
  function replaceUploadPlaceholder(editable, placeholder, reference) {
    const tracked = uploadPlaceholders.get(editable);
    if (!tracked?.placeholders.has(placeholder)) return;
    tracked.placeholders.delete(placeholder);

    const connected = editable.contains(placeholder.element);
    const offset = connected ?
      textOffsetBefore(editable, placeholder.element) :
      placeholder.offset;
    const text = reference === null ?
      '' :
      separateBlock(fieldText(editable), offset, reference);
    if (connected) {
      if (text) placeholder.element.replaceWith(text);
      else placeholder.element.remove();
    } else if (text) {
      insertTextAt(editable, placeholder.offset, text);
    }

    if (tracked.placeholders.size === 0) {
      uploadPlaceholders.delete(editable);
    } else {
      updateUploadPlaceholderOffsets(editable);
    }
  }

  async function handleAssetUpload(editable, files) {
    const uniqueFilenames = [...new Set(
      Array.from(files).map((file) => getImageFilename(file.name))
    )];
    if (uniqueFilenames.length === 0) return;

    const form = editable.closest('form');
    const documentMid = form.querySelector('[name="document_mid"]')?.value;
    const requirementMid =
      form.querySelector('[name="requirement_mid"]')?.value;
    const documentMarkup =
      form.querySelector('[name="document_markup"]')?.value || 'RST';
    if (!documentMid || !requirementMid) {
      console.error('Missing document_mid or requirement_mid for file upload.');
      return;
    }

    // Immediate feedback to inform the user that the upload has started.
    const placeholders = uniqueFilenames.map((filename) => ({
      filename,
      element: createUploadPlaceholder(getImageStem(filename)),
      offset: 0,
    }));

    // Insert the placeholders into the DOM
    const selection = window.getSelection();
    let insertedIntoSelection = false;
    if (selection?.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      if (editable.contains(range.commonAncestorContainer)) {
        range.deleteContents();
        // insertNode() inserts new nodes before the previous one,
        // so iterate in reverse order.
        for (let index = placeholders.length - 1; index >= 0; index--) {
          range.insertNode(placeholders[index].element);
        }
        insertedIntoSelection = true;
      }
    }

    if (!insertedIntoSelection) {
      for (const placeholder of placeholders) {
        editable.appendChild(placeholder.element);
      }
    }
    trackUploadPlaceholders(editable, placeholders);
    // The placeholders can replace a selected text. The DOM change fires no
    // 'input' event, so fire it: the hidden field must not keep the deleted
    // text until the upload ends.
    editable.dispatchEvent(new Event('input', {
      bubbles: true
    }));

    // Build multipart request.
    const formData = new FormData();
    for (const file of files) {
      formData.append('uploaded_files', file);
    }

    const uploadUrl =
      '/actions/document/upload_asset' +
      `?document_mid=${encodeURIComponent(documentMid)}` +
      `&requirement_mid=${encodeURIComponent(requirementMid)}`;

    try {
      const response = await fetch(uploadUrl, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        // Try to extract the JSON detail message from FastAPI
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail || 'Network response was not ok';
        throw new Error(errorMessage);
      }

      const data = await response.json();
      const imagesByFilename = data.images;
      let currentText = editable.innerText;
      const insertedUris = new Set();
      const updatedFilenames = new Set();

      // For each returned image URI:
      // - replace the placeholder with the markup-specific image reference;
      // - remove the placeholder if the image is already referenced;
      // - insert a shared wildcard URI only once for a multi-file pair.
      for (const placeholder of placeholders) {
        const {
          filename
        } = placeholder;
        const uri = imagesByFilename[filename];
        if (!uri) continue;

        if (
          documentMarkup === 'RST' &&
          replaceDirectImageUris(editable, uri)
        ) {
          replaceUploadPlaceholder(editable, placeholder, null);
          currentText = editable.innerText;
          continue;
        }

        const referenceUri = documentMarkup === 'RST' ?
          uri :
          getDirectImageUri(uri, filename);

        if (currentText.includes(referenceUri)) {
          // The image is already referenced in the document.
          // The user has re-uploaded, and the backend has overwritten the file,
          // so we just clean up the placeholder.
          replaceUploadPlaceholder(editable, placeholder, null);
          updatedFilenames.add(filename);
          continue;
        }

        if (insertedUris.has(referenceUri)) {
          replaceUploadPlaceholder(editable, placeholder, null);
          continue;
        }

        // Otherwise, this is a newly uploaded image, we add an image directive
        // suitable to the documentMarkup mode.
        let reference;
        switch (documentMarkup) {
          case 'RST':
            reference = `.. image:: ${referenceUri}`;
            break;
          case 'HTML':
            reference = `<img src="${referenceUri}" />`;
            break;
          case 'Markdown':
            reference = `![](${referenceUri})`;
            break;
        }
        replaceUploadPlaceholder(editable, placeholder, reference);
        insertedUris.add(referenceUri);
      }
      if (updatedFilenames.size > 0) {
        showImagesUpdatedToast(
          files.filter((file) =>
            updatedFilenames.has(getImageFilename(file.name))
          ),
        );
      }
    } catch (error) {
      console.error('Upload failed', error);
      showUploadFailedToast(files, error.message);
    } finally {
      // Removes the placeholders that are left: the ones of a failed upload,
      // or of a file that the response does not mention.
      for (const placeholder of placeholders) {
        replaceUploadPlaceholder(editable, placeholder, null);
      }
      // Fire a synthetic bubbling 'input' event to sync the hidden field.
      editable.dispatchEvent(new Event('input', {
        bubbles: true
      }));
    }
  }

  function findMultilineEditable(target) {
    const editable = target.closest?.(SEL_EDITABLE);
    if (!editable || editable.dataset.fieldType === 'singleline') return null;
    return editable;
  }
  // @relation(SDOC-LLR-214, scope=range_end)

  document.addEventListener('paste', async (event) => {
    const editable = event.target.closest?.(SEL_EDITABLE);
    if (!editable) return;
    event.preventDefault();

    const isSingle = editable.dataset.fieldType === 'singleline';

    // Read the text before the first await. Firefox returns an empty string
    // from getData() once the synchronous part of the event handler is over.
    const clipboardText = (event.clipboardData || window.clipboardData).getData('text');

    // @relation(SDOC-LLR-214, scope=range_start)
    // For multiline, we also handle copy paste of images here.
    if (!isSingle && await handleImagePaste(editable, event)) return;
    // @relation(SDOC-LLR-214, scope=range_end)

    const text = isSingle ? filterSingleLine(clipboardText) : clipboardText;

    // The write fires the 'input' event: the input listener below syncs the
    // hidden field, and other scripts, such as the field widgets, see the
    // new text.
    const selected = textSelection(editable);
    if (selected) writeText(editable, selected.from, selected.to, text);
  });

  // A contenteditable field is not a form control, so the form sends the
  // hidden field, an input next to it. Every change of the field comes
  // here as an 'input' event, and the listener copies the text into the
  // hidden field.
  document.addEventListener('input', (event) => {
    const editable = event.target.closest?.(SEL_EDITABLE);
    if (!editable) return;

    const isSingle = editable.dataset.fieldType === 'singleline';
    const hidden = editable.nextElementSibling;

    const editedText = editable.innerText;
    hidden.value = isSingle ? filterSingleLine(editedText) : editedText;

    updateUploadPlaceholderOffsets(editable);
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Enter') return;
    const editable = event.target.closest?.(SEL_EDITABLE);
    if (!editable) return;
    if (editable.dataset.fieldType !== 'singleline') return;
    event.preventDefault();
  });

  // @relation(SDOC-LLR-214, scope=range_start)

  // Image drag-and-drop is handled at two levels.
  // Document-level (1) listeners process images dropped into multiline editable
  // fields. Window-level (2) listeners reject drops elsewhere to prevent
  // the browser from leaving the current page and opening the dropped file.

  // * (1)
  // For multiline, we also handle drag-and-drop of images here.

  document.addEventListener('dragenter', (event) => {
    const editable = findMultilineEditable(event.target);
    if (!editable) return;

    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';
    editable.classList.add('is-dragging');
  });

  document.addEventListener('dragleave', (event) => {
    const editable = findMultilineEditable(event.target);
    if (!editable) return;

    event.preventDefault();
    editable.classList.remove('is-dragging');
  });

  document.addEventListener('dragover', (event) => {
    const editable = findMultilineEditable(event.target);
    if (!editable) return;

    event.preventDefault();
    event.stopPropagation();
    event.dataTransfer.dropEffect = 'copy';
  });

  document.addEventListener('drop', async (event) => {
    const editable = findMultilineEditable(event.target);
    if (!editable) return;

    event.preventDefault();
    editable.classList.remove('is-dragging');

    // Validate every dropped file before starting an upload.
    const droppedFiles = Array.from(event.dataTransfer.files);
    if (droppedFiles.length === 0) return;

    await uploadSupportedImages(editable, droppedFiles);
  });

  // * (2)
  // Prevent the browser from opening files dropped outside multiline editable fields.

  window.addEventListener('dragenter', (event) => {
    if (findMultilineEditable(event.target)) return;
    event.preventDefault();
    event.dataTransfer.dropEffect = 'none';
  });

  window.addEventListener('dragover', (event) => {
    if (findMultilineEditable(event.target)) return;
    event.preventDefault();
    event.dataTransfer.dropEffect = 'none';
  });

  window.addEventListener('drop', (event) => {
    if (findMultilineEditable(event.target)) return;
    event.preventDefault();
  });
  // @relation(SDOC-LLR-214, scope=range_end)

})();
