// Delegated document-level listeners for every contenteditable field.
// The event types bubble, so no per-element registration (StrictDoc.onInsert)
// is needed - unlike the click-only controls, these only ever need to know
// about the element an event already fired on.

(() => {

  const SEL_EDITABLE = '[data-js-editable-field]';
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
  let removeUnsupportedFormatToast = null;

  function filterSingleLine(text) {
    return text.replace(/\s/g, ' ').replace(/\s\s+/g, ' ');
  }

  // @relation(SDOC-LLR-214, scope=range_start)
  function getImageStem(path) {
    const filename = path.split('/').pop();
    return filename.replace(/\.[^/.]+$/, '').replace(/ /g, '_');
  }

  function isSupportedImageFile(file) {
    const extensionMatch = file.name.toLowerCase().match(/\.[^.]+$/);
    if (!extensionMatch) return false;
    return SUPPORTED_IMAGE_FORMATS.get(extensionMatch[0]) === file.type;
  }

  function showUnsupportedFormatToast(files) {
    removeUnsupportedFormatToast?.();

    const filenames = files.map((file) => file.name).join(', ');
    const toast = document.createElement('sdoc-toast');
    // toast.className = 'toast';
    toast.dataset.testid = 'unsupported-image-format-message';

    const message = document.createElement('div');
    message.innerHTML =
      `<div>Unsupported format: <code class="toast-warn">${filenames}.</code></div>` +
      `<div>You can use <code class="toast-loud">${SUPPORTED_IMAGE_FORMAT_NAMES}</code>.</div>`;

    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'toast-close';
    closeButton.dataset.testid = 'unsupported-image-format-close';
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
      if (removeUnsupportedFormatToast === removeToast) {
        removeUnsupportedFormatToast = null;
      }
    };
    removeUnsupportedFormatToast = removeToast;

    closeButton.addEventListener('click', (event) => {
      event.stopPropagation();
      removeToast();
    });
    document.addEventListener('click', onOutsideClick);
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
        const randomId = typeof crypto !== 'undefined' && crypto.randomUUID
          ? crypto.randomUUID().substring(0, 8)
          : Date.now().toString(36);
        const newName = `pasted_${randomId}${extension}`;
        file = new File([file], newName, { type: file.type });
      }
      pastedFiles.push(file);
    }

    if (pastedFiles.length === 0) return false;

    // If the clipboard contains files, validate and handle them here.
    await uploadSupportedImages(editable, pastedFiles);
    return true;
  }

  async function handleAssetUpload(editable, files) {
    const uniqueStems = [...new Set(
      Array.from(files).map((file) => getImageStem(file.name))
    )];
    if (uniqueStems.length === 0) return;

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
    // Create TextNodes instead of plain strings for placeholders.
    const placeholders = uniqueStems.map((stem) => ({
      stem,
      node: document.createTextNode(`\n.. image:: Uploading ${stem}...\n`),
    }));

    // Insert the placeholder nodes into the DOM
    const selection = window.getSelection();
    let insertedIntoSelection = false;
    if (selection?.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      if (editable.contains(range.commonAncestorContainer)) {
        range.deleteContents();
        // insertNode() inserts new nodes before the previous one,
        // so iterate in reverse order.
        for (let index = placeholders.length - 1; index >= 0; index--) {
          range.insertNode(placeholders[index].node);
        }
        insertedIntoSelection = true;
      }
    }

    if (!insertedIntoSelection) {
      if (editable.innerText.length > 0) {
        editable.appendChild(document.createTextNode('\n'));
      }
      for (const placeholder of placeholders) {
        editable.appendChild(placeholder.node);
      }
    }

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
      const imagesByStem = data.images;
      const currentText = editable.innerText;

      // For each returned image URI:
      // - replace the placeholder with the markup-specific image reference;
      // - remove the placeholder instead if the image is already referenced.
      for (const { stem, node } of placeholders) {
        const uri = imagesByStem[stem];
        if (!uri) continue;

        if (currentText.includes(uri)) {
          // The image is already referenced in the document.
          // The user has re-uploaded, and the backend has overwritten the file,
          // so we just clean up the placeholder.
          node.nodeValue = '';
          continue;
        }

        // Otherwise, this is a newly uploaded image, we add an image directive
        // suitable to the documentMarkup mode.
        switch (documentMarkup) {
          case 'RST':
            node.nodeValue = `\n.. image:: ${uri}\n`;
            break;
          case 'HTML':
            node.nodeValue = `\n<img src="${uri}" />\n`;
            break;
          case 'Markdown':
            node.nodeValue = `\n![](${uri})\n`;
            break;
        }
      }
    } catch (error) {
      console.error('Upload failed', error);
      // Update node to show failure
      for (const placeholder of placeholders) {
        placeholder.node.nodeValue =
          `\n**[Image upload failed: ${error.message}]**\n`;
      }
    } finally {
      // Fire a synthetic bubbling 'input' event to sync the hidden field.
      editable.dispatchEvent(new Event('input', { bubbles: true }));
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
    const hidden = editable.nextElementSibling;

    // @relation(SDOC-LLR-214, scope=range_start)
    // For multiline, we also handle copy paste of images here.
    if (!isSingle && await handleImagePaste(editable, event)) return;
    // @relation(SDOC-LLR-214, scope=range_end)

    const clipboardText = (event.clipboardData || window.clipboardData).getData('text');
    const text = isSingle ? filterSingleLine(clipboardText) : clipboardText;

    const selection = window.getSelection();
    if (selection.rangeCount) {
      selection.deleteFromDocument();
      selection.getRangeAt(0).insertNode(document.createTextNode(text));
    }

    hidden.value = editable.innerText;
  });

  document.addEventListener('input', (event) => {
    const editable = event.target.closest?.(SEL_EDITABLE);
    if (!editable) return;

    const isSingle = editable.dataset.fieldType === 'singleline';
    const hidden = editable.nextElementSibling;

    const editedText = editable.innerText;
    hidden.value = isSingle ? filterSingleLine(editedText) : editedText;
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
