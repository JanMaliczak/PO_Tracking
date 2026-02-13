from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from apps.ingestion.models import ERPSnapshot
from apps.po.models import POLine


DEFAULT_CUSTOM_COLUMN_MAPPING: dict[str, str] = {
    **{f"custom_date_{idx}": f"custom_date_{idx}" for idx in range(1, 6)},
    **{f"custom_text_{idx}": f"custom_text_{idx}" for idx in range(1, 6)},
    **{f"custom_decimal_{idx}": f"custom_decimal_{idx}" for idx in range(1, 6)},
}


@dataclass(frozen=True)
class CustomColumnIngestionResult:
    run_identifier: str
    processed_po_lines_count: int
    updated_po_lines_count: int
    populated_fields_count: int


def ingest_custom_columns_from_snapshot(
    *,
    run_identifier: str,
    mapping: dict[str, str] | None = None,
) -> CustomColumnIngestionResult:
    snapshot_rows = list(
        ERPSnapshot.objects.filter(run_identifier=run_identifier)
        .select_related("supplier")
        .order_by("id")
    )
    if not snapshot_rows:
        raise ValueError(f"No snapshots found for run '{run_identifier}'.")

    mapping = mapping or DEFAULT_CUSTOM_COLUMN_MAPPING
    keys = {(row.po_number, row.line_number) for row in snapshot_rows}
    po_numbers = sorted({po_number for po_number, _line_number in keys})
    po_lines_by_key = {
        (po_line.po_number, po_line.line_number): po_line
        for po_line in POLine.objects.filter(po_number__in=po_numbers)
    }

    updated_po_lines: list[POLine] = []
    updated_fields_count = 0
    for snapshot in snapshot_rows:
        key = (snapshot.po_number, snapshot.line_number)
        po_line = po_lines_by_key.get(key)
        if po_line is None:
            continue

        sources = dict(po_line.custom_column_sources or {})
        line_touched = False
        for po_field, snapshot_field in mapping.items():
            current_source = str(sources.get(po_field, "")).strip().lower()
            if current_source == "user":
                continue

            if not hasattr(snapshot, snapshot_field):
                continue

            incoming_value = getattr(snapshot, snapshot_field)
            if incoming_value is None:  # M2: never overwrite with a null ERP value
                continue
            if getattr(po_line, po_field) == incoming_value:  # L1: skip unchanged values
                continue
            setattr(po_line, po_field, incoming_value)
            sources[po_field] = "erp"
            line_touched = True
            updated_fields_count += 1

        if line_touched:
            po_line.custom_column_sources = sources
            updated_po_lines.append(po_line)

    if updated_po_lines:
        unique_update_fields = sorted(set(mapping.keys()) | {"custom_column_sources"})
        POLine.objects.bulk_update(updated_po_lines, fields=unique_update_fields, batch_size=1000)

    return CustomColumnIngestionResult(
        run_identifier=run_identifier,
        processed_po_lines_count=len(snapshot_rows),
        updated_po_lines_count=len(updated_po_lines),
        populated_fields_count=updated_fields_count,
    )
