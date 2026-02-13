(function () {
  // Global HTMX error handling - show toast on failed requests
  document.body.addEventListener("htmx:responseError", function (event) {
    var xhr = event.detail && event.detail.xhr ? event.detail.xhr : null;
    var status = xhr ? xhr.status : 0;

    if (status === 403) {
      document.body.dispatchEvent(
        new CustomEvent("showToast", {
          detail: {
            level: "error",
            message: "Access denied.",
            duration: 5000,
          },
        })
      );
      return;
    }

    document.body.dispatchEvent(
      new CustomEvent("showToast", {
        detail: {
          level: "error",
          message: "Request failed. Please try again.",
          duration: 5000,
        },
      })
    );
  });

  // HX-Redirect support: HTMX 2.0 handles HX-Redirect natively in its
  // response handler (performs window.location redirect). This listener
  // adds toast feedback and ensures indicator cleanup on redirect responses.
  document.body.addEventListener("htmx:beforeSwap", function (event) {
    var xhr = event.detail.xhr;
    if (xhr && xhr.getResponseHeader("HX-Redirect")) {
      event.detail.shouldSwap = false;
      window.location.href = xhr.getResponseHeader("HX-Redirect");
    }
  });

  // HX-Trigger support: HTMX 2.0 processes HX-Trigger headers natively,
  // dispatching custom events on the triggering element. Server views can
  // set HX-Trigger: {"showToast": {"message": "...", "level": "success"}}
  // to display toast notifications via the toast.js listener.
})();
