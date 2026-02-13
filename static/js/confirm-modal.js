(function () {
  var modalEl = document.getElementById("confirm-modal");
  if (!modalEl) return;

  var messageEl = document.getElementById("confirm-modal-message");
  var titleEl = document.getElementById("confirm-modal-title");
  var acceptBtn = document.getElementById("confirm-modal-accept");
  var pendingCallback = null;

  /**
   * Show the confirmation modal.
   *
   * Usage from JS:
   *   window.appConfirm({ title: "Delete?", message: "This cannot be undone." })
   *     .then(function (accepted) { if (accepted) { ... } });
   *
   * Usage from HTMX (hx-confirm via event):
   *   <button hx-delete="/items/1" hx-confirm="Delete this item?">Delete</button>
   *   The htmx:confirm event is intercepted below to show this modal instead of
   *   the browser's native confirm() dialog.
   */
  function showModal(options) {
    var opts = options || {};
    if (titleEl) titleEl.textContent = opts.title || "Confirm action";
    if (messageEl) messageEl.textContent = opts.message || "Are you sure you want to continue?";

    var bsModal = bootstrap.Modal.getOrCreateInstance(modalEl);

    return new Promise(function (resolve) {
      pendingCallback = resolve;
      bsModal.show();
    });
  }

  acceptBtn.addEventListener("click", function () {
    var bsModal = bootstrap.Modal.getInstance(modalEl);
    if (bsModal) bsModal.hide();
    if (pendingCallback) {
      pendingCallback(true);
      pendingCallback = null;
    }
  });

  modalEl.addEventListener("hidden.bs.modal", function () {
    if (pendingCallback) {
      pendingCallback(false);
      pendingCallback = null;
    }
  });

  // Intercept HTMX hx-confirm to use Bootstrap modal instead of native confirm()
  document.body.addEventListener("htmx:confirm", function (event) {
    var message = event.detail.question;
    if (!message) return;

    event.preventDefault();
    showModal({ message: message }).then(function (accepted) {
      if (accepted) {
        event.detail.issueRequest(true);
      }
    });
  });

  // Expose globally for programmatic usage
  window.appConfirm = showModal;
})();
