(function () {
  function getContainer() {
    return document.getElementById("toast-container");
  }

  function normalizePayload(detail) {
    if (typeof detail === "string") {
      return { message: detail, level: "info", duration: 4000 };
    }
    if (!detail || typeof detail !== "object") {
      return { message: "Operation completed.", level: "info", duration: 4000 };
    }
    return {
      message: detail.message || "Operation completed.",
      level: detail.level || "info",
      duration: Number.isInteger(detail.duration) ? detail.duration : 4000,
    };
  }

  function buildToast(payload) {
    const toast = document.createElement("div");
    toast.className = "app-toast app-toast-" + payload.level;
    toast.setAttribute("role", "status");
    toast.textContent = payload.message;
    return toast;
  }

  function removeToast(toast) {
    if (!toast || !toast.parentElement) {
      return;
    }
    toast.classList.add("app-toast-hide");
    setTimeout(function () {
      if (toast.parentElement) {
        toast.parentElement.removeChild(toast);
      }
    }, 180);
  }

  function showToast(detail) {
    const container = getContainer();
    if (!container) {
      return;
    }
    const payload = normalizePayload(detail);
    const toast = buildToast(payload);
    container.appendChild(toast);
    setTimeout(function () {
      removeToast(toast);
    }, Math.max(payload.duration, 1000));
  }

  document.body.addEventListener("showToast", function (event) {
    showToast(event.detail);
  });
})();

