from django.conf import settings
from django.test import SimpleTestCase


class HtmxUiConfigTests(SimpleTestCase):
    def _read_static(self, name):
        path = settings.BASE_DIR / "static" / name
        self.assertTrue(path.exists(), f"Missing static/{name}")
        return path.read_text(encoding="utf-8")

    def _read_template(self, name):
        path = settings.BASE_DIR / "templates" / name
        return path.read_text(encoding="utf-8")

    def test_htmx_and_toast_scripts_exist(self):
        self._read_static("js/htmx-config.js")
        self._read_static("js/toast.js")

    def test_confirm_modal_script_exists(self):
        self._read_static("js/confirm-modal.js")

    def test_htmx_config_contains_global_error_handling_hook(self):
        content = self._read_static("js/htmx-config.js")
        self.assertIn("htmx:responseError", content)

    def test_htmx_config_contains_redirect_handling(self):
        content = self._read_static("js/htmx-config.js")
        self.assertIn("HX-Redirect", content)

    def test_toast_script_listens_for_show_toast_event(self):
        content = self._read_static("js/toast.js")
        self.assertIn("showToast", content)

    def test_confirm_modal_script_intercepts_htmx_confirm(self):
        content = self._read_static("js/confirm-modal.js")
        self.assertIn("htmx:confirm", content)
        self.assertIn("appConfirm", content)

    def test_base_template_references_custom_css_and_ui_scripts(self):
        content = self._read_template("base.html")
        self.assertIn("css/custom.css", content)
        self.assertIn("js/htmx-config.js", content)
        self.assertIn("js/toast.js", content)
        self.assertIn("js/confirm-modal.js", content)
