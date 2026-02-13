from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from apps.audit.models import AuditEvent
from apps.core.services import create_audit_event
from apps.ingestion.batch_reconstruction import reconstruct_historical_batches
from apps.ingestion.custom_columns import ingest_custom_columns_from_snapshot
from apps.ingestion.diff_engine import run_snapshot_diff
from apps.ingestion.snapshot import run_snapshot_extraction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run end-to-end ERP ingestion pipeline and emit structured results."

    def add_arguments(self, parser):
        parser.add_argument(
            "--baseline",
            action="store_true",
            help="Run first-time baseline mode (skips diff and treats rows as new).",
        )

    def handle(self, *args, **options):
        baseline = options.get("baseline", False)
        started = time.monotonic()
        # H2: generate a fallback identifier so the failure audit event is always
        # traceable, even when snapshot extraction fails before producing its own.
        run_identifier = f"pending-{uuid.uuid4().hex[:12]}"

        try:
            snapshot_result = run_snapshot_extraction(baseline_mode=baseline)
            run_identifier = snapshot_result.run_identifier

            # Snapshot extraction already applies xref mapping logic and gap detection;
            # this stage preserves explicit pipeline sequencing for reporting.
            xref_stage = {
                "xref_gaps_found": snapshot_result.unmapped_item_count,
                "unmapped_item_codes": list(snapshot_result.unmapped_item_codes),
            }

            if baseline:
                diff_result = None
                new_lines_created = snapshot_result.baseline_created_po_lines
                change_events_detected = 0
            else:
                diff_result = run_snapshot_diff(current_run_identifier=run_identifier)
                new_lines_created = diff_result.new_po_lines_count
                change_events_detected = diff_result.change_events_count

            batch_result = reconstruct_historical_batches(current_run_identifier=run_identifier)
            custom_columns_result = ingest_custom_columns_from_snapshot(run_identifier=run_identifier)

            duration_seconds = round(time.monotonic() - started, 3)
            summary = {
                "run_identifier": run_identifier,
                "baseline": baseline,
                "duration_seconds": duration_seconds,
                "po_lines_processed": snapshot_result.snapshot_count,
                "new_lines_created": new_lines_created,
                "change_events_detected": change_events_detected,
                "batches_reconstructed": batch_result.created_batches_count,
                "custom_columns_populated": custom_columns_result.populated_fields_count,
                "xref_gaps_found": xref_stage["xref_gaps_found"],
                "unmapped_item_codes": xref_stage["unmapped_item_codes"],
                "errors_encountered": [],
            }
            if diff_result is not None:
                summary["absent_po_lines"] = diff_result.absent_po_lines_count

            create_audit_event(
                event_type="ingestion_completed",
                source=AuditEvent.SOURCE_INGESTION,
                new_values=summary,
                reason="Ingestion pipeline completed successfully.",
            )

            logger.info("Ingestion completed: %s", json.dumps(summary, sort_keys=True))
            self.stdout.write(self.style.SUCCESS(json.dumps(summary, sort_keys=True)))
            return
        except Exception as exc:
            duration_seconds = round(time.monotonic() - started, 3)
            failure_payload: dict[str, Any] = {
                "run_identifier": run_identifier,
                "baseline": baseline,
                "duration_seconds": duration_seconds,
                "errors_encountered": [str(exc)],
            }
            # H1: log unconditionally BEFORE the audit DB write so observability is
            # preserved even if the database is unavailable during failure handling.
            logger.exception("Ingestion failed: %s", exc)
            try:
                create_audit_event(
                    event_type="ingestion_failed",
                    source=AuditEvent.SOURCE_INGESTION,
                    new_values=failure_payload,
                    reason="Ingestion pipeline failed.",
                )
            except Exception as audit_exc:
                logger.exception("Failed to write ingestion failure audit event: %s", audit_exc)
            raise CommandError(f"Ingestion failed: {exc}") from exc
