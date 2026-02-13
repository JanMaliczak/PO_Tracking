---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - prd.md
  - ux-design-specification.md
  - product-brief-PO_Tracking-2026-02-11.md
  - RESEARCH.md
  - STACK.md
  - PRODUCT_BRIEF.md
  - prd-validation-report.md
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: '2026-02-13'
project_name: 'PO_Tracking'
user_name: 'J.maliczak'
date: '2026-02-13'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

51 FRs across 8 capability areas:

| Capability Area | FR Count | Architectural Significance |
|----------------|----------|---------------------------|
| Data Ingestion & Synchronization | 11 (FR1-FR8c) | Background job pipeline, ERP integration, snapshot/diff engine, cross-region replication, custom column ingestion |
| PO Visibility & Navigation | 13 (FR9-FR17e) | Dense server-rendered table with role-scoped queries, filter presets, column-level filtering, sort, column chooser with per-user persistence, custom column display |
| PO Investigation & Detail | 4 (FR18-FR21) | Slide-over panel with lazy-loaded sections (timeline, batches, status history), complex audit query aggregation |
| Milestone & Status Management | 10 (FR22-FR28) | Three update modes (single modal, bulk, inline), mandatory field validation, append-only event creation, status lifecycle state machine |
| Batch Tracking | 5 (FR29-FR33) | Historical batch reconstruction from ERP data, planned batch creation, batch lifecycle, quantity allocation without ERP line splitting |
| Supplier Communication | 3 (FR34-FR36) | Server-side Excel file generation with structured templates |
| User & Access Management | 4 (FR37-FR40) | Local authentication, 3-role RBAC, supplier-scope enforcement at API boundary |
| System Administration | 11 (FR41-FR51) | User CRUD, xref management, ingestion monitoring, audit log viewer, system config, custom column configuration with activation/deactivation |

**Non-Functional Requirements:**

29 NFRs across 6 quality areas driving architectural decisions:

| Quality Area | NFR Count | Key Constraints |
|-------------|----------|----------------|
| Performance | 7 (NFR1-7) | 3s initial page load, 2s partial updates for 5K PO lines, 2s detail load, 5s Excel gen, 10 concurrent users, 500ms cross-firewall latency budget, 1hr ingestion window |
| Security | 6 (NFR8-13) | Industry-standard password hashing, API-level RBAC enforcement, append-only audit (no app-level delete), read-only ERP credentials, encrypted cross-region channel, 30-min session timeout |
| Reliability | 6 (NFR14-19) | 00:00-18:00 UTC availability, 1hr maintenance window, 95% ingestion success rate, zero audit data loss, 24hr RPO with 4hr restore, retry logic for transient ERP errors |
| Integration | 4 (NFR20-23) | Read-only ERP (no write-back), nightly replication completing within sync window, graceful replication failure handling, xref gap handling without ingestion failure |
| Accessibility | 3 (NFR24-26) | WCAG 2.1 Level A, color+icon+text indicators, keyboard accessible forms |
| Deployability | 3 (NFR27-29) | Single-admin deployable, no container runtime, admin event log within 60s of detection |

**UX Architectural Implications:**

- Django + HTMX server-rendered architecture — no SPA, no client-side framework
- Bootstrap 5 via CDN or static files — no npm build pipeline
- 13 custom components requiring Django template fragments + HTMX attributes
- Three update interaction patterns all using HTMX partial page swaps
- Slide-over detail panel with lazy-loaded sections via HTMX
- Filter preset tabs triggering server-side query changes with HTMX table body swap
- Per-user column visibility preferences persisted across sessions
- Desktop-first responsive design (1280px+ primary, 768px+ secondary)

### Scale & Complexity

- **Primary domain:** Full-stack server-rendered web application
- **Complexity level:** Medium-high
- **User scale:** Single-tenant, 10 max concurrent users (6-7 active), 3 roles
- **Data scale:** 5,000 active PO lines, ~30 suppliers, growing append-only event history
- **Integration scale:** 1 external system (supplier ERP via read-only SQL), nightly batch
- **Deployment scale:** 2 regions (China write, Europe read), Windows-native, no containers

### Technical Constraints & Dependencies

| Constraint | Source | Impact |
|-----------|--------|--------|
| Windows Server infrastructure | STACK.md / organizational | No Linux, no Docker, no container orchestration. IIS as reverse proxy. Windows services for background processes. |
| MS SQL Server (both ERP and app DB) | STACK.md / ERP dependency | ORM must support MS SQL. ERP is read-only SQL connection. App DB is full CRUD. |
| Python ecosystem | STACK.md / organizational | Django or FastAPI as web framework. SQLAlchemy or Django ORM for data access. |
| No container runtime | NFR28 | Must deploy as native Windows services behind IIS. No Docker, no Kubernetes. |
| Single administrator operations | NFR27-28 | Deployment, updates, and monitoring must be manageable by one person. |
| Cross-firewall network | PRD Domain Requirements | China-Europe connectivity via private encrypted channel. Latency budget 500ms (NFR6). |
| Read-only ERP integration | NFR20 | Zero write-back risk. Ingestion is one-directional. |
| Append-only audit storage | NFR10, NFR17 | No application-level UPDATE or DELETE on audit event tables. Zero data loss requirement. |

**Stack Decision to Resolve:**

STACK.md references both FastAPI (section 3.3) and Django+HTMX (section 3.6). The PRD and UX specification consistently reference Django+HTMX as the server-rendered framework. The architecture must resolve this to one of:

1. **Django monolith** — Django handles both server-rendered views (HTMX) and any API endpoints. Django ORM for data access. Simplest for a single developer.
2. **FastAPI API + Django frontend** — Separate API layer and presentation layer. More complex deployment, but clean API separation for future consumers (supplier portal, mobile).
3. **Django + Django REST Framework** — Django monolith with optional DRF API endpoints. Best of both worlds if API consumers are anticipated.

This decision will be addressed in the technology stack step.

### Cross-Cutting Concerns Identified

| Concern | Description | Affected Components |
|---------|-------------|-------------------|
| **Audit event creation** | Every write operation (milestone update, batch create, status change, admin action) must produce an append-only event record with user, timestamp, previous/new values, reason, and source | All write endpoints, ingestion pipeline, admin operations |
| **Role-based access control** | Three roles with supplier-scope scoping for expeditors. Enforced at API/view boundary, not just UI | All views, all API endpoints, query filtering |
| **HTMX response patterns** | Consistent partial HTML fragment rendering for table body swaps, modal content, panel sections, toast notifications | All dynamic views, template architecture |
| **Cross-region data replication** | Primary (China) to secondary (Europe) nightly sync. Failure handling with stale-data fallback and admin alerts | Database layer, deployment topology, monitoring |
| **Custom column handling** | 15 dynamic columns with admin-configurable types, labels, sources, and per-role visibility. Affects queries, templates, forms, and exports | PO list view, PO detail, admin config, Excel generation, ingestion |
| **Error handling & monitoring** | Ingestion failures, replication failures, xref gaps must be logged and surfaced within 60 seconds (NFR29) | Background jobs, admin dashboard, event logging |
| **Session management** | 30-minute inactivity timeout with re-authentication. Must work across HTMX partial requests | Authentication middleware, HTMX error handling |

## Starter Template Evaluation

### Primary Technology Domain

Full-stack server-rendered web application (Django monolith with HTMX progressive enhancement), based on project requirements analysis across PRD, UX specification, STACK.md, and RESEARCH.md.

### Existing Technical Preferences

Strong technical preferences were already documented across project inputs:

- **Language:** Python (STACK.md, PRD)
- **Framework:** Django + HTMX server-rendered (PRD, UX specification — resolves STACK.md's FastAPI/Django ambiguity)
- **Database:** MS SQL Server via `mssql-django` (STACK.md, RESEARCH.md)
- **Frontend:** Bootstrap 5 via CDN, htmx via CDN — no npm build pipeline (UX specification)
- **Deployment:** Windows Server, IIS reverse proxy, NSSM for services (STACK.md, NFR27-29)
- **Containers:** None — no Docker, no Kubernetes (NFR28)
- **Authentication:** Local authentication stored in app DB (PRD FR37-FR40)
- **Background jobs:** Python scripts scheduled via SQL Server Agent (STACK.md)

### Critical Version Constraint

`mssql-django` 1.6 (latest release, Aug 2025) does **not** support Django 6.0. An open GitHub issue (microsoft/mssql-django#483) targets end of March 2026 for Django 6.0 support. The project must use **Django 5.2 LTS** (currently 5.2.11), which provides long-term security support through April 2028 and is the correct choice for production stability.

### Starter Options Considered

| Starter | Version | Fit | Assessment |
|---------|---------|-----|------------|
| **Cookiecutter Django** | 2026.6.6 | Poor | Oriented toward PostgreSQL, Docker, Celery, Heroku/AWS. Includes npm toolchain for Webpack/Gulp. Would require removing more infrastructure than it provides — creates negative value for this project's constraints. |
| **Django+HTMX boilerplates** | Various | Poor | Community starters (e.g., Django_Boilerplate_Free, BaseApp-Django-HTMX-Tailwind) all use Tailwind CSS (requires npm), PostgreSQL, and Linux deployment. None support MS SQL Server. |
| **`django-admin startproject`** | Django 5.2.11 | Best | Clean foundation with zero assumptions about database, deployment platform, or frontend toolchain. Full control over project structure. Add only what's needed. No stripping or overriding required. |

### Selected Starter: `django-admin startproject` (Vanilla Django)

**Rationale for Selection:**

1. **No existing starter matches project constraints** — MS SQL Server + Windows-native + Bootstrap 5 via CDN + no Docker + no npm is an uncommon combination not served by any maintained starter template.
2. **Cookiecutter Django creates negative value** — Stripping PostgreSQL config, Docker files, Celery setup, npm toolchain, and cloud deployment scripts produces more work and confusion than starting clean.
3. **Single-developer simplicity** — A fully understood, minimal foundation is more maintainable than a stripped-down opinionated framework.
4. **Django's built-in scaffolding is sufficient** — `startproject` + `startapp` provides the correct structure for a Django monolith.

**Initialization Command:**

```bash
# Create virtual environment
py -m venv .venv
.venv\Scripts\activate

# Install core dependencies
pip install Django==5.2.11
pip install mssql-django==1.6
pip install django-htmx==1.27.0

# Create project
django-admin startproject po_tracking .
```

### Architectural Decisions Provided by Starter

**Language & Runtime:**
- Python 3.13.x (latest bugfix release compatible with Django 5.2 LTS)
- Django 5.2.11 LTS (long-term support through April 2028)

**Database Backend:**
- `mssql-django` 1.6 (Microsoft's official Django backend for SQL Server)
- Dual database connection configuration: read-only ERP + read-write application DB
- Django ORM as primary data access layer

**Frontend Delivery:**
- Bootstrap 5.3.x via CDN (no build step, no npm)
- htmx 2.0.x via CDN (no build step, no npm)
- `django-htmx` 1.27.0 for server-side HTMX integration (middleware, request attributes)
- Django template engine for all HTML rendering

**Development Tooling:**
- Django's built-in development server (`manage.py runserver`)
- Django's built-in migration framework for schema management
- Django Debug Toolbar for development profiling (optional)

**Code Organization:**
- Django's app-based modular structure via `startapp`
- App boundaries to be defined during architectural decisions step

**Testing Framework:**
- Django's built-in test framework (`unittest`-based)
- `pytest-django` as optional enhancement for fixture ergonomics

**Upgrade Path:**
- Django 6.0 upgrade available once `mssql-django` adds support (expected Q1 2026)
- No architectural changes required for the upgrade — Django LTS-to-next migration path is well-documented

**Note:** Project initialization using this command should be the first implementation story.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Django multi-database routing for dual MS SQL connections (ERP + app DB)
- Custom column implementation approach (15 admin-configurable columns)
- RBAC implementation pattern (3 roles with supplier-scope scoping)
- HTMX response pattern (fragment template strategy)
- WSGI server selection for Windows/IIS deployment

**Important Decisions (Shape Architecture):**
- Session backend and timeout implementation
- Password hashing algorithm
- Excel generation library
- Environment configuration approach
- Django settings organization
- Static file serving strategy
- Logging strategy

**Deferred Decisions (Post-MVP):**
- Caching strategy — add if performance monitoring shows need
- Cross-region replication mechanism — infrastructure decision, not application architecture
- Django 6.0 upgrade — blocked by `mssql-django` support timeline

### Data Architecture

**DA-1: Django Multi-Database Routing**
- **Decision:** Custom `DatabaseRouter` class
- **Rationale:** Django's native multi-database support routes ERP models to a read-only connection and all app models to the default read-write connection. Standard, well-documented pattern.
- **Configuration:** Two entries in `DATABASES` setting — `default` (app DB, read-write) and `erp` (supplier ERP, read-only). Router enforces `db_for_read` only on ERP models; blocks `db_for_write`, `allow_migrate`, and `allow_relation` for the ERP connection.
- **Affects:** All ERP ingestion models, database configuration, migration strategy.

**DA-2: Custom Column Implementation**
- **Decision:** Physical pre-created columns on `po_line` table
- **Rationale:** The PRD specifies exactly 15 columns with known types (5 date, 5 text, 5 decimal). Pre-created nullable columns (`custom_date_1` through `custom_date_5`, `custom_text_1` through `custom_text_5`, `custom_decimal_1` through `custom_decimal_5`) are simplest to query, filter, sort, index, and export. No schema changes at runtime. Admin configures labels, visibility, and source mapping via a `CustomColumnConfig` model.
- **Alternatives rejected:** EAV pattern (complex joins, poor filter/sort performance), JSON field (weak MS SQL JSON support, complex filtering).
- **Affects:** PO list view queries, column chooser, admin configuration, Excel export, ingestion pipeline.

**DA-3: Caching Strategy**
- **Decision:** No caching initially; Django's cache framework (database backend) as documented upgrade path
- **Rationale:** For 10 concurrent users and 5,000 PO lines, properly indexed MS SQL queries should meet NFR1 (3s initial load) and NFR2 (2s partial updates) without caching. Adding caching prematurely increases complexity. If performance monitoring shows need, Django's database-backed cache can be added without architectural changes.
- **Affects:** Performance tuning, future optimization.

### Authentication & Security

**AS-1: Password Hashing**
- **Decision:** PBKDF2 (Django default)
- **Version:** Django 5.2's built-in `PBKDF2PasswordHasher` with SHA-256
- **Rationale:** Zero extra dependencies, meets NFR8 (industry-standard hashing), and Django's implementation is well-hardened with automatic iteration count increases. For 10 users, the marginal security benefit of Argon2 doesn't justify the added C-extension dependency on Windows.
- **Affects:** User model, authentication backend.

**AS-2: Session Backend**
- **Decision:** Database-backed sessions (`django.contrib.sessions.backends.db`)
- **Rationale:** Sessions stored in MS SQL app database. Reliable across multiple Waitress workers, supports forced logout/invalidation, auditable, and handles the 30-minute inactivity timeout (NFR12) via `SESSION_COOKIE_AGE` + `SESSION_SAVE_EVERY_REQUEST`.
- **Configuration:** `SESSION_COOKIE_AGE = 1800` (30 minutes), `SESSION_SAVE_EVERY_REQUEST = True` (reset timeout on every request including HTMX partials).
- **Affects:** Authentication middleware, HTMX request handling, session table in app DB.

**AS-3: RBAC Implementation**
- **Decision:** Custom role field on User model + role-checking decorators + scoped querysets
- **Rationale:** With only 3 fixed roles (Admin, Planner, Expeditor), Django's full Groups/Permissions system is unnecessary overhead. A `role` CharField on the User model + `@role_required('admin', 'planner')` decorator + `get_scoped_queryset(user)` method provides explicit, readable access control. Supplier-scope filtering for Expeditors is implemented as a queryset method that filters by `supplier_id` when the user's role is Expeditor.
- **Pattern:** Custom `AbstractUser` subclass with `role` field and `supplier` ForeignKey (nullable, only populated for Expeditor role).
- **Affects:** All views, all API endpoints, query filtering, admin operations.

**AS-4: CSRF Protection with HTMX**
- **Decision:** Django CSRF via cookie + HTMX `hx-headers` configuration
- **Rationale:** `django-htmx` middleware handles HTMX-specific request detection. A `<meta>` tag with the CSRF token in the base template + HTMX `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` on `<body>` ensures all HTMX requests include the token. Standard, well-documented pattern.
- **Affects:** Base template, HTMX configuration, all POST/PUT/DELETE requests.

### API & Communication Patterns

**AC-1: HTMX Response Pattern**
- **Decision:** Dedicated fragment templates with `request.htmx` detection
- **Rationale:** Separate template files for each HTMX partial (e.g., `po/_table_body.html`, `po/_detail_panel.html`, `po/_timeline.html`). Views check `request.htmx` to return fragments for HTMX requests or full pages for standard navigation. Clearer separation of concerns, easier to test independently, and aligns with the UX spec's 13 custom components.
- **Convention:** Fragment templates prefixed with underscore (e.g., `_table_body.html`). Full-page templates include fragments via `{% include %}`.
- **Affects:** All dynamic views, template directory structure, component architecture.

**AC-2: HTMX Error Handling**
- **Decision:** Server-side error detection + toast notification pattern
- **Rationale:** HTMX requests that fail (4xx, 5xx) trigger a `HX-Trigger` response header that fires a client-side toast notification. Session expiry (401) triggers a full-page redirect to login via `HX-Redirect`. Validation errors return the form fragment with inline error messages.
- **Pattern:** Custom Django middleware detects HTMX errors and sets appropriate `HX-Trigger` or `HX-Redirect` headers.
- **Affects:** Error middleware, base template toast container, authentication flow.

**AC-3: Excel Generation**
- **Decision:** `openpyxl`
- **Rationale:** Supports both read and write operations (useful for template-based generation), well-maintained, handles the structured supplier communication templates described in FR34-FR36. Formatting, styles, and cell-level control are all supported.
- **Affects:** Supplier communication feature, Excel download endpoints.

**AC-4: Cross-Region Replication**
- **Decision:** SQL Server log shipping (infrastructure-level, not application-level)
- **Rationale:** This is a DBA/infrastructure decision, not an application concern. SQL Server log shipping is the simplest native option for nightly China-to-Europe sync. Requires no application code — the European instance uses a read-only connection string. Application detects stale data via a `last_sync_timestamp` check and displays a staleness indicator (per UX spec component).
- **Application responsibility:** Read-only database connection for European deployment, staleness detection query, admin alert on sync failure.
- **Affects:** Deployment topology, database configuration, admin monitoring dashboard.

### Frontend Architecture

**FA-1: JavaScript Approach**
- **Decision:** Vanilla JavaScript only (no Alpine.js)
- **Rationale:** The UX spec's 13 components are primarily HTMX-driven server interactions. Bootstrap 5's built-in JavaScript handles dropdowns, modals, tooltips, and collapse. The few client-side interactions (column chooser drag, inline edit activation) can be handled with small vanilla JS utility functions. Adding Alpine.js introduces another dependency for minimal benefit.
- **Affects:** Template architecture, component implementation, dependency management.

**FA-2: Static File Serving**
- **Decision:** Django `staticfiles` app + IIS static file serving in production
- **Rationale:** Standard Django pattern. `manage.py collectstatic` gathers all static files into a single directory. In development, Django's dev server serves them. In production, IIS serves the collected static directory directly — no additional Python middleware needed. IIS is already the reverse proxy, so this adds zero infrastructure complexity.
- **Configuration:** `STATIC_ROOT` for collected files, `STATIC_URL` for URL prefix, IIS virtual directory for static serving.
- **Affects:** IIS configuration, deployment scripts, development workflow.

### Infrastructure & Deployment

**ID-1: WSGI Server**
- **Decision:** Waitress
- **Rationale:** Pure Python WSGI server that works natively on Windows without C extensions. Production-grade, handles concurrent requests via thread pool, simple to run as a Windows service via NSSM. The project is fully synchronous (no WebSocket, no streaming), so WSGI is the correct protocol. STACK.md's Uvicorn reference was for the FastAPI option — not applicable to the Django architecture.
- **Configuration:** `waitress-serve --port=8000 po_tracking.wsgi:application`, wrapped as Windows service via NSSM.
- **Affects:** Production deployment, IIS reverse proxy configuration, Windows service setup.

**ID-2: Environment Configuration**
- **Decision:** `django-environ`
- **Rationale:** Clean separation of configuration from code. `.env` file support for development, environment variables for production. Typed parsing for database URLs, boolean flags, and integer values. Well-maintained, widely used in Django projects.
- **Configuration:** `.env` file in project root (gitignored), `environ.Env()` in settings files.
- **Affects:** All settings files, deployment configuration, secrets management.

**ID-3: Logging Strategy**
- **Decision:** Django's built-in logging (Python `logging` module) to file + audit event table for admin-visible events
- **Rationale:** Two-layer approach: (1) File-based logging for developer/ops debugging using Django's `LOGGING` configuration — rotating file handler, structured format, log level per module. (2) Append-only audit event table for admin-visible events (ingestion results, replication status, user actions) — this meets NFR29's 60-second detection requirement by writing events to the database in real-time. No additional dependency needed.
- **Affects:** Settings configuration, admin monitoring dashboard, background job scripts.

**ID-4: Django Settings Organization**
- **Decision:** Split settings (`base.py`, `development.py`, `production.py`, `production_eu.py`)
- **Rationale:** With dual-region deployment (China primary, Europe read-only secondary) plus development, separate settings files for each environment prevent configuration errors. `base.py` contains shared configuration, environment-specific files override database connections, debug flags, allowed hosts, and static file paths.
- **File structure:** `po_tracking/settings/base.py`, `development.py`, `production.py`, `production_eu.py`, `__init__.py`
- **Affects:** Project structure, deployment scripts, WSGI configuration.

### Decision Impact Analysis

**Implementation Sequence:**
1. Project initialization (starter command + split settings + `django-environ`)
2. Dual-database configuration (app DB + ERP connection + database router)
3. Custom User model + RBAC (role field, supplier FK, decorators, session backend)
4. HTMX fragment pattern (base templates, fragment naming convention, CSRF config)
5. Core models (PO line with physical custom columns, events, batches)
6. Ingestion pipeline (background job + database router + ERP models)
7. Excel generation (`openpyxl`), static files (IIS config), logging
8. Cross-region deployment (SQL Server log shipping, European settings, staleness detection)

**Cross-Component Dependencies:**
- Database router must be configured before any ERP model access
- Custom User model must be defined before first migration (Django requirement)
- RBAC decorators must exist before any view is protected
- HTMX fragment pattern must be established before building any interactive views
- Custom column physical schema must be in initial migration (altering later requires careful migration)
- Split settings must be in place before any environment-specific configuration

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:** 12 areas where AI agents could make incompatible choices if not specified, spanning naming, structure, format, communication, and process patterns.

### Naming Patterns

**Database Naming Conventions:**
- Table naming: Django default — `{app_label}_{model_name}` lowercase (e.g., `po_poline`, `accounts_user`). Do not override `db_table` unless interfacing with existing ERP tables.
- Column naming: `snake_case` (Django default). Foreign keys suffixed with `_id` (e.g., `supplier_id`, `created_by_id`).
- Custom column fields: `custom_date_1` through `custom_date_5`, `custom_text_1` through `custom_text_5`, `custom_decimal_1` through `custom_decimal_5`.
- Index naming: Django auto-generated. Only specify explicit names for multi-column indexes: `ix_{table}_{col1}_{col2}`.
- ERP snapshot tables: Prefixed with `erp_` (e.g., `erp_snapshot`, `erp_change_event`).

**URL Pattern Naming Conventions:**
- URL names: `{app}:{action}` namespaced (e.g., `po:list`, `po:detail`, `po:update-milestone`, `accounts:login`).
- URL paths: lowercase, hyphenated (e.g., `/po/`, `/po/<int:pk>/detail/`, `/po/bulk-update/`, `/admin-portal/users/`).
- HTMX fragment endpoints: same path as parent or nested path (e.g., `/po/<int:pk>/timeline/` returns timeline fragment).

**Template File Naming Conventions:**
- Full page templates: `{model}_{action}.html` (e.g., `po_list.html`, `po_detail.html`).
- HTMX fragment templates: prefixed with underscore: `_{fragment_name}.html` (e.g., `_table_body.html`, `_timeline.html`, `_milestone_modal.html`).
- Shared partials: `_partials/{name}.html` (e.g., `_partials/_toast.html`, `_partials/_pagination.html`).

**Python Code Naming Conventions:**
- Classes: `PascalCase` (e.g., `POLine`, `AuditEvent`, `MilestoneUpdateView`).
- Functions/methods: `snake_case` (e.g., `get_scoped_queryset`, `run_ingestion`).
- Constants: `UPPER_SNAKE_CASE` (e.g., `STATUS_CHOICES`, `ROLE_ADMIN`).
- Django views: class-based where appropriate, suffixed with `View` (e.g., `POListView`, `MilestoneUpdateView`). Function-based views for simple HTMX fragments.
- Django forms: suffixed with `Form` (e.g., `MilestoneUpdateForm`, `BatchCreateForm`).

### Structure Patterns

**Django App Organization:**
- `accounts/` — User model, authentication, RBAC decorators, login/logout views
- `po/` — PO line model, list/detail/update views, HTMX fragments, filter presets
- `ingestion/` — ERP models, snapshot/diff engine, change event generation, database router
- `batches/` — Batch model, batch lifecycle, batch creation views
- `audit/` — Audit event model, timeline views, audit log viewer
- `admin_portal/` — User CRUD, xref management, ingestion monitoring, system config, custom column config
- `exports/` — Excel generation, supplier communication templates
- `core/` — Shared utilities, base models, template tags, middleware, decorators

**Template Directory Structure:**
```
templates/
├── base.html                    # Full page base with Bootstrap + HTMX CDN links
├── base_auth.html               # Base for login/unauthenticated pages
├── _partials/
│   ├── _toast.html              # Toast notification container
│   ├── _pagination.html         # Reusable pagination fragment
│   ├── _confirm_modal.html      # Reusable confirmation dialog
│   └── _loading_spinner.html    # HTMX loading indicator
├── accounts/
│   ├── login.html
│   └── ...
├── po/
│   ├── po_list.html             # Full page
│   ├── _table_body.html         # HTMX fragment: table rows
│   ├── _detail_panel.html       # HTMX fragment: slide-over panel
│   ├── _timeline.html           # HTMX fragment: audit timeline
│   ├── _milestone_modal.html    # HTMX fragment: update modal
│   └── ...
└── ...
```

**Test Organization:**
- Tests inside each app: `{app}/tests/` directory with `__init__.py`.
- Test file naming: `test_{module}.py` (e.g., `po/tests/test_models.py`, `po/tests/test_views.py`).
- Factory pattern: `{app}/tests/factories.py` using `factory_boy` or manual factory functions.
- Fixtures: `{app}/fixtures/` for JSON test data if needed.

### Format Patterns

**HTMX Response Conventions:**
- Standard navigation (non-HTMX): Return full HTML page via `render(request, 'po/po_list.html', context)`.
- HTMX request (partial): Return fragment via `render(request, 'po/_table_body.html', context)`.
- Detection pattern in every view that serves both:
  ```python
  template = 'po/_table_body.html' if request.htmx else 'po/po_list.html'
  return render(request, template, context)
  ```
- Success feedback: Set `HX-Trigger: showToast` header with JSON payload `{"message": "...", "level": "success"}`.
- Validation error: Return form fragment (HTTP 200) with inline error messages rendered.
- Server error: Return HTTP 500 with error fragment or trigger toast.
- Session expiry: Return HTTP 200 with `HX-Redirect: /accounts/login/` header.

**Audit Event Structure:**
Every write operation creates an audit event with this consistent structure:
- `event_type`: String enum (e.g., `milestone_updated`, `batch_created`, `status_changed`, `ingestion_completed`).
- `po_line_id`: FK to the affected PO line (nullable for system events).
- `user_id`: FK to the user who performed the action (nullable for ingestion/system).
- `source`: String enum (`manual`, `bulk`, `inline`, `ingestion`, `system`).
- `timestamp`: UTC datetime, auto-set on creation.
- `previous_values`: JSON — serialized dict of changed fields' old values.
- `new_values`: JSON — serialized dict of changed fields' new values.
- `reason`: Optional text — user-provided reason for change (when applicable).

**Date/Time Handling:**
- Storage: UTC in database for all timestamps.
- Display: Server-side formatting in Django templates using `|date:"Y-m-d"` and `|time:"H:i"` filters.
- User timezone: Not required (single-timezone operations per region — China or Europe).
- Date fields on PO lines (milestones, readiness dates): Date only (no time component), stored as `DateField`.

**Null Value Display:**
- Empty text: Display `—` (em dash).
- Empty date: Display `—`.
- Empty number: Display `—`.
- Zero quantity: Display `0` (zero is meaningful, not null).

### Communication Patterns

**HTMX Event/Trigger Naming:**
- Toast notifications: `showToast` (triggered via `HX-Trigger` response header).
- Table refresh: `refreshTable` (triggered after successful updates to reload table body).
- Panel close: `closePanel` (triggered to dismiss slide-over detail panel).
- Modal close: `closeModal` (triggered after successful form submission).
- Custom events follow `camelCase` convention (matching HTMX conventions).

**Django Signal Usage:**
- Do NOT use Django signals for business logic. Signals create hidden coupling that is difficult for AI agents to trace.
- Use explicit function calls for audit event creation (e.g., `create_audit_event(...)` called directly in the view/service).
- Signals are acceptable only for framework-level hooks (e.g., `post_save` for cache invalidation if caching is added later).

### Process Patterns

**View Authorization Pattern:**
Every view must check authorization before processing:
```python
@login_required
@role_required('admin', 'planner')
def milestone_update_view(request, pk):
    po_line = get_object_or_404(POLine.objects.for_user(request.user), pk=pk)
    ...
```
- `@login_required` first (Django built-in).
- `@role_required(...)` second (custom decorator checking `request.user.role`).
- Queryset scoping via `.for_user(user)` custom manager method (returns supplier-filtered queryset for Expeditors, full queryset for others).

**Form Validation Pattern:**
- Use Django forms/model forms for all user input validation.
- Validate in the view: `if form.is_valid(): ...`
- On validation failure: Return the form fragment with errors (HTMX swaps in the form with inline error messages).
- On success: Perform action, create audit event, return success response with `HX-Trigger`.

**Loading State Pattern:**
- HTMX provides loading indicators natively via `hx-indicator`.
- Standard indicator: A spinner element with class `htmx-indicator` placed next to the trigger element.
- Table loading: The table body gets an `htmx-indicator` spinner overlay during reload.
- Button loading: Submit buttons get `disabled` attribute + spinner during request via HTMX's CSS class toggling.

**Error Recovery Pattern:**
- Transient errors (network timeout on HTMX request): Client-side retry is NOT implemented. User sees error toast and manually retries.
- Ingestion errors: Logged to audit event table + file log. Admin dashboard shows ingestion status. Retry is manual (re-run SQL Server Agent job).
- Database connection errors: Django's `CONN_MAX_AGE` handles reconnection. Log the error.

### Enforcement Guidelines

**All AI Agents MUST:**
1. Follow the template naming convention (underscore prefix for fragments, app-namespaced directories).
2. Use `request.htmx` to detect HTMX requests — never inspect raw headers.
3. Create audit events for every write operation using the explicit `create_audit_event()` function — never via Django signals.
4. Scope all querysets through `.for_user(request.user)` to enforce RBAC — never trust client-side role checks alone.
5. Return HTMX fragments with appropriate `HX-Trigger` headers for toast notifications — never return bare text responses.
6. Use Django forms for all user input — never parse `request.POST` directly.

**Anti-Patterns (MUST NOT):**
- Do NOT use Django signals for business logic or audit event creation.
- Do NOT bypass `@role_required` by checking roles inline in views.
- Do NOT return full HTML pages for HTMX requests (swap target mismatch).
- Do NOT use JavaScript for data fetching — all data flows through HTMX server interactions.
- Do NOT use `raw()` SQL queries unless absolutely necessary (ERP ingestion queries are the exception).
- Do NOT create model instances without corresponding audit events for user-facing operations.

## Project Structure & Boundaries

### Complete Project Directory Structure

```
po_tracking/                          # Project root (repository root)
├── .env.example                      # Example environment variables
├── .gitignore                        # Git ignore rules
├── manage.py                         # Django management entry point
├── requirements/
│   ├── base.txt                      # Shared dependencies
│   ├── development.txt               # Dev-only dependencies (Debug Toolbar, etc.)
│   └── production.txt                # Production-only dependencies
├── po_tracking/                      # Django project package
│   ├── __init__.py
│   ├── wsgi.py                       # WSGI entry point (Waitress serves this)
│   ├── urls.py                       # Root URL configuration
│   └── settings/
│       ├── __init__.py               # Imports from environment-specific module
│       ├── base.py                   # Shared settings (apps, middleware, templates, etc.)
│       ├── development.py            # DEBUG=True, local DB, dev tools
│       ├── production.py             # China primary (read-write app DB + ERP)
│       └── production_eu.py          # Europe secondary (read-only app DB, no ERP)
├── apps/
│   ├── __init__.py
│   ├── core/                         # Shared utilities & cross-cutting concerns
│   │   ├── __init__.py
│   │   ├── middleware.py             # HTMX error handling, session timeout, staleness detection
│   │   ├── decorators.py            # @role_required, @audit_action
│   │   ├── mixins.py                # RoleRequiredMixin, ScopedQuerysetMixin
│   │   ├── services.py              # create_audit_event(), shared service functions
│   │   ├── templatetags/
│   │   │   ├── __init__.py
│   │   │   └── core_tags.py         # Custom template tags (null display, badge rendering)
│   │   ├── constants.py             # Role constants, status choices, event type enums
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_decorators.py
│   │       ├── test_middleware.py
│   │       └── test_services.py
│   ├── accounts/                     # User & access management
│   │   ├── __init__.py
│   │   ├── models.py               # Custom User model (role, supplier FK)
│   │   ├── forms.py                # LoginForm, PasswordChangeForm
│   │   ├── views.py                # Login, logout, password change views
│   │   ├── urls.py                 # /accounts/ URL patterns
│   │   ├── admin.py                # Django admin registration
│   │   ├── managers.py             # Custom UserManager
│   │   ├── backends.py             # Authentication backend
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       └── factories.py
│   ├── po/                           # PO visibility, navigation, detail, milestones
│   │   ├── __init__.py
│   │   ├── models.py               # POLine, Supplier, CustomColumnConfig
│   │   ├── forms.py                # MilestoneUpdateForm, BulkUpdateForm, InlineEditForm
│   │   ├── views.py                # POListView, detail panel, milestone update, bulk update
│   │   ├── urls.py                 # /po/ URL patterns
│   │   ├── filters.py             # Filter preset logic, column filtering, supplier filter
│   │   ├── managers.py             # POLineManager with .for_user() scoping
│   │   ├── admin.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       ├── test_filters.py
│   │       └── factories.py
│   ├── batches/                      # Batch tracking & lifecycle
│   │   ├── __init__.py
│   │   ├── models.py               # Batch, BatchLine
│   │   ├── forms.py                # BatchCreateForm, BatchUpdateForm
│   │   ├── views.py                # Batch CRUD views, batch list fragment
│   │   ├── urls.py                 # /batches/ URL patterns
│   │   ├── services.py             # Batch lifecycle logic, quantity allocation
│   │   ├── admin.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       ├── test_services.py
│   │       └── factories.py
│   ├── audit/                        # Audit events & timeline
│   │   ├── __init__.py
│   │   ├── models.py               # AuditEvent (append-only)
│   │   ├── views.py                # Timeline fragment, audit log viewer
│   │   ├── urls.py                 # /audit/ URL patterns
│   │   ├── managers.py             # AuditEventManager (no delete/update)
│   │   ├── admin.py                # Read-only admin view
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       └── test_views.py
│   ├── ingestion/                    # ERP data ingestion & synchronization
│   │   ├── __init__.py
│   │   ├── models.py               # ERPSnapshot, ERPChangeEvent, ItemXref
│   │   ├── router.py               # DatabaseRouter for ERP connection
│   │   ├── erp_models.py           # Unmanaged Django models for ERP read-only tables
│   │   ├── snapshot.py             # Snapshot extraction from ERP
│   │   ├── diff_engine.py          # Snapshot comparison, change event generation
│   │   ├── batch_reconstruction.py # Historical batch reconstruction from DeliveredQty/InDate
│   │   ├── custom_columns.py       # Custom column ingestion from ERP sources
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── run_ingestion.py # Django management command for nightly ingestion
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_snapshot.py
│   │       ├── test_diff_engine.py
│   │       ├── test_batch_reconstruction.py
│   │       └── factories.py
│   ├── admin_portal/                 # System administration
│   │   ├── __init__.py
│   │   ├── views.py                # User CRUD, xref management, ingestion monitoring,
│   │   │                           # system config, custom column config, audit log viewer
│   │   ├── forms.py                # UserCreateForm, UserEditForm, XrefForm,
│   │   │                           # CustomColumnConfigForm, SystemConfigForm
│   │   ├── urls.py                 # /admin-portal/ URL patterns
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_views.py
│   │       └── factories.py
│   └── exports/                      # Excel generation & supplier communication
│       ├── __init__.py
│       ├── views.py                # Excel download endpoint
│       ├── generators.py           # openpyxl-based Excel file generators
│       ├── templates_xl/           # Excel template definitions (column mappings, styles)
│       ├── urls.py                 # /exports/ URL patterns
│       └── tests/
│           ├── __init__.py
│           ├── test_generators.py
│           └── test_views.py
├── templates/                        # Project-level Django templates
│   ├── base.html                    # Full page base: Bootstrap 5 + htmx CDN, navbar, toast container
│   ├── base_auth.html               # Base for unauthenticated pages (login)
│   ├── _partials/
│   │   ├── _toast.html              # Toast notification container + JS listener
│   │   ├── _pagination.html         # Reusable pagination fragment
│   │   ├── _confirm_modal.html      # Reusable confirmation dialog
│   │   ├── _loading_spinner.html    # HTMX loading indicator overlay
│   │   └── _staleness_banner.html   # Stale data warning for European instance
│   ├── accounts/
│   │   ├── login.html
│   │   └── password_change.html
│   ├── po/
│   │   ├── po_list.html             # Full page: PO list with filter presets, column chooser
│   │   ├── _table_body.html         # Fragment: table rows (swapped on filter/sort/page)
│   │   ├── _table_header.html       # Fragment: table header (swapped on column change)
│   │   ├── _detail_panel.html       # Fragment: slide-over detail panel shell
│   │   ├── _timeline.html           # Fragment: audit timeline in detail panel
│   │   ├── _batch_list.html         # Fragment: batch list in detail panel
│   │   ├── _status_history.html     # Fragment: status history in detail panel
│   │   ├── _milestone_modal.html    # Fragment: single PO milestone update modal
│   │   ├── _bulk_update_bar.html    # Fragment: bulk action bar
│   │   ├── _inline_edit_row.html    # Fragment: inline edit mode for a table row
│   │   └── _column_chooser.html     # Fragment: column visibility chooser
│   ├── batches/
│   │   ├── _batch_create_form.html  # Fragment: batch creation form
│   │   └── _batch_detail.html       # Fragment: batch detail view
│   ├── admin_portal/
│   │   ├── dashboard.html           # Full page: admin dashboard
│   │   ├── user_list.html           # Full page: user management
│   │   ├── _user_form.html          # Fragment: user create/edit form
│   │   ├── xref_list.html           # Full page: item xref management
│   │   ├── _xref_form.html          # Fragment: xref create/edit form
│   │   ├── ingestion_monitor.html   # Full page: ingestion status & history
│   │   ├── audit_log.html           # Full page: system audit log viewer
│   │   ├── custom_columns.html      # Full page: custom column configuration
│   │   ├── _custom_column_form.html # Fragment: custom column config form
│   │   └── system_config.html       # Full page: system configuration
│   ├── exports/
│   │   └── _export_options.html     # Fragment: export format/filter options
│   └── audit/
│       └── _audit_log_table.html    # Fragment: audit log table body
├── static/
│   ├── css/
│   │   └── custom.css              # Custom Bootstrap overrides, component styles (~500 lines)
│   ├── js/
│   │   ├── htmx-config.js         # HTMX global configuration (CSRF, error handling)
│   │   ├── toast.js                # Toast notification listener
│   │   ├── column-chooser.js       # Column visibility persistence
│   │   └── inline-edit.js          # Inline edit activation/deactivation
│   └── img/
│       └── logo.svg                # Application logo
├── scripts/
│   ├── install_service.bat         # NSSM service installation script (Waitress)
│   ├── run_ingestion.bat           # Wrapper for SQL Server Agent to call Django management command
│   └── collect_static.bat          # Static file collection for deployment
└── docs/
    └── deployment.md               # IIS configuration, NSSM setup, SQL Server Agent job setup
```

### Architectural Boundaries

**View Layer Boundary (HTTP/HTMX):**
- All user interaction flows through Django views in each app's `views.py`.
- Views handle: request parsing, authentication/authorization checks, form validation, calling service functions, rendering templates.
- Views do NOT contain: business logic, direct ORM queries beyond simple lookups, audit event creation logic.

**Service Layer Boundary:**
- Business logic lives in `services.py` within each app (or `core/services.py` for shared functions).
- Services handle: complex business operations, audit event creation via `create_audit_event()`, multi-model transactions.
- Services do NOT handle: HTTP concerns, template rendering, authentication checks.

**Data Access Boundary:**
- Django ORM models and custom managers handle all data access.
- `.for_user(user)` queryset method on all user-facing models enforces RBAC at the data layer.
- ERP connection is isolated via `DatabaseRouter` — only `ingestion/erp_models.py` accesses the ERP database.
- Append-only enforcement on `AuditEvent`: custom manager overrides `delete()` and `update()` to raise exceptions.

**Template Boundary:**
- Full page templates include fragments via `{% include %}`.
- HTMX endpoints return only fragments — never full pages.
- Template tags in `core/templatetags/` provide shared rendering logic (badges, null display, date formatting).
- No business logic in templates — only display logic and HTMX attributes.

### Requirements to Structure Mapping

| FR Capability Area | Django App(s) | Key Files |
|---|---|---|
| Data Ingestion & Synchronization (FR1-FR8c) | `ingestion/` | `snapshot.py`, `diff_engine.py`, `batch_reconstruction.py`, `custom_columns.py`, `management/commands/run_ingestion.py` |
| PO Visibility & Navigation (FR9-FR17e) | `po/` | `views.py` (POListView), `filters.py`, `_table_body.html`, `_column_chooser.html` |
| PO Investigation & Detail (FR18-FR21) | `po/`, `audit/` | `_detail_panel.html`, `_timeline.html`, `_batch_list.html`, `_status_history.html` |
| Milestone & Status Management (FR22-FR28) | `po/` | `forms.py`, `_milestone_modal.html`, `_bulk_update_bar.html`, `_inline_edit_row.html` |
| Batch Tracking (FR29-FR33) | `batches/` | `models.py`, `services.py`, `_batch_create_form.html`, `_batch_detail.html` |
| Supplier Communication (FR34-FR36) | `exports/` | `generators.py`, `views.py` |
| User & Access Management (FR37-FR40) | `accounts/`, `core/` | `models.py`, `decorators.py`, `views.py` |
| System Administration (FR41-FR51) | `admin_portal/` | `views.py`, `forms.py`, all admin template files |

**Cross-Cutting Concerns Mapping:**

| Concern | Location |
|---|---|
| Audit event creation | `core/services.py` → `create_audit_event()` |
| RBAC enforcement | `core/decorators.py` → `@role_required`, `core/mixins.py` → `ScopedQuerysetMixin` |
| HTMX error handling | `core/middleware.py` → `HtmxErrorMiddleware` |
| Session timeout | `core/middleware.py` → `SessionTimeoutMiddleware` |
| Staleness detection | `core/middleware.py` → `StalenessMiddleware` (Europe only) |
| Custom column rendering | `core/templatetags/core_tags.py` → custom column display tags |
| Toast notifications | `templates/_partials/_toast.html` + `static/js/toast.js` |

### Integration Points

**Internal Communication:**
- Views call service functions directly (no message queue, no async).
- Service functions call model managers for data access.
- Template tags provide reusable rendering across apps.
- HTMX events (`HX-Trigger`) coordinate client-side UI updates (toast, table refresh, panel close).

**External Integrations:**
- Supplier ERP (MS SQL, read-only): Accessed via `ingestion/erp_models.py` through `DatabaseRouter`. Nightly batch job only — no real-time connection.
- SQL Server Agent: Triggers `run_ingestion.bat` → `manage.py run_ingestion` on schedule.

**Data Flow:**

```
Supplier ERP (MS SQL, read-only)
    │
    ▼
ingestion/snapshot.py ──→ ingestion/diff_engine.py ──→ audit/models.py (AuditEvent)
    │                          │
    ▼                          ▼
ingestion/models.py        po/models.py (POLine updated)
(ERPSnapshot,              batches/models.py (Batch reconstructed)
 ERPChangeEvent)


User Browser (Bootstrap 5 + htmx 2.0)
    │ HTMX partial requests
    ▼
po/views.py ──→ po/filters.py ──→ po/managers.py (.for_user()) ──→ App DB (MS SQL)
    │                                                                    │
    ▼                                                                    ▼
templates/po/_table_body.html                              audit/models.py (AuditEvent)
    │
    ▼
HX-Trigger: showToast ──→ static/js/toast.js ──→ Toast notification displayed
```

### Development Workflow Integration

**Development Server:**
```bash
# Activate virtual environment and start dev server
.venv\Scripts\activate
set DJANGO_SETTINGS_MODULE=po_tracking.settings.development
py manage.py migrate
py manage.py runserver
```

**Production Deployment (China Primary):**
```bash
# Collect static files for IIS serving
py manage.py collectstatic --noinput
# Waitress managed by NSSM as Windows service
waitress-serve --port=8000 --threads=4 po_tracking.wsgi:application
```

**Ingestion Job (SQL Server Agent):**
```bash
# Called by SQL Server Agent scheduled job nightly
.venv\Scripts\python.exe manage.py run_ingestion --settings=po_tracking.settings.production
```

## Architecture Validation Results

### Coherence Validation

**Decision Compatibility:** All technology choices verified compatible:
- Django 5.2.11 LTS + `mssql-django` 1.6 + Python 3.13.x — confirmed compatible
- `django-htmx` 1.27.0 supports Django 4.2 through 6.0 — compatible with Django 5.2
- htmx 2.0.x (CDN) + `django-htmx` middleware — standard pairing
- Bootstrap 5.3.x (CDN) + Django templates — no conflicts
- Waitress (WSGI) + Django 5.2 — correct protocol match
- `openpyxl` + Python 3.13 — fully compatible
- `django-environ` + split settings — standard Django pattern
- No version conflicts or incompatibilities detected.

**Pattern Consistency:** No contradictions found:
- Naming conventions follow Python/Django standards consistently
- HTMX fragment pattern aligns with `request.htmx` detection
- Audit event structure used consistently by all write operations
- RBAC pattern applied uniformly across all apps

**Structure Alignment:** Project structure fully supports all decisions:
- 8 Django apps map cleanly to 8 FR capability areas
- `core/` app houses all cross-cutting concerns
- Template directory mirrors app structure with clear fragment naming
- Split settings accommodate 3 deployment environments

### Requirements Coverage Validation

**Functional Requirements Coverage — All 51 FRs Supported:**

| FR Range | Count | Architectural Support |
|----------|-------|----------------------|
| FR1-FR8c | 11 | `ingestion/` app: snapshot, diff engine, batch reconstruction, custom column ingestion, ERP models, database router, management command. FR8 replication via SQL Server log shipping. |
| FR9-FR17e | 13 | `po/` app: POListView, filters, scoped managers, column chooser, per-user prefs. Physical custom columns on POLine model. |
| FR18-FR21 | 4 | `po/` + `audit/` apps: detail panel, timeline, batch list, status history. Lazy-loaded HTMX sections. |
| FR22-FR28 | 10 | `po/` app: milestone forms (single/bulk/inline), append-only audit via create_audit_event(), status lifecycle model. |
| FR29-FR33 | 5 | `batches/` app: Batch/BatchLine models, lifecycle services, historical reconstruction. |
| FR34-FR36 | 3 | `exports/` app: openpyxl generators, download endpoint. |
| FR37-FR40 | 4 | `accounts/` + `core/` apps: custom User model, @role_required, .for_user() scoping, API-boundary enforcement. |
| FR41-FR51 | 11 | `admin_portal/` app: user CRUD, xref management, ingestion monitoring, audit log viewer, system config, custom column config. |

**Non-Functional Requirements Coverage — All 29 NFRs Addressed:**

| NFR Range | Count | Architectural Support |
|-----------|-------|----------------------|
| NFR1-NFR7 | 7 | HTMX partial rendering, server-side filtering, indexed queries, Waitress thread pool, European read-only instance, management command pipeline. |
| NFR8-NFR13 | 6 | PBKDF2 hashing, @role_required + .for_user(), append-only AuditEvent manager, read-only DatabaseRouter, infrastructure-level encryption, database-backed sessions with 30min timeout. |
| NFR14-NFR19 | 6 | NSSM Windows service auto-start, deployment scripts, ingestion retry logic, append-only + MS SQL durability, backup strategy, management command error handling. |
| NFR20-NFR23 | 4 | DatabaseRouter write-blocking, SQL Server log shipping, StalenessMiddleware + banner, xref gap flagging without ingestion failure. |
| NFR24-NFR26 | 3 | Bootstrap 5 semantic HTML, UX spec color+icon+text badges, keyboard-accessible form components. |
| NFR27-NFR29 | 3 | Single-admin scripts, no Docker (Waitress+NSSM+IIS), real-time audit event writes for 60s detection. |

### Implementation Readiness Validation

**Decision Completeness:** 16 architectural decisions documented with versions, rationale, and affected components. No open decisions remain for MVP.

**Structure Completeness:** Complete directory tree with ~80 files across 8 Django apps, 13 template directories, static assets, deployment scripts, and configuration files.

**Pattern Completeness:** 12 conflict points addressed with concrete code examples. 6 mandatory enforcement rules and 6 anti-patterns defined.

### Gap Analysis Results

**No Critical Gaps Found.**

**Important Gaps (non-blocking, addressable during implementation):**
1. **Database indexing strategy** — Specific index definitions deferred to model implementation. Django auto-creates indexes for ForeignKey and unique fields. Additional indexes can be added based on query profiling.
2. **Pagination strategy** — Django's built-in Paginator is the default. Page size and offset/cursor choice can be decided during PO list view implementation.
3. **Custom column user-entry UI (FR51)** — Follows the same inline-edit pattern as milestone updates. No additional architectural decision needed.

**Deferred (Post-MVP, per PRD phasing):**
- Caching layer — add if performance monitoring shows need
- Django 6.0 upgrade — blocked by `mssql-django` support timeline (expected Q1 2026)
- CDC/real-time ingestion — Phase 3
- ML batch forecasting — Phase 3
- Chinese Simplified UI — Phase 2
- Management KPI dashboards — Phase 2

### Architecture Completeness Checklist

**Requirements Analysis**
- [x] Project context thoroughly analyzed (51 FRs, 29 NFRs, UX implications)
- [x] Scale and complexity assessed (medium-high, 10 users, 5K PO lines)
- [x] Technical constraints identified (8 constraints documented)
- [x] Cross-cutting concerns mapped (7 concerns with affected components)

**Architectural Decisions**
- [x] Critical decisions documented with versions (16 decisions)
- [x] Technology stack fully specified and version-verified
- [x] Integration patterns defined (ERP, HTMX, cross-region)
- [x] Performance considerations addressed (NFR1-7 mapped)

**Implementation Patterns**
- [x] Naming conventions established (database, URL, template, Python)
- [x] Structure patterns defined (app organization, templates, tests)
- [x] Communication patterns specified (HTMX triggers, audit events)
- [x] Process patterns documented (auth, validation, loading, errors)

**Project Structure**
- [x] Complete directory structure defined (~80 files)
- [x] Component boundaries established (view/service/data/template)
- [x] Integration points mapped (ERP, HTMX, SQL Server Agent)
- [x] Requirements to structure mapping complete (8 areas → 8 apps)

### Architecture Readiness Assessment

**Overall Status:** READY FOR IMPLEMENTATION

**Confidence Level:** High — all 51 FRs and 29 NFRs have clear architectural support, all technology versions verified current, implementation patterns are comprehensive with enforcement guidelines.

**Key Strengths:**
- Clean Django monolith avoids distributed system complexity for a single-developer project
- HTMX fragment pattern enables progressive UI without JavaScript framework overhead
- Append-only audit model provides complete traceability with simple implementation
- Physical custom columns avoid runtime schema complexity
- Dual-database router cleanly isolates ERP read-only access
- Split settings handle 3 deployment environments without conditional logic
- All patterns include concrete examples for AI agent implementation

**Areas for Future Enhancement:**
- Database index optimization after query profiling
- Caching layer if performance monitoring shows need
- Django 6.0 upgrade when `mssql-django` adds support
- CDC/real-time ingestion if nightly latency becomes insufficient

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented
- Use implementation patterns consistently across all components
- Respect project structure and boundaries (view/service/data/template layers)
- Refer to this document for all architectural questions
- Use enforcement guidelines and anti-patterns as implementation guardrails

**First Implementation Priority:**
```bash
py -m venv .venv
.venv\Scripts\activate
pip install Django==5.2.11 mssql-django==1.6 django-htmx==1.27.0 django-environ waitress openpyxl
django-admin startproject po_tracking .
```
Then: create split settings, configure dual databases, define custom User model before first migration.
