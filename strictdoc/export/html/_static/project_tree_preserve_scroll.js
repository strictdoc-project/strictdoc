/*
How this script works:
1. On page load, restores left project-tree scroll position from localStorage
   (if a saved value exists for the current project).
2. Persists tree scroll only when user clicks a tree link (navigation intent).
3. Applies safety fallback: if the active tree item is outside the visible
   tree viewport, scrolls it to container center.
4. Persists resulting position after fallback-centering too, so next reload
   keeps centered state.

Required DOM:
1. Project tree root:
   <div class="tree" js-project_tree_preserve_scroll="tree">...</div>
2. Scroll container created by resizable bar:
   <div js-resizable_bar-scroll="y" data-content="tree">...</div>
   If missing, script falls back to the tree parent element.
3. Tree links:
   <a class="tree_item" href="...">...</a>

Optional DOM:
1. Active/current document marker:
   <a class="tree_item" active="true">...</a>
   Used only for fallback centering. If missing, script still restores saved
   scroll, but skips active-item centering.
2. Project namespace marker:
   <div ... data-project-title="StrictDoc Documentation">...</div>
   Used to namespace localStorage key by project title, so different projects
   on the same origin do not overwrite each other's tree scroll.
*/

const TREE_ROOT_SELECTOR = "[js-project_tree_preserve_scroll]";
const SCROLL_CONTAINER_SELECTOR = "[js-resizable_bar-scroll]";
const TREE_ITEM_SELECTOR = ".tree_item[href]";
const ACTIVE_ITEM_SELECTOR = ".tree_item[active='true']";
const STORAGE_KEY_PREFIX = "strictdoc.project_tree.scroll_top";
const BOUND_ATTR = "js-project_tree_preserve_scroll-bound";

// Returns project tree root element, or null when the script should be inactive.
function findTreeRoot() {
  return document.querySelector(TREE_ROOT_SELECTOR);
}

// Finds the actual scroll container that owns tree scrollTop.
function findScrollContainer(treeRoot) {
  return (
    treeRoot.closest(SCROLL_CONTAINER_SELECTOR) ||
    treeRoot.parentElement ||
    null
  );
}

// Builds localStorage key with per-project namespace (by project title).
function getStorageKey(treeRoot) {
  const projectTitle = (treeRoot.dataset.projectTitle || "").trim();
  const projectKey = projectTitle.length > 0 ? projectTitle : "default";
  return `${STORAGE_KEY_PREFIX}:${projectKey}`;
}

// Reads persisted scrollTop and validates it as a finite number.
function readSavedScrollTop(treeRoot) {
  const value = localStorage.getItem(getStorageKey(treeRoot));
  if (value === null) {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

// Persists current scrollTop for the current project namespace.
function saveScrollTop(treeRoot, container) {
  localStorage.setItem(getStorageKey(treeRoot), String(container.scrollTop));
}

// Keeps target scrollTop within valid container bounds.
function clampScrollTop(container, value) {
  const maxScrollTop = Math.max(0, container.scrollHeight - container.clientHeight);
  return Math.max(0, Math.min(value, maxScrollTop));
}

// Checks whether item rectangle is fully visible in current container viewport.
function isFullyVisibleInContainer(containerRect, itemRect) {
  return (
    itemRect.top >= containerRect.top &&
    itemRect.bottom <= containerRect.bottom
  );
}

// Safety fallback: center active item only when it is outside the visible area.
function alignActiveItemToCenterIfNeeded(treeRoot, container) {
  const activeItem = treeRoot.querySelector(ACTIVE_ITEM_SELECTOR);
  if (!activeItem) {
    return;
  }

  const containerRect = container.getBoundingClientRect();
  const activeRect = activeItem.getBoundingClientRect();

  if (isFullyVisibleInContainer(containerRect, activeRect)) {
    return;
  }

  const activeCenter = activeRect.top + activeRect.height / 2;
  const containerCenter = containerRect.top + containerRect.height / 2;
  const delta = activeCenter - containerCenter;
  const nextScrollTop = container.scrollTop + delta;

  container.scrollTop = clampScrollTop(container, nextScrollTop);
}

// Restores persisted scroll, then applies active-item fallback correction.
function restoreScrollTop() {
  const treeRoot = findTreeRoot();
  if (!treeRoot) {
    return false;
  }

  const container = findScrollContainer(treeRoot);
  if (!container) {
    return false;
  }

  const savedScrollTop = readSavedScrollTop(treeRoot);
  if (savedScrollTop !== null) {
    container.scrollTop = clampScrollTop(container, savedScrollTop);
  }
  // Independent safety rule:
  // if active item is outside current viewport, center it.
  alignActiveItemToCenterIfNeeded(treeRoot, container);
  // Persist resulting position (restored and/or centered) for next reload.
  saveScrollTop(treeRoot, container);
  return true;
}

// Subscribes to tree-link clicks and persists scroll state for navigation.
function bindPersistence() {
  const treeRoot = findTreeRoot();
  if (!treeRoot) {
    return false;
  }

  const container = findScrollContainer(treeRoot);
  if (!container) {
    return false;
  }

  if (treeRoot.hasAttribute(BOUND_ATTR)) {
    return true;
  }

  treeRoot.addEventListener("click", function (event) {
    const treeItem = event.target.closest(TREE_ITEM_SELECTOR);
    if (!treeItem || !treeRoot.contains(treeItem)) {
      return;
    }
    saveScrollTop(treeRoot, container);
  });
  treeRoot.setAttribute(BOUND_ATTR, "");

  return true;
}

// Retries init for a few frames because resizable_bar wrapper is attached on load.
function initWithRetries(maxAttempts) {
  let attempt = 0;

  // Attempts restore/bind until tree and scroll container are both available.
  function tryInit() {
    attempt += 1;

    const restored = restoreScrollTop();
    const bound = bindPersistence();

    if (restored && bound) {
      return;
    }

    if (attempt < maxAttempts) {
      requestAnimationFrame(tryInit);
    }
  }

  tryInit();
}

window.addEventListener("load", function () {
  // Wait a few frames in case resizable_bar.js wraps content asynchronously.
  initWithRetries(20);
});
