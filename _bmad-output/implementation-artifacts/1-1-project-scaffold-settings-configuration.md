# Story 1.1: Project Scaffold & Settings Configuration

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want the Django project initialized with split settings, environment configuration, and dual-database routing,
so that all subsequent development has a correctly structured foundation to build upon.

## Acceptance Criteria

1. Given no project exists yet
   - When the project scaffold is created
   - Then the Django project is initialized via `django-admin startproject po_tracking .` with Django 5.2.11 LTS
   - And a virtual environment exists with all core dependencies installed: Django 5.2.11, mssql-django 1.6, django-htmx 1.27.0, django-environ, waitress, openpyxl
   - And requirements files exist at `requirements/base.txt`, `requirements/development.txt`, and `requirements/production.txt`
2. Given the project is initialized
   - When settings are configured
   - Then split settings exist at `po_tracking/settings/base.py`, `development.py`, `production.py`, `production_eu.py`, and `__init__.py`
   - And `base.py` contains shared configuration: INSTALLED_APPS, MIDDLEWARE (including django-htmx), TEMPLATES, and common settings
   - And `django-environ` reads configuration from a `.env` file and a `.env.example` file documents all required variables
   - And `development.py` sets `DEBUG=True` and uses local database settings
   - And `production.py` configures the China primary environment (read-write app DB + read-only ERP)
   - And `production_eu.py` configures the Europe secondary environment (read-only app DB, no ERP connection)
3. Given split settings are configured
   - When dual-database routing is set up
   - Then `DATABASES` contains `default` (app DB, read-write) and `erp` (supplier ERP, read-only) entries
   - And a `DatabaseRouter` class in `apps/ingestion/router.py` routes ERP models to the `erp` connection and blocks write/migrate/relation operations on it
   - And the router is registered in `DATABASE_ROUTERS` setting
4. Given the project scaffold is complete
   - When the directory structure is reviewed
   - Then the `apps/` directory exists with `__init__.py` and subdirectories for: `core`, `accounts`, `po`, `ingestion`, `batches`, `audit`, `admin_portal`, `exports` — each with `__init__.py`
   - And `templates/` and `static/` directories exist at project root
   - And `.gitignore` excludes `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `db.sqlite3`, and `staticfiles/`

## Tasks / Subtasks

- [x] Task 1: Initialize Django project and dependency management (AC: 1)
  - [x] Subtask 1.1: Create virtual environment and install core dependencies (Django 5.2.11, mssql-django 1.6, django-htmx 1.27.0, django-environ 0.12.0, waitress 3.0.2, openpyxl 3.1.5)
  - [x] Subtask 1.2: Create requirements/base.txt, requirements/development.txt, requirements/production.txt
  - [x] Subtask 1.3: Initialize Django project via `django-admin startproject po_tracking .`
- [x] Task 2: Configure split settings and environment loading (AC: 2)
  - [x] Subtask 2.1: Create po_tracking/settings/ package with __init__.py (DJANGO_ENV-based switcher)
  - [x] Subtask 2.2: Implement base.py with shared INSTALLED_APPS, MIDDLEWARE (including HtmxMiddleware), TEMPLATES, django-environ loading
  - [x] Subtask 2.3: Implement development.py (DEBUG=True, local defaults)
  - [x] Subtask 2.4: Implement production.py (China primary: RW app DB + RO ERP)
  - [x] Subtask 2.5: Implement production_eu.py (Europe secondary: RO app DB, no ERP)
  - [x] Subtask 2.6: Create .env.example documenting all required variables
- [x] Task 3: Set up dual-database routing (AC: 3)
  - [x] Subtask 3.1: Configure DATABASES with default (app) and erp (supplier ERP) entries
  - [x] Subtask 3.2: Implement DatabaseRouter in apps/ingestion/router.py (read-only ERP policy)
  - [x] Subtask 3.3: Register DATABASE_ROUTERS in base settings
- [x] Task 4: Create directory structure and project scaffolding (AC: 4)
  - [x] Subtask 4.1: Create apps/ directory with __init__.py and subdirectories (core, accounts, po, ingestion, batches, audit, admin_portal, exports)
  - [x] Subtask 4.2: Create templates/ and static/ directories at project root
  - [x] Subtask 4.3: Create .gitignore with required exclusions (.env, .venv/, __pycache__/, *.pyc, db.sqlite3, staticfiles/)
- [x] Task 5: Add validation tests
  - [x] Subtask 5.1: Router policy unit tests (apps/ingestion/tests/test_router.py)
  - [x] Subtask 5.2: Scaffold path existence tests (tests/test_story_1_1_scaffold.py)
  - [x] Subtask 5.3: Settings import smoke tests (tests/test_settings_imports.py)

## Dev Notes

### Developer Context Section

- Story 1.1 is the foundation story for Epic 1 and must be completed before Story 1.2 (custom user model/auth), Story 1.3 (base UI/HTMX), and Story 1.4 (RBAC).
- Scope for this story is scaffold and configuration only: project bootstrapping, split settings, environment variable wiring, dual-database router setup, and baseline folder structure.
- Do not implement business-domain models or feature endpoints in this story beyond what is required to make scaffold and settings coherent.
- This repository currently contains planning artifacts, not implementation code; create the runtime project structure in place without breaking existing `_bmad` and `_bmad-output` artifacts.

Implementation order to avoid rework:
1. Create virtual environment and dependency constraints (`requirements/base.txt`, `requirements/development.txt`, `requirements/production.txt`).
2. Initialize Django project (`django-admin startproject po_tracking .`) and split settings package.
3. Add `django-environ` and `.env`/`.env.example` variable contracts.
4. Define dual `DATABASES` entries and `DATABASE_ROUTERS` pointing at `apps/ingestion/router.py`.
5. Create required `apps/` package directories and root `templates/` and `static/` directories.
6. Add `.gitignore` entries mandated by acceptance criteria.

Guardrails:
- Keep Django pinned to `5.2.x` while using `mssql-django 1.6`.
- Ensure ERP connection is explicitly read-only by router policy (no write/migrate/relation to ERP DB).
- Keep environment-specific behavior isolated to `development.py`, `production.py`, `production_eu.py`; avoid conditional sprawl in `base.py`.
- Preserve compatibility with forthcoming stories by using the architecture-defined app names and paths exactly.

### Technical Requirements

- Initialize project in repository root using `django-admin startproject po_tracking .` after creating and activating `.venv`.
- Create dependency split files: `requirements/base.txt`, `requirements/development.txt`, `requirements/production.txt`.
- Pin core stack versions for this story baseline:
  - `Django==5.2.11`
  - `mssql-django==1.6`
  - `django-htmx==1.27.0`
  - `django-environ`
  - `waitress`
  - `openpyxl`
- Implement split settings package exactly at:
  - `po_tracking/settings/base.py`
  - `po_tracking/settings/development.py`
  - `po_tracking/settings/production.py`
  - `po_tracking/settings/production_eu.py`
  - `po_tracking/settings/__init__.py`
- Configure `base.py` with shared `INSTALLED_APPS`, `MIDDLEWARE` (including `django_htmx.middleware.HtmxMiddleware`), `TEMPLATES`, `STATIC_*`, and shared auth/session defaults.
- Add environment loading with `django-environ` and maintain `.env.example` as the contract for required variables.
- Configure dual databases in settings:
  - `default`: application database (read-write)
  - `erp`: supplier ERP database (read-only policy enforced by router)
- Register `DATABASE_ROUTERS = ['apps.ingestion.router.DatabaseRouter']`.
- Create `apps/ingestion/router.py` with explicit policy:
  - route ERP read models to `erp`
  - block ERP writes
  - block ERP migrations
  - block ERP relations unless explicitly intended
- Create baseline package/directories for: `apps/core`, `apps/accounts`, `apps/po`, `apps/ingestion`, `apps/batches`, `apps/audit`, `apps/admin_portal`, `apps/exports`, plus root `templates/` and `static/`.
- Update `.gitignore` to exclude: `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `db.sqlite3`, `staticfiles/`.

### Architecture Compliance

- Use Django monolith architecture with server-rendered templates and HTMX progressive enhancement; do not introduce SPA frameworks or API-first split for this story.
- Keep layering boundaries aligned with architecture guidance:
  - settings/configuration work in `po_tracking/settings/*`
  - DB routing policy in `apps/ingestion/router.py`
  - no business logic in templates
- Enforce ERP read-only isolation at architecture level through router behavior (`db_for_read` only for ERP models, deny write/migrate/relation).
- Prepare structure for later RBAC and audit enforcement by creating the canonical app modules now (`core`, `accounts`, `po`, `ingestion`, `batches`, `audit`, `admin_portal`, `exports`).
- Preserve cross-region deployment intent in settings split:
  - `production.py`: China primary (RW app DB + RO ERP)
  - `production_eu.py`: Europe secondary (RO app DB, no ERP access)
- Keep deployment compatibility with Windows + IIS + Waitress + NSSM assumptions; avoid Linux/container-specific defaults.
- Keep HTMX conventions architecture-ready from day one:
  - include `django_htmx.middleware.HtmxMiddleware`
  - use fragment naming convention (`_fragment.html`) for future partials
  - keep CSRF strategy compatible with HTMX headers
- Do not add conflicting patterns called out as anti-patterns in architecture:
  - no Django signals for business/audit logic
  - no role checks only in UI
  - no full-page responses for HTMX fragment endpoints

### Library Framework Requirements

Required stack for this story implementation:
- Python: 3.13.x runtime target (architecture baseline).
- Django: use `5.2.11` for this project scaffold and SQL Server compatibility baseline.
- mssql backend: `mssql-django==1.6`.
- HTMX integration: `django-htmx==1.27.0`.
- Environment configuration: `django-environ==0.12.0` (or project-approved compatible pin).
- WSGI server (production profile prep): `waitress==3.0.2` (or project-approved compatible pin).
- Excel library (needed by later stories, installed now as core dependency): `openpyxl==3.1.5`.

Compatibility guardrails:
- Do not move scaffold to Django 6.x while using `mssql-django 1.6`; Story 1.1 foundation remains on Django 5.2 LTS per architecture and Epic 1 acceptance criteria.
- Keep `django-htmx` enabled in middleware from the start so Story 1.3 HTMX fragment behavior does not require settings refactor.
- Bootstrap and htmx frontend script versions are applied in template work (Story 1.3), but scaffold should remain compatible with:
  - Bootstrap 5.3.x CDN pattern
  - htmx 2.0.x CDN pattern

Security and maintenance notes relevant now:
- Waitress 3.0.2 includes trusted-proxy header hardening; align proxy/header config accordingly in production deployment docs later.
- openpyxl documentation warns about XML entity attack classes; if untrusted workbook parsing is introduced later, include `defusedxml` hardening.

### File Structure Requirements

Create and verify this minimum scaffold during Story 1.1:

- Project root:
  - `manage.py`
  - `.env.example`
  - `.gitignore`
  - `requirements/base.txt`
  - `requirements/development.txt`
  - `requirements/production.txt`
- Django project package:
  - `po_tracking/__init__.py`
  - `po_tracking/urls.py`
  - `po_tracking/wsgi.py`
  - `po_tracking/settings/__init__.py`
  - `po_tracking/settings/base.py`
  - `po_tracking/settings/development.py`
  - `po_tracking/settings/production.py`
  - `po_tracking/settings/production_eu.py`
- Application package root:
  - `apps/__init__.py`
  - `apps/core/__init__.py`
  - `apps/accounts/__init__.py`
  - `apps/po/__init__.py`
  - `apps/ingestion/__init__.py`
  - `apps/ingestion/router.py`
  - `apps/batches/__init__.py`
  - `apps/audit/__init__.py`
  - `apps/admin_portal/__init__.py`
  - `apps/exports/__init__.py`
- UI/static roots:
  - `templates/`
  - `static/`

Path/naming compliance requirements:
- Use lowercase snake_case names for Python modules and settings files.
- Keep app names exactly as defined in architecture (`admin_portal`, not variants).
- Keep fragment-template naming convention reserved for future HTMX partials (`_fragment_name.html`).
- Do not nest apps under alternative roots or rename `po_tracking` package; future stories reference these exact paths.

Conflict prevention:
- Avoid creating duplicate project packages (for example, nested `po_tracking/po_tracking/po_tracking`).
- Ensure `DATABASE_ROUTERS` path matches actual module path (`apps.ingestion.router.DatabaseRouter`).
- Ensure settings import resolution in `po_tracking/settings/__init__.py` is deterministic per environment selection.

### Testing Requirements

Validation targets for Story 1.1 completion:

- Environment/bootstrap checks:
  - `python --version` confirms expected runtime line (3.13.x target).
  - `pip list` (or lock inspection) confirms required packages installed with pinned versions for this story baseline.
- Django project integrity checks:
  - `python manage.py check --settings=po_tracking.settings.development` passes with no critical errors.
  - `python manage.py diffsettings --settings=po_tracking.settings.development` confirms split-settings override behavior is active.
- Settings/package checks:
  - importing each settings module succeeds: `base`, `development`, `production`, `production_eu`.
  - `django_htmx.middleware.HtmxMiddleware` is present in middleware chain from base settings.
- Database routing checks:
  - router class import path resolves: `apps.ingestion.router.DatabaseRouter`.
  - router behavior unit test covers:
    - ERP models route reads to `erp`
    - ERP writes rejected
    - ERP migrations rejected
- File system/scaffold checks:
  - required files and directories from this story exist at exact architecture paths.
  - `.gitignore` includes all required exclusions from acceptance criteria.
- Regression guard for next stories:
  - scaffolding and settings work without requiring model definitions from Story 1.2.
  - no business feature endpoints introduced in Story 1.1 changes.

Recommended minimal automated tests to add in this story:
- `apps/ingestion/tests/test_router.py` for router policy behavior.
- `po_tracking/settings/tests` (or equivalent smoke tests) for settings-module import and key config invariants.

### Latest Tech Information

Version checks validated on 2026-02-13 (UTC) against primary sources:

- Django:
  - Django 6.0 is current major line; Django 6.0.2 release notes (2026-02-03) include multiple security fixes.
  - For this project, keep Django on `5.2.11` LTS because Story 1.1 and architecture baseline depend on SQL Server backend compatibility.
  - Source: https://docs.djangoproject.com/en/6.0/releases/6.0.2/
  - Source: https://www.djangoproject.com/weblog/2025/dec/03/django-60-released/

- SQL Server backend (`mssql-django`):
  - Latest release is `1.6` (PyPI/GitHub releases).
  - Backend documentation indicates support through Django 5.2 with documented limitations, which aligns with this story's framework pin.
  - Source: https://pypi.org/project/mssql-django/
  - Source: https://github.com/microsoft/mssql-django
  - Source: https://github.com/microsoft/mssql-django/releases

- HTMX integration:
  - `django-htmx` latest release shown is `1.27.0` (2025-11-28).
  - htmx docs currently show CDN install using `htmx.org@2.0.8`.
  - Source: https://pypi.org/project/django-htmx/
  - Source: https://htmx.org/docs/

- Bootstrap:
  - Bootstrap docs and blog currently show v5.3.8 CDN/package references.
  - Source: https://getbootstrap.com/docs/5.3/getting-started/introduction/
  - Source: https://getbootstrap.com/docs/5.3/getting-started/download/
  - Source: https://blog.getbootstrap.com/2025/08/25/bootstrap-5-3-8/

- Waitress:
  - Waitress `3.0.2` is the latest release listed in the docs/PyPI pages used; includes trusted-proxy header hardening notes relevant to IIS/proxy setups.
  - Source: https://pypi.org/project/waitress/
  - Source: https://docs.pylonsproject.org/projects/waitress/en/latest/index.html
  - Source: https://docs.pylonsproject.org/projects/waitress/en/latest/runner.html

- django-environ and openpyxl:
  - `django-environ` latest release shown: `0.12.0` (2025-01-13).
  - `openpyxl` latest stable shown: `3.1.5`; security note recommends `defusedxml` when handling untrusted XLSX content.
  - Source: https://pypi.org/project/django-environ/
  - Source: https://pypi.org/project/openpyxl/

Implementation implication for Story 1.1:
- Keep scaffold pins as defined in acceptance criteria and architecture (`Django 5.2.11`, `mssql-django 1.6`, `django-htmx 1.27.0`) while capturing newer upstream lines for future upgrade planning.

### Project Context Reference

Project context file discovery result:
- `docs/project-context.md`: not found in this repository at story creation time.

Context sources used instead for this story:
- Epic and story source: `_bmad-output/planning-artifacts/epics.md` (Epic 1, Story 1.1 acceptance criteria).
- PRD baseline: `_bmad-output/planning-artifacts/prd.md` (scope, FR/NFR constraints).
- Architecture constraints: `_bmad-output/planning-artifacts/architecture.md` (stack, structure, routing, deployment patterns).
- UX baseline (forward compatibility for Story 1.3): `_bmad-output/planning-artifacts/ux-design-specification.md`.

If a dedicated project context document is added later, link it here and reconcile any differences before implementation starts.

### Project Structure Notes

- Alignment with unified project structure (paths, modules, naming)
- Detected conflicts or variances (with rationale)

### References

- Cite all technical details with source paths and sections, e.g. [Source: docs/<file>.md#Section]

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Debug Log References

- `python -m unittest tests/test_story_1_1_red.py -v` (initial red failure, then passing after implementation)
- `python -m unittest apps/ingestion/tests/test_router.py -v` (router policy tests)
- `python -m unittest tests/test_story_1_1_scaffold.py -v` (scaffold and dependency pin checks)
- `.venv\Scripts\python -m unittest discover -v` (full regression test run)
- `.venv\Scripts\python manage.py check --settings=po_tracking.settings.development` (Django system checks)
- `.venv\Scripts\python manage.py diffsettings --settings=po_tracking.settings.development` (split settings verification)
- `.venv\Scripts\python -m pip install -r requirements/development.txt` (dependency installation)

### Completion Notes List

- Implemented Story 1.1 project scaffold from an empty runtime codebase with split settings and required package structure.
- Added dependency pinning and installable requirements split: `requirements/base.txt`, `requirements/development.txt`, `requirements/production.txt`.
- Created `.venv` and installed required baseline stack: Django 5.2.11, mssql-django 1.6, django-htmx 1.27.0, django-environ 0.12.0, waitress 3.0.2, openpyxl 3.1.5.
- Implemented environment contract via `.env.example` and settings loading with `django-environ` (with fallback guard for local import checks).
- Implemented split settings modules (`base`, `development`, `production`, `production_eu`) and registered `DATABASE_ROUTERS`.
- Implemented `apps.ingestion.router.DatabaseRouter` to route ERP reads and block ERP writes/migrations/relations.
- Created required `apps/*` package directories, plus root `templates/` and `static/` directories.
- Added validation tests for router behavior and scaffold/settings invariants; all tests and checks pass.

### File List

- `.env.example`
- `.gitignore`
- `manage.py`
- `requirements/base.txt`
- `requirements/development.txt`
- `requirements/production.txt`
- `po_tracking/__init__.py`
- `po_tracking/urls.py`
- `po_tracking/wsgi.py`
- `po_tracking/settings/__init__.py`
- `po_tracking/settings/base.py`
- `po_tracking/settings/development.py`
- `po_tracking/settings/production.py`
- `po_tracking/settings/production_eu.py`
- `apps/__init__.py`
- `apps/core/__init__.py`
- `apps/accounts/__init__.py`
- `apps/po/__init__.py`
- `apps/ingestion/__init__.py`
- `apps/ingestion/router.py`
- `apps/ingestion/tests/__init__.py`
- `apps/ingestion/tests/test_router.py`
- `apps/batches/__init__.py`
- `apps/audit/__init__.py`
- `apps/admin_portal/__init__.py`
- `apps/exports/__init__.py`
- `templates/.gitkeep`
- `static/.gitkeep`
- `tests/test_story_1_1_red.py`
- `tests/test_story_1_1_scaffold.py`
- `tests/__init__.py`
- `tests/test_story_1_1_red.py`
- `tests/test_story_1_1_scaffold.py`
- `tests/test_settings_imports.py`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/1-1-project-scaffold-settings-configuration.md`

### Review Follow-ups (AI)

- [x] [AI-Review][HIGH] H1: Fixed settings resolution dual-path — wsgi.py and manage.py now use `po_tracking.settings` consistently
- [x] [AI-Review][HIGH] H2: Added SECRET_KEY crash guard in production.py and production_eu.py (no insecure default)
- [x] [AI-Review][HIGH] H3: Replaced non-existent `django.db.backends.dummy` with `del DATABASES["erp"]` in production_eu.py
- [x] [AI-Review][HIGH] H4: Replaced empty task placeholders with actual task descriptions mapped to ACs
- [x] [AI-Review][HIGH] H5: Removed hardcoded database override in development.py — base.py env vars used consistently
- [x] [AI-Review][MEDIUM] M2: Added ALLOWED_HOSTS crash guard in production.py and production_eu.py
- [x] [AI-Review][MEDIUM] M3: Removed fake `read_only: True` from ERP OPTIONS — router enforces read-only policy
- [x] [AI-Review][LOW] L2: Added missing tests/__init__.py

## Change Log

- 2026-02-13: Initialized Django scaffold with split settings, dual database configuration, ERP read-only router, app package skeleton, environment contract files, and required ignore rules.
- 2026-02-13: Added Story 1.1 validation tests for router behavior and scaffold/settings invariants; executed full unittest suite and Django checks successfully.
- 2026-02-13: Code review fixes — 5 HIGH, 2 MEDIUM, 1 LOW issues resolved. Fixed settings dual-path conflict, production SECRET_KEY/ALLOWED_HOSTS guards, dummy backend removal, development.py hardcoding, and fake read_only option.
