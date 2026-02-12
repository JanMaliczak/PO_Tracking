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

PO Timeline and Batch Tracker is a self-hosted cross-firewall web application that replaces the Excel-based PO tracking workflow between expeditors in China and planners in Europe. It becomes the operational source of truth for PO milestones, batch-level deliveries, and change history across two incompatible ERPs.

### Problem

Two legacy ERPs model PO lifecycle differently and neither provides trustworthy milestone history. The supplier ERP overwrites line state, destroying historical context. Weekly Excel exchange consumes major expeditor capacity and delays planner reaction. Teams cannot reliably answer who changed what, when, and why.

### Solution

The product provides:

- Nightly ERP ingestion with snapshot and diff change detection
- Structured milestone recording with mandatory source classification
- Exception-first planner views for late and at-risk lines
- Supplier-request Excel generation to replace manual split workflows
- Append-only audit trail for every operational change

### Key Differentiator

Designed for China-Europe operations across network boundaries, with audit-grade accountability and no vendor dependency.

### Target Users

| Role | Location | Primary Need |
|------|----------|--------------|
| Expeditor (Wei) | China | Structured supplier update capture and request generation |
| Planner (Katrin) | Europe | Fast exception detection and self-service PO investigation |
| Admin (J.maliczak) | Europe | Ingestion monitoring, access control, xref and config management |
| Management | Europe | Phase 2 KPI visibility and rollout readiness confidence |

## Success Criteria

### User Success

- Expeditor weekly data cycle reduced from 2.5+ days to <= 1 day
- Planner delay detection reduced to <= 1 day from status change
- 100% of milestone updates captured with date, reason, and source
- 100% of active PO lines visible with audit traceability

### Business Success

- All three expeditors use the system daily within 4 weeks
- Zero weekly operational Excel handoff from China to Europe within 6 weeks
- 100% coverage of active PO lines for onboarded suppliers
- Data quality sufficient for Phase 2 KPI dashboards by month 12

### Technical Success

- Nightly ingestion completes in <= 1 hour and >= 95% success over rolling 30 days
- Key list/detail interactions meet performance targets in NFR1-NFR4
- Availability supports 00:00-18:00 UTC operational window

### Measurable Outcomes

| Outcome | Baseline | Target (3 months) | Measurement |
|---------|----------|-------------------|-------------|
| Expeditor weekly data cycle | 2.5+ days | <= 1 day | Time from first request to full supplier update completion |
| Planner delay detection | 3-5+ days | <= 1 day | Time between delay entry and planner visibility |
| Weekly Excel handoffs | Dozens | 0 | Operational process observation |
| Audit-covered PO updates | 0% | 100% | Audit completeness query |
| Ingestion success | N/A | >= 95% | Job monitoring logs |

## Product Scope & Phased Development

### MVP Strategy

Deliver a complete Excel-replacement workflow as a coherent MVP unit. Prioritize operational simplicity and low maintenance with proven components.

### MVP Feature Set (Phase 1) - All 9 Required

| # | Feature | Day-One Justification |
|---|---------|----------------------|
| 1 | ERP Data Ingestion | No reliable operations without baseline data and change detection |
| 2 | PO List View | Primary interface for planner and expeditor daily work |
| 3 | PO Detail View | Required for timeline/audit/batch-level investigation |
| 4 | Milestone Date Recording | Core accountability mechanism |
| 5 | Batch Tracking | Required for partial-delivery reality |
| 6 | Excel Download Tool | Immediate expeditor time savings |
| 7 | Status Model | Shared operational language across users |
| 8 | Authentication and Authorization | Role security and data scoping |
| 9 | Admin Functions | Operability and long-term maintainability |

### Core User Journeys Supported (MVP)

1. Wei weekly supplier cycle
2. Wei accountability challenge
3. Katrin daily exception review
4. Admin operational control day
5. Day-one bootstrap and first sync
6. Management visibility readiness checkpoint

### Phase 2 - Expand Reach (Months 4-6)

- Chinese Simplified UI
- Supplier collaboration enhancements
- Management KPI dashboards
- Additional ERP cross-check integration

### Phase 3 - Intelligence Layer (Months 7-12)

- Rules plus ML forecasting for batch timing
- Near-real-time ingestion options
- Advanced alerting and predictive risk scoring

## User Journeys

### Journey 1: Wei's Monday Morning - Weekly Supplier Cycle

Wei opens the app, filters by supplier urgency, generates supplier request files in minutes, and records responses with required source and reasons. The cycle shifts from spreadsheet coordination to operational expediting.

**Requirements Revealed:**
- Fast supplier filtering and sorting
- Per-supplier Excel generation
- Structured update capture with required fields
- Completion visibility for weekly workflow

### Journey 2: Wei's Accountability Challenge - Source Integrity

When suppliers do not respond, Wei must record updates as estimate or no response. This preserves visibility and avoids hidden optimism bias.

**Requirements Revealed:**
- Mandatory source classification
- Clear visual distinction of source quality
- Staleness and no-response indicators
- Append-only auditability for coaching and governance

### Journey 3: Katrin's Daily Check - Exception Dashboard

Katrin starts the day with a focused late/at-risk list, drills into PO details, and acts without waiting for asynchronous clarification loops.

**Requirements Revealed:**
- Exception-first default views
- Rich PO detail timeline and batch context
- Fast filtering by delay/state/source freshness

### Journey 4: J.maliczak's Admin Day - System Operations

Admin verifies ingestion health, resolves xref gaps, manages access scopes, and reviews audit patterns.

**Requirements Revealed:**
- Ingestion health dashboard
- Xref mapping management
- User and role administration
- Audit log filtering and analysis

### Journey 5: Day One Setup - First-Time System Activation

Admin configures ingestion and performs first baseline snapshot. Users log in with immediate historical context and begin operational use.

**Requirements Revealed:**
- Baseline sync mode
- Historical batch reconstruction
- Xref gap visibility and safe handling
- Configurable ingestion schedule and lookback

### Journey 6: Management Visibility Readiness - Monthly Operational Review (Phase 2 Prep)

Management reviews evidence on coverage, freshness, and reliability before approving KPI dashboard rollout.

**Requirements Revealed:**
- Monthly readiness evidence package
- Reliable trend visibility from operational logs
- Clear rollout decision support signals

### Journey Requirements Summary

| Capability Area | Journeys That Require It |
|-----------------|--------------------------|
| PO list view with smart filtering and sorting | 1, 3, 5 |
| Excel download tool (per-supplier) | 1, 5 |
| Structured data entry with mandatory fields | 1, 2 |
| Source field (confirmed/estimate/no-response) | 2, 3, 4 |
| Audit trail (who/when/what/why) | 1, 2, 3, 4 |
| PO detail timeline and batch context | 3, 5 |
| Admin operations and governance | 4, 5 |
| Change detection visibility | 3 |
| Management visibility readiness (Phase 2 KPI review) | 6 |

## Domain-Specific Requirements

### Cross-Border Infrastructure

- Primary write environment located close to expeditor operations
- Secondary read environment for European planners
- Nightly replication to satisfy <= 1 day freshness tolerance
- Private encrypted cross-region data channel

### Audit and Data Retention

- Append-only event history for operational changes
- Retention and archival policy for closed PO histories
- No silent overwrite of milestone history

### Operational Security

- Read-only ERP integration credentials
- Role-scoped access control
- Admin-auditable security events

## Web App Specific Requirements

### Project-Type Overview

PO_Tracking is a browser-based internal operational web application with server-rendered and progressively enhanced interactions.

### Browser Support Matrix

| Browser | Version | User Group | Priority |
|---------|---------|------------|----------|
| Microsoft Edge | Latest 2 major versions | Expeditors + Planners | Primary |
| Google Chrome | Latest 2 major versions | Planners | Primary |
| Mozilla Firefox | Latest 2 major versions | Planners | Secondary |
| 360 Secure Browser | Latest stable | Expeditors (occasional) | Best effort |

### Responsive Design

- Primary: Desktop 1280px+
- Secondary: Tablet 768-1279px
- Mobile: Not targeted in MVP

### SEO Strategy

- MVP SEO scope is not applicable for core authenticated PO workflows
- If public pages are introduced, include basic metadata and canonical tags
- Protected routes remain no-index/no-follow
- Success criterion: only explicitly public pages are indexable

### Implementation Considerations

- Progressive enhancement for interactive workflows
- Manual refresh model acceptable for MVP operational cadence
- Favor stable web standards for browser compatibility

## Functional Requirements

### Data Ingestion and Synchronization

- **FR1:** System can connect to supplier ERP database (read-only SQL) and extract active PO line data on a configurable schedule
- **FR2:** System can store snapshots of ERP data and detect changes between consecutive snapshots using field-level comparison
- **FR3:** System can generate change events when ERP fields differ from previous snapshot, recording what changed, when, and the previous/new values
- **FR4:** System can reconstruct historical batch deliveries from ERP DeliveredQty and InDate records during ingestion
- **FR5:** System can perform a first-run baseline snapshot without change detection (initial data load)
- **FR6:** System can report ingestion results including duration, PO lines processed, change events detected, new lines created, and errors encountered
- **FR7:** System can identify and report PO lines with item codes not found in the cross-reference table after ingestion
- **FR8:** System can replicate data from the primary write environment to the secondary read environment on a nightly schedule

### PO Visibility and Navigation

- **FR9:** Expeditors can view a list of all active PO lines scoped to their assigned suppliers
- **FR10:** Planners can view a list of all active PO lines across all suppliers
- **FR11:** Users can filter the PO list by supplier, item, status, and delay classification (late, at-risk, on-track)
- **FR12:** Users can sort the PO list by any displayed column, with due date as the default sort
- **FR13:** System can display visual exception indicators on PO lines that are overdue or approaching their due date
- **FR14:** Users can view PO lines updated within a specified time window (for example last 24 hours) for cross-timezone awareness
- **FR15:** Users can view PO lines with no expeditor update within a configurable staleness threshold
- **FR16:** Users can apply filter presets for common exception views (Late, At Risk, Updated Recently, No Response)
- **FR17:** Users can manually refresh the current view data via a dedicated in-app refresh action

### PO Investigation and Detail

- **FR18:** Users can view a PO line detail page showing the full chronological timeline of all date changes with who, when, source, and reason
- **FR19:** Users can view the batch delivery table for a PO line showing historical batches and planned future batches
- **FR20:** Users can view the current status and complete status transition history for a PO line
- **FR21:** Users can view the remaining quantity and delivery progress (delivered versus outstanding) for a PO line

### Milestone and Status Management

- **FR22:** Expeditors can record or update milestone dates (production-ready, ready-to-dispatch) for PO lines within their supplier scope
- **FR23:** Expeditors can submit milestone updates only when date, reason, and source are provided; submissions missing any required field are rejected with validation feedback
- **FR24:** Expeditors can classify each update source as "Supplier confirmed," "Expeditor estimate," or "No supplier response"
- **FR25:** System can visually distinguish between confirmed, estimated, and no-response statuses in all views
- **FR26:** System can store every milestone update as an append-only audit event with user, timestamp, previous value, new value, reason, and source
- **FR27:** Users can add free-text notes or comments when recording a milestone update
- **FR28:** System can manage PO line status transitions through the defined lifecycle: Planned -> In Production -> Ready to Dispatch -> Part Delivered -> Fully Delivered -> Cancelled/Closed

### Batch Tracking

- **FR29:** System can create historical batch records from ERP delivery data (DeliveredQty and InDate) during ingestion
- **FR30:** Expeditors can create planned future batches with allocated quantity and expected dispatch date for PO lines within their scope
- **FR31:** System can track batch status through: Planned -> Confirmed -> Dispatched -> Delivered
- **FR32:** System can allocate batch quantities to PO lines without requiring ERP line splitting
- **FR33:** Users can view batch-level delivery progress showing delivered batches versus remaining planned batches

### Supplier Communication

- **FR34:** Expeditors can generate a structured Excel file for a selected supplier containing all open PO lines for that supplier
- **FR35:** System can pre-fill the Excel template with PO numbers, items, ordered quantity, remaining quantity, promised date, and current status
- **FR36:** System can include supplier response fields in the generated Excel: Ready Date, Qty Ready, and Comments

### User and Access Management

- **FR37:** Users can authenticate using local credentials (username and password)
- **FR38:** System can enforce role-based access control with three roles: Expeditor, Planner, Admin
- **FR39:** System can scope expeditor access to only their assigned suppliers' PO data
- **FR40:** System can enforce authorization at the API boundary, preventing unauthorized access regardless of UI state

### System Administration

- **FR41:** Admins can create, edit, and deactivate user accounts with role assignment
- **FR42:** Admins can assign and modify supplier scope for expeditor users
- **FR43:** Admins can manage the item cross-reference table including individual and bulk operations
- **FR44:** Admins can view ingestion job history with status, duration, record counts, and error details
- **FR45:** Admins can view and filter the audit log by user, source type, date range, and event type
- **FR46:** Admins can configure ERP connection parameters and ingestion schedule settings
- **FR47:** Admins can configure system parameters including staleness thresholds and ingestion lookback window
- **FR48:** System can flag unmapped items visibly in the UI rather than silently dropping them during ingestion

## Non-Functional Requirements

### Performance

- **NFR1:** PO list view and dashboard pages render within 3 seconds on initial load
- **NFR2:** Partial list updates (filter, sort, refresh) complete within 2 seconds for datasets up to 5,000 active PO lines
- **NFR3:** PO detail view (timeline plus batch table plus audit history) loads within 2 seconds
- **NFR4:** Excel generation completes within 5 seconds for a single supplier with up to 200 PO lines
- **NFR5:** System supports up to 10 concurrent users without observable performance degradation
- **NFR6:** Additional cross-firewall latency up to 500ms round-trip is acceptable for remote read users
- **NFR7:** Nightly ERP ingestion completes within 1 hour including snapshot, diff, change event generation, and historical batch reconstruction

### Security

- **NFR8:** User passwords are stored using secure hashing (bcrypt or argon2), never plaintext or reversible encryption
- **NFR9:** Role-based access control is enforced at the API boundary for supplier-scope restrictions
- **NFR10:** Audit event storage is append-only with no application-level update or delete path
- **NFR11:** ERP integration uses read-only SQL credentials with minimum necessary permissions
- **NFR12:** Network communication between the primary operations environment and remote access environments is secured in transit through a private encrypted channel
- **NFR13:** User sessions expire after 30 minutes of inactivity and require re-authentication before additional protected actions are allowed

### Reliability and Availability

- **NFR14:** System is available during business hours across both timezones (approximately 00:00-18:00 UTC)
- **NFR15:** A 1-hour off-hours maintenance window is supported; brief downtime up to 10 minutes is acceptable
- **NFR16:** Nightly ERP ingestion achieves >= 95% success over any rolling 30-day period
- **NFR17:** Audit event storage must achieve zero data loss from committed events
- **NFR18:** Daily backups provide RPO <= 24 hours and restore capability within 4 hours
- **NFR19:** Ingestion includes retry logic for transient ERP connection errors before final failure state

### Integration

- **NFR20:** ERP integration remains read-only with no write-back behavior
- **NFR21:** Data replication from the primary write environment to the secondary read environment completes within the nightly sync window (10:00-07:00 UTC)
- **NFR22:** On replication failure, secondary read environment serves last successful sync and generates an admin alert
- **NFR23:** Unmapped item codes are flagged for admin review without failing the full ingestion run

### Accessibility

- **NFR24:** User-facing pages comply with WCAG 2.1 Level A success criteria
- **NFR25:** Status indicators use color plus icon or text; color is never the only signal
- **NFR26:** Form inputs are labeled and interactive elements are keyboard accessible

### Deployability and Operations

- **NFR27:** Application updates are deployable by a single administrator within the maintenance window
- **NFR28:** Application runtime components operate as managed background services behind an enterprise reverse proxy without requiring container runtime dependencies
- **NFR29:** Ingestion failures, replication failures, and xref mapping gaps are recorded in the admin-visible event log within 60 seconds of detection, including timestamp, severity, and event type
