// No YouTube Shorts — Popup toggle logic

const toggle = document.getElementById("toggle");
const status = document.getElementById("status");

// Load current state
browser.storage.local.get("enabled").then((result) => {
  const isEnabled = result.enabled !== false;
  toggle.checked = isEnabled;
  updateStatus(isEnabled);
});

// Handle toggle
toggle.addEventListener("change", () => {
  const isEnabled = toggle.checked;
  updateStatus(isEnabled);
  browser.storage.local.set({ enabled: isEnabled });
  browser.runtime.sendMessage({ type: "toggleEnabled", enabled: isEnabled });
});

function updateStatus(isEnabled) {
  if (isEnabled) {
    status.textContent = "Blocking Shorts";
    status.className = "status active";
  } else {
    status.textContent = "Disabled";
    status.className = "status inactive";
  }
}
