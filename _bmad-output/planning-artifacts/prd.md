---
stepsCompleted: [step-01-init, step-02-discovery, step-03-success, step-04-journeys, step-05-domain, step-06-innovation-skipped, step-01b-continue, step-07-project-type, step-08-scoping, step-09-functional, step-10-nonfunctional, step-11-polish]
inputDocuments:
  - product-brief-PO_Tracking-2026-02-11.md
  - RESEARCH.md
  - PRODUCT_BRIEF.md
  - STACK.md
documentCounts:
  briefs: 2
  research: 1
  brainstorming: 0
  projectDocs: 1
workflowType: 'prd'
date: 2026-02-11
classification:
  projectType: web_app
  domain: supply_chain_procurement
  complexity: medium-high
  projectContext: greenfield
---

# Product Requirements Document - PO_Tracking

**Author:** J.maliczak
**Date:** 2026-02-11

## Executive Summary

### Vision

PO Timeline & Batch Tracker is a self-hosted, cross-firewall web application that replaces the current Excel-based workflow for purchase order tracking between expeditors in China and planners in Europe. It becomes the single operational truth for PO milestones, batch-level deliveries, and change history across two incompatible ERPs.

### Problem

Two aging ERPs represent the PO lifecycle in incompatible ways. The supplier ERP overwrites PO line state on each update, destroying audit history. Neither system captures why dates change, who provided updates, or when information was received. Expeditors spend 2.5+ days per week manually compiling Excel files. Planners discover delays days after they occur. There is no accountability trail.

### Solution

A server-rendered MPA (Django + HTMX, FastAPI, MS SQL) hosted on Alibaba Cloud (China) with a European read-replica, providing:

- **Nightly ERP ingestion** with snapshot+diff change detection and historical batch reconstruction
- **Structured milestone recording** with mandatory source classification (Supplier confirmed / Expeditor estimate / No supplier response)
- **Exception-first dashboard** for planners to identify delays without scanning thousands of rows
- **Excel download tool** replacing the manual ERP export + split workflow
- **Append-only audit trail** for every change â€” who, when, what, why

### Key Differentiator

Cross-firewall by design, audit-grade accountability, zero vendor dependency. Purpose-built for China-Europe operations where commercial SaaS solutions fail at the network boundary.

### Target Users

| Role | Location | Primary Need |
|------|----------|-------------|
| Expeditor (Wei) | China (3 users) | Record supplier updates with structured input; generate Excel requests |
| Planner (Katrin) | Europe (3 users) | Exception dashboard; self-service PO investigation with audit trail |
| Admin (J.maliczak) | Europe (1 user) | System operations: ingestion monitoring, user/xref management |
| Management | Europe (read-only) | Phase 2: OTIF dashboards, supplier scorecards |


## Product Scope & Phased Development

### MVP Strategy

**Approach:** Problem-solving MVP â€” deliver the complete workflow replacement for Excel-based PO tracking. The 9 core features form an indivisible unit; partial delivery breaks the value chain and prevents adoption validation.

**Resource model:** Solo developer/admin (J.maliczak). Prioritize proven, low-maintenance technology choices (Django + HTMX, MS SQL, FastAPI) over cutting-edge options. Infrastructure simplicity is a first-class requirement.

**Language decision:** English-only MVP confirmed viable. Expeditors have sufficient English proficiency for a structured UI. Chinese Simplified UI is Phase 2 â€” high priority but not a launch blocker.

### MVP Feature Set (Phase 1) â€” All 9 Required

| # | Feature | Day-One Justification |
|---|---------|----------------------|
| 1 | ERP Data Ingestion | No data = no system. Nightly snapshot+diff with change event generation and historical batch reconstruction |
| 2 | PO List View | Primary interface for both expeditors and planners. Filterable, sortable, with exception indicators and role-scoped views |
| 3 | PO Detail View | Timeline of date changes, batch delivery table, status history, milestone editing |
| 4 | Milestone Date Recording | Structured input with mandatory source field â€” solves the accountability problem |
| 5 | Batch Tracking | Historical reconstruction for day-one insights; planned batches enable forward-looking workflow |
| 6 | Excel Download Tool | Replaces manual ERP export + split workflow â€” direct expeditor time savings |
| 7 | Status Model | Planned â†’ In Production â†’ Ready to Dispatch â†’ Part Delivered â†’ Fully Delivered â†’ Cancelled/Closed |
| 8 | Authentication & Authorization | Local auth, role-based access (Expeditor, Planner, Admin) with supplier scoping |
| 9 | Admin Functions | User/role management, item xref mapping, ingestion monitoring, audit log viewer, system config |

**MVP rationale**: These 9 features form an indivisible unit â€” removing any one breaks the core value chain. Without ingestion there's no data; without the list view there's no visibility; without milestone recording there's no audit trail; without Excel download expeditors can't communicate with suppliers; without batch tracking there's no delivery granularity; without auth there's no accountability.

**Historical batch reconstruction rationale:** Reconstructing batch history from ERP DeliveredQty + InDate records at go-live is essential. Without it, the system launches with zero context about delivery patterns, making the PO detail timeline empty and the exception dashboard blind to existing delays.

### Core User Journeys Supported (MVP)

All 5 documented journeys are fully supported:
1. Wei's Monday Morning â€” weekly supplier update cycle
2. Wei's Accountability Challenge â€” source field and audit trail
3. Katrin's Daily Check â€” exception dashboard
4. J.maliczak's Admin Day â€” system operations
5. Day One Setup â€” first-time ingestion and onboarding

### Phase 2 â€” Expand Reach (Months 4-6)

- Chinese Simplified UI (i18n) â€” high priority to reduce expeditor friction
- Supplier portal with batch proposal engine (confirm/adjust/reject workflow)
- Management dashboards â€” OTIF, delay rates, supplier reliability scorecards
- Customer ERP integration â€” cross-check baseline, ETD/ETA signals
- WeChat integration â€” structured request/response for sub-supplier communication

### Phase 3 â€” Intelligence Layer (Months 7-12)

- Rules-based batch proposal engine (auto-suggest next batch dates)
- ML quantile forecasting â€” batch date prediction, risk scoring
- CDC real-time ingestion (Debezium/SQL Server CDC)
- Advanced alerting â€” configurable delay thresholds, supplier non-response rules
- Entra ID authentication â€” replace local auth with Azure AD SSO

### Phase 4 â€” Platform Potential (12-24 months)

- Multi-site / multi-ERP deployment
- WeChat miniapp for direct supplier input
- ERP write-back capabilities
- Container-level tracking and reconciliation

### Risk Mitigation Strategy

**Technical Risks:**

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Dual-DB sync failure** (highest risk) | Critical | Launch China-only (single Alibaba DB) first. Add European replica as fast-follow once core app is validated. Manual fallback: nightly DB backup transfer via VPN. |
| ERP ingestion logic errors | High | Build and test ingestion against real ERP data in isolation. Comprehensive logging and dry-run mode. Validate reconstruction against known delivery records. |
| Historical batch reconstruction accuracy | Medium | Spot-check reconstructed batches against known PO lines. Flag anomalies (overdelivery, negative remaining) as first-class alerts. |
| Solo developer bottleneck | Medium | Leverage mature stack (Django, FastAPI, MS SQL). Avoid custom infrastructure. Prioritize operational simplicity. |

**Market/Adoption Risks:**

| Risk | Severity | Mitigation |
|------|----------|------------|
| Expeditor resistance to new tool | High | Involve Wei in early testing. Excel download tool must work flawlessly from day one. |
| Data quality during transition | Medium | Run parallel (Excel + app) for 2-4 weeks. Compare outputs to build confidence. |
| Planner skepticism about data freshness | Low | "Last updated" timestamps and source indicators build trust organically. |

**Resource Risks:**

| Risk | Severity | Mitigation |
|------|----------|------------|
| Solo developer capacity | High | Build incrementally (ingestion â†’ list view â†’ detail view â†’ data entry â†’ Excel download â†’ admin). Internal testing before all 9 are complete. |
| Infrastructure maintenance burden | Medium | Windows-native stack avoids Docker complexity. MS SQL and IIS are well-understood in-house. |
| Scope creep during development | Medium | PRD defines clear MVP boundaries. Any new request evaluated against "does this break the value chain?" test. |

**Dual-DB De-Risking Strategy (recommended):**
1. **Development + initial launch:** Single Alibaba Cloud DB. European users accept cross-firewall latency (~500ms+).
2. **Post-launch validation:** Add European read-replica with nightly sync once core app is stable.
3. **Fallback:** Manual nightly DB backup transfer via VPN satisfies the â‰¤ 1 day freshness requirement.


### Journey 2: Wei's Accountability Challenge â€” The "Protection" Problem (Critical Edge Case)

**Scene**: Wednesday 2:00 PM in Shenzhen. Supplier B hasn't responded about 15 PO lines due next week.

**The Old Way** (before): Wei would either leave the cells blank in her Excel (hoping Katrin doesn't notice), or fill in optimistic dates that the supplier hasn't confirmed â€” "protecting" her supplier relationship by hiding the problem. Katrin receives the Excel on Thursday and has no way to know which dates are real confirmations vs. Wei's guesses. The deception only surfaces weeks later when goods don't arrive.

**The New Way**:

1. **Wednesday 2:00 PM â€” Non-Response Visible**: Wei's dashboard shows 15 PO lines for Supplier B still marked as "awaiting update." The system knows these haven't been updated since last week's ERP sync. The status is visible to everyone â€” there's no way to hide it.

2. **Wei's Dilemma**: Wei wants to enter optimistic dates to avoid pressure from Katrin. But the system requires a **source field** for every update:
   - "Supplier confirmed" (means supplier actually responded)
   - "Expeditor estimate" (Wei's best guess â€” flagged differently in the system)
   - "No supplier response" (honest status)

3. **The Accountability Mechanism**: If Wei marks dates as "Supplier confirmed" but the supplier later misses, the audit trail shows Wei entered a confirmation that wasn't real. Over time, this pattern becomes visible in the data. The system doesn't prevent Wei from entering data â€” but it makes every entry *traceable and auditable*.

4. **The Better Outcome**: Wei marks the 15 lines as "No supplier response" and adds a note: "WeChat sent Monday, no reply. Will follow up Thursday." Katrin sees this in Europe and knows exactly what's happening â€” no surprises. She can factor the risk into her planning.

5. **Escalation Path**: If Supplier B remains non-responsive for 2+ cycles, the pattern is clear in the data. Management can see which suppliers are chronically unresponsive â€” something that was invisible in the Excel world.

**Climax**: The first time Katrin says "I can see Supplier B hasn't responded â€” let's escalate together" instead of discovering a missed delivery 2 weeks late, trust between China and Europe improves. Wei realizes that honest reporting protects *her* more than hiding problems.

**Requirements Revealed**:
- **Source field** on every update: "Supplier confirmed" / "Expeditor estimate" / "No supplier response"
- Visual distinction in UI between confirmed vs. estimated vs. no-response statuses
- "Last updated" timestamp visible on every PO line (staleness detection)
- Non-response tracking: PO lines not updated within X days are flagged
- Audit trail that makes patterns of inaccurate reporting discoverable over time
- Notes/comments field for context on each update


### Journey 4: J.maliczak's Admin Day â€” System Operations

**Scene**: Wednesday 7:00 AM in Europe. J.maliczak checks the system before the team starts working.

1. **7:00 AM â€” Ingestion Check**: Opens the admin panel. Last night's ERP sync shows: "Completed at 02:47 AM, duration: 38 minutes. 4,230 PO lines processed. 87 change events detected. 3 new PO lines created. 0 errors." Green status. Good.

2. **7:05 AM â€” Exception Alert**: One warning: "12 PO lines have item codes not found in xref table." J.maliczak opens the xref management screen â€” a new supplier was added to the ERP last week with item codes that haven't been mapped yet. He adds 12 mappings (supplier code â†’ internal code) and marks them for re-processing in tonight's sync.

3. **7:15 AM â€” New User Request**: An email from the China office â€” a new expeditor is starting next week. J.maliczak opens user management, creates the account (username, password, role: Expeditor, assigned suppliers: Supplier C, D, E), and sends the credentials.

4. **7:20 AM â€” Audit Spot Check**: Curious about the "protection" pattern, J.maliczak opens the audit log filtered to "source = Expeditor estimate" for the past month. He notices one expeditor has 40% of entries as estimates vs. confirmed â€” worth a coaching conversation.

**Requirements Revealed**:
- Admin dashboard: ingestion job status, duration, counts, errors
- Warning system for unmapped item codes (xref gaps)
- Xref management CRUD with bulk import capability
- User management: create/edit/deactivate, role assignment, supplier scope assignment
- Audit log filtering: by user, by source type, by date range
- Pattern detection capability in audit data


### Journey 6: Management Visibility Readiness — Monthly Operational Review (Phase 2 Prep)

**Scene**: End of month in Europe. Management asks whether the operation is ready for dashboard rollout in Phase 2.

1. **Data confidence check**: Admin reviews ingestion reliability, coverage, and audit completeness trends from the operational logs.
2. **Exception trend review**: Planner reviews late and at-risk movement across the month using existing filtering views and timeline evidence.
3. **Readiness pack creation**: Admin compiles a monthly KPI-readiness summary (coverage %, delay trend direction, data freshness, audit completeness) for management review.
4. **Decision point**: Management confirms whether data quality is sufficient to enable Phase 2 dashboard delivery.

**Climax**: Management can decide on Phase 2 dashboard rollout using evidence from system-tracked operations rather than anecdotal updates.

**Requirements Revealed**:
- Consistent ingestion and audit logging quality signals across the month
- Access to operational evidence for delay/freshness/coverage review
- Repeatable monthly readiness summary for management decision-making

---
### Journey Requirements Summary

| Capability Area | Journeys That Require It |
|----------------|-------------------------|
| PO list view with smart filtering & sorting | 1, 3, 5 |
| Excel download tool (per-supplier) | 1, 5 |
| Structured data entry with mandatory fields | 1, 2 |
| **Source field (confirmed/estimate/no-response)** | **2, 3, 4** (critical for accountability) |
| Audit trail (who/when/what/why) | 1, 2, 3, 4 |
| PO detail view with timeline | 3 |
| Batch tracking (historical + planned) | 3, 5 |
| Non-response / staleness detection | 2, 3 |
| Notes/comments on updates | 2 |
| Admin: ingestion monitoring | 4, 5 |
| Admin: xref management | 4, 5 |
| Admin: user management with supplier scoping | 4 |
| Admin: audit log filtering & pattern analysis | 4 |
| ERP connection & ingestion configuration | 5 |
| First-run / baseline mode | 5 |
| Status model with visual indicators | 1, 3 |
| Change detection ("updated in last 24h") | 3 |
| Management visibility readiness (Phase 2 KPI review) | 6 |

**Critical Discovery from Journey 2**: The **source field** requirement ("Supplier confirmed" / "Expeditor estimate" / "No supplier response") is essential for solving the accountability problem â€” the core trust gap between China and Europe. It is included in the Milestone Date Recording feature (#4) as a mandatory field.


## Web App Specific Requirements

### Project-Type Overview

PO_Tracking is a server-rendered Multi-Page Application (MPA) built with Django + HTMX, served behind IIS with a FastAPI backend. The architecture prioritizes simplicity, reliability, and cross-firewall compatibility over client-side richness. HTMX provides targeted dynamic interactivity (filtering, inline updates) without the complexity of a full SPA framework. No real-time push features are required for MVP â€” users refresh data on demand via a dedicated in-app refresh button.

### Browser Support Matrix

| Browser | Version | User Group | Priority |
|---------|---------|------------|----------|
| Microsoft Edge | Latest 2 major versions | Expeditors (China) + Planners (Europe) | Primary |
| Google Chrome | Latest 2 major versions | Planners (Europe) | Primary |
| Mozilla Firefox | Latest 2 major versions | Planners (Europe) | Secondary |
| 360 Secure Browser | Latest stable | Expeditors (China, occasional) | Best-effort |

**Chromium baseline**: Edge, Chrome, and 360 Browser share the Chromium engine, reducing cross-browser risk. Firefox is the only non-Chromium target. Testing priority: Edge and Chrome cover the critical path; Firefox and 360 receive regression testing but are not release-blocking.

### Responsive Design

- **Primary target**: Desktop browsers (1280px+ viewport) â€” primary work tool on office workstations
- **Secondary target**: Tablet-width viewports (768px-1279px) for occasional use
- **Mobile**: Not targeted for MVP
- **Layout approach**: Fluid layout with breakpoints at 768px and 1280px; data-heavy tables use horizontal scroll on narrower viewports

### SEO Strategy

- **MVP SEO scope:** Not applicable for primary authenticated workflows because core PO tracking screens require login and are not intended for public indexing
- **Public surface:** If a public landing/help page is added, implement basic metadata (title, description, canonical URL) and allow indexing only for those public routes
- **Indexing policy:** Protected operational routes must remain no-index/no-follow
- **Success criterion:** Search crawlers can index only explicitly public pages; authenticated application pages are excluded from indexing
### Implementation Considerations

- **No SPA framework needed**: Django templates + HTMX covers all interactivity requirements (list filtering, inline editing, form submission)
- **Progressive enhancement**: Core functionality works without JavaScript; HTMX enhances with partial page updates
- **Data refresh pattern**: Dedicated "Refresh" button triggers HTMX request to reload current view data â€” no WebSocket infrastructure for MVP
- **Browser testing**: Chromium-based majority simplifies QA; spot-checks on Firefox
- **360 Browser compatibility**: Avoid bleeding-edge CSS/JS features; stick to well-established web standards

Performance targets and accessibility requirements are specified in [Non-Functional Requirements](#non-functional-requirements) (NFR1â€“NFR7 for performance, NFR24â€“NFR26 for accessibility).


## Non-Functional Requirements

### Performance

- **NFR1:** PO list view and dashboard pages render within 3 seconds on initial load, including server-side rendering and HTMX initialization
- **NFR2:** HTMX partial updates (filter, sort, refresh) complete within 2 seconds for datasets up to 5,000 active PO lines
- **NFR3:** PO detail view (timeline + batch table + audit history) loads within 2 seconds
- **NFR4:** Excel file generation completes within 5 seconds for a single supplier with up to 200 PO lines
- **NFR5:** System supports up to 10 concurrent users without performance degradation
- **NFR6:** Cross-firewall latency of up to 500ms additional round-trip time is acceptable for European users accessing the China-hosted application
- **NFR7:** Nightly ERP ingestion job completes within 1 hour including snapshot, diff, change event generation, and historical batch reconstruction

### Security

- **NFR8:** User passwords are stored using secure hashing (bcrypt or argon2) â€” never in plaintext or reversible encryption
- **NFR9:** Role-based access control is enforced at the API level â€” expeditors cannot access data outside their assigned supplier scope regardless of client-side manipulation
- **NFR10:** The audit event log is append-only â€” no delete or update operations are permitted on audit records at the application or API level
- **NFR11:** ERP database connection uses read-only SQL credentials with minimal required permissions
- **NFR12:** Network communication between the primary operations environment and remote access environments is secured in transit through a private encrypted channel
- **NFR13:** User sessions expire after 30 minutes of inactivity and require re-authentication before additional protected actions are allowed

### Reliability & Availability

- **NFR14:** System is available during all business hours across both timezones (approximately 00:00â€“18:00 UTC)
- **NFR15:** A 1-hour maintenance window is reserved during off-hours for updates and deployments; brief downtime (5â€“10 minutes) during this window is acceptable
- **NFR16:** Nightly ERP ingestion achieves a success rate of 95% or higher over any rolling 30-day period
- **NFR17:** Zero data loss on the audit event log â€” append-only storage must never lose or overwrite events
- **NFR18:** Daily database backups with a Recovery Point Objective (RPO) of 24 hours and ability to restore within 4 hours
- **NFR19:** Ingestion job includes retry logic on transient ERP connection failures before reporting a failed run

### Integration

- **NFR20:** ERP integration uses read-only direct SQL connection to MS SQL Server â€” no write-back under any circumstances
- **NFR21:** Data replication from the primary write environment to the secondary read environment completes within the nightly sync window (10:00–07:00 UTC)
- **NFR22:** If database replication fails, the European replica retains last-synced data and an alert is generated for the admin
- **NFR23:** Ingestion gracefully handles unmapped item codes â€” flagging them for admin review rather than failing the entire job or silently dropping records

### Accessibility

- **NFR24:** All user-facing pages comply with WCAG 2.1 Level A success criteria
- **NFR25:** Status indicators use color combined with icon or text â€” color is never the sole means of conveying information
- **NFR26:** All form inputs have associated labels; all interactive elements are keyboard-accessible

### Deployability & Operations

- **NFR27:** Application updates can be deployed within the 1-hour maintenance window by a single administrator
- **NFR28:** Application runtime components operate as managed background services behind an enterprise reverse proxy without requiring container runtime dependencies
- **NFR29:** Ingestion failures, replication failures, and xref mapping gaps are recorded in the admin-visible event log within 60 seconds of detection, including timestamp, severity, and event type

