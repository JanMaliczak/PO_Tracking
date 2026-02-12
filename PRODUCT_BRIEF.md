> BMAD Workflow: /bmad-bmm-create-product-brief  
> Product: PO Timeline & Batch Tracker (Cross-ERP)  
> Date: 2026-02-10  
> Version: v0.1

## 1) Product summary
Build a lightweight “third system” that becomes the operational truth for:
- PO line readiness milestones (production / ready-to-dispatch)
- batch-level deliveries (partial shipments)
- change/audit history across two ERPs
- delay/OTIF visibility and exception management
- proposed next batch dates (rules + ML)

This product bridges incompatible ERP models and enables proactive expediting with audit-grade traceability.

BMAD context: This Product Brief is the recommended foundation document before PRD/architecture. :contentReference[oaicite:7]{index=7}

## 2) Target users & jobs-to-be-done
### Primary users
- Supply chain / procurement expeditors
- Planners (inventory, production coordination)
- Customer service (ETA communication)

### Secondary users
- Suppliers / supplier planners (optional portal)
- Management (KPI dashboards)

### JTBD
- “Tell me what is late, by how much, and how much quantity is impacted.”
- “Let me record the real readiness date and see how it changed over time.”
- “Track partial batches without manually splitting ERP order lines.”
- “Predict likely next batch delivery window so I can expedite earlier.”

## 3) Problem statement
Current ERPs store PO dates and partial shipments inconsistently:
- Supplier ERP overwrites PO line state → no reliable audit history.
- Customer ERP uses shipments and line splitting → hard to reconcile and track end-to-end.

As a result:
- users don’t trust dates
- delays are discovered late
- tracking partial deliveries is manual and error-prone

## 4) Goals and non-goals
### Goals (MVP)
- Single list view of active PO lines with:
  - current status
  - delay in days
  - remaining qty
  - next expected readiness/dispatch date
- PO detail view showing:
  - timeline of date changes (audit-grade)
  - batch deliveries (derived from DeliveredQty+InDate, and/or manual batch records)
- Ability to record/update milestone dates (with reason + audit trail)
- Daily sync from supplier ERP (direct DB read) to refresh baseline + detect changes
- Batch proposal engine (rules-based) to suggest next batch date window (optional MVP-2)

### Non-goals (initially)
- Full carrier/transport tracking (GPS, multimodal tracking)
- Automated reconciliation of container/invoice across all suppliers without identifiers
- Real-time streaming ingestion (CDC/Kafka) in v1 (keep as Phase 2)

## 5) Core concepts and definitions
- **PO Line (canonical):** (PO number, supplier, item) with ordered qty and promised date.
- **Milestone dates:** production-ready, ready-to-dispatch, etc. (versioned).
- **Batch:** “part (or whole) ready to dispatch” with allocated qty.
- **Audit-grade history:** append-only event history for every change + provenance.

## 6) Data sources (v1)
### Supplier ERP (MS SQL)
- PO lines: qty, PO date, promised delivery date, lead time, etc.
- Delivery history: DeliveredQty + InDate (used to reconstruct batches)
- Optional: container/invoice/packing list IDs if available at order level

### Customer ERP
- Optional in v1: baseline cross-check only
- v2+: ETD/ETA pseudo/real shipment signals

## 7) Key workflows (MVP)
1) **Daily ingestion**
   - pull active PO lines for last N months and all open orders
   - compute snapshot hashes
   - write change events when fields differ from last snapshot

2) **Exception dashboard**
   - filter by supplier, item, “late”, “at risk”
   - show: promised date vs current expected dispatch date vs remaining qty

3) **Milestone update**
   - user sets “production ready” and/or “ready-to-dispatch”
   - system records event (who/when/source/comment)

4) **Batch tracking**
   - system reconstructs historical batches from DeliveredQty+InDate
   - users can create future batches (planned) and allocate qty (no ERP line splitting)

## 8) Status model (simple and useful)
- Planned (baseline only)
- In Production (has production-ready estimate)
- Ready to Dispatch (batch planned/confirmed)
- Part Delivered (some batches delivered, remaining > 0)
- Fully Delivered (remaining = 0)
- Cancelled/Closed (if signal exists)

## 9) Success metrics
Operational:
- % PO lines with an explicit readiness date set
- reduction in “unknown” late orders
- mean time to detect slippage (days earlier than today)
- expeditor workload reduced (manual tracking time)

Performance/KPI:
- OTIF improvement or improved measurement confidence (audit completeness)
- forecast accuracy for next batch date window (P50/P80 hit rate)

## 10) Risks & mitigations
- **Identity mismatch (item codes):** implement item cross-reference table + review workflow.
- **Overwritten ERP records:** use snapshot+diff event generation; add CDC later if needed.
- **User adoption:** keep UI minimal (list + timeline + 2 date fields) and automate proposals.
- **Data anomalies (overdelivery, negative remaining):** treat as first-class flags, not silent “cleanup”.

## 11) Competitive landscape (positioning)
- SCV platforms provide transit visibility and predictive ETAs, but often don’t solve upstream readiness truth and cross-ERP audit-grade milestone history. :contentReference[oaicite:8]{index=8}
- AI PO visibility tools exist, but your differentiator is *canonical audit history + batch model built from ERP reality* + tailored readiness workflow. :contentReference[oaicite:9]{index=9}

## 12) MVP scope proposal (implementation-oriented)
### Screens
- Dashboard: Active PO lines + filters + delay/remaining/status
- PO detail: timeline + batch table + edit milestone dates
- Admin: suppliers, item xref mapping, users/roles

### Integrations
- Supplier ERP read-only SQL connection (scheduled nightly job)
- (Optional) CSV import for edge suppliers (not preferred)

### Data model (high level)
- po_line
- date_event (append-only)
- dispatch_batch + batch_line
- erp_snapshot + erp_change_event
- item_xref

## 13) Next BMAD step
Proceed to PRD workflow for full requirements, personas, user stories, metrics, and risks:
- /bmad-bmm-create-prd → output PRD.md :contentReference[oaicite:10]{index=10}