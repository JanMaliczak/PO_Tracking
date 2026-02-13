from django.db import models


class ERPTableBase(models.Model):
    # Class-level marker used by DatabaseRouter to identify read-only ERP models.
    # Must NOT be placed in class Meta — Django 5.x rejects unknown Meta attributes.
    erp_managed: bool = True

    class Meta:
        abstract = True
        managed = False


class ERPOrderLine(ERPTableBase):
    # DEPLOYMENT NOTE (H2): Django auto-assigns an implicit `id` AutoField as PK.
    # Verify that the actual ERP table `erp_order_lines` has an `id` column, or
    # define the real PK explicitly, e.g.:
    #   order_line_id = models.IntegerField(primary_key=True, db_column="order_line_id")
    # Without a matching PK column all ORM queries will raise ProgrammingError at runtime.
    po_number = models.CharField(max_length=64, db_column="po_number")
    line_number = models.IntegerField(db_column="line_number")
    sku = models.CharField(max_length=128, db_column="sku")
    item_code = models.CharField(max_length=128, db_column="item_code")
    ordered_quantity = models.DecimalField(max_digits=18, decimal_places=3, db_column="ordered_quantity")
    delivered_quantity = models.DecimalField(max_digits=18, decimal_places=3, db_column="delivered_quantity")
    remaining_quantity = models.DecimalField(max_digits=18, decimal_places=3, db_column="remaining_quantity")
    in_date = models.DateField(null=True, blank=True, db_column="in_date")
    promised_date = models.DateField(null=True, blank=True, db_column="promised_date")
    current_status = models.CharField(max_length=64, blank=True, default="", db_column="current_status")
    po_insert_date = models.DateField(null=True, blank=True, db_column="po_insert_date")
    final_customer = models.CharField(max_length=255, blank=True, default="", db_column="final_customer")
    last_update_timestamp = models.DateTimeField(null=True, blank=True, db_column="last_update_timestamp")
    custom_date_1 = models.DateField(null=True, blank=True, db_column="custom_date_1")
    custom_date_2 = models.DateField(null=True, blank=True, db_column="custom_date_2")
    custom_date_3 = models.DateField(null=True, blank=True, db_column="custom_date_3")
    custom_date_4 = models.DateField(null=True, blank=True, db_column="custom_date_4")
    custom_date_5 = models.DateField(null=True, blank=True, db_column="custom_date_5")
    custom_text_1 = models.CharField(max_length=255, null=True, blank=True, db_column="custom_text_1")
    custom_text_2 = models.CharField(max_length=255, null=True, blank=True, db_column="custom_text_2")
    custom_text_3 = models.CharField(max_length=255, null=True, blank=True, db_column="custom_text_3")
    custom_text_4 = models.CharField(max_length=255, null=True, blank=True, db_column="custom_text_4")
    custom_text_5 = models.CharField(max_length=255, null=True, blank=True, db_column="custom_text_5")
    custom_decimal_1 = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True, db_column="custom_decimal_1")
    custom_decimal_2 = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True, db_column="custom_decimal_2")
    custom_decimal_3 = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True, db_column="custom_decimal_3")
    custom_decimal_4 = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True, db_column="custom_decimal_4")
    custom_decimal_5 = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True, db_column="custom_decimal_5")

    class Meta(ERPTableBase.Meta):
        db_table = "erp_order_lines"


class ERPItemXref(ERPTableBase):
    # DEPLOYMENT NOTE (H2): Same PK caveat as ERPOrderLine — verify `erp_item_xref`
    # has an `id` column or define the actual primary key explicitly.
    erp_item_code = models.CharField(max_length=128, db_column="erp_item_code")
    mapped_sku = models.CharField(max_length=128, db_column="mapped_sku")
    mapped_item = models.CharField(max_length=255, db_column="mapped_item")
    supplier_code = models.CharField(max_length=64, db_column="supplier_code")
    is_active = models.BooleanField(default=True, db_column="is_active")
    updated_at = models.DateTimeField(null=True, blank=True, db_column="updated_at")

    class Meta(ERPTableBase.Meta):
        db_table = "erp_item_xref"
