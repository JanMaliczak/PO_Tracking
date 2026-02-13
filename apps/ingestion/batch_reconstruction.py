from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.db import transaction

from apps.batches.models import Batch
from apps.ingestion.models import ERPSnapshot
from apps.po.models import POLine


@dataclass(frozen=True)
class BatchReconstructionResult:
    run_identifier: str
    created_batches_count: int
    processed_po_lines_count: int


def reconstruct_historical_batches(
    *,
    current_run_identifier: str,
    previous_run_identifier: str | None = None,
) -> BatchReconstructionResult:
    current_rows = list(
        ERPSnapshot.objects.filter(run_identifier=current_run_identifier)
        .select_related("supplier")
        .order_by("id")
    )
    if not current_rows:
        raise ValueError(f"No snapshots found for current run '{current_run_identifier}'.")

    if previous_run_identifier is None:
        previous_run_identifier = (
            ERPSnapshot.objects.exclude(run_identifier=current_run_identifier)
            .order_by("-snapshot_timestamp", "-id")
            .values_list("run_identifier", flat=True)
            .first()
        )

    previous_by_key: dict[tuple[str, int], ERPSnapshot] = {}
    if previous_run_identifier:
        previous_by_key = {
            (snapshot.po_number, snapshot.line_number): snapshot
            for snapshot in ERPSnapshot.objects.filter(run_identifier=previous_run_identifier).order_by("id")
        }

    current_by_key = {(snapshot.po_number, snapshot.line_number): snapshot for snapshot in current_rows}
    po_numbers = sorted({key[0] for key in current_by_key.keys()})
    po_lines_by_key = {
        (po_line.po_number, po_line.line_number): po_line
        for po_line in POLine.objects.filter(po_number__in=po_numbers)
    }

    # Ensure all current snapshot lines have a POLine for batch linkage.
    missing_po_lines = []
    for key, snapshot in current_by_key.items():
        if key in po_lines_by_key:
            continue
        missing_po_lines.append(
            POLine(
                po_number=snapshot.po_number,
                line_number=snapshot.line_number,
                sku=snapshot.sku,
                item=snapshot.item,
                supplier=snapshot.supplier,
                ordered_quantity=snapshot.ordered_quantity or 0,
                delivered_quantity=snapshot.delivered_quantity or 0,
                remaining_quantity=snapshot.remaining_quantity or 0,
                promised_date=snapshot.promised_date,
                current_status=snapshot.current_status,
                po_insert_date=snapshot.po_insert_date,
                final_customer=snapshot.final_customer,
                source_quality=snapshot.source_quality or POLine.SOURCE_QUALITY_ERP,
                last_update_timestamp=snapshot.last_update_timestamp,
                is_stale=snapshot.is_stale,
                staleness_checked_at=snapshot.staleness_checked_at,
                custom_date_1=snapshot.custom_date_1,
                custom_date_2=snapshot.custom_date_2,
                custom_date_3=snapshot.custom_date_3,
                custom_date_4=snapshot.custom_date_4,
                custom_date_5=snapshot.custom_date_5,
                custom_text_1=snapshot.custom_text_1,
                custom_text_2=snapshot.custom_text_2,
                custom_text_3=snapshot.custom_text_3,
                custom_text_4=snapshot.custom_text_4,
                custom_text_5=snapshot.custom_text_5,
                custom_decimal_1=snapshot.custom_decimal_1,
                custom_decimal_2=snapshot.custom_decimal_2,
                custom_decimal_3=snapshot.custom_decimal_3,
                custom_decimal_4=snapshot.custom_decimal_4,
                custom_decimal_5=snapshot.custom_decimal_5,
                custom_column_sources=snapshot.custom_column_sources,
            )
        )

    # M1: POLine creation and Batch creation are atomic — both succeed or neither does.
    created_batches_count = 0
    with transaction.atomic():
        if missing_po_lines:
            POLine.objects.bulk_create(missing_po_lines, ignore_conflicts=True, batch_size=1000)
            po_lines_by_key = {
                (po_line.po_number, po_line.line_number): po_line
                for po_line in POLine.objects.filter(po_number__in=po_numbers)
            }

        batches_to_create: list[Batch] = []
        for key, current in sorted(current_by_key.items()):
            po_line = po_lines_by_key.get(key)
            if po_line is None:
                continue

            previous = previous_by_key.get(key)
            previous_delivered = Decimal(str(previous.delivered_quantity or 0)) if previous else Decimal("0")
            current_delivered = Decimal(str(current.delivered_quantity or 0))
            delta = current_delivered - previous_delivered
            if delta <= 0:
                continue

            delivery_date = _resolve_delivery_date(current)
            batches_to_create.append(
                Batch(
                    po_line=po_line,
                    delivered_quantity=delta,
                    delivery_date=delivery_date,
                    source=Batch.SOURCE_INGESTION,
                    run_identifier=current_run_identifier,
                )
            )

        if batches_to_create:
            before = Batch.objects.count()
            Batch.objects.bulk_create(batches_to_create, ignore_conflicts=True, batch_size=1000)
            created_batches_count = max(Batch.objects.count() - before, 0)

    return BatchReconstructionResult(
        run_identifier=current_run_identifier,
        created_batches_count=created_batches_count,
        processed_po_lines_count=len(current_by_key),
    )


def _resolve_delivery_date(snapshot: ERPSnapshot) -> date:
    if snapshot.in_date:
        return snapshot.in_date
    if snapshot.last_update_timestamp:
        return snapshot.last_update_timestamp.date()
    return snapshot.snapshot_timestamp.date()
