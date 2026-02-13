class DatabaseRouter:
    """Route ERP read models to erp DB and prevent write/migrate/relation actions."""

    ERP_APP_LABELS = {"erp"}

    def _is_erp_model(self, model) -> bool:
        meta = getattr(model, "_meta", None)
        app_label = getattr(meta, "app_label", "")
        # erp_managed is a class-level attribute on ERPTableBase subclasses, not a Meta option.
        return app_label in self.ERP_APP_LABELS or bool(getattr(model, "erp_managed", False))

    def db_for_read(self, model, **hints):
        if self._is_erp_model(model):
            return "erp"
        return None

    def db_for_write(self, model, **hints):
        if self._is_erp_model(model):
            raise RuntimeError("ERP models are read-only and cannot be written.")
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if self._is_erp_model(obj1.__class__) or self._is_erp_model(obj2.__class__):
            return False
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        model = hints.get("model")
        if db == "erp":
            return False
        if app_label in self.ERP_APP_LABELS:
            return False
        if model is not None and self._is_erp_model(model):
            return False
        return None
