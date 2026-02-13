from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.core.services import create_audit_event
from apps.ingestion.erp_models import ERPItemXref, ERPOrderLine
from apps.ingestion.models import ERPSnapshot
from apps.po.models import POLine, Supplier

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SnapshotExtractionResult:
    run_identifier: str
    snapshot_timestamp: Any
    extracted_count: int
    snapshot_count: int
    baseline_initialized: bool
    baseline_created_po_lines: int
    unmapped_item_count: int = 0
    unmapped_item_codes: tuple[str, ...] = ()


def run_snapshot_extraction(
    *,
    run_identifier: str | None = None,
    baseline_mode: bool | None = None,
    now=None,
) -> SnapshotExtractionResult:
    snapshot_timestamp = now or timezone.now()
    run_identifier = run_identifier or _generate_run_identifier(snapshot_timestamp)
    retry_count = max(int(getattr(settings, "INGESTION_ERP_RETRY_COUNT", 3)), 1)
    retry_backoff = max(float(getattr(settings, "INGESTION_ERP_RETRY_BACKOFF_SECONDS", 1.0)), 0.0)

    records = _extract_with_retry(retry_count=retry_count, retry_backoff=retry_backoff)
    unmapped_item_codes = _collect_unmapped_item_codes(records)

    with transaction.atomic():
        # Strip private in-memory keys (prefixed "_") before persisting to DB
        db_records = [{k: v for k, v in record.items() if not k.startswith("_")} for record in records]
        snapshots = [ERPSnapshot(run_identifier=run_identifier, snapshot_timestamp=snapshot_timestamp, **record) for record in db_records]
        ERPSnapshot.objects.bulk_create(snapshots, ignore_conflicts=True, batch_size=1000)
        snapshot_count = ERPSnapshot.objects.filter(run_identifier=run_identifier).count()
        # M2: evaluate baseline auto-detection inside the transaction to reduce the
        # concurrent double-initialisation window (two runs both seeing an empty table).
        if baseline_mode is None:
            prior_exists = ERPSnapshot.objects.exclude(run_identifier=run_identifier).exists()
            baseline_requested = not prior_exists
        else:
            baseline_requested = baseline_mode

    baseline_created_po_lines = 0
    if baseline_requested:
        baseline_created_po_lines = _initialize_baseline_from_snapshot_run(run_identifier=run_identifier)

    _record_xref_gap_events(run_identifier=run_identifier, unmapped_item_codes=unmapped_item_codes)

    return SnapshotExtractionResult(
        run_identifier=run_identifier,
        snapshot_timestamp=snapshot_timestamp,
        extracted_count=len(records),
        snapshot_count=snapshot_count,
        baseline_initialized=baseline_requested,
        baseline_created_po_lines=baseline_created_po_lines,
        unmapped_item_count=len(unmapped_item_codes),
        unmapped_item_codes=tuple(unmapped_item_codes),
    )


def _extract_with_retry(*, retry_count: int, retry_backoff: float) -> list[dict[str, Any]]:
    for attempt in range(1, retry_count + 1):
        try:
            return _extract_active_erp_rows()
        except Exception as exc:  # M4: catch all exceptions — ERP drivers may raise beyond OperationalError
            if attempt >= retry_count:
                _record_snapshot_failure_event(error=exc, attempts=retry_count)
                raise

            sleep_seconds = retry_backoff * (2 ** (attempt - 1))
            logger.warning(
                "ERP snapshot extraction failed on attempt %s/%s (%s). Retrying in %.2fs.",
                attempt,
                retry_count,
                exc,
                sleep_seconds,
            )
            time.sleep(sleep_seconds)

    raise RuntimeError("retry_count must be >= 1")  # pragma: no cover — enforced by max(..., 1) above


def _extract_active_erp_rows() -> list[dict[str, Any]]:
    xref_map = _load_active_item_xrefs()
    supplier_map = _load_supplier_map({value["supplier_code"] for value in xref_map.values() if value.get("supplier_code")})
    inactive_statuses = _inactive_statuses()
    fallback_supplier = None  # M1: loaded lazily — avoids a DB write when every item has a valid xref

    extracted: list[dict[str, Any]] = []
    for row in ERPOrderLine.objects.using("erp").all():
        current_status = (row.current_status or "").strip()  # L2: direct field access
        if current_status.lower() in inactive_statuses:
            continue

        item_code = str(getattr(row, "item_code", "") or "")
        xref = xref_map.get(item_code)
        if xref:
            supplier = supplier_map.get(xref.get("supplier_code"))
            xref_gap = False
        else:
            if fallback_supplier is None:
                fallback_supplier = _get_default_supplier()
            supplier = fallback_supplier
            xref_gap = True

        extracted.append(
            {
                "po_number": row.po_number,
                "line_number": row.line_number,
                "sku": xref.get("mapped_sku") if xref and xref.get("mapped_sku") else row.sku,
                "item": xref.get("mapped_item") if xref and xref.get("mapped_item") else item_code,
                "supplier": supplier,
                "ordered_quantity": row.ordered_quantity,
                "delivered_quantity": row.delivered_quantity,
                "remaining_quantity": row.remaining_quantity,
                "in_date": getattr(row, "in_date", None),
                "promised_date": row.promised_date,
                "current_status": current_status,
                "po_insert_date": row.po_insert_date,
                "final_customer": getattr(row, "final_customer", "") or "",
                "source_quality": POLine.SOURCE_QUALITY_ERP,
                "last_update_timestamp": row.last_update_timestamp,
                "custom_date_1": getattr(row, "custom_date_1", None),
                "custom_date_2": getattr(row, "custom_date_2", None),
                "custom_date_3": getattr(row, "custom_date_3", None),
                "custom_date_4": getattr(row, "custom_date_4", None),
                "custom_date_5": getattr(row, "custom_date_5", None),
                "custom_text_1": getattr(row, "custom_text_1", None),
                "custom_text_2": getattr(row, "custom_text_2", None),
                "custom_text_3": getattr(row, "custom_text_3", None),
                "custom_text_4": getattr(row, "custom_text_4", None),
                "custom_text_5": getattr(row, "custom_text_5", None),
                "custom_decimal_1": getattr(row, "custom_decimal_1", None),
                "custom_decimal_2": getattr(row, "custom_decimal_2", None),
                "custom_decimal_3": getattr(row, "custom_decimal_3", None),
                "custom_decimal_4": getattr(row, "custom_decimal_4", None),
                "custom_decimal_5": getattr(row, "custom_decimal_5", None),
                "_xref_gap": xref_gap,
                "_erp_item_code": item_code,
            }
        )

    return extracted


def _initialize_baseline_from_snapshot_run(*, run_identifier: str) -> int:
    baseline_snapshots = list(ERPSnapshot.objects.filter(run_identifier=run_identifier).select_related("supplier").order_by("id"))
    fallback_supplier = _get_default_supplier()

    po_lines = [
        POLine(
            po_number=snapshot.po_number,
            line_number=snapshot.line_number,
            sku=snapshot.sku,
            item=snapshot.item,
            supplier=snapshot.supplier or fallback_supplier,
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
        for snapshot in baseline_snapshots
    ]

    # H1: POLine creation and audit event are atomic — both succeed or neither does.
    with transaction.atomic():
        before_count = POLine.objects.count()
        POLine.objects.bulk_create(po_lines, ignore_conflicts=True, batch_size=1000)
        created_count = max(POLine.objects.count() - before_count, 0)
        create_audit_event(
            event_type="ingestion.baseline.initialized",
            source=AuditEvent.SOURCE_INGESTION,
            new_values={
                "run_identifier": run_identifier,
                "snapshot_count": len(baseline_snapshots),
                "created_po_lines": created_count,
            },
            reason="Baseline initialization from ERP snapshot run.",
        )

    return created_count


def _record_snapshot_failure_event(*, error: Exception, attempts: int) -> None:
    logger.exception("ERP snapshot extraction failed after %s attempts.", attempts)
    create_audit_event(
        event_type="ingestion.snapshot.failed",
        source=AuditEvent.SOURCE_INGESTION,
        new_values={
            "attempts": attempts,
            "error_type": error.__class__.__name__,
            "error": str(error),
        },
        reason="ERP snapshot extraction failed after retry exhaustion.",
    )


def _load_active_item_xrefs() -> dict[str, dict[str, str]]:
    rows = ERPItemXref.objects.using("erp").filter(is_active=True)
    return {
        row.erp_item_code: {
            "mapped_sku": row.mapped_sku,
            "mapped_item": row.mapped_item,
            "supplier_code": row.supplier_code,
        }
        for row in rows
    }


def _load_supplier_map(supplier_codes: set[str]) -> dict[str, Supplier]:
    if not supplier_codes:
        return {}
    return {supplier.code: supplier for supplier in Supplier.objects.filter(code__in=supplier_codes)}


def _get_default_supplier() -> Supplier:
    code = getattr(settings, "INGESTION_DEFAULT_SUPPLIER_CODE", "DEFAULT")
    name = getattr(settings, "INGESTION_DEFAULT_SUPPLIER_NAME", "Default Supplier")
    supplier, _ = Supplier.objects.get_or_create(code=code, defaults={"name": name})
    return supplier


def _inactive_statuses() -> set[str]:
    configured = getattr(settings, "INGESTION_INACTIVE_STATUSES", ("closed", "cancelled", "complete", "completed"))
    return {str(value).strip().lower() for value in configured if str(value).strip()}


def _collect_unmapped_item_codes(records: list[dict[str, Any]]) -> list[str]:
    unmapped = {
        str(record.get("_erp_item_code") or "").strip()
        for record in records
        if record.get("_xref_gap")
    }
    return sorted(code for code in unmapped if code)


def _record_xref_gap_events(*, run_identifier: str, unmapped_item_codes: list[str]) -> None:
    if not unmapped_item_codes:
        return
    # H2: idempotence guard — skip if gap events already emitted for this run
    if AuditEvent.objects.filter(
        event_type="xref_gap",
        source=AuditEvent.SOURCE_INGESTION,
        new_values__run_identifier=run_identifier,
    ).exists():
        return
    # M1: all gap events emitted atomically — partial failure emits none
    with transaction.atomic():
        for item_code in unmapped_item_codes:
            create_audit_event(
                event_type="xref_gap",
                source=AuditEvent.SOURCE_INGESTION,
                new_values={
                    "run_identifier": run_identifier,
                    "erp_item_code": item_code,
                },
                reason="Unmapped ERP item code detected during ingestion.",
            )


def _generate_run_identifier(snapshot_timestamp) -> str:
    return f"snapshot-{snapshot_timestamp:%Y%m%d%H%M%S}-{uuid.uuid4().hex[:8]}"
