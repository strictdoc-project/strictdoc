(() => {
  // The server renders hierarchy and placement permissions as data attributes.
  // This controller only adds interaction, so a Turbo-inserted modal can be
  // initialized without rebuilding or inferring the project tree in JavaScript.
  const ROOT_SELECTOR = '[data-js-move-node-tree]';
  const ITEM_SELECTOR = '[data-js-move-node-tree-item]';
  const DOCUMENT_SELECTOR = '[data-js-move-node-tree-document]';
  const TARGET_SELECTOR = '[data-js-move-node-tree-target]';
  const COLLAPSE_SELECTOR = '[data-js-move-node-tree-collapse]';
  const CHILDREN_SELECTOR = ':scope > [data-js-move-node-tree-children]';
  const CONFIRMATION_SELECTOR = '[data-js-move-node-tree-confirmation]';
  const NEW_LOCATION_LINK_SELECTOR =
    '[data-js-move-node-tree-new-location]';
  const INITIALIZED_ATTRIBUTE = 'data-js-move-node-tree-initialized';
  const LABEL_ATTRIBUTE = 'data-js-move-node-tree-label';
  const PLACEMENT_ATTRIBUTE = 'data-js-move-node-tree-placement';
  const TARGET_MID_ATTRIBUTE = 'data-js-move-node-tree-target-mid';
  const TARGET_PLACEMENTS_ATTRIBUTE =
    'data-js-move-node-tree-target-placements';
  const NODE_TYPE_ATTRIBUTE = 'data-js-move-node-tree-node-type';
  const CHILD_PLACEMENT_OFFSET_PX = 32;

  function initializeMoveNodeTree(treeRoot) {
    if (treeRoot.hasAttribute(INITIALIZED_ATTRIBUTE)) return;
    treeRoot.setAttribute(INITIALIZED_ATTRIBUTE, '');

    const statusElement = treeRoot.querySelector(
      '[data-js-move-node-tree-status]'
    );
    const confirmationElement = treeRoot.querySelector(CONFIRMATION_SELECTOR);
    const confirmationMessageElement = confirmationElement.querySelector(
      '[data-js-move-node-tree-confirmation-message]'
    );
    const confirmationMessageLabelElement = confirmationMessageElement.querySelector(
      '[data-js-move-node-tree-confirm-message-label]'
    );
    const confirmationDocumentTitleElement = confirmationMessageElement.querySelector(
      '[data-js-move-node-tree-confirm-target-document-title]'
    );
    const confirmationTargetNodeInfoElement = confirmationMessageElement.querySelector(
      '[data-js-move-node-tree-confirm-target-node-info]'
    );
    const confirmationPlacementLabelElement = confirmationMessageElement.querySelector(
      '[data-js-move-node-tree-confirm-placement-label]'
    );
    const confirmationTargetNodeTitleElement = confirmationMessageElement.querySelector(
      '[data-js-move-node-tree-confirm-target-node-title]'
    );
    const confirmationTargetNodeTypeElement = confirmationMessageElement.querySelector(
      '[data-js-move-node-tree-confirm-target-node-type]'
    );
    const confirmationTargetNodeTypeBadge =
      confirmationTargetNodeTypeElement.querySelector('[text]');
    const confirmButton = confirmationElement.querySelector(
      '[data-js-move-node-tree-confirm]'
    );
    const cancelButton = confirmationElement.querySelector(
      '[data-js-move-node-tree-cancel]'
    );
    let previewedItem = null;
    let previewedPlacement = null;
    let pendingMove = null;
    let focusBeforeConfirmation = null;
    let requestIsPending = false;

    function clearPlacementPreview() {
      if (previewedItem) previewedItem.removeAttribute(PLACEMENT_ATTRIBUTE);
      previewedItem = null;
      previewedPlacement = null;
    }

    function showPlacementPreview(targetRow, placement) {
      const targetItem = targetRow.closest(ITEM_SELECTOR);
      if (!targetItem || previewedItem === targetItem &&
        previewedPlacement === placement) return;

      clearPlacementPreview();
      previewedItem = targetItem;
      previewedPlacement = placement;
      targetItem.setAttribute(PLACEMENT_ATTRIBUTE, placement);

      const targetTitle = getItemTitle(targetItem);
      statusElement.textContent = `${placement} ${targetTitle}`;
    }

    function getItemTitle(treeItem) {
      return treeItem.getAttribute(LABEL_ATTRIBUTE) || '';
    }

    function getDestinationDocumentTitle(targetRow) {
      const documentItem = targetRow.closest(DOCUMENT_SELECTOR);
      return documentItem ? getItemTitle(documentItem) : '';
    }

    function fillConfirmationMessage(targetRow, placement) {
      const destinationDocumentTitle = getDestinationDocumentTitle(targetRow);
      const targetItem = targetRow.closest(ITEM_SELECTOR);
      const targetTitle = targetItem ? getItemTitle(targetItem) : '';
      const targetIsDocument = targetItem?.matches(DOCUMENT_SELECTOR);

      confirmationMessageLabelElement.textContent = targetIsDocument ?
        'Move into' : 'Move to';
      confirmationDocumentTitleElement.textContent = destinationDocumentTitle;
      confirmationDocumentTitleElement.title = destinationDocumentTitle;

      if (targetIsDocument) {
        confirmationTargetNodeInfoElement.style.display = 'none';
        confirmationPlacementLabelElement.textContent = '';
        confirmationTargetNodeTitleElement.textContent = '';
        confirmationTargetNodeTypeBadge.setAttribute('text', '');
        return;
      }

      const placementLabels = {
        before: 'before',
        after: 'after',
        child: 'inside',
      };
      confirmationTargetNodeInfoElement.style.display = 'contents';
      confirmationPlacementLabelElement.textContent =
        placementLabels[placement];
      confirmationTargetNodeTitleElement.textContent = targetTitle;
      confirmationTargetNodeTypeBadge.setAttribute(
        'text',
        targetItem?.getAttribute(NODE_TYPE_ATTRIBUTE) || ''
      );
    }

    // A placement click only records the intended request. The separate
    // confirmation step absorbs accidental clicks without changing the tree
    // or contacting the server.
    function showMoveConfirmation(targetRow, placement) {
      pendingMove = {
        targetRow,
        placement
      };
      focusBeforeConfirmation = document.activeElement;
      fillConfirmationMessage(targetRow, placement);
      confirmationElement.hidden = false;
      confirmButton.focus();
    }

    function hideMoveConfirmation() {
      confirmationElement.hidden = true;
      pendingMove = null;
      if (focusBeforeConfirmation instanceof HTMLElement) {
        focusBeforeConfirmation.focus();
      }
      focusBeforeConfirmation = null;
    }

    function getAllowedPlacements(targetRow) {
      return targetRow.getAttribute(TARGET_PLACEMENTS_ATTRIBUTE).split(' ');
    }

    // The pointer zones follow the existing TOC move control. The upper half
    // means "before". In the lower half, moving one indentation step to the
    // right means "inside" for containers; otherwise the position is "after".
    function resolvePointerPlacement(targetRow, pointerEvent) {
      const allowedPlacements = getAllowedPlacements(targetRow);
      if (allowedPlacements.length === 1) return allowedPlacements[0];

      const targetBounds = targetRow.getBoundingClientRect();
      const pointerIsInUpperHalf = pointerEvent.clientY <
        targetBounds.top + targetBounds.height / 2;
      if (pointerIsInUpperHalf && allowedPlacements.includes('before')) {
        return 'before';
      }

      const pointerIsInChildZone = pointerEvent.clientX >
        targetBounds.left + CHILD_PLACEMENT_OFFSET_PX;
      if (pointerIsInChildZone && allowedPlacements.includes('child')) {
        return 'child';
      }
      return allowedPlacements.includes('after') ? 'after' : 'child';
    }

    function submitMove(targetRow, placement) {
      if (requestIsPending) return;
      requestIsPending = true;
      treeRoot.setAttribute('aria-busy', 'true');

      const requestParameters = new URLSearchParams({
        moved_node_mid: treeRoot.getAttribute(
          'data-js-move-node-tree-moved-node-mid'
        ),
        target_mid: targetRow.getAttribute(TARGET_MID_ATTRIBUTE),
        whereto: placement,
        context_document_mid: treeRoot.getAttribute(
          'data-js-move-node-tree-context-document-mid'
        ),
      });
      const requestUrl =
        `${treeRoot.getAttribute('data-js-move-node-tree-endpoint')}` +
        `?${requestParameters}`;

      fetch(requestUrl, {
          method: 'POST',
          headers: {
            Accept: 'text/vnd.turbo-stream.html',
          },
        })
        // Validation failures use HTTP 422 but still return a Turbo stream
        // for the modal, so every completed response body must be rendered.
        .then((response) => response.text())
        .then((responseHtml) => Turbo.renderStreamMessage(responseHtml))
        .catch(() => {
          statusElement.textContent = 'The node could not be moved.';
          requestIsPending = false;
          treeRoot.removeAttribute('aria-busy');
        });
    }

    function confirmPendingMove() {
      if (!pendingMove || requestIsPending) return;
      const {
        targetRow,
        placement
      } = pendingMove;
      confirmationElement.hidden = true;
      pendingMove = null;
      submitMove(targetRow, placement);
    }

    confirmButton.addEventListener('click', confirmPendingMove);
    cancelButton.addEventListener('click', hideMoveConfirmation);
    confirmationElement.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        event.stopPropagation();
        hideMoveConfirmation();
      } else if (event.key === 'Enter') {
        event.preventDefault();
        confirmPendingMove();
      }
    });

    treeRoot.querySelectorAll(COLLAPSE_SELECTOR).forEach((collapseButton) => {
      collapseButton.addEventListener('click', (event) => {
        event.stopPropagation();
        const treeItem = collapseButton.closest(ITEM_SELECTOR);
        const childList = treeItem?.querySelector(CHILDREN_SELECTOR);
        if (!childList) return;

        const willExpand = childList.hidden;
        childList.hidden = !willExpand;
        collapseButton.setAttribute('aria-expanded', String(willExpand));

        // Keep the accessible name synchronized because the symbol itself is
        // deliberately visual-only and generated by CSS.
        const itemTitle = getItemTitle(treeItem);
        collapseButton.setAttribute(
          'aria-label',
          `${willExpand ? 'Collapse' : 'Expand'} ${itemTitle}`
        );
      });
    });

    treeRoot.querySelectorAll(TARGET_SELECTOR).forEach((targetRow) => {
      targetRow.addEventListener('pointermove', (event) => {
        showPlacementPreview(
          targetRow,
          resolvePointerPlacement(targetRow, event)
        );
      });
      targetRow.addEventListener('pointerleave', clearPlacementPreview);
      targetRow.addEventListener('click', (event) => {
        if (event.target.closest(COLLAPSE_SELECTOR)) return;
        const placement = resolvePointerPlacement(targetRow, event);
        showPlacementPreview(targetRow, placement);
        showMoveConfirmation(targetRow, placement);
      });
    });
  }

  if (!window.StrictDoc?.onInsert) {
    throw new Error('move_node_tree.js requires app_core.js.');
  }
  window.StrictDoc.onInsert(ROOT_SELECTOR, initializeMoveNodeTree);

  // The success link can point to a hash in the current document or to a node
  // in another document. Native navigation handles both, but a same-document
  // hash change does not replace the page and therefore cannot remove the
  // modal. Close it explicitly before leaving or scrolling to the destination.
  document.addEventListener('click', (event) => {
    const newLocationLink = event.target.closest?.(
      NEW_LOCATION_LINK_SELECTOR
    );
    if (!newLocationLink) return;

    event.preventDefault();
    newLocationLink.closest('[data-js-modal]')?.remove();

    const destinationUrl = new URL(newLocationLink.href);
    const destinationIsInCurrentDocument =
      destinationUrl.origin === window.location.origin &&
      destinationUrl.pathname === window.location.pathname &&
      destinationUrl.search === window.location.search;
    if (destinationIsInCurrentDocument) {
      window.location.hash = destinationUrl.hash;
      const destinationAnchor = decodeURIComponent(
        destinationUrl.hash.slice(1)
      );
      document.getElementById(destinationAnchor)?.scrollIntoView();
      return;
    }
    window.location.assign(destinationUrl.href);
  });
})();
