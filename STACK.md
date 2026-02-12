# STACK.md
## PO Timeline & Batch Tracker
### Windows-Native Architecture (No Docker)

---

# 1. Overview

This document defines the technical stack and system behavior for the first release of the **PO Timeline & Batch Tracker**, designed as:

- System-of-truth for PO milestones and batch tracking
- Reporting and OTIF visibility platform
- Used by both internal planners and suppliers (portal)
- No write-back to ERP (read-only integration)

Environment constraint:
- Windows infrastructure
- No Docker allowed
- MS SQL + Python preferred

---

# 2. High-Level Architecture

Supplier ERP (MS SQL - Read Only)
│
▼
Ingestion Layer (Python Scheduled Jobs)
│
▼
Canonical App DB (MS SQL Server)
│
▼
FastAPI Backend (Hosted behind IIS)
│
▼
Web UI (Planner + Supplier Portal)


---

# 3. Infrastructure Stack (Windows Native)

## 3.1 Operating System
- Windows Server >= 2019
- Windows >= 10 

---

## 3.2 Database Layer

### Microsoft SQL Server
Two connections:

1. Supplier ERP Database (read-only)
2. Application Database (system-of-truth)

### App DB Core Tables
- `po_line`
- `date_event` (append-only audit log)
- `dispatch_batch`
- `batch_line`
- `batch_proposal`
- `erp_snapshot`
- `erp_change_event`
- `item_xref`
- `users`, `roles`

---

## 3.3 Backend (Python)

### Framework
- FastAPI
- SQLAlchemy 2.0
- Alembic (migrations)
- Pydantic (validation schemas)

### Hosting
- IIS as reverse proxy
- Uvicorn running as Windows Service
- Service managed via NSSM

---

## 3.4 Background Processing (No Docker)

- SQL Server Agent scheduled jobs
- Python scripts for:
  - nightly ingestion
  - snapshot diff
  - proposal generation
  - alert generation

---

## 3.5 Authentication

### Internal Planners
- Azure AD / Entra ID (OIDC)

### Supplier Portal
Option 1 (Preferred):
- Entra External ID (B2B/B2C)

Option 2 (Simpler v1):
- Local authentication stored in App DB

---

## 3.6 Frontend

- Django + HTMX (server-rendered)
- Hosted behind IIS

---

# 4. Data Flow

## 4.1 ERP Data Ingestion

Nightly process:

1. Pull active PO lines from Supplier ERP
2. Store snapshot in `erp_snapshot`
3. Compare hash against previous snapshot
4. Write differences to `erp_change_event`
5. Derive historical batches from:
   - DeliveredQty
   - InDate

Result:
- Canonical DB updated
- Full audit trail preserved

---

# 5. Automatic & Low-Effort Supplier Batch Updates

The system minimizes manual work using:

## 5.1 Batch Proposal Engine

After ingestion, system runs proposal logic:

- Analyze remaining qty
- Analyze readiness dates
- Use historical supplier patterns
- Group by supplier & due window

Creates:
- Proposed batch dates
- Proposed quantities
- Confidence score (future ML-ready)

Stored in:
- `batch_proposal`

---

## 5.2 Supplier Portal Workflow

Supplier does NOT manually edit every PO.

Instead, they see:

### “Batch Proposals Inbox”
Grouped by:
- Due this week
- Due next 2–3 weeks

Supplier can:
- Confirm all (1 click)
- Adjust date for entire group
- Edit only exceptions
- Reject proposal and propose alternative

Each action:
- Writes append-only audit event
- Creates/updates `dispatch_batch`
- Updates current expected readiness

---

## 5.3 Bulk Edit Tools

Supplier can:
- Select multiple PO lines
- Apply strategy:
  - Ship all remaining
  - Split 30% / 70%
  - Weekly equal split
  - MOQ-based rounding
- Apply one date to multiple lines

Reduces workload dramatically.

---

## 5.4 Optional Structured CSV Upload

Supplier may upload small structured template:

Columns:
- PO
- Item
- Qty
- ReadyDate

System validates and converts into planned batches.

Note:
This is portal input only — not ERP integration.

---

# 6. User Flow Diagram

Supplier ERP (Read Only MS SQL)
│
▼
Ingestion Job (Python via SQL Agent / RQ)

Snapshot active POs

Detect changes

Derive historical batches
│
▼
App DB (MS SQL - Canonical Truth)

po_line

date_event (audit log)

dispatch_batch

batch_proposal
│
▼
Proposal Engine (Python)

Suggest next batches

Group by supplier
│
▼
FastAPI Backend (IIS)
│
▼
Web UI (Planner + Supplier Portal)
│
┌────────┴────────┐
▼                 ▼
Planner User Supplier User
Monitor & Confirm / adjust
Override proposals


---

# 7. Planner Experience

Planner:
- Sees dashboard of delayed POs
- Reviews timeline & audit trail
- Overrides milestone dates if needed
- Monitors supplier confirmations
- Works on exceptions only

---

# 8. Supplier Experience

Supplier:
- Logs into portal
- Sees grouped batch proposals
- Confirms majority with 1 click
- Edits only problematic lines
- Uses bulk tools when needed

All updates:
- Stored append-only
- Visible immediately to planners
- Never overwrite ERP data

---

# 9. Core Principles

1. ERP is read-only baseline.
2. Application DB is operational truth.
3. All changes are append-only (audit-grade).
4. Supplier workload must be minimized.
5. Automation assists, humans confirm.

---

# 10. Future Extensions (Not in v1)

- CDC real-time ingestion
- ML quantile forecasting for batch dates
- ERP write-back
- Container-level reconciliation
- Advanced alert engine

---

# End of Document
