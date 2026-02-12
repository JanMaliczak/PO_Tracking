---
stepsCompleted: [1, 2, 3, 4, 5, 6]
status: complete
inputDocuments:
  - RESEARCH.md
  - PRODUCT_BRIEF.md
  - STACK.md
date: 2026-02-11
author: J.maliczak
---

# Product Brief: PO_Tracking

## Executive Summary

PO Timeline & Batch Tracker is a lightweight, self-hosted "third system" that becomes the single operational truth for purchase order milestones, batch-level deliveries, and change history across two incompatible ERPs. It replaces the current workflow of dozens of weekly Excel files — manually compiled by expeditors in China and consumed by planners in Europe — with a structured, audit-grade platform accessible from both sides of the Great Firewall.

The tool eliminates the information black hole between sub-suppliers, expeditors, and planners by enforcing structured input with full accountability (who updated what, when, and why), enabling proactive delay detection instead of weekly stale snapshots, and providing batch-level delivery tracking that neither ERP supports natively.

Built and maintained in-house on a Windows-native stack (Python/FastAPI, MS SQL, Django+HTMX), the system is designed for cost-effective ownership where commercial alternatives are either prohibitively expensive or incompatible with cross-firewall operations.

---

## Core Vision

### Problem Statement

Two aging ERPs (supplier-side and customer-side) represent the PO lifecycle in incompatible ways. The supplier ERP overwrites PO line state on each update, destroying audit history. The customer ERP splits lines on partial delivery, making end-to-end tracking nearly impossible. Neither system captures *why* dates change, *who* provided updates, or *when* information was received.

Today, expeditors in China manually compile weekly Excel files with thousands of records — requesting status from local sub-suppliers, then reporting what's done, what's delayed, and what's ready. This data flows to planners in Europe who work 6-8 hours offset, across different holiday calendars, with no way to verify data freshness, accuracy, or accountability.

### Problem Impact

- **Delays discovered too late**: With weekly Excel batches and thousands of records, planners often notice slippage days after it occurs — too late for meaningful intervention
- **No accountability trail**: Excel provides no record of who updated what and when, making it impossible to enforce data accuracy or trace information origins
- **Inconsistent, unreliable data**: Expeditors compile data under time pressure with no validation — errors propagate silently through the planning chain
- **Massive manual workload**: Dozens of Excel files maintained weekly, each with thousands of rows, duplicated across expeditors and planners
- **Timezone and cultural gaps**: China-Europe split (6-8h offset, different holidays including Chinese New Year and Golden Week) means the tool must serve as the asynchronous communication bridge — people can't just call each other

### Why Existing Solutions Fall Short

- **ERP modules**: Both ERPs are aging systems with no compatible modules for cross-system PO milestone tracking or batch-level visibility
- **Third-party SCV platforms**: Focus on carrier/transport visibility (where is the shipment?) rather than upstream production readiness and milestone truth; most are prohibitively expensive for this use case
- **AI PO visibility tools**: Exist but don't operate reliably across the Great Firewall, and licensing + maintenance costs are not acceptable
- **No cross-firewall solution**: No off-the-shelf product addresses the specific constraint of daily use by expeditors in China and planners in Europe across network boundaries

### Proposed Solution

A self-hosted, cross-firewall web application that:

1. **Ingests PO data nightly** from the supplier ERP (read-only SQL) and reconstructs batch history from delivery records (DeliveredQty + InDate)
2. **Provides structured input** for expeditors to record milestone updates, delay reasons, and goods readiness — with full audit trail (who/when/why)
3. **Surfaces exceptions proactively** so planners see delays, risks, and outstanding items without digging through spreadsheets
4. **Tracks batches explicitly** — partial deliveries, proposed future batches, and supplier confirmations — without requiring ERP line splitting
5. **Bridges sub-supplier communication** via WeChat or structured Excel templates, giving expeditors efficient tools to collect and relay status from Chinese suppliers
6. **Operates across the Great Firewall** with infrastructure prepared for both sides

### Key Differentiators

- **Cross-firewall by design**: Purpose-built for China-Europe operations where commercial SaaS solutions fail at the network boundary
- **Audit-grade accountability**: Every change logged with who, when, source, and reason — transforming an opaque Excel workflow into a transparent, traceable process
- **Sub-supplier communication integration**: WeChat and structured Excel options aligned with how Chinese suppliers actually communicate — not forcing Western email/portal paradigms
- **Zero vendor dependency**: Fully self-hosted, self-maintained on Windows-native infrastructure (MS SQL + Python), eliminating recurring license costs and external development dependencies
- **Built on real ERP access**: Direct SQL connection to supplier ERP provides ground-truth data that third-party tools can't access
- **Asynchronous-first design**: Engineered for timezone-offset teams — expeditors and planners work independently with the system as the always-current bridge

---

## Target Users

### Primary Users

#### 1. Expeditor (China-based) — "Wei"

**Profile:** One of 3 expeditors based in China, managing relationships with up to 30 local suppliers. Communicates primarily in Mandarin/Chinese Simplified, with limited English proficiency. The front line of PO status collection and supplier coordination.

**Current Workflow (pain):**
1. Downloads open orders from supplier ERP as Excel at the start of each week
2. Splits the file into per-supplier Excel sheets
3. Sends each supplier their sheet via WeChat (or occasionally email) requesting goods readiness updates
4. Waits for supplier responses (WeChat messages, marked-up Excel files)
5. Consolidates all supplier responses into one master Excel with line-by-line status: what's done, what's delayed, readiness dates
6. Sends the consolidated file to Planners in Europe

**Time cost:** This cycle consumes at least half of each working week — 50%+ of productive time spent on data gathering and formatting rather than actual expediting and problem-solving.

**Frustrations:**
- Repetitive manual work (download, split, send, collect, consolidate) every single week
- No way to track who provided what information and when
- Suppliers respond inconsistently — some via WeChat voice, some via marked-up Excel, some not at all
- Poor data quality because there's no structured input or validation
- When planners ask "why is this late?" — hard to trace back to the original supplier response

**Success vision:** Open the app, see which POs need supplier updates, send structured requests via WeChat or Excel template, record responses with one click, and move on to actual problem-solving. The weekly data compilation cycle drops from 2.5 days to hours.

**Language requirement:** Chinese Simplified UI is essential.

---

#### 2. Planner (Europe-based) — "Katrin"

**Profile:** One of 3 planners in Europe responsible for inventory coordination, production planning, and customer delivery commitments. Relies entirely on expeditor-provided data to understand PO status.

**Current Workflow (pain):**
1. Receives one consolidated Excel file from China (weekly, often Monday/Tuesday)
2. Searches through thousands of rows to find relevant PO lines
3. Identifies delays by comparing dates manually
4. Updates ERP with new information or directly informs Customer Service about delays
5. By the time a delay is noticed, it's often too late for corrective action

**Frustrations:**
- Data is already stale by the time it arrives (compiled over several days in China)
- One massive Excel file with thousands of records — finding exceptions is like finding needles in a haystack
- No way to verify when information was last updated or by whom
- 6-8 hour timezone offset means questions to expeditors are answered next day at earliest
- Different holiday calendars (Chinese New Year, Golden Week) create data blackout periods

**Success vision:** Open a dashboard showing only exceptions — what's late, what's at risk, what changed since yesterday. Trust the data because every update has an audit trail. React to delays in days, not weeks.

---

### Secondary Users

#### 3. Management — Supply Chain Director & Customer Service Directors

**Profile:** Senior leaders who need aggregate visibility into PO performance without diving into operational detail. Located in Europe.

**Needs:**
- **OTIF dashboards**: On-Time In-Full delivery performance by supplier, category, period
- **Delay rate tracking**: Percentage and volume of late POs, trend over time
- **Supplier reliability scorecards**: Which suppliers consistently deliver on time vs. chronically late
- **Quality issue tracking**: Quality problems per item/supplier as a KPI dimension
- **No operational input**: Read-only consumers of dashboards and reports

**Success vision:** Weekly or real-time KPI dashboards that answer: "Are we getting better or worse? Which suppliers need attention? What's the customer impact?"

---

#### 4. System Administrator — J.maliczak

**Profile:** Builder, owner, and administrator of the system. Full access to all application functions including user management, system configuration, data ingestion settings, supplier/item mappings, and troubleshooting.

**Needs:**
- Full CRUD access to all entities
- User and role management
- Ingestion job monitoring and configuration
- Item cross-reference (xref) mapping management
- System health and audit log visibility

---

### Explicitly Out of Scope (MVP)

- **Customer Service**: Receives delay information from Planners verbally or via ERP — no direct app access in MVP
- **Suppliers / Sub-suppliers**: No app access in MVP. Future possibility via WeChat miniapp for direct status input

---

### User Journey

#### Expeditor Journey (Wei)

| Phase | Today (Excel) | Tomorrow (PO Tracker) |
|-------|--------------|----------------------|
| **Monday AM** | Download open orders from ERP as Excel | Open app — see prioritized list of POs needing supplier updates |
| **Monday–Tuesday** | Manually split Excel by supplier, send via WeChat | Select supplier group, generate structured request (WeChat/Excel template), send in bulk |
| **Tuesday–Wednesday** | Collect responses via WeChat/email, interpret free-text | Record supplier responses in structured form — date, qty, reason — with one-click entry |
| **Wednesday–Thursday** | Consolidate into master Excel, check for errors | Data is already live in the system — planners see updates in real-time as entered |
| **Thursday–Friday** | Send file to Europe, answer follow-up questions | Focus on actual expediting — follow up on at-risk POs, escalate problems |
| **Time saved** | 2.5+ days/week on data handling | Target: reduce to < 1 day, freeing 1.5+ days for real expediting work |

#### Planner Journey (Katrin)

| Phase | Today (Excel) | Tomorrow (PO Tracker) |
|-------|--------------|----------------------|
| **Data arrival** | Wait until mid-week for Excel file | See updates as expeditors enter them (near real-time) |
| **Exception finding** | Scroll through thousands of rows | Dashboard shows only late, at-risk, and changed POs |
| **Investigation** | Ask expeditor via email/chat (next-day response) | Click PO line → see full timeline, audit trail, delay reasons |
| **Action** | Update ERP or call Customer Service | Same actions, but days earlier with better information |
| **Confidence** | "Is this data current? Who updated it?" | Every entry timestamped with author and source |

---

## Success Metrics

### User Success Metrics

#### Expeditor Success (Wei)

| Metric | Current State | Target | How Measured |
|--------|--------------|--------|-------------|
| Weekly data compilation cycle | 2.5+ days/week | ≤ 1 day/week | Time from first supplier request to all PO lines updated in system |
| Data entry method | Unstructured Excel, no validation | Structured app input with mandatory fields | % of updates entered via app vs. offline/Excel |
| Accountability trail | None — impossible to trace who/when | 100% of updates logged with user, timestamp, and source | Audit log completeness rate |
| Supplier request workflow | Manual split + WeChat per supplier | Bulk generation of structured requests from app | # of suppliers covered per session |

**Key user success moment:** When Wei opens the app on Monday morning, sees a prioritized list of POs needing updates, and finishes the full supplier request cycle before lunch — instead of Thursday.

#### Planner Success (Katrin)

| Metric | Current State | Target | How Measured |
|--------|--------------|--------|-------------|
| Data freshness | Weekly (mid-week Excel arrival) | Same-day (≤ 1 day lag acceptable) | Average age of latest update per PO line |
| Time to detect delay | Days (hidden in thousands of Excel rows) | Same-day (exception dashboard) | Time between expeditor entering a delay and planner viewing it |
| Investigation effort | Manual: email expeditor, wait for next-day reply | Self-service: click PO → see timeline + reasons | # of cross-timezone follow-up queries per week |
| Data confidence | Low — "Is this current? Who updated this?" | High — every entry timestamped with author | User trust survey or support ticket reduction |

**Key user success moment:** When Katrin opens the dashboard and immediately sees 5 PO lines flagged as delayed with reasons attached — no digging, no waiting, no guessing.

---

### Business Objectives

#### 3-Month Milestones (Launch Success)

- **Excel elimination**: All 3 expeditors using the app as primary workflow — zero weekly Excel compilation cycles
- **Data consistency**: Single source of truth operational — planners no longer receive or need Excel files
- **Adoption**: 100% of active PO lines tracked in the system (for covered suppliers)
- **Reaction speed**: Planners acting on delay information within 1 day of expeditor entry (vs. 3-5+ days today)

#### 12-Month Milestones (Operational Maturity)

- **Baseline KPIs established**: First-ever OTIF, delay rate, and supplier reliability measurements available with full historical trend data
- **Supplier performance visibility**: All 30 suppliers scored and ranked on delivery reliability
- **Proactive expediting**: Shift from reactive ("we discovered it's late") to proactive ("the system flagged it at risk before it's late")
- **Management dashboards live**: Supply Chain Director and CS Directors using KPI dashboards for decision-making

---

### Key Performance Indicators

#### Operational KPIs (built from scratch — no current baselines)

| KPI | Definition | Measurement Method | First Baseline |
|-----|-----------|-------------------|---------------|
| **OTIF Rate** | % of PO lines delivered on-time and in-full vs. original promised date | Calculated from date_event history + delivery records | Established after 3 months of data collection |
| **Delay Rate** | % of active PO lines currently past promised delivery date | Real-time calculation from canonical PO data | Available from day 1 of system operation |
| **Mean Delay Duration** | Average days late for delayed PO lines | Calculated from promised date vs. actual/expected date | Established after 1 month |
| **Supplier Reliability Score** | Composite score per supplier based on OTIF, delay frequency, and response timeliness | Weighted formula across delivery history | Established after 3 months |
| **Quality Issue Rate** | # of quality-flagged items per supplier per period | Manual flags by expeditors/planners in app | Tracked from day 1 |

#### System Health KPIs

| KPI | Target |
|-----|--------|
| **Data coverage** | 100% of open PO lines from covered suppliers in the system |
| **Update freshness** | ≥ 90% of active PO lines updated within last 5 business days |
| **Expeditor daily usage** | All 3 expeditors logging in and entering updates daily |
| **Audit completeness** | 100% of status changes have user + timestamp + source |

#### Strategic Value Indicators

- **First-ever OTIF measurement**: The ability to report OTIF at all is a strategic milestone — moving from "we don't know" to "we know and can improve"
- **Expeditor time reclaimed**: 1.5+ days/week per expeditor redirected from data handling to actual supplier management and problem-solving
- **Cross-timezone data continuity**: Planners in Europe see updates from China without waiting for file handoffs or overlapping work hours

---

## MVP Scope

### Core Features

#### 1. ERP Data Ingestion
- Nightly scheduled job: pull active PO lines from supplier ERP (read-only MS SQL)
- Store snapshots in `erp_snapshot`, compute hashes, detect changes
- Write change events to `erp_change_event` when fields differ from last snapshot
- Reconstruct historical batch deliveries from DeliveredQty + InDate records
- All ingestion activity logged for admin monitoring

#### 2. PO List View (Expeditor + Planner Dashboard)
- Filterable list of all active PO lines with key columns: PO number, supplier, item, ordered qty, remaining qty, promised date, current expected date, delay days, status
- Filter by: supplier, item, status, delay (late/at-risk/on-track)
- Sort by any column
- Visual indicators for exceptions (late, at-risk)
- Role-appropriate views: expeditors see their supplier scope, planners see all

#### 3. PO Detail View
- Full timeline of date changes (audit-grade): every milestone update with who, when, source, and reason
- Batch delivery table: historical batches (reconstructed from ERP) + planned future batches
- Current status with status transition history
- Edit capability for milestone dates (production-ready, ready-to-dispatch) with mandatory reason field

#### 4. Milestone Date Recording
- Structured input: expeditors record/update readiness dates with mandatory fields (date, reason, source)
- Every update creates an append-only `date_event` record
- Full audit trail: user, timestamp, previous value, new value, reason
- No overwrites — all changes are versioned

#### 5. Batch Tracking (Historical + Planned)
- **Historical**: Auto-reconstructed from ERP delivery records (DeliveredQty + InDate) during ingestion
- **Planned**: Users create future batches with allocated qty and expected dispatch date
- Batch-to-PO-line allocation without requiring ERP line splitting
- Batch status tracking: Planned → Confirmed → Dispatched → Delivered

#### 6. Excel Download Tool (Supplier Request Generation)
- Expeditor selects supplier(s) → generates structured Excel file with open PO lines for that supplier
- Pre-formatted template ready to send to supplier via WeChat or email
- Columns: PO, Item, Ordered Qty, Remaining Qty, Promised Date, Current Status, Supplier Response Fields (Ready Date, Qty Ready, Comments)
- Replaces the manual "download from ERP → split by supplier" workflow

#### 7. Status Model
- **Planned**: Baseline only (PO created, no production signal)
- **In Production**: Has production-ready estimate
- **Ready to Dispatch**: Batch planned/confirmed for dispatch
- **Part Delivered**: Some batches delivered, remaining qty > 0
- **Fully Delivered**: Remaining qty = 0
- **Cancelled/Closed**: If signal exists from ERP or manual flag

#### 8. Authentication & Authorization
- Simple local authentication (username + password stored in app DB)
- Role-based access: Expeditor, Planner, Admin
- Admin: full CRUD on all entities, user management, ingestion config, item xref mapping

#### 9. Admin Functions
- User and role management
- Item cross-reference (xref) table management (supplier item codes ↔ internal codes)
- Ingestion job monitoring (last run, status, errors)
- Audit log viewer
- System configuration

---

### Out of Scope for MVP

| Feature | Rationale | Target Phase |
|---------|-----------|-------------|
| Supplier portal / batch proposal engine | Expeditors are primary users in MVP; suppliers interact via Excel/WeChat | Phase 2 |
| WeChat integration | Expeditors continue using WeChat manually; app provides structured Excel for requests | Phase 2 |
| Chinese Simplified UI (i18n) | English-only MVP reduces complexity; expeditors have basic English for a structured UI | Phase 2 |
| Management dashboards & KPI reports | Data needs to accumulate first; management value comes after 1-3 months of operation | Phase 2 |
| CDC / real-time ingestion (Debezium/Kafka) | Daily snapshot+diff is sufficient; real-time adds infra complexity | Phase 3+ |
| ML predictive features | Requires historical data baseline; rules-based approach first | Phase 3+ |
| Customer ERP integration | Supplier ERP is primary data source; customer ERP is cross-check only | Phase 2-3 |
| Customer Service app access | CS receives info from planners; no direct app access needed yet | Phase 2 |
| ERP write-back | Read-only integration is a core principle for MVP | Phase 3+ |

---

### MVP Success Criteria

| Criteria | Measurement | Go/No-Go Threshold |
|----------|-------------|-------------------|
| **Expeditor adoption** | All 3 expeditors using the app as primary daily workflow | 100% within 4 weeks of launch |
| **Excel elimination** | No more weekly Excel compilation cycles sent to Europe | Zero Excel handoffs within 6 weeks |
| **Data freshness** | Planners see expeditor updates within same day | ≥ 90% of updates visible within 24 hours |
| **Audit trail coverage** | Every status/date change has user + timestamp + reason | 100% from day 1 |
| **ERP ingestion reliability** | Nightly sync runs successfully and detects changes | ≥ 95% success rate over first month |
| **Data coverage** | All open PO lines for covered suppliers are in the system | 100% within 2 weeks of launch |

**Decision point for Phase 2:** If MVP success criteria are met within 2 months, proceed with supplier portal + Chinese Simplified UI + management dashboards.

---

### Future Vision

#### Phase 2 (Months 4-6): Expand Reach
- **Supplier portal**: Batch proposal engine with confirm/adjust/reject workflow
- **Chinese Simplified UI**: Full i18n for expeditor and (future) supplier interfaces
- **Management dashboards**: OTIF, delay rates, supplier reliability scorecards, quality issue tracking
- **Customer ERP integration**: Cross-check baseline, ETD/ETA signals
- **WeChat integration**: Structured request/response via WeChat for sub-supplier communication

#### Phase 3+ (Months 7-12): Intelligence Layer
- **Rules-based batch proposal engine**: Auto-suggest next batch dates based on historical patterns
- **ML refinement**: Quantile regression for batch date prediction, risk scoring
- **CDC real-time ingestion**: Debezium/SQL Server CDC for near-real-time event streaming
- **Advanced alerting**: Configurable alert rules for delay thresholds, supplier non-response
- **Entra ID authentication**: Replace local auth with Azure AD/Entra ID for SSO

#### Long-term (12-24 months): Platform Potential
- If successful within 6 months, opportunity for broader expansion into adjacent procurement workflows
- Potential for multi-site / multi-ERP deployment
- WeChat miniapp for direct supplier input
- Container-level tracking and reconciliation
- ERP write-back capabilities
