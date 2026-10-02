// Panel open/close + Esc + focus management. This script binds ONLY to the
// storefront's new opener/close elements and the dialog container. It does not
// touch #log / #chatForm / #message / #orderId / #receiptBtn, and it never
// calls the chat logic in app.js — so it cannot regress chat/refund/receipt
// behavior.

(function () {
  const panel = document.getElementById("chatPanel");
  const closeBtn = document.getElementById("closeChat");
  const messageInput = document.getElementById("message");
  if (!panel) return;

  // All openers: explicit ids plus any element carrying the shared hook.
  const openers = Array.prototype.slice.call(
    document.querySelectorAll(
      "#openChat, #openChatFab, [data-open-chat]"
    )
  );

  let lastOpener = null;

  function setExpanded(state) {
    openers.forEach(function (el) {
      el.setAttribute("aria-expanded", state ? "true" : "false");
    });
  }

  function isOpen() {
    return !panel.hasAttribute("hidden");
  }

  function openPanel(opener) {
    if (isOpen()) return;
    lastOpener = opener || null;
    panel.removeAttribute("hidden");
    setExpanded(true);
    // Move focus into the panel for keyboard users.
    const focusTarget = messageInput || closeBtn;
    if (focusTarget && typeof focusTarget.focus === "function") {
      focusTarget.focus();
    }
  }

  function closePanel() {
    if (!isOpen()) return;
    panel.setAttribute("hidden", "");
    setExpanded(false);
    // Return focus to the control that opened the panel.
    if (lastOpener && typeof lastOpener.focus === "function") {
      lastOpener.focus();
    }
    lastOpener = null;
  }

  openers.forEach(function (el) {
    el.addEventListener("click", function () {
      openPanel(el);
    });
  });

  if (closeBtn) {
    closeBtn.addEventListener("click", closePanel);
  }

  document.addEventListener("keydown", function (e) {
    if ((e.key === "Escape" || e.key === "Esc") && isOpen()) {
      closePanel();
    }
  });
})();
