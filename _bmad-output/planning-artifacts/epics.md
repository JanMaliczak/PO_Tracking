---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - prd.md
  - architecture.md
  - ux-design-specification.md
---

# PO_Tracking - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for PO_Tracking, decomposing the requirements from the PRD, UX Design, and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: System can connect to supplier ERP database (read-only SQL) and extract active PO line data on a configurable schedule
FR2: System can store snapshots of ERP data and detect changes between consecutive snapshots using field-level comparison
FR3: System can generate change events when ERP fields differ from previous snapshot, recording what changed, when, and the previous/new values
FR4: System can reconstruct historical batch deliveries from ERP DeliveredQty and InDate records during ingestion
FR5: System can perform a first-run baseline snapshot without change detection (initial data load)
FR6: System can report ingestion results including duration, PO lines processed, change events detected, new lines created, and errors encountered
FR7: System can identify and report PO lines with SKU codes not found in the cross-reference table after ingestion
FR8: System can replicate data from the primary write environment to the secondary read environment on a nightly schedule
FR8a: System can ingest Item (product family/category grouping above SKU), PO insert date (original PO creation date), and final customer fields from the supplier ERP during data extraction
FR8b: System can ingest up to 15 configurable custom columns from the supplier ERP: 5 date-type, 5 text-type, and 5 decimal-type fields, mapped to ERP SQL columns via admin configuration
FR8c: System can populate custom columns from either ERP read-only ingestion or direct user input in the application, with the data source (ERP or user-entered) tracked per field per PO line
FR9: Expeditors can view a list of all active PO lines scoped to their assigned suppliers
FR10: Planners can view a list of all active PO lines across all suppliers
FR11: Users can filter the PO list by any displayed column including supplier, item, SKU, PO number, final customer, status, delay classification, source quality, ready quantity, date ranges, and any active custom columns
FR12: Users can sort the PO list by any displayed column, with due date as the default sort
FR13: System can display visual exception indicators on PO lines that are overdue or within a configurable number of days of their due date
FR14: Users can view PO lines updated within a specified time window (for example last 24 hours) for cross-timezone awareness
FR15: Users can view PO lines with no expeditor update within a configurable staleness threshold
FR16: Users can apply filter presets for common exception views (Late, At Risk, Updated Recently, No Response)
FR17: Users can manually refresh the current view data via a dedicated in-app refresh action
FR17a: Users can show or hide individual columns in the PO list view via a column chooser control
FR17b: System can persist each user's column visibility preferences across sessions
FR17c: System can apply role-based default column visibility (expeditor defaults differ from planner defaults) that users can override
FR17d: System can display Item (product family/category), PO insert date, and final customer as standard columns available in the PO list view
FR17e: System can display up to 15 admin-configured custom columns (5 date-type, 5 text-type, 5 decimal-type) in the PO list view, with admin-defined display labels
FR18: Users can view a PO line detail page showing the full chronological timeline of all date changes with who, when, source, and reason
FR19: Users can view the batch delivery table for a PO line showing historical batches and planned future batches
FR20: Users can view the current status and complete status transition history for a PO line
FR21: Users can view the remaining quantity and delivery progress (ordered versus ready versus dispatched versus delivered) for a PO line
FR22: Expeditors can record or update milestone dates (production-ready, ready-to-dispatch) for PO lines within their supplier scope
FR22a: Expeditors can record ready quantity (goods produced but not yet dispatched) with a readiness date for PO lines within their supplier scope
FR22b: System can track partial production readiness, allowing multiple ready-quantity entries as suppliers complete production in increments
FR22c: System can display cumulative ready quantity alongside ordered quantity and remaining quantity, distinguishing between goods produced, goods dispatched, and goods outstanding
FR23: Expeditors can submit milestone updates only when date, reason, and source are provided; submissions missing any required field are rejected with validation feedback
FR24: Expeditors can classify each update source as "Supplier confirmed," "Expeditor estimate," or "No supplier response"
FR25: System can visually distinguish between confirmed, estimated, and no-response statuses in all views
FR26: System can store every milestone update as an append-only audit event with user, timestamp, previous value, new value, reason, and source
FR27: Users can add free-text notes or comments when recording a milestone update
FR27a: Expeditors can select multiple PO lines and apply the same milestone update (date, reason, source, ready quantity) to all selected lines in a single action
FR27b: Expeditors can edit milestone fields inline across multiple PO line rows with row-specific values before submitting all changes as a batch
FR28: System can manage PO line status transitions through the defined lifecycle: Planned -> In Production -> Ready to Dispatch -> Part Delivered -> Fully Delivered -> Cancelled/Closed
FR29: System can create historical batch records from ERP delivery data (DeliveredQty and InDate) during ingestion
FR30: Expeditors can create planned future batches with allocated quantity and expected dispatch date for PO lines within their scope
FR31: System can track batch status through: Planned -> Confirmed -> Dispatched -> Delivered
FR32: System can allocate batch quantities to PO lines without requiring ERP line splitting
FR33: Users can view batch-level delivery progress showing delivered batches versus remaining planned batches
FR34: Expeditors can generate a structured Excel file for a selected supplier containing all open PO lines for that supplier
FR35: System can pre-fill the Excel template with PO numbers, item, SKU, ordered quantity, remaining quantity, promised date, current status, and final customer
FR36: System can include supplier response fields in the generated Excel: Ready Date, Qty Ready, and Comments
FR37: Users can authenticate using local credentials (username and password)
FR38: System can enforce role-based access control with three roles: Expeditor, Planner, Admin
FR39: System can scope expeditor access to only their assigned suppliers' PO data
FR40: System can enforce authorization at the API boundary, preventing unauthorized access regardless of UI state
FR41: Admins can create, edit, and deactivate user accounts with role assignment
FR42: Admins can assign and modify supplier scope for expeditor users
FR43: Admins can manage the SKU cross-reference table including individual and bulk operations
FR44: Admins can view ingestion job history with status, duration, record counts, and error details
FR45: Admins can view and filter the audit log by user, source type, date range, and event type
FR46: Admins can configure ERP connection parameters and ingestion schedule settings
FR47: Admins can configure system parameters including staleness thresholds and ingestion lookback window
FR48: System can flag unmapped items with a distinct visual indicator in the PO list view and admin dashboard rather than silently dropping them during ingestion
FR49: Admins can configure custom columns by defining: display label, data type (date, text, or decimal), data source (ERP SQL column mapping or user-entered), and default visibility per role
FR50: Admins can activate or deactivate individual custom columns without losing existing data in those columns
FR51: Users can enter or update values in user-entered custom columns directly from the PO list view (inline) or PO detail panel

### NonFunctional Requirements

NFR1: PO list view and dashboard pages render within 3 seconds on initial load
NFR2: Partial list updates (filter, sort, refresh) complete within 2 seconds for datasets up to 5,000 active PO lines
NFR3: PO detail view (timeline plus batch table plus audit history) loads within 2 seconds
NFR4: Excel generation completes within 5 seconds for a single supplier with up to 200 PO lines
NFR5: System supports up to 10 concurrent users while maintaining NFR1-NFR4 response time targets
NFR6: Additional cross-firewall latency up to 500ms round-trip is acceptable for remote read users
NFR7: Nightly ERP ingestion completes within 1 hour including snapshot, diff, change event generation, and historical batch reconstruction
NFR8: User passwords are stored using industry-standard cryptographic hashing, never plaintext or reversible encryption
NFR9: Role-based access control is enforced at the API boundary for supplier-scope restrictions
NFR10: Audit event storage is append-only with no application-level update or delete path
NFR11: ERP integration uses read-only SQL credentials with minimum necessary permissions
NFR12: Network communication between the primary operations environment and remote access environments is secured in transit through a private encrypted channel
NFR13: User sessions expire after 30 minutes of inactivity and require re-authentication before additional protected actions are allowed
NFR14: System is available during business hours across both timezones (approximately 00:00-18:00 UTC)
NFR15: A 1-hour off-hours maintenance window is supported; brief downtime up to 10 minutes is acceptable
NFR16: Nightly ERP ingestion achieves >= 95% success over any rolling 30-day period
NFR17: Audit event storage must achieve zero data loss from committed events
NFR18: Daily backups provide RPO <= 24 hours and restore capability within 4 hours
NFR19: Ingestion includes retry logic for transient ERP connection errors before final failure state
NFR20: ERP integration remains read-only with no write-back behavior
NFR21: Data replication from the primary write environment to the secondary read environment completes within the nightly sync window (10:00-07:00 UTC)
NFR22: On replication failure, secondary read environment serves last successful sync and generates an admin alert
NFR23: Unmapped SKU codes are flagged for admin review without failing the full ingestion run
NFR24: User-facing pages comply with WCAG 2.1 Level A success criteria
NFR25: Status indicators use color plus icon or text; color is never the only signal
NFR26: Form inputs are labeled and interactive elements are keyboard accessible
NFR27: Application updates are deployable by a single administrator within the maintenance window
NFR28: Application runtime components are deployable and operable by a single administrator without requiring container runtime infrastructure
NFR29: Ingestion failures, replication failures, and xref mapping gaps are recorded in the admin-visible event log within 60 seconds of detection, including timestamp, severity, and event type

### Additional Requirements

**From Architecture:**
- Starter template: `django-admin startproject` with Django 5.2.11 LTS, mssql-django 1.6, django-htmx 1.27.0 — Epic 1, Story 1 must initialize this project scaffold
- Split settings: base.py, development.py, production.py, production_eu.py — required before any other implementation
- Custom User model with role field and supplier FK must be defined before first migration (Django requirement)
- Dual-database configuration: DatabaseRouter for read-only ERP + read-write app DB
- Waitress WSGI server managed by NSSM as Windows service behind IIS reverse proxy
- HTMX fragment pattern: underscore-prefixed templates for all partial responses
- Append-only AuditEvent model with custom manager blocking delete/update
- RBAC via @role_required decorator + .for_user() queryset scoping on all models
- CSRF protection via django-htmx middleware + HX-Headers configuration
- create_audit_event() explicit function call for all write operations (no Django signals)
- Physical custom columns on POLine (custom_date_1-5, custom_text_1-5, custom_decimal_1-5)
- Database-backed sessions with SESSION_COOKIE_AGE=1800, SESSION_SAVE_EVERY_REQUEST=True
- openpyxl for Excel generation
- django-environ for environment configuration
- SQL Server log shipping for cross-region replication (infrastructure, not application)
- Django management command (run_ingestion) for nightly ERP ingestion via SQL Server Agent

**From UX Design:**
- Direction B "Data Command Center" visual design: dark blue navbar, bold badges, colored row borders
- 13 custom components defined: Source Quality Badge, Status Lifecycle Badge, Staleness Indicator, Quantity Progress Display, Bulk Action Bar, Inline Edit Mode, PO Detail Slide-over Panel, Audit Timeline, Supplier Progress Indicator, Filter Preset Navigation, Column Chooser Control
- Three update interaction patterns: single modal, bulk multi-select bar, inline edit
- Bootstrap 5.3.x via CDN with ~500 lines custom CSS
- Desktop-first responsive: 1280px+ primary, 768px+ secondary
- WCAG 2.1 Level A compliance with pragmatic Level AA practices
- Keyboard accessibility for all interactive elements
- Color + icon + text for all status indicators (never color alone)
- Toast notification pattern for success/error/warning/info feedback
- Slide-over detail panel with lazy-loaded HTMX sections

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1 | Epic 2 | ERP connection and data extraction |
| FR2 | Epic 2 | Snapshot storage and change detection |
| FR3 | Epic 2 | Change event generation |
| FR4 | Epic 2 | Historical batch reconstruction |
| FR5 | Epic 2 | First-run baseline snapshot |
| FR6 | Epic 2 | Ingestion results reporting |
| FR7 | Epic 2 | Xref gap identification |
| FR8 | Epic 8 | Cross-region replication |
| FR8a | Epic 2 | Item, PO insert date, final customer ingestion |
| FR8b | Epic 2 | Custom column ERP ingestion |
| FR8c | Epic 2 | Custom column source tracking |
| FR9 | Epic 3 | Expeditor scoped PO list |
| FR10 | Epic 3 | Planner full PO list |
| FR11 | Epic 3 | Column filtering |
| FR12 | Epic 3 | Column sorting |
| FR13 | Epic 3 | Exception indicators |
| FR14 | Epic 3 | Recently updated filter |
| FR15 | Epic 3 | Staleness filter |
| FR16 | Epic 3 | Filter presets |
| FR17 | Epic 3 | Manual refresh |
| FR17a | Epic 3 | Column chooser |
| FR17b | Epic 3 | Column preference persistence |
| FR17c | Epic 3 | Role-based default columns |
| FR17d | Epic 3 | Item, PO insert date, final customer columns |
| FR17e | Epic 3 | Custom column display |
| FR18 | Epic 4 | PO detail timeline |
| FR19 | Epic 4 | Batch delivery table |
| FR20 | Epic 4 | Status transition history |
| FR21 | Epic 4 | Quantity/delivery progress |
| FR22 | Epic 5 | Milestone date recording |
| FR22a | Epic 5 | Ready quantity recording |
| FR22b | Epic 5 | Partial production readiness tracking |
| FR22c | Epic 5 | Cumulative ready quantity display |
| FR23 | Epic 5 | Mandatory field validation |
| FR24 | Epic 5 | Source quality classification |
| FR25 | Epic 5 | Source quality visual distinction |
| FR26 | Epic 5 | Append-only audit events |
| FR27 | Epic 5 | Free-text notes |
| FR27a | Epic 5 | Bulk milestone update |
| FR27b | Epic 5 | Inline edit mode |
| FR28 | Epic 5 | Status lifecycle transitions |
| FR29 | Epic 6 | Historical batch creation from ERP |
| FR30 | Epic 6 | Planned batch creation |
| FR31 | Epic 6 | Batch status lifecycle |
| FR32 | Epic 6 | Batch quantity allocation |
| FR33 | Epic 6 | Batch progress view |
| FR34 | Epic 7 | Supplier Excel generation |
| FR35 | Epic 7 | Excel pre-fill |
| FR36 | Epic 7 | Excel response fields |
| FR37 | Epic 1 | Local authentication |
| FR38 | Epic 1 | Three-role RBAC |
| FR39 | Epic 1 | Supplier scope enforcement |
| FR40 | Epic 1 | API boundary authorization |
| FR41 | Epic 8 | User CRUD |
| FR42 | Epic 8 | Supplier scope assignment |
| FR43 | Epic 8 | Xref table management |
| FR44 | Epic 8 | Ingestion monitoring |
| FR45 | Epic 8 | Audit log viewer |
| FR46 | Epic 8 | ERP connection config |
| FR47 | Epic 8 | System parameter config |
| FR48 | Epic 8 | Unmapped item flagging |
| FR49 | Epic 8 | Custom column config |
| FR50 | Epic 8 | Custom column activate/deactivate |
| FR51 | Epic 3 | Custom column user entry |

**Coverage:** All 51 FRs mapped. Zero orphaned requirements.

## Epic List

### Epic 1: Project Foundation & User Access
Users can securely log in with role-based access, and the system enforces authorization boundaries. This epic bootstraps the entire application scaffold including the Django project, database connections, custom User model, and base templates.
**FRs covered:** FR37, FR38, FR39, FR40
**Standalone:** Yes — delivers complete authentication and RBAC. All subsequent epics build on this foundation.

### Epic 2: Data Ingestion Pipeline
The system automatically ingests PO data from the supplier ERP nightly, detects changes, reconstructs historical batches, and reports results. Admins can verify that data is flowing correctly.
**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR7, FR8a, FR8b, FR8c
**Standalone:** Yes — delivers complete ingestion with data in the app DB. Needs Epic 1 for auth/models.

### Epic 3: PO List View & Navigation
Planners and expeditors can view, filter, sort, and customize their PO line list with exception indicators, filter presets, column chooser, and custom column display. This is the primary daily work interface.
**FRs covered:** FR9, FR10, FR11, FR12, FR13, FR14, FR15, FR16, FR17, FR17a, FR17b, FR17c, FR17d, FR17e, FR51
**Standalone:** Yes — delivers complete list experience. Needs Epic 1 (auth) + Epic 2 (data).

### Epic 4: PO Detail & Investigation
Users can open a PO line's detail panel to investigate the full timeline, batch history, status transitions, and delivery progress.
**FRs covered:** FR18, FR19, FR20, FR21
**Standalone:** Yes — delivers complete investigation capability. Needs Epic 3 (list to navigate from).

### Epic 5: Milestone Recording & Status Management
Expeditors can record milestone updates (single, bulk, inline), track ready quantities, and manage PO status transitions — with full audit accountability.
**FRs covered:** FR22, FR22a, FR22b, FR22c, FR23, FR24, FR25, FR26, FR27, FR27a, FR27b, FR28
**Standalone:** Yes — delivers complete milestone workflow. Needs Epic 3 (list) + Epic 4 (detail context).

### Epic 6: Batch Tracking
Users can view historical batches from ERP data, create planned future batches, track batch lifecycle, and monitor batch-level delivery progress.
**FRs covered:** FR29, FR30, FR31, FR32, FR33
**Standalone:** Yes — delivers complete batch management. Needs Epic 4 (detail panel for batch views).

### Epic 7: Supplier Communication
Expeditors can generate structured Excel files for suppliers with pre-filled PO data and response fields, replacing manual spreadsheet workflows.
**FRs covered:** FR34, FR35, FR36
**Standalone:** Yes — delivers complete Excel generation. Needs Epic 3 (PO data/filtering).

### Epic 8: System Administration & Operations
Admins can manage users, supplier scopes, xref tables, ingestion monitoring, audit logs, system configuration, custom column configuration, and cross-region replication.
**FRs covered:** FR8, FR41, FR42, FR43, FR44, FR45, FR46, FR47, FR48, FR49, FR50
**Standalone:** Yes — delivers complete admin operational control. Needs Epic 1 (auth) + Epic 2 (ingestion data).

### Epic Dependency Flow

```
Epic 1 (Foundation) → Epic 2 (Ingestion) → Epic 3 (List View) → Epic 4 (Detail)
                                                  ↓                      ↓
                                            Epic 7 (Excel)         Epic 5 (Milestones)
                                                                        ↓
                    Epic 8 (Admin) ←──────────────────────────── Epic 6 (Batches)
```

## Epic 1: Project Foundation & User Access

Users can securely log in with role-based access, and the system enforces authorization boundaries. This epic bootstraps the entire application scaffold including the Django project, database connections, custom User model, and base templates.

### Story 1.1: Project Scaffold & Settings Configuration

As a developer,
I want the Django project initialized with split settings, environment configuration, and dual-database routing,
So that all subsequent development has a correctly structured foundation to build upon.

**Acceptance Criteria:**

**Given** no project exists yet
**When** the project scaffold is created
**Then** the Django project is initialized via `django-admin startproject po_tracking .` with Django 5.2.11 LTS
**And** a virtual environment exists with all core dependencies installed: Django 5.2.11, mssql-django 1.6, django-htmx 1.27.0, django-environ, waitress, openpyxl
**And** requirements files exist at `requirements/base.txt`, `requirements/development.txt`, and `requirements/production.txt`

**Given** the project is initialized
**When** settings are configured
**Then** split settings exist at `po_tracking/settings/base.py`, `development.py`, `production.py`, `production_eu.py`, and `__init__.py`
**And** `base.py` contains shared configuration: INSTALLED_APPS, MIDDLEWARE (including django-htmx), TEMPLATES, and common settings
**And** `django-environ` reads configuration from a `.env` file and a `.env.example` file documents all required variables
**And** `development.py` sets `DEBUG=True` and uses local database settings
**And** `production.py` configures the China primary environment (read-write app DB + read-only ERP)
**And** `production_eu.py` configures the Europe secondary environment (read-only app DB, no ERP connection)

**Given** split settings are configured
**When** dual-database routing is set up
**Then** `DATABASES` contains `default` (app DB, read-write) and `erp` (supplier ERP, read-only) entries
**And** a `DatabaseRouter` class in `apps/ingestion/router.py` routes ERP models to the `erp` connection and blocks write/migrate/relation operations on it
**And** the router is registered in `DATABASE_ROUTERS` setting

**Given** the project scaffold is complete
**When** the directory structure is reviewed
**Then** the `apps/` directory exists with `__init__.py` and subdirectories for: `core`, `accounts`, `po`, `ingestion`, `batches`, `audit`, `admin_portal`, `exports` — each with `__init__.py`
**And** `templates/` and `static/` directories exist at project root
**And** `.gitignore` excludes `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `db.sqlite3`, and `staticfiles/`

### Story 1.2: Custom User Model & Authentication

As a user,
I want to log in with my username and password and have my session managed securely,
So that I can access the application with my identity established.

**Acceptance Criteria:**

**Given** the project scaffold from Story 1.1 exists
**When** the User model is defined
**Then** a custom `User` model in `apps/accounts/models.py` extends `AbstractUser` with a `role` CharField (choices: `admin`, `planner`, `expeditor`) and a nullable `supplier` ForeignKey
**And** a `Supplier` model exists in `apps/po/models.py` with at minimum `id`, `name`, and `code` fields
**And** the custom User model is registered via `AUTH_USER_MODEL = 'accounts.User'` in base settings
**And** the first migration runs successfully creating all initial tables including the custom User model

**Given** the User model exists
**When** a user navigates to the login page
**Then** a login form is displayed at `/accounts/login/` with username and password fields
**And** the form uses Django's authentication backend with PBKDF2 password hashing (Django default)
**And** the login page extends `base_auth.html` (a minimal base template without the main navbar)
**And** form inputs are labeled and keyboard accessible per NFR26

**Given** a user submits valid credentials
**When** authentication succeeds
**Then** the user is redirected to the PO list view (or a placeholder home page)
**And** a database-backed session is created with `SESSION_COOKIE_AGE=1800` (30 minutes)
**And** `SESSION_SAVE_EVERY_REQUEST=True` resets the timeout on every request

**Given** a user submits invalid credentials
**When** authentication fails
**Then** the login form is re-displayed with an error message indicating invalid credentials
**And** the error message does not reveal whether the username or password was incorrect

**Given** a user is logged in
**When** they click logout
**Then** the session is invalidated and the user is redirected to the login page

**Given** a user's session has been inactive for 30+ minutes
**When** they make any request
**Then** the session is expired and the user is redirected to the login page for re-authentication per NFR13

### Story 1.3: Base UI Framework & HTMX Setup

As a user,
I want a consistent, accessible application interface with responsive feedback,
So that I can navigate and interact with the application efficiently.

**Acceptance Criteria:**

**Given** the project scaffold exists
**When** `base.html` is created
**Then** it includes Bootstrap 5.3.x via CDN link and htmx 2.0.x via CDN script tag
**And** the `<body>` tag includes `hx-headers='{"X-CSRFToken": "..."}'` using the Django CSRF token for all HTMX requests
**And** a dark blue navbar is rendered at the top following Direction B "Data Command Center" visual design
**And** the navbar displays the application name, the logged-in user's name and role, and a logout link
**And** the page is structured with `{% block content %}` for page-specific content

**Given** `base.html` exists
**When** `base_auth.html` is created
**Then** it provides a minimal layout for unauthenticated pages (login) without the main navbar
**And** it includes Bootstrap 5 CDN for consistent styling

**Given** base templates exist
**When** the toast notification system is implemented
**Then** a `_partials/_toast.html` template renders a toast container positioned at top-right
**And** a `static/js/toast.js` script listens for the `showToast` HTMX trigger event
**And** toasts support four levels: success (green), error (red), warning (yellow), info (blue)
**And** toasts auto-dismiss after a configurable duration

**Given** base templates exist
**When** HTMX configuration is set up
**Then** `static/js/htmx-config.js` configures HTMX global error handling
**And** `django-htmx` middleware is active and `request.htmx` is available in all views
**And** a `_partials/_loading_spinner.html` template provides a reusable HTMX loading indicator
**And** a `_partials/_confirm_modal.html` template provides a reusable confirmation dialog

**Given** the base UI framework is in place
**When** a `static/css/custom.css` file is created
**Then** it contains initial custom styles for Direction B visual design: dark blue navbar colors, badge styles, and Bootstrap overrides
**And** the desktop-first responsive approach targets 1280px+ primary and 768px+ secondary breakpoints

### Story 1.4: Role-Based Access Control

As an admin,
I want role-based access enforced across all application endpoints,
So that users can only access data and actions appropriate to their role and supplier scope.

**Acceptance Criteria:**

**Given** the custom User model with role field exists
**When** the `@role_required` decorator is implemented in `apps/core/decorators.py`
**Then** it accepts one or more role strings (e.g., `@role_required('admin', 'planner')`)
**And** it checks `request.user.role` against the allowed roles
**And** it returns HTTP 403 Forbidden if the user's role is not in the allowed list
**And** it works in combination with Django's `@login_required` (login check runs first)

**Given** the RBAC decorator exists
**When** the `.for_user()` queryset method is implemented
**Then** a custom manager on the `POLine` model (and other user-facing models) provides a `.for_user(user)` method
**And** for Expeditor users, the queryset is filtered to only PO lines belonging to the user's assigned supplier(s)
**And** for Planner and Admin users, the full unfiltered queryset is returned
**And** all views that access user-facing data use `.for_user(request.user)` to enforce scoping per FR39

**Given** RBAC is implemented at view and queryset level
**When** a request is made to any protected endpoint
**Then** authorization is enforced at the API boundary regardless of UI state per FR40
**And** an Expeditor cannot access PO data outside their supplier scope even by manipulating URLs or request parameters
**And** a Planner cannot perform Expeditor-only actions (e.g., milestone recording)
**And** only Admins can access admin portal endpoints

**Given** RBAC enforcement is in place
**When** an HTMX request is made by an unauthorized user
**Then** the response returns an appropriate error (403) with an `HX-Trigger` header to display an "Access denied" toast notification
**And** the response does not leak data from unauthorized scopes

## Epic 2: Data Ingestion Pipeline

The system automatically ingests PO data from the supplier ERP nightly, detects changes, reconstructs historical batches, and reports results. Admins can verify that data is flowing correctly.

### Story 2.1: Core Ingestion Models & ERP Connection

As a developer,
I want the core data models for PO lines, snapshots, change events, cross-references, and audit events defined,
So that the ingestion pipeline and all downstream features have a stable data foundation.

**Acceptance Criteria:**

**Given** the project scaffold and User/Supplier models from Epic 1 exist
**When** the POLine model is defined in `apps/po/models.py`
**Then** it includes fields for: PO number, line number, SKU, item (product family/category), supplier FK, ordered quantity, delivered quantity, remaining quantity, promised date, current status, PO insert date (original creation date), final customer, source quality, last update timestamp, and staleness tracking
**And** it includes 15 physical custom column fields: `custom_date_1` through `custom_date_5` (nullable DateField), `custom_text_1` through `custom_text_5` (nullable CharField), `custom_decimal_1` through `custom_decimal_5` (nullable DecimalField)
**And** it includes a `custom_column_sources` JSONField tracking whether each custom column value is ERP-sourced or user-entered per PO line
**And** a custom manager with `.for_user(user)` method is defined per the RBAC pattern from Story 1.4

**Given** the POLine model exists
**When** the ingestion models are defined in `apps/ingestion/models.py`
**Then** an `ERPSnapshot` model stores: snapshot timestamp, PO line reference data (PO number, line number, SKU, all tracked ERP fields), and a run identifier
**And** an `ERPChangeEvent` model stores: PO line FK (nullable for new lines), field name, previous value, new value, snapshot FK, and detection timestamp
**And** an `ItemXref` model stores: ERP item code, mapped SKU, mapped item (product family), supplier FK, active flag, and timestamps

**Given** the ingestion models exist
**When** the AuditEvent model is defined in `apps/audit/models.py`
**Then** it includes fields for: event_type (string), po_line FK (nullable), user FK (nullable), source (manual/bulk/inline/ingestion/system), timestamp (auto UTC), previous_values (JSON), new_values (JSON), and reason (optional text)
**And** a custom manager overrides `delete()` and `update()` to raise exceptions, enforcing append-only storage per NFR10
**And** a `create_audit_event()` function exists in `apps/core/services.py` as the single entry point for creating audit records

**Given** dual-database routing from Story 1.1 exists
**When** unmanaged ERP models are defined in `apps/ingestion/erp_models.py`
**Then** Django model classes with `managed = False` map to the supplier ERP's PO-related tables
**And** the DatabaseRouter routes these models to the `erp` database connection
**And** no write operations are possible on these models via the ORM

**Given** all models are defined
**When** migrations are generated and applied
**Then** all new tables are created successfully in the app database
**And** no migration attempts to create tables in the ERP database

### Story 2.2: ERP Snapshot Extraction

As an admin,
I want the system to connect to the supplier ERP and extract a complete snapshot of active PO line data,
So that the application has a current baseline of all PO information for change detection.

**Acceptance Criteria:**

**Given** the ERP database connection is configured and the unmanaged ERP models exist
**When** the snapshot extraction runs in `apps/ingestion/snapshot.py`
**Then** it connects to the supplier ERP using read-only SQL credentials per NFR11
**And** it extracts all active PO line records including: PO number, line number, SKU/item codes, ordered quantity, delivered quantity, promised date, status fields, Item (product family/category), PO insert date (original PO creation date), and final customer per FR1 and FR8a
**And** each extracted record is stored as an `ERPSnapshot` row linked to the current run identifier

**Given** a snapshot extraction is in progress
**When** the ERP connection encounters a transient error
**Then** the extraction retries with configurable retry count and backoff delay per NFR19
**And** if all retries fail, the extraction halts and logs a failure event

**Given** a snapshot extraction completes successfully
**When** the results are reviewed
**Then** the snapshot contains all active PO lines from the ERP with no write-back to the ERP per NFR20
**And** the snapshot timestamp and record count are recorded for reporting

**Given** this is the first-ever ingestion run (no previous snapshot exists)
**When** the snapshot extraction runs in baseline mode per FR5
**Then** all extracted records are treated as new PO lines without change detection
**And** POLine records are created in the app database from the baseline snapshot
**And** an audit event is logged recording the baseline initialization

### Story 2.3: Snapshot Diff & Change Event Generation

As an admin,
I want the system to detect field-level changes between consecutive ERP snapshots,
So that all PO data changes are tracked with full before/after context.

**Acceptance Criteria:**

**Given** a current snapshot and a previous snapshot exist for the same ERP data
**When** the diff engine in `apps/ingestion/diff_engine.py` runs
**Then** it compares every field of each PO line record between the two snapshots per FR2
**And** for each field that differs, it generates an `ERPChangeEvent` recording: the PO line reference, field name, previous value, new value, and the snapshot FK per FR3

**Given** the diff engine detects changes
**When** change events are generated
**Then** the corresponding `POLine` records in the app database are updated with the new values from the current snapshot
**And** an audit event is created for each PO line that had changes, with `event_type='ingestion_change'`, `source='ingestion'`, and the previous/new values serialized in JSON

**Given** the diff engine runs
**When** new PO lines appear in the current snapshot that were not in the previous snapshot
**Then** new `POLine` records are created in the app database
**And** an audit event is created for each new PO line with `event_type='po_line_created'` and `source='ingestion'`

**Given** the diff engine runs
**When** PO lines from the previous snapshot are absent from the current snapshot
**Then** the existing `POLine` records are not deleted but may be flagged or status-updated based on business rules
**And** the absence is recorded for ingestion reporting

**Given** the diff engine processes a large dataset
**When** up to 5,000 active PO lines are compared
**Then** the diff operation completes within a reasonable portion of the 1-hour ingestion window per NFR7

### Story 2.4: Xref Mapping & Gap Identification

As an admin,
I want PO lines mapped through the SKU cross-reference table with unmapped items flagged for review,
So that ERP item codes are correctly translated and data quality gaps are visible without failing the ingestion.

**Acceptance Criteria:**

**Given** the `ItemXref` table contains mappings from ERP item codes to application SKUs and Items
**When** the ingestion pipeline processes extracted PO line records
**Then** each record's ERP item code is looked up in the `ItemXref` table
**And** matched records have their `POLine.sku` and `POLine.item` fields populated from the cross-reference

**Given** a PO line's ERP item code is not found in the `ItemXref` table
**When** the xref lookup fails for that record per FR7
**Then** the PO line is still created/updated in the app database (ingestion does not fail) per NFR23
**And** the PO line is flagged as having an unmapped item code
**And** the unmapped item code is recorded in the ingestion results for admin review

**Given** the ingestion run completes
**When** xref gaps are summarized
**Then** a count of unmapped item codes is included in the ingestion results report
**And** an audit event with `event_type='xref_gap'` is logged for each unmapped item code within 60 seconds of detection per NFR29
**And** the list of unmapped codes is available for the admin monitoring dashboard (Epic 8)

### Story 2.5: Historical Batch Reconstruction & Custom Column Ingestion

As an admin,
I want historical batch deliveries reconstructed from ERP data and custom columns populated from ERP sources,
So that the application reflects the complete delivery history and extended data fields from day one.

**Acceptance Criteria:**

**Given** the ERP snapshot contains DeliveredQty and InDate records for PO lines
**When** the batch reconstruction logic in `apps/ingestion/batch_reconstruction.py` runs per FR4
**Then** historical `Batch` records are created in `apps/batches/models.py` from the ERP delivery data
**And** each batch record captures: PO line FK, delivered quantity, delivery date (InDate), and `source='ingestion'`
**And** batch records are linked to their parent PO lines with correct quantity allocation

**Given** historical batches are reconstructed
**When** the reconstruction processes a PO line with multiple delivery records
**Then** separate batch records are created for each distinct delivery event
**And** the cumulative delivered quantity across batches matches the ERP's total DeliveredQty for that PO line

**Given** the admin has configured custom columns with ERP SQL column mappings (via Epic 8, or seed data)
**When** the custom column ingestion in `apps/ingestion/custom_columns.py` runs per FR8b
**Then** up to 15 custom column values (5 date, 5 text, 5 decimal) are extracted from the mapped ERP SQL columns
**And** the corresponding `custom_date_N`, `custom_text_N`, or `custom_decimal_N` fields on the `POLine` record are populated

**Given** custom column values are ingested from the ERP
**When** the source tracking is updated per FR8c
**Then** the `custom_column_sources` field on the `POLine` records the data source as `'erp'` for each ERP-populated custom column
**And** existing user-entered custom column values (source `'user'`) are not overwritten by ERP ingestion

### Story 2.6: Ingestion Orchestration & Results Reporting

As an admin,
I want the full ingestion pipeline orchestrated as a single management command with comprehensive results reporting,
So that I can schedule nightly runs via SQL Server Agent and verify data health.

**Acceptance Criteria:**

**Given** all ingestion components (snapshot, diff, xref, batch reconstruction, custom columns) are implemented
**When** the Django management command `run_ingestion` in `apps/ingestion/management/commands/run_ingestion.py` is executed
**Then** it orchestrates the full pipeline in sequence: snapshot extraction → xref mapping → diff/change detection → batch reconstruction → custom column ingestion → results reporting
**And** the command accepts a `--baseline` flag for first-run mode (skip diff, treat all as new) per FR5
**And** the command is callable via `manage.py run_ingestion --settings=po_tracking.settings.production`

**Given** the ingestion pipeline completes (success or partial failure)
**When** results are reported per FR6
**Then** the report includes: run duration, PO lines processed, new lines created, change events detected, batches reconstructed, custom columns populated, xref gaps found, and errors encountered
**And** the results are logged to both file-based logging and an audit event with `event_type='ingestion_completed'` or `event_type='ingestion_failed'`
**And** the audit event is written within 60 seconds of pipeline completion per NFR29

**Given** the ingestion command runs
**When** transient ERP connection errors occur during execution
**Then** retry logic with configurable attempts and backoff is applied per NFR19
**And** if retries are exhausted, the pipeline logs a failure event and exits with a non-zero exit code for SQL Server Agent to detect

**Given** the ingestion pipeline is designed for scheduling
**When** a `scripts/run_ingestion.bat` wrapper script exists
**Then** it activates the virtual environment and invokes the management command with the production settings module
**And** it is suitable for execution by SQL Server Agent as a nightly scheduled job

**Given** the ingestion pipeline runs nightly
**When** performance is measured
**Then** the full pipeline (snapshot, diff, change events, batch reconstruction, custom columns) completes within 1 hour for up to 5,000 active PO lines per NFR7

## Epic 3: PO List View & Navigation

Planners and expeditors can view, filter, sort, and customize their PO line list with exception indicators, filter presets, column chooser, and custom column display. This is the primary daily work interface.

### Story 3.1: Basic PO List View with Role Scoping

As a planner or expeditor,
I want to see a list of active PO lines scoped to my role and sorted by due date,
So that I can immediately begin working with the most urgent items first.

**Acceptance Criteria:**

**Given** a logged-in expeditor with assigned suppliers
**When** they navigate to the PO list view at `/po/`
**Then** the list displays only PO lines belonging to their assigned supplier(s) per FR9
**And** the view uses `.for_user(request.user)` queryset scoping from Story 1.4

**Given** a logged-in planner
**When** they navigate to the PO list view at `/po/`
**Then** the list displays all active PO lines across all suppliers per FR10

**Given** the PO list is displayed
**When** the page renders
**Then** default columns are shown: PO number, line number, supplier, SKU, item, ordered quantity, remaining quantity, promised date, status, and source quality
**And** rows are sorted by promised date (due date) ascending as the default sort per FR12
**And** the page renders within 3 seconds on initial load per NFR1

**Given** the PO list view serves both full-page and HTMX requests
**When** a standard navigation request arrives
**Then** the full page `po/po_list.html` is rendered extending `base.html`
**When** an HTMX request arrives (detected via `request.htmx`)
**Then** only the `po/_table_body.html` fragment is returned for table body swap

**Given** the dataset contains many PO lines
**When** the list is rendered
**Then** server-side pagination is applied with a configurable page size
**And** pagination controls allow navigating between pages via HTMX partial refresh
**And** the `_partials/_pagination.html` fragment is used for pagination rendering

### Story 3.2: Column Filtering & Sorting

As a user,
I want to filter and sort the PO list by any displayed column,
So that I can quickly narrow down to the specific PO lines I need to work with.

**Acceptance Criteria:**

**Given** the PO list view is displayed
**When** the user applies a filter on any displayed column per FR11
**Then** filter controls are available for: supplier, item, SKU, PO number, final customer, status, delay classification, source quality, ready quantity, date ranges, and any active custom columns
**And** text-based columns support partial match (contains) filtering
**And** date columns support range filtering (from/to)
**And** status and source quality columns support multi-select filtering
**And** numeric columns (quantities) support range filtering

**Given** a filter is applied
**When** the filter value is submitted
**Then** the table body is refreshed via HTMX partial swap (`_table_body.html`) without full page reload
**And** the partial update completes within 2 seconds for up to 5,000 PO lines per NFR2
**And** active filters are visually indicated so the user knows which filters are applied
**And** pagination resets to page 1 when filters change

**Given** multiple filters are applied
**When** filters are combined
**Then** all active filters are applied together (AND logic)
**And** the user can clear individual filters or all filters at once

**Given** the PO list is displayed
**When** the user clicks a column header to sort per FR12
**Then** the table re-sorts by that column via HTMX partial refresh
**And** clicking the same column header toggles between ascending and descending order
**And** the current sort column and direction are visually indicated with an arrow icon
**And** due date remains the default sort when no explicit sort is selected

### Story 3.3: Exception Indicators & Status Badges

As a planner,
I want visual exception indicators and status badges on PO lines,
So that I can instantly identify overdue, at-risk, and quality-flagged items without reading every row.

**Acceptance Criteria:**

**Given** a PO line has a promised date that has passed
**When** the PO list is rendered
**Then** the row displays a visual overdue exception indicator per FR13
**And** the indicator uses color plus icon plus text (never color alone) per NFR25
**And** the overdue indicator uses a colored left border on the row per Direction B visual design

**Given** a PO line has a promised date within a configurable number of days (at-risk threshold)
**When** the PO list is rendered
**Then** the row displays an at-risk exception indicator per FR13
**And** the at-risk threshold is configurable via system parameters (Epic 8)

**Given** a PO line has a source quality classification (confirmed, estimate, no response)
**When** the PO list is rendered
**Then** a Source Quality Badge is displayed using distinct styling per FR25
**And** "Supplier confirmed" shows a green badge with checkmark icon
**And** "Expeditor estimate" shows a yellow/amber badge with estimate icon
**And** "No supplier response" shows a red badge with warning icon

**Given** a PO line has a status in the lifecycle
**When** the PO list is rendered
**Then** a Status Lifecycle Badge displays the current status with distinct color and icon per status stage
**And** the badge follows the UX spec's Status Lifecycle Badge component definition

**Given** a PO line has staleness information
**When** the PO list is rendered
**Then** a Staleness Indicator shows how recently the PO line was updated by an expeditor
**And** stale items (beyond the configurable threshold) are visually distinguished

**Given** a PO line has quantity data
**When** the PO list is rendered
**Then** a Quantity Progress Display shows ordered vs ready vs dispatched vs delivered quantities
**And** the display provides an at-a-glance progress visualization

**Given** all indicators and badges are rendered
**When** accessibility is checked
**Then** all status information is conveyed through color plus icon plus text per NFR25
**And** indicators are readable by screen readers via appropriate ARIA attributes per NFR24

### Story 3.4: Filter Presets & Time-Based Filters

As a planner,
I want preset filter views for common exception scenarios and time-based filters,
So that I can jump directly to late, at-risk, recently updated, or stale PO lines with one click.

**Acceptance Criteria:**

**Given** the PO list view is displayed
**When** the Filter Preset Navigation component is rendered
**Then** preset tabs are displayed for: "All", "Late", "At Risk", "Updated Recently", "No Response" per FR16
**And** the tabs follow the UX spec's Filter Preset Navigation component design
**And** "All" is the default active tab

**Given** the user clicks the "Late" preset tab
**When** the preset is applied
**Then** the table body refreshes via HTMX to show only PO lines with a promised date in the past
**And** the "Late" tab is visually highlighted as active

**Given** the user clicks the "At Risk" preset tab
**When** the preset is applied
**Then** the table shows PO lines within the configurable at-risk threshold of their due date

**Given** the user clicks the "Updated Recently" preset tab
**When** the preset is applied per FR14
**Then** the table shows PO lines updated within a specified time window (e.g., last 24 hours)
**And** this supports cross-timezone awareness so planners can see what expeditors updated during their working hours

**Given** the user clicks the "No Response" preset tab
**When** the preset is applied per FR15
**Then** the table shows PO lines with no expeditor update within the configurable staleness threshold

**Given** a filter preset is active
**When** the user applies additional column filters on top of the preset
**Then** both the preset filter and column filters are applied together (AND logic)
**And** clearing all filters returns to the "All" view

**Given** filter presets trigger HTMX partial refresh
**When** any preset tab is clicked
**Then** only the table body swaps via `_table_body.html` fragment
**And** the response completes within 2 seconds per NFR2

### Story 3.5: Column Chooser & Preference Persistence

As a user,
I want to show or hide columns in the PO list and have my preferences remembered,
So that I see only the information relevant to my workflow without reconfiguring each session.

**Acceptance Criteria:**

**Given** the PO list view is displayed
**When** the user opens the Column Chooser Control per FR17a
**Then** a panel or dropdown displays all available columns with checkboxes for visibility
**And** the control follows the UX spec's Column Chooser Control component design
**And** the user can check or uncheck individual columns to show or hide them

**Given** the user changes column visibility
**When** the selection is applied
**Then** the table header and table body refresh via HTMX to reflect the new column set
**And** both `_table_header.html` and `_table_body.html` fragments are swapped

**Given** a user has customized their column visibility
**When** they log out and log back in per FR17b
**Then** their column visibility preferences are persisted and restored from the database
**And** the `static/js/column-chooser.js` script handles the client-side interaction
**And** preferences are stored per-user in the app database (not browser local storage)

**Given** a new user logs in for the first time
**When** no saved preferences exist per FR17c
**Then** role-based default column visibility is applied
**And** expeditor defaults differ from planner defaults (expeditors see supplier-action-oriented columns, planners see exception-oriented columns)
**And** users can override these defaults at any time via the column chooser

**Given** column preferences are persisted
**When** the user model or a related preference model stores visibility
**Then** a `UserColumnPreference` model or JSON field stores the ordered list of visible column identifiers per user
**And** the preference is loaded on each PO list page render

### Story 3.6: Standard & Custom Column Display

As a user,
I want to see Item, PO insert date, final customer, and admin-configured custom columns in the PO list,
So that I have access to extended product and operational data alongside standard PO fields.

**Acceptance Criteria:**

**Given** the PO list view is displayed
**When** the column set is rendered per FR17d
**Then** Item (product family/category), PO insert date (original PO creation date), and final customer are available as standard columns in the PO list
**And** these columns are included in the column chooser and can be shown or hidden by the user
**And** they follow the same filtering and sorting behavior as other columns

**Given** an admin has configured custom columns (via Epic 8 or seed data)
**When** the PO list view renders per FR17e
**Then** up to 15 admin-configured custom columns are available for display: 5 date-type, 5 text-type, 5 decimal-type
**And** each custom column is displayed with its admin-defined label (not the physical field name)
**And** custom columns appear in the column chooser and can be shown or hidden

**Given** custom columns have role-based default visibility configured
**When** a user with no saved preferences views the list
**Then** only custom columns configured as visible-by-default for their role are shown
**And** the user can override this via the column chooser

**Given** a custom column has been deactivated by an admin
**When** the PO list renders
**Then** deactivated custom columns are not shown in the column chooser or the table
**And** existing data in deactivated columns is preserved but not displayed

**Given** custom columns are displayed
**When** the user filters or sorts by a custom column
**Then** date-type custom columns support date range filtering and date sorting
**And** text-type custom columns support text contains filtering and alphabetical sorting
**And** decimal-type custom columns support numeric range filtering and numeric sorting

### Story 3.7: Manual Refresh & Custom Column User Entry

As a user,
I want to manually refresh the PO list data and edit user-entered custom column values inline,
So that I see the latest data on demand and can maintain extended fields without leaving the list view.

**Acceptance Criteria:**

**Given** the PO list view is displayed
**When** the user clicks the manual refresh action per FR17
**Then** the current view data is reloaded from the server via HTMX partial refresh
**And** all active filters, sort order, and pagination position are preserved
**And** the refresh button shows a loading indicator during the request
**And** the refreshed data reflects the latest database state

**Given** a PO line has user-entered custom columns (source is not ERP-mapped)
**When** the user clicks to edit a custom column value inline in the PO list view per FR51
**Then** the cell becomes an editable input field appropriate to the column type: date picker for date columns, text input for text columns, numeric input for decimal columns
**And** the inline edit follows the UX spec's inline edit interaction pattern

**Given** the user enters or updates a custom column value inline
**When** the value is submitted
**Then** the `POLine` record is updated with the new value
**And** the `custom_column_sources` field records the source as `'user'` for that column per FR8c
**And** an audit event is created with `event_type='custom_column_updated'`, `source='inline'`, and the previous/new values
**And** a success toast notification is displayed
**And** the table row refreshes to show the updated value

**Given** the user attempts to edit a custom column that is ERP-sourced
**When** the cell is rendered
**Then** it is displayed as read-only and cannot be edited inline
**And** a visual indicator distinguishes ERP-sourced values from user-entered values

**Given** inline edit validation fails
**When** an invalid value is entered (e.g., non-date text in a date column)
**Then** the input shows inline validation feedback
**And** the submission is rejected until a valid value is provided
**And** no audit event is created for a rejected submission

## Epic 4: PO Detail & Investigation

Users can open a PO line's detail panel to investigate the full timeline, batch history, status transitions, and delivery progress.

### Story 4.1: PO Detail Slide-Over Panel

As a user,
I want to open a detail panel for any PO line directly from the list view,
So that I can investigate a specific PO line without losing my place in the list.

**Acceptance Criteria:**

**Given** the PO list view is displayed
**When** the user clicks on a PO line row
**Then** a slide-over detail panel opens from the right side of the screen per the UX spec's PO Detail Slide-over Panel component
**And** the panel is loaded via HTMX request to `/po/<int:pk>/detail/` returning the `po/_detail_panel.html` fragment

**Given** the slide-over panel is opening
**When** the panel shell renders
**Then** it displays PO header information: PO number, line number, supplier name, SKU, item, ordered quantity, current status, and promised date
**And** a loading indicator is shown for each lazy-loaded section below the header
**And** the panel loads within 2 seconds per NFR3

**Given** the panel shell is rendered
**When** lazy-loaded sections are initialized
**Then** separate HTMX requests are triggered for: timeline section, batch delivery section, status history section, and delivery progress section
**And** each section loads independently via its own HTMX endpoint returning its own fragment
**And** sections display a spinner while loading and render content when their response arrives

**Given** the detail panel is open
**When** the user clicks a close button or clicks outside the panel
**Then** the panel closes and the PO list view remains in its previous state (filters, sort, pagination preserved)
**And** a `closePanel` HTMX trigger event is fired

**Given** the detail panel is open
**When** the user clicks a different PO line row in the list behind the panel
**Then** the panel content refreshes to show the newly selected PO line's details
**And** all lazy-loaded sections reload for the new PO line

**Given** the detail panel renders
**When** accessibility is verified
**Then** the panel is keyboard navigable with focus trapped within while open per NFR26
**And** the close button is accessible via keyboard (Escape key closes the panel)
**And** panel content is readable by screen readers per NFR24

### Story 4.2: Audit Timeline & Change History

As a user,
I want to see the full chronological timeline of all changes for a PO line,
So that I can understand who changed what, when, from what source, and why.

**Acceptance Criteria:**

**Given** the PO detail panel is open and the timeline section loads
**When** the HTMX request to `/po/<int:pk>/timeline/` returns the `po/_timeline.html` fragment per FR18
**Then** a chronological timeline displays all audit events for that PO line
**And** events are sorted in reverse chronological order (most recent first)

**Given** the timeline is rendered
**When** each event is displayed
**Then** it shows: the date and time of the change, the user who made it (or "System" for ingestion), the source classification (manual, bulk, inline, ingestion), the fields that changed with previous and new values, and the reason provided (if any)
**And** the timeline follows the UX spec's Audit Timeline component design

**Given** the timeline contains date change events
**When** a milestone date was updated
**Then** the event clearly shows the previous date, new date, source quality (confirmed/estimate/no response), and the reason text

**Given** the timeline contains ingestion change events
**When** an ERP snapshot detected field changes
**Then** the event shows source as "ingestion", the ERP fields that changed, and the previous/new values
**And** ingestion events are visually distinguishable from manual user events

**Given** the timeline has many events
**When** the list is long
**Then** the timeline section supports scrolling within the panel
**And** an initial batch of events is loaded with a "Load more" action for older events if needed

**Given** the timeline is rendered
**When** accessibility is verified
**Then** timeline entries use semantic HTML for screen reader compatibility per NFR24
**And** timestamps and field changes are conveyed through text (not color alone) per NFR25

### Story 4.3: Batch Delivery Table

As a user,
I want to see the batch delivery table for a PO line showing both historical and planned batches,
So that I can understand the delivery breakdown and what has been shipped versus what is planned.

**Acceptance Criteria:**

**Given** the PO detail panel is open and the batch section loads
**When** the HTMX request to `/po/<int:pk>/batches/` returns the `po/_batch_list.html` fragment per FR19
**Then** a table displays all batches associated with that PO line

**Given** the batch table is rendered
**When** historical batches exist (reconstructed from ERP data in Epic 2)
**Then** each historical batch row shows: batch identifier, delivered quantity, delivery date (InDate), and source ("ERP")
**And** historical batches are visually distinguished from planned batches

**Given** the batch table is rendered
**When** planned future batches exist (created by expeditors in Epic 6)
**Then** each planned batch row shows: batch identifier, allocated quantity, expected dispatch date, batch status, and source ("Manual")
**And** planned batches display their current lifecycle status (Planned, Confirmed, Dispatched, Delivered)

**Given** the batch table contains both historical and planned batches
**When** the table is sorted
**Then** batches are ordered chronologically by delivery/dispatch date
**And** the table clearly separates or labels historical vs planned sections

**Given** no batches exist for a PO line
**When** the batch section renders
**Then** a message indicates no batch records are available for this PO line
**And** the empty state uses the em dash (`—`) display convention

### Story 4.4: Status History & Delivery Progress

As a user,
I want to see the complete status transition history and delivery progress for a PO line,
So that I can understand the lifecycle journey and how much quantity remains outstanding.

**Acceptance Criteria:**

**Given** the PO detail panel is open and the status history section loads
**When** the HTMX request to `/po/<int:pk>/status-history/` returns the `po/_status_history.html` fragment per FR20
**Then** the current status is prominently displayed with its Status Lifecycle Badge
**And** a chronological list of all status transitions is shown below: previous status, new status, timestamp, user who triggered the change, and source

**Given** the status history is rendered
**When** the PO line has transitioned through multiple lifecycle stages (Planned → In Production → Ready to Dispatch → etc.)
**Then** each transition is displayed as a discrete entry with the transition date and context
**And** the lifecycle flow is visually represented showing which stages have been completed

**Given** the PO detail panel is open and the delivery progress section loads
**When** the progress data is rendered per FR21
**Then** the Quantity Progress Display shows: ordered quantity, ready quantity (produced but not dispatched), dispatched quantity, delivered quantity, and remaining quantity
**And** progress is visualized as a segmented bar or meter showing the proportion of each stage
**And** zero values display as `0` and null values display as `—` per the null display convention

**Given** the delivery progress is rendered
**When** the PO line has partial deliveries
**Then** the visualization clearly distinguishes between: goods produced (ready), goods in transit (dispatched), goods received (delivered), and goods outstanding (remaining)
**And** the total of all segments equals the ordered quantity

**Given** progress and status sections are rendered
**When** accessibility is verified
**Then** all progress information is conveyed through text labels alongside visual elements per NFR25
**And** the segmented progress bar has ARIA attributes describing each segment per NFR24
**And** all interactive elements are keyboard accessible per NFR26

## Epic 5: Milestone Recording & Status Management

Expeditors can record milestone updates (single, bulk, inline), track ready quantities, and manage PO status transitions — with full audit accountability.

### Story 5.1: Single Milestone Update Modal

As an expeditor,
I want to record a milestone date update for a single PO line with required context,
So that planners have an accurate, sourced, and explained update for their decision-making.

**Acceptance Criteria:**

**Given** an expeditor is viewing the PO list or detail panel for a PO line within their supplier scope
**When** they click the update milestone action on a single PO line
**Then** a modal dialog opens via HTMX loading the `po/_milestone_modal.html` fragment
**And** the modal displays the PO line context (PO number, line, SKU, supplier, current promised date)

**Given** the milestone modal is open
**When** the form is displayed per FR22
**Then** it contains fields for: milestone type (production-ready or ready-to-dispatch), new date (date picker), reason (text input), source classification (dropdown), and optional free-text notes per FR27
**And** all three mandatory fields (date, reason, source) are clearly marked as required per FR23

**Given** the expeditor selects a source classification per FR24
**When** they choose from the dropdown
**Then** the options are: "Supplier confirmed", "Expeditor estimate", and "No supplier response"
**And** the selected source will be stored with the milestone update

**Given** the expeditor fills all required fields and submits
**When** the form passes validation
**Then** the PO line's milestone date is updated in the database
**And** an append-only audit event is created via `create_audit_event()` with: `event_type='milestone_updated'`, `source='manual'`, user FK, previous date, new date, reason, source quality, and notes per FR26
**And** the modal closes via `closeModal` HTMX trigger
**And** the table row refreshes to reflect the updated date and source quality badge
**And** a success toast notification is displayed

**Given** the expeditor submits with missing required fields per FR23
**When** validation fails
**Then** the modal form is re-rendered with inline error messages indicating which fields are missing
**And** the submission is rejected and no database update or audit event is created
**And** the modal remains open for correction

**Given** a planner or unauthorized user attempts to access the milestone update action
**When** the request is processed
**Then** it is rejected with HTTP 403 per FR40 and the RBAC enforcement from Story 1.4

### Story 5.2: Ready Quantity Recording

As an expeditor,
I want to record ready quantities as suppliers complete production in increments,
So that planners can see how much product is available for dispatch at any point.

**Acceptance Criteria:**

**Given** the milestone update modal is open for a PO line
**When** the ready quantity fields are displayed per FR22a
**Then** the form includes: ready quantity (numeric input) and readiness date (date picker)
**And** these fields are available alongside the milestone date update or independently

**Given** the expeditor enters a ready quantity and readiness date
**When** the form is submitted
**Then** a ready quantity record is created for that PO line with the specified quantity and date
**And** an audit event is created with `event_type='ready_qty_recorded'`, the quantity, date, and user

**Given** a PO line has had previous ready quantity entries per FR22b
**When** a new ready quantity is recorded
**Then** the new entry is added as an incremental record (not replacing previous entries)
**And** the system tracks multiple ready-quantity entries representing partial production completions

**Given** a PO line has multiple ready quantity entries per FR22c
**When** the PO list or detail panel renders quantity information
**Then** the cumulative ready quantity is displayed alongside ordered quantity and remaining quantity
**And** the display distinguishes between: goods produced (cumulative ready qty), goods dispatched, and goods outstanding (remaining)
**And** the Quantity Progress Display component reflects the cumulative ready quantity

**Given** the expeditor enters a ready quantity that would exceed the ordered quantity
**When** the form is submitted
**Then** a validation warning is displayed (the total ready quantity including this entry would exceed ordered quantity)
**And** the expeditor can confirm to proceed or correct the value

### Story 5.3: Source Quality Visual Distinction

As a user,
I want to immediately see whether a PO line's latest update is supplier-confirmed, an expeditor estimate, or has no supplier response,
So that I can assess data reliability at a glance across all views.

**Acceptance Criteria:**

**Given** a PO line has a source quality classification from its most recent milestone update
**When** the PO list view renders per FR25
**Then** the Source Quality Badge displays with consistent styling across all rows:
**And** "Supplier confirmed" renders as a green badge with checkmark icon and text label
**And** "Expeditor estimate" renders as a yellow/amber badge with estimate icon and text label
**And** "No supplier response" renders as a red badge with warning icon and text label

**Given** the PO detail panel is open
**When** source quality is displayed in the header and timeline per FR25
**Then** the same Source Quality Badge component is used consistently
**And** each timeline entry shows the source quality of that specific update

**Given** source quality badges are rendered
**When** accessibility is verified
**Then** every badge conveys its meaning through color plus icon plus text per NFR25
**And** badges have appropriate ARIA labels for screen readers per NFR24
**And** the three states are distinguishable in grayscale/high-contrast modes

**Given** a PO line has no milestone updates yet
**When** the source quality column is rendered
**Then** the cell displays em dash indicating no source quality data available

### Story 5.4: Bulk Milestone Update

As an expeditor,
I want to select multiple PO lines and apply the same milestone update to all of them at once,
So that I can efficiently process supplier responses that cover many PO lines.

**Acceptance Criteria:**

**Given** the PO list view is displayed for an expeditor
**When** the expeditor begins selecting PO lines per FR27a
**Then** checkboxes appear on each PO line row for multi-select
**And** a "Select all on page" checkbox is available in the table header
**And** the selection count is displayed as lines are checked

**Given** one or more PO lines are selected
**When** the selection is active
**Then** the Bulk Action Bar appears at the top or bottom of the list per the UX spec's Bulk Action Bar component
**And** the bar shows the count of selected lines and an "Update Milestones" action button

**Given** the expeditor clicks "Update Milestones" on the Bulk Action Bar
**When** the bulk update form loads via HTMX (`po/_bulk_update_bar.html` fragment or modal)
**Then** the form contains the same fields as the single update: milestone type, new date, reason, source classification, ready quantity, readiness date, and optional notes
**And** all mandatory fields (date, reason, source) are required per FR23

**Given** the expeditor submits the bulk update form with valid data
**When** the update is applied per FR27a
**Then** the same milestone update (date, reason, source, ready quantity) is applied to all selected PO lines in a single action
**And** an audit event is created for each affected PO line with `source='bulk'`
**And** the table body refreshes to reflect updated values on all affected rows
**And** a success toast shows the count of PO lines updated
**And** the selection is cleared and the Bulk Action Bar is hidden

**Given** the bulk update encounters a validation error on one or more lines
**When** the update cannot be applied
**Then** the error is reported indicating which PO lines failed and why
**And** successfully updated lines are committed (partial success is acceptable)
**And** the expeditor can correct and retry for failed lines

### Story 5.5: Inline Edit Mode

As an expeditor,
I want to edit milestone fields directly in the PO list table across multiple rows with different values per row,
So that I can quickly enter row-specific updates without opening modals for each line.

**Acceptance Criteria:**

**Given** the PO list view is displayed for an expeditor
**When** the expeditor activates inline edit mode per FR27b
**Then** editable milestone columns (milestone date, reason, source, ready quantity, notes) become inline input fields on each visible PO line row
**And** the `po/_inline_edit_row.html` fragment replaces the standard row rendering
**And** the `static/js/inline-edit.js` script manages activation/deactivation of edit mode

**Given** inline edit mode is active
**When** the expeditor enters values across multiple rows
**Then** each row can have different values for date, reason, source, ready quantity, and notes
**And** rows with changes are visually highlighted to distinguish them from unchanged rows
**And** mandatory fields (date, reason, source) are validated per-row per FR23

**Given** the expeditor has entered values across multiple rows
**When** they click a "Submit All Changes" action
**Then** all modified rows are submitted as a batch to the server
**And** each modified PO line is updated with its row-specific values
**And** an audit event is created for each modified PO line with `source='inline'` per FR26
**And** a success toast shows the count of rows updated
**And** inline edit mode deactivates and the table returns to normal display

**Given** inline edit mode is active
**When** the expeditor clicks "Cancel" or presses Escape
**Then** all unsaved changes are discarded
**And** the table rows revert to their normal read-only display
**And** no database updates or audit events are created

**Given** inline edit validation fails on one or more rows
**When** the batch submission is processed
**Then** rows with validation errors display inline error indicators
**And** valid rows are committed successfully (partial success)
**And** the expeditor can correct and resubmit failed rows

**Given** inline edit mode renders input fields
**When** accessibility is verified
**Then** all input fields are labeled per NFR26
**And** tab navigation moves between editable fields in logical order
**And** the edit mode state is announced to screen readers

### Story 5.6: Status Lifecycle Transitions

As a system,
I want to enforce valid PO line status transitions through a defined lifecycle,
So that status values are always consistent and every transition is audited.

**Acceptance Criteria:**

**Given** the PO line status lifecycle is defined per FR28
**When** the status model is implemented
**Then** valid statuses are: Planned, In Production, Ready to Dispatch, Part Delivered, Fully Delivered, Cancelled, Closed
**And** valid transitions are enforced:
- Planned to In Production
- In Production to Ready to Dispatch
- Ready to Dispatch to Part Delivered or Fully Delivered
- Part Delivered to Part Delivered (additional deliveries) or Fully Delivered
- Any active status to Cancelled
- Fully Delivered to Closed
- Cancelled to Closed

**Given** a status transition is attempted
**When** the transition is valid
**Then** the PO line status is updated
**And** an audit event is created with `event_type='status_changed'`, previous status, new status, user, and source
**And** the Status Lifecycle Badge updates in all views (list, detail panel, status history)

**Given** a status transition is attempted
**When** the transition is invalid (e.g., Planned directly to Fully Delivered)
**Then** the transition is rejected with a validation error message indicating the allowed transitions from the current status
**And** no database update or audit event is created

**Given** milestone events occur
**When** a ready-to-dispatch date is recorded for a PO line in "In Production" status
**Then** the system suggests or automatically transitions the status to "Ready to Dispatch" (configurable behavior)
**And** the transition is audited like any manual transition

**Given** delivery events occur
**When** batch deliveries are recorded and cumulative delivered quantity equals ordered quantity
**Then** the system suggests or automatically transitions the status to "Fully Delivered"
**And** partial deliveries transition to "Part Delivered" when some but not all quantity is delivered

**Given** status transitions are displayed
**When** the Status Lifecycle Badge renders
**Then** each status has a distinct color and icon per the UX spec
**And** the badge uses color plus icon plus text per NFR25

## Epic 6: Batch Tracking

Users can view historical batches from ERP data, create planned future batches, track batch lifecycle, and monitor batch-level delivery progress.

### Story 6.1: Planned Batch Creation

As an expeditor,
I want to create planned future batches for a PO line with allocated quantity and expected dispatch date,
So that planners can see the delivery plan broken down into manageable shipments.

**Acceptance Criteria:**

**Given** an expeditor is viewing the PO detail panel for a PO line within their supplier scope
**When** they click a "Create Batch" action in the batch delivery section
**Then** a batch creation form loads via HTMX returning the `batches/_batch_create_form.html` fragment
**And** the form displays the PO line context (PO number, line, SKU, ordered quantity, remaining unallocated quantity)

**Given** the batch creation form is displayed per FR30
**When** the form fields are shown
**Then** it contains: allocated quantity (numeric input), expected dispatch date (date picker), and optional notes
**And** the remaining unallocated quantity is displayed to guide the expeditor

**Given** the expeditor enters a valid quantity and dispatch date
**When** the form is submitted per FR32
**Then** a new Batch record is created with status "Planned", the allocated quantity, expected dispatch date, PO line FK, and `source='manual'`
**And** the batch quantity is allocated to the PO line without requiring ERP line splitting
**And** an audit event is created with `event_type='batch_created'`, `source='manual'`, quantity, date, and user
**And** the batch list in the detail panel refreshes to show the new batch
**And** a success toast notification is displayed

**Given** the expeditor enters a quantity that would exceed the remaining unallocated quantity
**When** the form is submitted
**Then** a validation warning is displayed indicating the total allocated quantity would exceed ordered quantity
**And** the expeditor can confirm to proceed or correct the value

**Given** multiple planned batches exist for a PO line
**When** the batch list is viewed
**Then** each batch shows its allocated quantity independently
**And** the sum of all batch allocations is displayed against the ordered quantity

**Given** a planner or unauthorized user attempts to create a batch
**When** the request is processed
**Then** it is rejected with HTTP 403 per the RBAC enforcement from Story 1.4

### Story 6.2: Batch Status Lifecycle

As an expeditor,
I want to update batch status through a defined lifecycle,
So that planners can track the progress of each shipment from planning through delivery.

**Acceptance Criteria:**

**Given** the batch status lifecycle is defined per FR31
**When** the status model is implemented
**Then** valid batch statuses are: Planned, Confirmed, Dispatched, Delivered
**And** valid transitions are enforced:
- Planned to Confirmed
- Confirmed to Dispatched
- Dispatched to Delivered

**Given** an expeditor views a batch in the PO detail panel batch list
**When** a status transition action is available
**Then** only valid next statuses are presented as options based on the current status
**And** invalid transitions are not offered in the UI

**Given** the expeditor selects a valid status transition
**When** the transition is submitted
**Then** the batch status is updated in the database
**And** an audit event is created with `event_type='batch_status_changed'`, previous status, new status, batch FK, PO line FK, user, and source
**And** the batch row in the detail panel refreshes to show the new status badge
**And** a success toast notification is displayed

**Given** a batch transitions to "Dispatched"
**When** the transition is processed
**Then** the dispatched quantity is reflected in the PO line's quantity tracking (dispatched total increases)
**And** the Quantity Progress Display in the detail panel updates accordingly

**Given** a batch transitions to "Delivered"
**When** the transition is processed
**Then** the delivered quantity is reflected in the PO line's quantity tracking (delivered total increases)
**And** if cumulative delivered quantity across all batches equals the ordered quantity, the system suggests transitioning the PO line status to "Fully Delivered" per Story 5.6
**And** if partial, the PO line status may transition to "Part Delivered"

**Given** an invalid batch status transition is attempted
**When** the transition is rejected
**Then** a validation error message indicates the allowed transitions from the current status
**And** no database update or audit event is created

### Story 6.3: Batch Progress View

As a user,
I want to see batch-level delivery progress showing delivered versus planned batches,
So that I can understand the overall delivery trajectory for a PO line at a glance.

**Acceptance Criteria:**

**Given** the PO detail panel batch section is loaded
**When** the batch progress is displayed per FR33
**Then** a summary shows: total batches, batches delivered, batches in transit (dispatched), batches confirmed, and batches planned
**And** the summary is displayed above the batch detail table

**Given** a PO line has both historical (ERP-reconstructed) and planned (manually created) batches
**When** the progress view renders per FR29 (display)
**Then** historical batches from ERP ingestion are shown with their delivered quantities and dates
**And** planned future batches are shown with their allocated quantities and expected dates
**And** the two categories are visually distinguishable (e.g., different background or label)

**Given** batch progress data is available
**When** the progress visualization renders
**Then** a progress indicator shows the proportion of delivered quantity versus total ordered quantity across all batches
**And** the visualization follows the Supplier Progress Indicator component from the UX spec where applicable

**Given** no batches exist for a PO line
**When** the batch progress section renders
**Then** the progress shows zero batches with ordered quantity fully unallocated
**And** the empty state displays appropriately with em dash convention for missing values

**Given** batch progress is rendered
**When** accessibility is verified
**Then** progress information is conveyed through text labels alongside visual indicators per NFR25
**And** batch status badges use color plus icon plus text per NFR25
**And** the progress summary is readable by screen readers per NFR24

## Epic 7: Supplier Communication

Expeditors can generate structured Excel files for suppliers with pre-filled PO data and response fields, replacing manual spreadsheet workflows.

### Story 7.1: Supplier Excel Generation & Download

As an expeditor,
I want to generate and download a structured Excel file for a selected supplier containing all their open PO lines,
So that I can send suppliers a professional, pre-filled request file instead of manually building spreadsheets.

**Acceptance Criteria:**

**Given** an expeditor is viewing the PO list filtered to a specific supplier
**When** they click a "Generate Supplier Excel" action per FR34
**Then** the system generates an Excel file containing all open PO lines for that supplier
**And** the file is downloaded to the user's browser as an `.xlsx` file
**And** the filename includes the supplier name and generation date (e.g., `SupplierName_PO_Request_2026-02-13.xlsx`)

**Given** the Excel file is being generated per FR35
**When** the data is populated
**Then** the file is pre-filled with columns for: PO number, item (product family/category), SKU, ordered quantity, remaining quantity, promised date, current status, and final customer
**And** data is sourced from the current database state using `.for_user(request.user)` scoping
**And** rows are sorted by promised date ascending (most urgent first)

**Given** the Excel file is generated using `openpyxl` in `apps/exports/generators.py`
**When** the file formatting is applied
**Then** the header row is styled with bold text and a distinct background color for readability
**And** date columns are formatted as dates (not text strings)
**And** numeric columns (quantities) are formatted as numbers
**And** column widths are auto-adjusted for content readability

**Given** a supplier has up to 200 open PO lines
**When** the Excel generation completes
**Then** the file is generated and download begins within 5 seconds per NFR4

**Given** a supplier has zero open PO lines
**When** the expeditor attempts to generate an Excel file
**Then** a warning message indicates there are no open PO lines for the selected supplier
**And** no empty file is generated

**Given** a planner or unauthorized user attempts to generate a supplier Excel
**When** the request is processed
**Then** it is rejected with HTTP 403 per RBAC enforcement from Story 1.4

### Story 7.2: Supplier Response Fields & Template Formatting

As an expeditor,
I want the generated Excel to include response columns for the supplier to fill in,
So that suppliers can provide structured feedback that I can efficiently process back into the system.

**Acceptance Criteria:**

**Given** the Excel file is generated
**When** the supplier response fields are added per FR36
**Then** three additional columns are appended after the pre-filled data columns: "Ready Date", "Qty Ready", and "Comments"
**And** these response columns are empty (for the supplier to fill in)
**And** the response column headers are visually distinguished from pre-filled data headers (e.g., different background color or border)

**Given** response columns are included
**When** the column formatting is applied
**Then** the "Ready Date" column has date format validation applied to guide suppliers toward correct date entry
**And** the "Qty Ready" column has numeric format applied
**And** the "Comments" column allows free text with adequate column width

**Given** the Excel template is complete
**When** the overall structure is reviewed
**Then** the first row contains column headers with clear labels
**And** a title or header section above the data identifies: supplier name, generation date, and the requesting organization
**And** the worksheet is named meaningfully (e.g., "PO Lines" or the supplier name)

**Given** the Excel file includes both pre-filled and response columns
**When** the pre-filled data columns are reviewed
**Then** pre-filled columns are protected or visually marked as read-only (e.g., light gray background) to discourage supplier edits to source data
**And** response columns have a white or highlighted background to indicate they are editable

**Given** the export endpoint is accessed
**When** the download is initiated at `/exports/supplier/<int:supplier_id>/excel/`
**Then** the response content type is set to `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
**And** the Content-Disposition header triggers a file download with the correct filename
**And** the endpoint uses `@login_required` and `@role_required('expeditor', 'admin')` decorators

## Epic 8: System Administration & Operations

Admins can manage users, supplier scopes, xref tables, ingestion monitoring, audit logs, system configuration, custom column configuration, and cross-region replication.

### Story 8.1: Admin Dashboard & Navigation

As an admin,
I want a central admin portal with navigation to all administrative functions and health summary,
So that I can quickly assess system status and navigate to the area that needs attention.

**Acceptance Criteria:**

**Given** an admin is logged in
**When** they navigate to `/admin-portal/`
**Then** the admin dashboard page is rendered (`admin_portal/dashboard.html`)
**And** it is accessible only to users with the `admin` role via `@role_required('admin')`

**Given** the admin dashboard is displayed
**When** the navigation is rendered
**Then** links are provided to: User Management, Xref Management, Ingestion Monitor, Audit Log, System Configuration, and Custom Column Configuration
**And** the navigation follows the Direction B visual design with the dark blue navbar

**Given** the admin dashboard is displayed
**When** summary health indicators are rendered
**Then** the dashboard shows: last ingestion run status and timestamp, count of unmapped xref items, count of active users by role, and replication status (if applicable)
**And** indicators use color plus icon plus text for status (healthy/warning/error) per NFR25

**Given** a non-admin user attempts to access `/admin-portal/`
**When** the request is processed
**Then** it is rejected with HTTP 403 per RBAC enforcement from Story 1.4

### Story 8.2: User Management

As an admin,
I want to create, edit, and deactivate user accounts with role assignment and supplier scope,
So that I can control who has access to the system and what data they can see.

**Acceptance Criteria:**

**Given** an admin navigates to the User Management page at `/admin-portal/users/`
**When** the page renders (`admin_portal/user_list.html`)
**Then** a list of all user accounts is displayed with: username, full name, role, assigned supplier (for expeditors), active status, and last login date
**And** the list supports sorting and filtering by role and active status

**Given** the admin clicks "Create User"
**When** the user form loads via HTMX (`admin_portal/_user_form.html` fragment) per FR41
**Then** the form contains fields for: username, password, first name, last name, role (dropdown: admin/planner/expeditor), and active status
**And** all required fields are validated on submission

**Given** the admin selects the "expeditor" role on the user form
**When** the role is selected per FR42
**Then** a supplier scope assignment field appears (dropdown or multi-select of available suppliers)
**And** at least one supplier must be assigned for an expeditor

**Given** the admin submits a valid new user form
**When** the user is created
**Then** a new User record is created with the specified role, supplier assignment (if expeditor), and active status
**And** the password is stored using PBKDF2 hashing per NFR8
**And** an audit event is created with `event_type='user_created'`, `source='manual'`, and the admin user
**And** a success toast notification is displayed
**And** the user list refreshes to include the new user

**Given** the admin clicks "Edit" on an existing user
**When** the edit form loads per FR41
**Then** it is pre-populated with the user's current data
**And** the admin can modify role, supplier scope, name, and active status
**And** password can be reset but the current password is not displayed

**Given** the admin deactivates a user per FR41
**When** the user's active status is set to false
**Then** the user can no longer log in
**And** existing sessions for that user are invalidated
**And** an audit event is created with `event_type='user_deactivated'`
**And** the user record is preserved (not deleted) for audit history integrity

**Given** the admin modifies an expeditor's supplier scope per FR42
**When** the supplier assignment is changed
**Then** the user's data access scope changes immediately on their next request
**And** an audit event records the previous and new supplier assignments

### Story 8.3: Xref Table Management

As an admin,
I want to manage the SKU cross-reference table and see which items are unmapped,
So that I can resolve data quality gaps and ensure all PO lines are properly categorized.

**Acceptance Criteria:**

**Given** an admin navigates to the Xref Management page at `/admin-portal/xref/`
**When** the page renders (`admin_portal/xref_list.html`) per FR43
**Then** a list of all xref entries is displayed with: ERP item code, mapped SKU, mapped item (product family), supplier, active status, and last modified date
**And** the list supports filtering by supplier, mapped/unmapped status, and search by item code or SKU

**Given** the admin clicks "Add Mapping"
**When** the xref form loads via HTMX (`admin_portal/_xref_form.html` fragment) per FR43
**Then** the form contains fields for: ERP item code, mapped SKU, mapped item (product family), supplier, and active flag
**And** required fields are validated on submission

**Given** the admin submits a valid xref mapping
**When** the mapping is created
**Then** an `ItemXref` record is created with the specified values
**And** an audit event is created with `event_type='xref_created'`
**And** subsequent ingestion runs will use this mapping for the ERP item code

**Given** the admin needs to import multiple mappings at once
**When** they use the bulk import function per FR43
**Then** a file upload (CSV or Excel) allows importing multiple xref entries at once
**And** the import validates each row and reports: rows imported, rows skipped (duplicates), and rows with errors
**And** an audit event is created for the bulk import operation

**Given** unmapped items have been flagged during ingestion per FR48
**When** the xref list is filtered to show unmapped items
**Then** all ERP item codes that were not found in the xref table during the last ingestion are listed
**And** unmapped items display a distinct visual indicator (warning badge) per FR48
**And** the admin can click an unmapped item to pre-fill the xref form with its ERP item code

**Given** the admin dashboard is displayed
**When** unmapped item count is shown
**Then** the count of unmapped items from the most recent ingestion is displayed as a health indicator
**And** the indicator links to the xref list filtered to unmapped items

### Story 8.4: Ingestion Monitoring

As an admin,
I want to view ingestion job history with run details and error information,
So that I can verify data is flowing correctly and diagnose failures quickly.

**Acceptance Criteria:**

**Given** an admin navigates to the Ingestion Monitor at `/admin-portal/ingestion/`
**When** the page renders (`admin_portal/ingestion_monitor.html`) per FR44
**Then** a list of ingestion job runs is displayed in reverse chronological order
**And** each run shows: run timestamp, status (success/partial/failed), duration, PO lines processed, new lines created, change events detected, batches reconstructed, xref gaps found, and error count

**Given** the ingestion history is displayed
**When** the admin clicks on a specific run
**Then** the run detail expands or loads showing: full error messages, list of unmapped item codes, list of PO lines with changes, and any retry attempts
**And** error details include sufficient context for diagnosis

**Given** the most recent ingestion run failed
**When** the monitor page renders
**Then** the latest run is highlighted with an error indicator
**And** the failure reason is visible without clicking into details
**And** the admin dashboard health indicator also reflects the failure state

**Given** ingestion runs are displayed
**When** the admin filters the history
**Then** filters are available for: date range, status (success/failed/partial), and the list refreshes via HTMX

**Given** ingestion failures and successes are logged per NFR29
**When** an ingestion event is recorded
**Then** the audit event is written within 60 seconds of detection
**And** the event includes timestamp, severity, and event type

### Story 8.5: Audit Log Viewer

As an admin,
I want to view and filter the complete audit log across all system events,
So that I can investigate user actions, verify data integrity, and support governance reviews.

**Acceptance Criteria:**

**Given** an admin navigates to the Audit Log at `/admin-portal/audit/`
**When** the page renders (`admin_portal/audit_log.html`) per FR45
**Then** a table of audit events is displayed in reverse chronological order
**And** each event shows: timestamp, event type, user (or "System"), source, PO line reference (if applicable), and a summary of changes

**Given** the audit log is displayed
**When** the admin applies filters per FR45
**Then** filter controls are available for: user (dropdown), source type (manual/bulk/inline/ingestion/system), date range (from/to), and event type (dropdown)
**And** filters are applied via HTMX partial refresh of the `audit/_audit_log_table.html` fragment
**And** multiple filters can be combined (AND logic)

**Given** the admin clicks on a specific audit event
**When** the event detail is expanded
**Then** the full event data is displayed: previous values (JSON rendered as readable key-value pairs), new values, reason text, and complete metadata

**Given** the audit log contains many events
**When** the table is rendered
**Then** server-side pagination is applied
**And** the total event count matching current filters is displayed
**And** pagination uses HTMX partial refresh

**Given** the audit log viewer is accessed
**When** data integrity is verified
**Then** audit events are displayed as read-only with no edit or delete actions available
**And** the append-only nature of the audit table is preserved (no UI path to modify events) per NFR10

### Story 8.6: System & ERP Configuration

As an admin,
I want to configure ERP connection parameters, ingestion schedule, and system-wide operational thresholds,
So that I can tune the system for our operational environment without code changes.

**Acceptance Criteria:**

**Given** an admin navigates to System Configuration at `/admin-portal/config/`
**When** the ERP configuration section renders per FR46
**Then** configurable fields are displayed for: ERP database host, database name, connection timeout, and ingestion schedule description
**And** sensitive fields (connection credentials) are masked and only editable (not displayed in clear text)
**And** current values are loaded from the system configuration store

**Given** the admin updates ERP connection parameters
**When** the form is submitted per FR46
**Then** the configuration is saved to the database or environment configuration
**And** an audit event is created with `event_type='config_updated'`, the changed parameters (without sensitive values), and the admin user
**And** a success toast confirms the update
**And** changes take effect on the next ingestion run (not retroactively)

**Given** the system configuration page is displayed
**When** the system parameters section renders per FR47
**Then** configurable fields include: staleness threshold (days), at-risk threshold (days before due date), ingestion lookback window, recently-updated time window, and session timeout duration
**And** current values are displayed with input fields for modification

**Given** the admin updates system parameters
**When** the form is submitted per FR47
**Then** the parameter values are saved and take effect immediately for applicable settings
**And** an audit event records the previous and new values
**And** a success toast confirms the update

**Given** system configuration is accessed
**When** validation is applied
**Then** numeric parameters are validated for reasonable ranges (e.g., staleness threshold must be positive)
**And** invalid values are rejected with inline validation feedback
**And** no configuration change is saved for invalid submissions

### Story 8.7: Custom Column Configuration & Cross-Region Replication

As an admin,
I want to configure custom columns and monitor cross-region data replication status,
So that I can extend the data model for operational needs and ensure European users have current data.

**Acceptance Criteria:**

**Given** an admin navigates to Custom Column Configuration at `/admin-portal/custom-columns/`
**When** the page renders (`admin_portal/custom_columns.html`) per FR49
**Then** a list of all 15 custom column slots is displayed: 5 date-type, 5 text-type, 5 decimal-type
**And** each slot shows: slot number, current display label (or "Unconfigured"), data type, data source (ERP or user-entered), default visibility per role, and active/inactive status

**Given** the admin clicks to configure a custom column slot
**When** the configuration form loads via HTMX (`admin_portal/_custom_column_form.html`) per FR49
**Then** the form contains fields for: display label, data source (ERP SQL column mapping or user-entered), and default visibility per role (checkboxes for expeditor/planner/admin)
**And** the data type is fixed by the slot (date/text/decimal) and displayed as read-only

**Given** the admin configures a custom column with ERP source
**When** the ERP SQL column mapping is specified per FR49
**Then** a field allows entering the ERP SQL column name to map to this custom column
**And** the mapping will be used by the ingestion pipeline to populate the column from ERP data

**Given** the admin submits a valid custom column configuration
**When** the configuration is saved
**Then** a `CustomColumnConfig` record is created or updated
**And** an audit event is created with `event_type='custom_column_configured'`
**And** the column becomes available in the PO list column chooser and detail panel
**And** a success toast confirms the update

**Given** the admin activates or deactivates a custom column per FR50
**When** the active status is toggled
**Then** deactivated columns are hidden from the PO list column chooser and all views
**And** existing data in deactivated columns is preserved in the database (not deleted)
**And** reactivating a column restores visibility with all previous data intact
**And** an audit event records the activation/deactivation

**Given** the system uses cross-region replication per FR8
**When** the admin dashboard renders replication status
**Then** the last successful replication timestamp is displayed
**And** if replication has not completed within the expected nightly window (10:00-07:00 UTC per NFR21), a warning indicator is shown
**And** on replication failure, the European instance serves the last successful sync data and an admin alert audit event is generated per NFR22

**Given** the European instance is serving stale data
**When** a user on the European instance accesses the application
**Then** a staleness banner is displayed via `_partials/_staleness_banner.html` indicating the data age
**And** the `StalenessMiddleware` in `apps/core/middleware.py` detects and injects the banner for the European deployment
