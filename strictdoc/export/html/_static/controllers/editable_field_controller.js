// Prevent the browser from opening files dropped outside our editable field.
window.addEventListener("dragenter", (e) => {
  e.preventDefault();
  e.dataTransfer.dropEffect = "none";
}, false);

window.addEventListener("dragover", (e) => {
  e.preventDefault();
  e.dataTransfer.dropEffect = "none";
}, false);

window.addEventListener("drop", (e) => {
  e.preventDefault();
}, false);

(() => {

  class EditableField extends Stimulus.Controller {
    static targets = ["name"];

    connect() {
      // this.element is the DOM element to which the controller is connected to.
      const editable = this.element;

      const fieldType = editable.getAttribute('data-field-type');
      const isSingle = !!(fieldType === 'singleline');
      const hidden = editable.nextElementSibling;

      editable.addEventListener('paste', async (event) => {
        event.preventDefault();

        if (!isSingle) {
          // For multiline, we also handle copy paste of images here.
          const isImagePasted = await handleImagePaste(editable, event);
          if (isImagePasted) return;
        }

        const clipboardText = (event.clipboardData || window.clipboardData).getData('text');
        const text = isSingle ? filterSingleLine(clipboardText) : clipboardText;

        const selection = window.getSelection();

        if (selection.rangeCount) {
          selection.deleteFromDocument();
          selection.getRangeAt(0).insertNode(document.createTextNode(text));
        }

        hidden.value = editable.innerText;
      });

      editable.addEventListener('input', (event) => {
        const editedText = editable.innerText;
        const text = isSingle ? filterSingleLine(editedText) : editedText;

        hidden.value = text;
      });

      if (isSingle) {
        editable.addEventListener('keydown', (event) => {
          if (event.key === 'Enter') {
            event.preventDefault();
          }
        });
      } else {
        // For multiline, we also handle drag-and-drop of images here.
        handleImageDragAndDrop(editable)
      }
    }
  }

  Stimulus.application.register("editablefield", EditableField);

  function filterSingleLine(text) {
    return text.replace(/\s/g, ' ').replace(/\s\s+/g, ' ')
  }

  function getImageStem(path) {
    const filename = path.split('/').pop();
    return filename.replace(/\.[^/.]+$/, "").replace(/ /g, "_");
  }

  async function handleImagePaste(editable, event) {
    const pasted_items = (event.clipboardData || event.originalEvent.clipboardData).items;
    const imageFiles = [];

    for (const pasted_item of pasted_items) {
      if (pasted_item.type.indexOf("image") !== -1) {
        let file = pasted_item.getAsFile();
        if (file) {
          // rename the generic pasted filenames to something unique
          if (file.name === "image.png" || file.name === "image.jpg") {
            const ext = file.type === "image/jpeg" ? ".jpg" : ".png";
            const random_uuid = typeof crypto !== 'undefined' && crypto.randomUUID
              ? crypto.randomUUID().substring(0, 8)
              : Date.now().toString(36);

            const newName = `pasted_${random_uuid}${ext}`;
            file = new File([file], newName, { type: file.type });
          }
          imageFiles.push(file);
        }
      }
    }

    // If we found images, handle them as an upload
    if (imageFiles.length > 0) {
      await handleAssetUpload(editable, imageFiles);
      return true;
    }
    return false
  }

  async function handleImageDragAndDrop(editable) {
    editable.addEventListener('dragenter', (event) => {
      if (editable.dataset.editable === 'single' || event.currentTarget !== editable) return;
      event.preventDefault();
      event.dataTransfer.dropEffect = "copy";
      editable.classList.add('is-dragging');
    });
    editable.addEventListener('dragleave', (event) => {
      if (event.currentTarget !== editable) return;
      event.preventDefault();
        editable.classList.remove('is-dragging');
    });
    editable.addEventListener('dragover', (event) => {
      event.preventDefault();
      event.stopPropagation();
      event.dataTransfer.dropEffect = "copy";
    });
    editable.addEventListener('drop', async (event) => {
      event.preventDefault();
      editable.classList.remove('is-dragging');
      if (event.currentTarget !== editable) {
        return;
      }
      // Only accept images here for now.
      const files = Array.from(event.dataTransfer.files)
        .filter(file => file.type.startsWith('image/'));
      
      await handleAssetUpload(editable, files);
    });
  }

  async function handleAssetUpload(editable, files) {
    const uniqueStems = [...new Set(Array.from(files).map(file => getImageStem(file.name)))];
    if (uniqueStems.length === 0) return;

    const document_mid = document.getElementById('document_mid').value;
    const requirement_mid = document.getElementById('requirement_mid').value;
    if (!document_mid || !requirement_mid) {
        console.error("Missing document_mid or requirement_mid for file upload.")
        return;
    }

    // Immediate feedback to inform the user that the upload has started.
    // Create TextNodes instead of plain strings for placeholders.
    const placeholders = uniqueStems.map(stem => {
      const node = document.createTextNode(`\n.. image:: Uploading ${stem}...\n`);
      return { stem, node };
    });

    //  Insert the placeholder nodes into the DOM
    const selection = window.getSelection();
    let insertedIntoSelection = false;

    if (selection?.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      if (editable.contains(range.commonAncestorContainer)) {
        range.deleteContents();
        // Insert nodes (working backwards so they appear in correct order)
        for (let i = placeholders.length - 1; i >= 0; i--) {
            range.insertNode(placeholders[i].node);
        }
        insertedIntoSelection = true;
      }
    }
    if (!insertedIntoSelection) {
      const separator = editable.innerText.length > 0 ? "\n" : "";
      if (separator) editable.appendChild(document.createTextNode(separator));
      placeholders.forEach(p => editable.appendChild(p.node));
    }

    // Build multipart request.
    const formData = new FormData();
    for (const file of files) {
      formData.append('uploaded_files', file);
    }

    const uploadUrl =
      `/actions/document/upload_asset` +
      `?document_mid=${encodeURIComponent(document_mid)}` +
      `&requirement_mid=${encodeURIComponent(requirement_mid)}`;

    try {
      const response = await fetch(uploadUrl, { 
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();
      const imagesByStem = data.images;

      // Replace the placeholders for the real ReST paths.
      for (const { stem, node } of placeholders) {
        const uri = imagesByStem[stem];
        if (uri) {
          node.nodeValue = `\n.. image:: ${uri}\n`;
        }
      }

    } catch (error) {
      console.error("Upload failed", error);
      // Update node to show failure
      placeholders.forEach(p => {
        p.node.nodeValue = `\n**[Image upload failed: ${p.stem}]**\n`;
      });
    } finally {
      // Fire a syntetic 'input' event to sync content.
      editable.dispatchEvent(new Event('input'));
    }
  }
})();
