from django.db import models
from django.utils import timezone


class ERPSnapshot(models.Model):
    snapshot_timestamp = models.DateTimeField(db_index=True)
    run_identifier = models.CharField(max_length=64, db_index=True)

    po_number = models.CharField(max_length=64)
    line_number = models.PositiveIntegerField()
    sku = models.CharField(max_length=128)
    item = models.CharField(max_length=255)
    supplier = models.ForeignKey("po.Supplier", on_delete=models.SET_NULL, null=True, blank=True, related_name="erp_snapshots")
    ordered_quantity = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    delivered_quantity = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    remaining_quantity = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    in_date = models.DateField(null=True, blank=True)
    promised_date = models.DateField(null=True, blank=True)
    current_status = models.CharField(max_length=64, blank=True, default="")
    po_insert_date = models.DateField(null=True, blank=True)
    final_customer = models.CharField(max_length=255, blank=True, default="")
    source_quality = models.CharField(max_length=16, blank=True, default="")
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["run_identifier", "po_number", "line_number"],
                name="ing_snapshot_run_po_line_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["po_number", "line_number"], name="ing_snapshot_po_line_idx"),
            models.Index(fields=["snapshot_timestamp"], name="ing_snapshot_time_idx"),
        ]


class ERPChangeEvent(models.Model):
    po_line = models.ForeignKey("po.POLine", on_delete=models.SET_NULL, null=True, blank=True, related_name="erp_change_events")
    field_name = models.CharField(max_length=128)
    previous_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    snapshot = models.ForeignKey(ERPSnapshot, on_delete=models.CASCADE, related_name="change_events")
    detected_at = models.DateTimeField(default=timezone.now, db_index=True)


class ItemXref(models.Model):
    erp_item_code = models.CharField(max_length=128)
    mapped_sku = models.CharField(max_length=128)
    mapped_item = models.CharField(max_length=255)
    supplier = models.ForeignKey("po.Supplier", on_delete=models.CASCADE, related_name="item_xrefs")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["supplier", "erp_item_code"],
                name="ing_itemxref_supplier_erp_item_unique",
            ),
        ]
