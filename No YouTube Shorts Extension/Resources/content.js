// No YouTube Shorts — JS layer (injected at document_idle)

(function () {
  "use strict";

  let enabled = true;

  // Read initial state
  browser.storage.local.get("enabled").then((result) => {
    enabled = result.enabled !== false; // default true
    if (enabled) {
      redirectIfShorts();
      startObserver();
    }
  });

  // Listen for toggle changes from popup
  browser.storage.onChanged.addListener((changes) => {
    if (changes.enabled) {
      enabled = changes.enabled.newValue !== false;
      if (enabled) {
        redirectIfShorts();
        startObserver();
      } else {
        stopObserver();
      }
    }
  });

  // Redirect /shorts/ID → /watch?v=ID
  function redirectIfShorts() {
    const match = location.pathname.match(/^\/shorts\/([a-zA-Z0-9_-]+)/);
    if (match) {
      const videoId = match[1];
      location.replace(`/watch?v=${videoId}`);
    }
  }

  // YouTube SPA navigation event
  document.addEventListener("yt-navigate-finish", () => {
    if (enabled) {
      redirectIfShorts();
    }
  });

  // MutationObserver to hide dynamically loaded Shorts elements
  let observer = null;

  const SHORTS_SELECTORS = [
    'ytd-reel-shelf-renderer',
    'ytd-rich-shelf-renderer[is-shorts]',
    'ytd-rich-section-renderer:has(ytd-reel-shelf-renderer)',
    'ytd-rich-item-renderer:has([overlay-style="SHORTS"])',
    'ytd-grid-video-renderer:has([overlay-style="SHORTS"])',
    'ytd-video-renderer:has([overlay-style="SHORTS"])',
  ].join(",");

  function hideShorts() {
    const elements = document.querySelectorAll(SHORTS_SELECTORS);
    for (const el of elements) {
      el.style.display = "none";
    }
  }

  function startObserver() {
    if (observer) return;
    hideShorts();
    observer = new MutationObserver(() => {
      hideShorts();
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  function stopObserver() {
    if (observer) {
      observer.disconnect();
      observer = null;
    }
  }
})();
