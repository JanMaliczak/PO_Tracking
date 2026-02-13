from django.conf import settings
from django.db import models


class AppendOnlyAuditQuerySet(models.QuerySet):
    def delete(self):
        raise RuntimeError("AuditEvent is append-only; delete is not allowed.")

    def update(self, **kwargs):
        raise RuntimeError("AuditEvent is append-only; update is not allowed.")


class AppendOnlyAuditManager(models.Manager):
    def get_queryset(self):
        return AppendOnlyAuditQuerySet(self.model, using=self._db)

    def delete(self):
        raise RuntimeError("AuditEvent is append-only; delete is not allowed.")

    def update(self, **kwargs):
        raise RuntimeError("AuditEvent is append-only; update is not allowed.")


class AuditEvent(models.Model):
    SOURCE_MANUAL = "manual"
    SOURCE_BULK = "bulk"
    SOURCE_INLINE = "inline"
    SOURCE_INGESTION = "ingestion"
    SOURCE_SYSTEM = "system"

    SOURCE_CHOICES = (
        (SOURCE_MANUAL, "Manual"),
        (SOURCE_BULK, "Bulk"),
        (SOURCE_INLINE, "Inline"),
        (SOURCE_INGESTION, "Ingestion"),
        (SOURCE_SYSTEM, "System"),
    )

    event_type = models.CharField(max_length=64)
    po_line = models.ForeignKey("po.POLine", on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_events")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_events")
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    previous_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    reason = models.TextField(blank=True, default="")

    objects = AppendOnlyAuditManager()

    class Meta:
        indexes = [
            models.Index(fields=["event_type", "timestamp"], name="audit_type_time_idx"),
        ]

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise RuntimeError("AuditEvent is append-only; modification after creation is not allowed.")
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        raise RuntimeError("AuditEvent is append-only; delete is not allowed.")
