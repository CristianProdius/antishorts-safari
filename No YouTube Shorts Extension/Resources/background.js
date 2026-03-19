// No YouTube Shorts — Background service worker

browser.runtime.onInstalled.addListener(() => {
  browser.storage.local.set({ enabled: true });
});

// Handle toggle messages from popup
browser.runtime.onMessage.addListener((message) => {
  if (message.type === "toggleEnabled") {
    const newEnabled = message.enabled;

    // Toggle the declarativeNetRequest ruleset
    if (newEnabled) {
      browser.declarativeNetRequest.updateEnabledRulesets({
        enableRulesetIds: ["redirect_shorts"],
      });
    } else {
      browser.declarativeNetRequest.updateEnabledRulesets({
        disableRulesetIds: ["redirect_shorts"],
      });
    }

    // Persist state
    browser.storage.local.set({ enabled: newEnabled });
  }
});
