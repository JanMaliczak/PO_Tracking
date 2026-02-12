> BMAD Workflow: /bmad-bmm-research  
> Project: Cross-ERP Purchase Order (PO) Timeline, Batch Tracking & Forecasting  
> Date: 2026-02-10  
> Owner: (fill)

## 1) Problem framing
### Context
Two ERPs (supplier-side and customer-side) represent PO lifecycle differently:
- Supplier ERP overwrites PO line state (shipped qty + last shipment date mutate), making audit-grade history difficult.
- Customer ERP models shipments separately and often splits PO lines on partial delivery, making it hard to track “the same” order across systems.

Business needs:
- Expediting and exception management
- OTIF measurement (On-Time In-Full)
- Inventory planning
- Customer service visibility
- Mandatory audit-grade change history

### Core pain points
- No single “truth” for readiness dates and stage milestones.
- Partial delivery (“batches”) exist in reality, but are not consistently represented in both ERPs.
- Enormous manual workload if users must split lines or maintain batch data in ERPs.
- Change history is hard because at least one ERP overwrites records.

## 2) What sample SQL extract enables (supplier ERP)
Your SQL extract (per SKU sample) includes:
- PO baseline: PO date, promised delivery date, lead time (LT), POQty
- Delivery evidence: DeliveredQty + InDate (+ optional container fields)
- Derived diffs: DD_diff, InDate_diff, etc.

### Key insight: DeliveredQty + InDate = implicit batch events
Each distinct (PO/Contract, SKU, InDate) with DeliveredQty > 0 can be normalized into a “batch receipt event”.
This provides:
- number of batches per PO line
- inter-batch gaps (days between receipts)
- batch size distributions (% of PO per batch)
- lateness distributions (InDate vs promised delivery date)
- supplier reliability patterns
Even if ERPs don’t store batches explicitly, history can reconstruct them.

## 3) Market research: solution landscape
### 3.1 Supply chain visibility (SCV) platforms
SCV tools focus on shipment tracking, predictive ETAs, and exception management; many integrate with ERP/TMS/WMS. Examples include large enterprise offerings like IBM supply chain visibility solutions. :contentReference[oaicite:1]{index=1}  
Many SCV platforms emphasize “single source of truth” for transit visibility, not necessarily detailed pre-shipment production readiness.

### 3.2 AI-driven PO visibility & supplier follow-up tools
Some vendors position themselves specifically around PO visibility and supplier collaboration “inside your ERP”, often with AI/exceptions. :contentReference[oaicite:2]{index=2}

### 3.3 OTIF analytics & order management tools
OTIF is a widely used KPI (on-time + complete). Tools and guidance exist, but data collection and standardization is frequently cited as the core challenge. :contentReference[oaicite:3]{index=3}

### 3.4 Open-source / composable building blocks
There are open-source logistics / supply chain platforms that can inspire design patterns (portals, tracking, modular architecture), but they won’t solve your “cross-ERP audit-grade PO stage truth” out of the box. :contentReference[oaicite:4]{index=4}

### Market gap / differentiation opportunity
Most solutions prioritize:
- carrier / transport visibility (where is the shipment?)
- downstream status

Your key gap:
- upstream production readiness and milestone truth (what will be ready, when?)
- audit-grade history across two incompatible ERP models
- batch-level tracking rooted in real deliveries (DeliveredQty + InDate), plus proposed future batches

## 4) Technical research
### 4.1 Recommended architectural pattern: Canonical PO Timeline + Event Log
Because at least one ERP overwrites rows, audit-grade history should be created outside the ERP via:
- periodic snapshots + diffs, OR
- database change data capture (CDC), OR
- both (CDC for hot tables, snapshots for safety)

Store everything as append-only events:
- date changes (promised / production ready / ready-to-dispatch / ETD / ETA)
- quantity allocations into batches
- status transitions
- mismatch and reconciliation events

This enables:
- immutable audit history (who/when/what)
- reconstruction of “current state” at any time
- downstream analytics & ML features

### 4.2 Data ingestion options for MS SQL supplier ERP
#### Option A: Snapshot + diff (simplest, robust)
- Nightly query: extract active/open PO lines (filtered window)
- Hash key fields; store snapshot version
- Produce change events when fields change

Pros: easy, low risk  
Cons: only daily granularity unless run more frequently

#### Option B: SQL Server CDC + Debezium/Kafka (near real-time)
Debezium supports SQL Server CDC by reading change tables; requires CDC enabled on DB and captured tables. :contentReference[oaicite:5]{index=5}  
Pros: fine-grained event stream, close to real-time  
Cons: infra complexity (Kafka/Connect), operational ownership

Recommendation for your stated requirement (1 day latency acceptable):
- Start with Snapshot+Diff (daily)
- Keep CDC as Phase 2 if needed

### 4.3 Canonical data model (high level)
- PO Line (canonical identity + ordered qty + promised date baseline)
- Stage dates (append-only, versioned)
- Batch (ready-to-dispatch event) + BatchLine allocations
- Shipment/Container linkage (optional but supported)
- Event/Audit log (all changes, all sources)

### 4.4 How historical DeliveredQty/InDate helps
- Creates training data for:
  - inter-batch time prediction
  - probability of partial shipment
  - expected batch size ratio
  - lateness risk
- Enables supplier-SKU lead-time profiling:
  - median, P80/P90 lead time
  - drift vs promised dates
  - “first partial then remainder” patterns

## 5) ML research: feasibility & recommended approach
### 5.1 Where ML adds value
Use ML to propose:
- next batch date window (e.g., P50/P80)
- risk score that promised date will be missed
- expected remaining-qty completion date

### 5.2 Start with a hybrid: Rules baseline + ML refinement
Because batch quantities are only known near dispatch, ML should *assist* rather than fully automate.
Baseline rules:
- if first receipt < X% of POQty, expect additional batches
- use supplier+SKU empirical distribution of inter-batch gaps
- cap predictions with percentiles (avoid extreme forecasts)

ML refinement:
- Quantile regression (predict P50/P80/P90 dates)
- Gradient boosting or Bayesian hierarchical model for sparse supplier/SKU history
- Features:
  - promised date, PO_LT, seasonality (month)
  - historical lateness for supplier/SKU
  - first batch size ratio
  - days late at first batch
  - count of prior batches
  - remaining qty ratio

### 5.3 Data constraints & mitigation
- Current sample is 1 SKU. Real model needs more SKUs and/or supplier diversity.
- Use hierarchical pooling:
  - supplier-level priors (fallback)
  - supplier+category
  - supplier+SKU (when sufficient history)

## 6) Security & governance research (practical)
- Audit-grade history implies immutable event storage + access controls
- Data minimization: store only fields needed for planning/OTIF
- Role-based access: internal planner vs supplier view (if portal)
- Provenance tagging: every event has source (SupplierERP, CustomerERP, Manual)

## 7) Research conclusions
1) Your supplier ERP extract already supports batch reconstruction via DeliveredQty+InDate.
2) A canonical “PO Timeline + Event Log” system is the correct foundation for audit-grade history.
3) Start with daily snapshot+diff; keep SQL Server CDC/Debezium as optional Phase 2. :contentReference[oaicite:6]{index=6}
4) ML is feasible and valuable for “next batch window” and risk scoring, but should be layered after a deterministic baseline.

## 8) Open questions (can be answered later)
- Write-back requirement into ERPs?
- Identity resolution rules when item codes mismatch (xref governance workflow)?
- What milestone stages must be tracked (production start, production complete, ready-to-dispatch, etc.)?