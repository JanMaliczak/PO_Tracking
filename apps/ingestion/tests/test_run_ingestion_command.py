from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone

from apps.ingestion.batch_reconstruction import BatchReconstructionResult
from apps.ingestion.custom_columns import CustomColumnIngestionResult
from apps.ingestion.diff_engine import SnapshotDiffResult
from apps.ingestion.snapshot import SnapshotExtractionResult


class RunIngestionCommandTests(TestCase):
    def setUp(self):
        self.snapshot_result = SnapshotExtractionResult(
            run_identifier="run-cmd-1",
            snapshot_timestamp=timezone.make_aware(datetime(2026, 2, 13, 22, 0, 0)),
            extracted_count=3,
            snapshot_count=3,
            baseline_initialized=False,
            baseline_created_po_lines=0,
            unmapped_item_count=1,
            unmapped_item_codes=("UNMAP-1",),
        )
        self.diff_result = SnapshotDiffResult(
            current_run_identifier="run-cmd-1",
            previous_run_identifier="run-prev",
            processed_po_lines_count=3,
            changed_po_lines_count=1,
            new_po_lines_count=1,
            absent_po_lines_count=0,
            absent_po_lines=[],
            change_events_count=2,
            audit_events_count=3,
            rerun_skipped=False,
        )
        self.batch_result = BatchReconstructionResult(
            run_identifier="run-cmd-1",
            created_batches_count=1,
            processed_po_lines_count=3,
        )
        self.custom_columns_result = CustomColumnIngestionResult(
            run_identifier="run-cmd-1",
            processed_po_lines_count=3,
            updated_po_lines_count=2,
            populated_fields_count=4,
        )

    @patch("apps.ingestion.management.commands.run_ingestion.create_audit_event")
    @patch("apps.ingestion.management.commands.run_ingestion.ingest_custom_columns_from_snapshot")
    @patch("apps.ingestion.management.commands.run_ingestion.reconstruct_historical_batches")
    @patch("apps.ingestion.management.commands.run_ingestion.run_snapshot_diff")
    @patch("apps.ingestion.management.commands.run_ingestion.run_snapshot_extraction")
    def test_orchestrates_pipeline_and_emits_completion_summary(
        self,
        snapshot_mock,
        diff_mock,
        batch_mock,
        custom_mock,
        audit_mock,
    ):
        snapshot_mock.return_value = self.snapshot_result
        diff_mock.return_value = self.diff_result
        batch_mock.return_value = self.batch_result
        custom_mock.return_value = self.custom_columns_result

        call_command("run_ingestion")

        snapshot_mock.assert_called_once_with(baseline_mode=False)
        diff_mock.assert_called_once_with(current_run_identifier="run-cmd-1")
        batch_mock.assert_called_once_with(current_run_identifier="run-cmd-1")
        custom_mock.assert_called_once_with(run_identifier="run-cmd-1")
        audit_mock.assert_called_once()

        kwargs = audit_mock.call_args.kwargs
        self.assertEqual(kwargs["event_type"], "ingestion_completed")
        self.assertEqual(kwargs["source"], "ingestion")
        self.assertEqual(kwargs["new_values"]["po_lines_processed"], 3)
        self.assertEqual(kwargs["new_values"]["new_lines_created"], 1)
        self.assertEqual(kwargs["new_values"]["change_events_detected"], 2)
        self.assertEqual(kwargs["new_values"]["batches_reconstructed"], 1)
        self.assertEqual(kwargs["new_values"]["custom_columns_populated"], 4)
        self.assertEqual(kwargs["new_values"]["xref_gaps_found"], 1)
        self.assertEqual(kwargs["new_values"]["unmapped_item_codes"], ["UNMAP-1"])
        self.assertEqual(kwargs["new_values"]["errors_encountered"], [])
        # M1: absent_po_lines is conditionally added in non-baseline mode
        self.assertEqual(kwargs["new_values"]["absent_po_lines"], 0)

    @patch("apps.ingestion.management.commands.run_ingestion.create_audit_event")
    @patch("apps.ingestion.management.commands.run_ingestion.ingest_custom_columns_from_snapshot")
    @patch("apps.ingestion.management.commands.run_ingestion.reconstruct_historical_batches")
    @patch("apps.ingestion.management.commands.run_ingestion.run_snapshot_diff")
    @patch("apps.ingestion.management.commands.run_ingestion.run_snapshot_extraction")
    def test_baseline_mode_skips_diff_and_uses_baseline_created_count(
        self,
        snapshot_mock,
        diff_mock,
        batch_mock,
        custom_mock,
        audit_mock,
    ):
        snapshot_mock.return_value = replace(self.snapshot_result, baseline_created_po_lines=5)
        batch_mock.return_value = self.batch_result
        custom_mock.return_value = self.custom_columns_result

        call_command("run_ingestion", "--baseline")

        snapshot_mock.assert_called_once_with(baseline_mode=True)
        diff_mock.assert_not_called()
        kwargs = audit_mock.call_args.kwargs
        self.assertEqual(kwargs["event_type"], "ingestion_completed")
        self.assertEqual(kwargs["new_values"]["baseline"], True)
        self.assertEqual(kwargs["new_values"]["new_lines_created"], 5)
        self.assertEqual(kwargs["new_values"]["change_events_detected"], 0)

    @patch("apps.ingestion.management.commands.run_ingestion.create_audit_event")
    @patch("apps.ingestion.management.commands.run_ingestion.run_snapshot_extraction", side_effect=RuntimeError("erp down"))
    def test_failure_path_emits_failed_audit_and_raises_command_error(self, _snapshot_mock, audit_mock):
        with self.assertRaises(CommandError):
            call_command("run_ingestion")

        audit_mock.assert_called_once()
        kwargs = audit_mock.call_args.kwargs
        self.assertEqual(kwargs["event_type"], "ingestion_failed")
        self.assertEqual(kwargs["source"], "ingestion")
        self.assertEqual(kwargs["new_values"]["errors_encountered"], ["erp down"])
        self.assertEqual(kwargs["new_values"]["baseline"], False)

    # M2: post-snapshot partial failure — run_identifier must be non-empty
    @patch("apps.ingestion.management.commands.run_ingestion.create_audit_event")
    @patch("apps.ingestion.management.commands.run_ingestion.ingest_custom_columns_from_snapshot")
    @patch("apps.ingestion.management.commands.run_ingestion.reconstruct_historical_batches")
    @patch("apps.ingestion.management.commands.run_ingestion.run_snapshot_diff", side_effect=RuntimeError("diff error"))
    @patch("apps.ingestion.management.commands.run_ingestion.run_snapshot_extraction")
    def test_post_snapshot_failure_includes_run_identifier_in_failure_payload(
        self,
        snapshot_mock,
        _diff_mock,
        _batch_mock,
        _custom_mock,
        audit_mock,
    ):
        snapshot_mock.return_value = self.snapshot_result

        with self.assertRaises(CommandError):
            call_command("run_ingestion")

        _batch_mock.assert_not_called()
        _custom_mock.assert_not_called()
        audit_mock.assert_called_once()
        kwargs = audit_mock.call_args.kwargs
        self.assertEqual(kwargs["event_type"], "ingestion_failed")
        self.assertEqual(kwargs["new_values"]["run_identifier"], "run-cmd-1")
        self.assertEqual(kwargs["new_values"]["errors_encountered"], ["diff error"])

    # M3: stdout output must be parseable JSON with required metric keys
    @patch("apps.ingestion.management.commands.run_ingestion.create_audit_event")
    @patch("apps.ingestion.management.commands.run_ingestion.ingest_custom_columns_from_snapshot")
    @patch("apps.ingestion.management.commands.run_ingestion.reconstruct_historical_batches")
    @patch("apps.ingestion.management.commands.run_ingestion.run_snapshot_diff")
    @patch("apps.ingestion.management.commands.run_ingestion.run_snapshot_extraction")
    def test_stdout_output_is_valid_json_with_required_fields(
        self,
        snapshot_mock,
        diff_mock,
        batch_mock,
        custom_mock,
        _audit_mock,
    ):
        snapshot_mock.return_value = self.snapshot_result
        diff_mock.return_value = self.diff_result
        batch_mock.return_value = self.batch_result
        custom_mock.return_value = self.custom_columns_result

        out = StringIO()
        call_command("run_ingestion", stdout=out, no_color=True)

        parsed = json.loads(out.getvalue().strip())
        self.assertEqual(parsed["po_lines_processed"], 3)
        self.assertEqual(parsed["xref_gaps_found"], 1)
        self.assertIn("duration_seconds", parsed)
        self.assertIn("run_identifier", parsed)
        self.assertIn("absent_po_lines", parsed)  # present in non-baseline mode

    # M4: --baseline failure path must set baseline=True in the failure audit payload
    @patch("apps.ingestion.management.commands.run_ingestion.create_audit_event")
    @patch("apps.ingestion.management.commands.run_ingestion.run_snapshot_extraction", side_effect=RuntimeError("erp down"))
    def test_baseline_failure_path_emits_failed_audit_with_baseline_true(self, _snapshot_mock, audit_mock):
        with self.assertRaises(CommandError):
            call_command("run_ingestion", "--baseline")

        audit_mock.assert_called_once()
        kwargs = audit_mock.call_args.kwargs
        self.assertEqual(kwargs["event_type"], "ingestion_failed")
        self.assertEqual(kwargs["new_values"]["baseline"], True)
        self.assertEqual(kwargs["new_values"]["errors_encountered"], ["erp down"])
