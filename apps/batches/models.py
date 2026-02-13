from django.db import models


class Batch(models.Model):
    SOURCE_INGESTION = "ingestion"
    SOURCE_MANUAL = "manual"

    SOURCE_CHOICES = (
        (SOURCE_INGESTION, "Ingestion"),
        (SOURCE_MANUAL, "Manual"),
    )

    po_line = models.ForeignKey("po.POLine", on_delete=models.CASCADE, related_name="batches")
    delivered_quantity = models.DecimalField(max_digits=18, decimal_places=3)
    delivery_date = models.DateField()
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES, default=SOURCE_INGESTION)
    run_identifier = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            # H1: restrict to ingestion source only so manual batches are never blocked.
            # run_identifier is non-empty for every ingestion batch (set to current_run_identifier).
            models.UniqueConstraint(
                fields=["po_line", "run_identifier"],
                condition=models.Q(source="ingestion"),
                name="batches_batch_poline_run_ingestion_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["delivery_date"], name="bat_deliv_date_idx"),
        ]
