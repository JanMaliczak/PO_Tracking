from django.db import models

from apps.core.querysets import ScopedManager


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64, unique=True)

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class POLine(models.Model):
    SOURCE_QUALITY_ERP = "erp"
    SOURCE_QUALITY_USER = "user"
    SOURCE_QUALITY_MIXED = "mixed"

    SOURCE_QUALITY_CHOICES = (
        (SOURCE_QUALITY_ERP, "ERP"),
        (SOURCE_QUALITY_USER, "User"),
        (SOURCE_QUALITY_MIXED, "Mixed"),
    )

    po_number = models.CharField(max_length=64)
    line_number = models.PositiveIntegerField()
    sku = models.CharField(max_length=128)
    item = models.CharField(max_length=255)
    supplier = models.ForeignKey("po.Supplier", on_delete=models.PROTECT, related_name="po_lines")
    ordered_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    delivered_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    remaining_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    promised_date = models.DateField(null=True, blank=True)
    current_status = models.CharField(max_length=64, blank=True, default="")
    po_insert_date = models.DateField(null=True, blank=True)
    final_customer = models.CharField(max_length=255, blank=True, default="")
    source_quality = models.CharField(
        max_length=16,
        choices=SOURCE_QUALITY_CHOICES,
        default=SOURCE_QUALITY_ERP,
    )
    last_update_timestamp = models.DateTimeField(null=True, blank=True)
    is_stale = models.BooleanField(default=False)
    staleness_checked_at = models.DateTimeField(null=True, blank=True)

    custom_date_1 = models.DateField(null=True, blank=True)
    custom_date_2 = models.DateField(null=True, blank=True)
    custom_date_3 = models.DateField(null=True, blank=True)
    custom_date_4 = models.DateField(null=True, blank=True)
    custom_date_5 = models.DateField(null=True, blank=True)
    custom_text_1 = models.CharField(max_length=255, null=True, blank=True)
    custom_text_2 = models.CharField(max_length=255, null=True, blank=True)
    custom_text_3 = models.CharField(max_length=255, null=True, blank=True)
    custom_text_4 = models.CharField(max_length=255, null=True, blank=True)
    custom_text_5 = models.CharField(max_length=255, null=True, blank=True)
    custom_decimal_1 = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    custom_decimal_2 = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    custom_decimal_3 = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    custom_decimal_4 = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    custom_decimal_5 = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    custom_column_sources = models.JSONField(default=dict, blank=True)

    objects = ScopedManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["po_number", "line_number"],
                name="po_poline_po_number_line_number_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.po_number}/{self.line_number} [{self.sku}]"
