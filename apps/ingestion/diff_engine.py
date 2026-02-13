from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
import json
from typing import Any

from django.db import transaction
from django.utils import timezone

from apps.audit.models import AuditEvent
from apps.core.services import create_audit_event
from apps.ingestion.models import ERPChangeEvent, ERPSnapshot
from apps.po.models import POLine


# (event field name, ERPSnapshot attribute, POLine attribute)
FIELD_MAP: tuple[tuple[str, str, str], ...] = (
    ("sku", "sku", "sku"),
    ("item", "item", "item"),
    ("supplier", "supplier_id", "supplier_id"),
    ("ordered_quantity", "ordered_quantity", "ordered_quantity"),
    ("delivered_quantity", "delivered_quantity", "delivered_quantity"),
    ("remaining_quantity", "remaining_quantity", "remaining_quantity"),
    ("promised_date", "promised_date", "promised_date"),
    ("current_status", "current_status", "current_status"),
    ("po_insert_date", "po_insert_date", "po_insert_date"),
    ("final_customer", "final_customer", "final_customer"),
    ("source_quality", "source_quality", "source_quality"),
    ("last_update_timestamp", "last_update_timestamp", "last_update_timestamp"),
    ("custom_date_1", "custom_date_1", "custom_date_1"),
    ("custom_date_2", "custom_date_2", "custom_date_2"),
    ("custom_date_3", "custom_date_3", "custom_date_3"),
    ("custom_date_4", "custom_date_4", "custom_date_4"),
    ("custom_date_5", "custom_date_5", "custom_date_5"),
    ("custom_text_1", "custom_text_1", "custom_text_1"),
    ("custom_text_2", "custom_text_2", "custom_text_2"),
    ("custom_text_3", "custom_text_3", "custom_text_3"),
    ("custom_text_4", "custom_text_4", "custom_text_4"),
    ("custom_text_5", "custom_text_5", "custom_text_5"),
    ("custom_decimal_1", "custom_decimal_1", "custom_decimal_1"),
    ("custom_decimal_2", "custom_decimal_2", "custom_decimal_2"),
    ("custom_decimal_3", "custom_decimal_3", "custom_decimal_3"),
    ("custom_decimal_4", "custom_decimal_4", "custom_decimal_4"),
    ("custom_decimal_5", "custom_decimal_5", "custom_decimal_5"),
    ("custom_column_sources", "custom_column_sources", "custom_column_sources"),
)

POLINE_UPDATE_FIELDS: tuple[str, ...] = tuple(sorted({mapping[2] for mapping in FIELD_MAP} | {"is_stale", "staleness_checked_at"}))


@dataclass(frozen=True)
class SnapshotDiffResult:
    current_run_identifier: str
    previous_run_identifier: str | None
    processed_po_lines_count: int
    changed_po_lines_count: int
    new_po_lines_count: int
    absent_po_lines_count: int
    absent_po_lines: list[tuple[str, int]]
    change_events_count: int
    audit_events_count: int
    rerun_skipped: bool = False


def run_snapshot_diff(
    *,
    current_run_identifier: str,
    previous_run_identifier: str | None = None,
    now=None,
) -> SnapshotDiffResult:
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

    previous_rows: list[ERPSnapshot] = []
    if previous_run_identifier:
        previous_rows = list(
            ERPSnapshot.objects.filter(run_identifier=previous_run_identifier)
            .select_related("supplier")
            .order_by("id")
        )
        if not previous_rows:
            raise ValueError(f"No snapshots found for previous run '{previous_run_identifier}'.")

    timestamp = now or timezone.now()

    with transaction.atomic():
        if _already_processed(current_run_identifier=current_run_identifier):
            return SnapshotDiffResult(
                current_run_identifier=current_run_identifier,
                previous_run_identifier=previous_run_identifier,
                processed_po_lines_count=len(current_rows),
                changed_po_lines_count=0,
                new_po_lines_count=0,
                absent_po_lines_count=0,
                absent_po_lines=[],
                change_events_count=0,
                audit_events_count=0,
                rerun_skipped=True,
            )

        current_by_key = {(row.po_number, row.line_number): row for row in current_rows}
        previous_by_key = {(row.po_number, row.line_number): row for row in previous_rows}

        current_keys = set(current_by_key.keys())
        previous_keys = set(previous_by_key.keys())
        shared_keys = current_keys & previous_keys
        new_keys = current_keys - previous_keys
        absent_keys = previous_keys - current_keys

        po_numbers = sorted({key[0] for key in (current_keys | absent_keys)})
        existing_po_lines = {
            (po_line.po_number, po_line.line_number): po_line
            for po_line in POLine.objects.filter(po_number__in=po_numbers)
        }

        changed_payloads: dict[tuple[str, int], dict[str, Any]] = {}
        for key in sorted(shared_keys):
            previous = previous_by_key[key]
            current = current_by_key[key]
            previous_values: dict[str, Any] = {}
            new_values: dict[str, Any] = {}
            field_changes: list[tuple[str, Any, Any]] = []

            for field_name, snapshot_attr, _po_attr in FIELD_MAP:
                previous_value = getattr(previous, snapshot_attr)
                current_value = getattr(current, snapshot_attr)
                if not _values_equal(previous_value, current_value):
                    previous_values[field_name] = _to_jsonable(previous_value)
                    new_values[field_name] = _to_jsonable(current_value)
                    field_changes.append((field_name, previous_value, current_value))

            if field_changes:
                changed_payloads[key] = {
                    "previous_values": previous_values,
                    "new_values": new_values,
                    "field_changes": field_changes,
                    "snapshot": current,
                }

        # Upsert PO lines from current snapshot rows
        to_create: list[POLine] = []
        to_update: list[POLine] = []
        for key in sorted(current_keys):
            snapshot = current_by_key[key]
            po_line = existing_po_lines.get(key)
            if po_line is None:
                po_line = POLine(po_number=snapshot.po_number, line_number=snapshot.line_number)
                _apply_snapshot_values(po_line=po_line, snapshot=snapshot, stale=False, checked_at=timestamp)
                to_create.append(po_line)
                continue

            _apply_snapshot_values(po_line=po_line, snapshot=snapshot, stale=False, checked_at=timestamp)
            to_update.append(po_line)

        if to_create:
            POLine.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=1000)
            created_keys_set = {(pl.po_number, pl.line_number) for pl in to_create}
            for po_line in POLine.objects.filter(po_number__in=[key[0] for key in created_keys_set]):
                key = (po_line.po_number, po_line.line_number)
                if key in created_keys_set:
                    existing_po_lines[key] = po_line

        if to_update:
            POLine.objects.bulk_update(to_update, fields=POLINE_UPDATE_FIELDS, batch_size=1000)

        # Mark absent lines as stale without deleting
        absent_po_lines: list[tuple[str, int]] = sorted(absent_keys)
        stale_updates: list[POLine] = []
        for key in absent_po_lines:
            po_line = existing_po_lines.get(key)
            if po_line is None:
                continue
            po_line.is_stale = True
            po_line.staleness_checked_at = timestamp
            stale_updates.append(po_line)

        if stale_updates:
            POLine.objects.bulk_update(stale_updates, fields=["is_stale", "staleness_checked_at"], batch_size=1000)

        # Create field-level ERP change events and per-line audit entries
        change_events: list[ERPChangeEvent] = []
        audit_events_created = 0
        for key in sorted(changed_payloads.keys()):
            payload = changed_payloads[key]
            po_line = existing_po_lines.get(key)
            snapshot = payload["snapshot"]
            for field_name, previous_value, new_value in payload["field_changes"]:
                change_events.append(
                    ERPChangeEvent(
                        po_line=po_line,
                        field_name=field_name,
                        previous_value=_to_text(previous_value),
                        new_value=_to_text(new_value),
                        snapshot=snapshot,
                        detected_at=timestamp,
                    )
                )

            create_audit_event(
                event_type="ingestion.change",
                source=AuditEvent.SOURCE_INGESTION,
                po_line=po_line,
                previous_values=payload["previous_values"],
                new_values=payload["new_values"],
                reason=f"Snapshot diff detected for run {current_run_identifier}.",
            )
            audit_events_created += 1

        if change_events:
            ERPChangeEvent.objects.bulk_create(change_events, batch_size=1000)

        # Audit events for new PO lines
        for key in sorted(new_keys):
            po_line = existing_po_lines.get(key)
            create_audit_event(
                event_type="ingestion.po_line.created",
                source=AuditEvent.SOURCE_INGESTION,
                po_line=po_line,
                previous_values={},
                new_values={
                    "po_number": po_line.po_number if po_line else key[0],
                    "line_number": po_line.line_number if po_line else key[1],
                    "run_identifier": current_run_identifier,
                },
                reason=f"PO line created from snapshot run {current_run_identifier}.",
            )
            audit_events_created += 1

        # Optional summary event captures absent-line reporting and run-level idempotence marker.
        create_audit_event(
            event_type="ingestion.diff.processed",
            source=AuditEvent.SOURCE_INGESTION,
            previous_values={"previous_run_identifier": previous_run_identifier},
            new_values={
                "run_identifier": current_run_identifier,
                "processed_po_lines": len(current_keys),
                "changed_po_lines": len(changed_payloads),
                "new_po_lines": len(new_keys),
                "absent_po_lines": len(absent_po_lines),
            },
            reason="Snapshot diff processing completed.",
        )
        audit_events_created += 1

        return SnapshotDiffResult(
            current_run_identifier=current_run_identifier,
            previous_run_identifier=previous_run_identifier,
            processed_po_lines_count=len(current_keys),
            changed_po_lines_count=len(changed_payloads),
            new_po_lines_count=len(new_keys),
            absent_po_lines_count=len(absent_po_lines),
            absent_po_lines=absent_po_lines,
            change_events_count=len(change_events),
            audit_events_count=audit_events_created,
            rerun_skipped=False,
        )


def _apply_snapshot_values(*, po_line: POLine, snapshot: ERPSnapshot, stale: bool, checked_at) -> None:
    for _field_name, snapshot_attr, po_attr in FIELD_MAP:
        setattr(po_line, po_attr, getattr(snapshot, snapshot_attr))
    po_line.is_stale = stale
    po_line.staleness_checked_at = checked_at


def _already_processed(*, current_run_identifier: str) -> bool:
    return AuditEvent.objects.filter(
        event_type="ingestion.diff.processed",
        source=AuditEvent.SOURCE_INGESTION,
        new_values__run_identifier=current_run_identifier,
    ).exists()


def _values_equal(left: Any, right: Any) -> bool:
    if isinstance(left, Decimal) or isinstance(right, Decimal):
        left_decimal = Decimal(str(left)) if left is not None else None
        right_decimal = Decimal(str(right)) if right is not None else None
        return left_decimal == right_decimal
    return left == right


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _to_jsonable(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(inner) for inner in value]
    return value


def _to_text(value: Any) -> str | None:
    if value is None:
        return None
    return json.dumps(_to_jsonable(value), sort_keys=True)
