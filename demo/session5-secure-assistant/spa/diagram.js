// Architecture-diagram modal: open/close + Esc + backdrop click + focus
// management. Mirrors ui.js. Binds ONLY to the diagram opener/close elements and
// the diagram dialog container; it never touches the chat ids or app.js logic,
// so it cannot regress the chat/refund/order flows. The diagram image is a
// static asset served same-origin from the SPA bucket (architecture.png) — no
// API call, no secrets.

(function () {
  const modal = document.getElementById("diagramModal");
  const closeBtn = document.getElementById("closeDiagram");
  if (!modal) return;

  const openers = Array.prototype.slice.call(
    document.querySelectorAll("#openDiagram, [data-open-diagram]")
  );

  let lastOpener = null;

  function setExpanded(state) {
    openers.forEach(function (el) {
      el.setAttribute("aria-expanded", state ? "true" : "false");
    });
  }

  function isOpen() {
    return !modal.hasAttribute("hidden");
  }

  function openModal(opener) {
    if (isOpen()) return;
    lastOpener = opener || null;
    modal.removeAttribute("hidden");
    setExpanded(true);
    if (closeBtn && typeof closeBtn.focus === "function") {
      closeBtn.focus();
    }
  }

  function closeModal() {
    if (!isOpen()) return;
    modal.setAttribute("hidden", "");
    setExpanded(false);
    if (lastOpener && typeof lastOpener.focus === "function") {
      lastOpener.focus();
    }
    lastOpener = null;
  }

  openers.forEach(function (el) {
    el.addEventListener("click", function () {
      openModal(el);
    });
  });

  if (closeBtn) {
    closeBtn.addEventListener("click", closeModal);
  }

  // Click on the dim backdrop (outside the modal box) closes it.
  modal.addEventListener("click", function (e) {
    if (e.target === modal) {
      closeModal();
    }
  });

  document.addEventListener("keydown", function (e) {
    if ((e.key === "Escape" || e.key === "Esc") && isOpen()) {
      closeModal();
    }
  });
})();
