# Story 1.2: Custom User Model & Authentication

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a user,
I want to log in with my username and password and have my session managed securely,
so that I can access the application with my identity established.

## Acceptance Criteria

1. Given the project scaffold from Story 1.1 exists
   - When the User model is defined
   - Then a custom `User` model in `apps/accounts/models.py` extends `AbstractUser` with a `role` CharField (choices: `admin`, `planner`, `expeditor`) and a nullable `supplier` ForeignKey
   - And a `Supplier` model exists in `apps/po/models.py` with at minimum `id`, `name`, and `code` fields
   - And the custom User model is registered via `AUTH_USER_MODEL = 'accounts.User'` in base settings
   - And the first migration runs successfully creating all initial tables including the custom User model
2. Given the User model exists
   - When a user navigates to the login page
   - Then a login form is displayed at `/accounts/login/` with username and password fields
   - And the form uses Django's authentication backend with PBKDF2 password hashing (Django default)
   - And the login page extends `base_auth.html` (a minimal base template without the main navbar)
   - And form inputs are labeled and keyboard accessible per NFR26
3. Given a user submits valid credentials
   - When authentication succeeds
   - Then the user is redirected to the PO list view (or a placeholder home page)
   - And a database-backed session is created with `SESSION_COOKIE_AGE=1800` (30 minutes)
   - And `SESSION_SAVE_EVERY_REQUEST=True` resets the timeout on every request
4. Given a user submits invalid credentials
   - When authentication fails
   - Then the login form is re-displayed with an error message indicating invalid credentials
   - And the error message does not reveal whether the username or password was incorrect
5. Given a user is logged in
   - When they click logout
   - Then the session is invalidated and the user is redirected to the login page
6. Given a user's session has been inactive for 30+ minutes
   - When they make any request
   - Then the session is expired and the user is redirected to the login page for re-authentication per NFR13
## Tasks / Subtasks

- [x] Task 1: Implement custom auth data model and settings wiring (AC: 1, 3)
  - [x] Subtask 1.1: Add `Supplier` model in `apps/po/models.py` with required fields (`id`, `name`, `code`)
  - [x] Subtask 1.2: Add custom `User(AbstractUser)` model in `apps/accounts/models.py` with `role` choices (`admin`, `planner`, `expeditor`) and nullable `supplier` FK to `po.Supplier`
  - [x] Subtask 1.3: Configure `AUTH_USER_MODEL = 'accounts.User'` and session policy (`SESSION_COOKIE_AGE=1800`, `SESSION_SAVE_EVERY_REQUEST=True`) in base settings
  - [x] Subtask 1.4: Create initial migrations for `accounts` and `po` and verify migration chain includes custom user and supplier tables
- [x] Task 2: Implement login/logout HTTP flow and templates (AC: 2, 4, 5)
  - [x] Subtask 2.1: Implement authentication views in `apps/accounts/views.py` using Django auth framework and safe redirects
  - [x] Subtask 2.2: Implement `apps/accounts/urls.py` routes for `/accounts/login/` and logout endpoint, include in `po_tracking/urls.py`
  - [x] Subtask 2.3: Create `templates/base_auth.html` and `templates/accounts/login.html` with labeled, keyboard-accessible username/password inputs and generic invalid-credential messaging
  - [x] Subtask 2.4: Provide authenticated placeholder landing route for post-login redirect target and add logout control for click path
- [x] Task 3: Validate session expiration and authentication guard behavior (AC: 3, 6)
  - [x] Subtask 3.1: Ensure authenticated routes require login and redirect unauthenticated/expired sessions to `/accounts/login/`
  - [x] Subtask 3.2: Verify inactivity timeout behavior is enforced by session settings contract
- [x] Task 4: Author and execute automated tests for models, auth flow, and session policy (AC: 1-6)
  - [x] Subtask 4.1: Add model/settings tests for custom user wiring, role choices, supplier FK, and session settings invariants
  - [x] Subtask 4.2: Add auth view tests covering login page rendering, valid login redirect + session creation, invalid credentials generic error, and logout invalidation
  - [x] Subtask 4.3: Add session-expiration behavior test to verify forced re-authentication after inactivity timeout
  - [x] Subtask 4.4: Run full test suite and Django checks to confirm no regressions

## Dev Notes

### Developer Context Section

- Story 1.2 is the authentication foundation for all secured workflows and must follow Story 1.1 scaffold/settings decisions without introducing stack drift.
- Primary scope is identity establishment: custom user model, login/logout flow, and secure session behavior. Keep advanced authorization policies for Story 1.4.
- Implement `Supplier` minimum model (`id`, `name`, `code`) before wiring `User.supplier` FK to satisfy the story acceptance criteria and avoid temporary schema hacks.
- Ensure `AUTH_USER_MODEL = 'accounts.User'` is set before creating initial auth migrations; changing user model after migrations causes major rework.
- Keep UI work minimal and functional in this story: `base_auth.html` and `/accounts/login/` should be accessible, keyboard-friendly, and integrated with Django auth error handling.
- Preserve existing project planning artifacts (`_bmad`, `_bmad-output`) and implement runtime code in the architecture-defined paths only.

Implementation sequencing for lowest risk:
1. Define `Supplier` in `apps/po/models.py` (minimal fields for FK target).
2. Define custom `User` in `apps/accounts/models.py` extending `AbstractUser` with `role` and nullable `supplier`.
3. Set `AUTH_USER_MODEL` and verify settings import integrity.
4. Create/apply initial migrations once model wiring is stable.
5. Implement login/logout URLs, views, and templates.
6. Verify session timeout behavior and invalid-credential handling.
### Technical Requirements

- Define `Supplier` model in `apps/po/models.py` with at minimum: `id` (implicit PK), `name`, `code`.
- Define custom `User` model in `apps/accounts/models.py`:
  - subclass `AbstractUser`
  - add `role` field with choices: `admin`, `planner`, `expeditor`
  - add nullable FK `supplier` to `po.Supplier`
- Configure `AUTH_USER_MODEL = 'accounts.User'` in base settings before generating migrations.
- Implement authentication endpoints under `apps/accounts/urls.py`:
  - `/accounts/login/`
  - logout route (POST preferred for CSRF-safe logout semantics)
- Implement login/logout views in `apps/accounts/views.py` using Django authentication framework.
- Create login template `templates/accounts/login.html` extending `templates/base_auth.html`.
- Ensure invalid credential errors are generic and do not disclose whether username or password was wrong.
- Enforce secure session baseline from Story 1.1 settings:
  - `SESSION_COOKIE_AGE = 1800`
  - `SESSION_SAVE_EVERY_REQUEST = True`
- Ensure successful login redirects to PO list view (or temporary authenticated home route if list view is not yet implemented).
- Ensure logout invalidates session and redirects to login page.
- First migration sequence must include custom user model tables and complete cleanly on app DB.
### Architecture Compliance

- Keep Django monolith architecture; do not introduce alternative auth stacks or external identity providers in this story.
- Respect architecture boundary split:
  - model definitions in `apps/accounts/models.py` and `apps/po/models.py`
  - HTTP auth flow in `apps/accounts/views.py` + `apps/accounts/urls.py`
  - templates in `templates/accounts/` and `templates/base_auth.html`
- Align with architecture sequence: custom user model must be in place before downstream RBAC decorators (`apps/core/decorators.py`) are used by protected views.
- Do not implement role-based authorization logic only in templates/UI; story focus is identity/authentication foundation, with authorization enforcement expanded in Story 1.4.
- Keep session handling compatible with HTMX request model and middleware chain established in Story 1.1 (`django_htmx.middleware.HtmxMiddleware` remains active in base settings).
- Preserve environment split behavior (`development`, `production`, `production_eu`) and avoid hardcoding environment-specific auth/session values in app code.
- Avoid introducing business feature endpoints or domain workflows unrelated to authentication in this story.
### Library Framework Requirements

Required stack constraints for Story 1.2:
- `Django==5.2.11` (project baseline; compatible with SQL Server backend requirements)
- `mssql-django==1.6` (do not upgrade Django major version beyond supported matrix in this story)
- `django-htmx==1.27.0` (middleware/request compatibility retained from Story 1.1)
- `django-environ==0.12.0` (or locked project-approved equivalent)

Authentication/session implementation requirements:
- Use Django built-in authentication flow (`authenticate`, `login`, `logout`) rather than custom password/session mechanisms.
- Use Django default PBKDF2 hasher baseline (meets NFR8); do not store or process plaintext credentials outside Django auth APIs.
- Keep database-backed sessions enabled with inactivity timeout settings from Story 1.1.

Version guardrails:
- Django 6.0.x exists, but Story 1.2 must remain on Django 5.2.11 due to `mssql-django` compatibility boundary.
- Keep auth implementation free of experimental async-only patterns; Waitress/WSGI deployment path remains synchronous.
### File Structure Requirements

Create or update these paths in Story 1.2:
- `apps/accounts/models.py`
  - custom `User(AbstractUser)` with `role` + nullable `supplier` FK
- `apps/po/models.py`
  - minimal `Supplier` model (`id`, `name`, `code`)
- `po_tracking/settings/base.py`
  - `AUTH_USER_MODEL = 'accounts.User'`
  - confirm session settings remain aligned (`SESSION_COOKIE_AGE`, `SESSION_SAVE_EVERY_REQUEST`)
- `apps/accounts/views.py`
  - login view and logout endpoint behavior
- `apps/accounts/urls.py`
  - route declarations for login/logout
- `po_tracking/urls.py`
  - include `accounts` URL configuration
- `templates/base_auth.html`
  - minimal unauthenticated layout baseline
- `templates/accounts/login.html`
  - username/password form with accessible labels and generic error display
- migration files under `apps/accounts/migrations/` and `apps/po/migrations/`
  - include user/supplier schema in first stable migration sequence

Path and naming constraints:
- Keep app names and module paths exactly as architecture defines (`accounts`, `po`, `core`, etc.).
- Keep template locations aligned with app domain (`templates/accounts/*`).
- Do not create duplicate auth entrypoints outside `apps/accounts/`.
### Testing Requirements

Minimum validation targets for Story 1.2:

- Model/schema checks:
  - custom user model is active (`AUTH_USER_MODEL` resolves to `accounts.User`)
  - `User.role` choices validate correctly (`admin`, `planner`, `expeditor`)
  - `User.supplier` nullable FK is valid and points to `po.Supplier`
  - first migration chain applies cleanly on app DB

- Authentication flow checks:
  - GET `/accounts/login/` renders login form with labeled username/password fields
  - valid credentials authenticate and redirect to target route
  - invalid credentials re-render form with generic error message (no username/password leak)
  - logout invalidates session and redirects to login

- Session/security checks:
  - session timeout settings present: `SESSION_COOKIE_AGE=1800`, `SESSION_SAVE_EVERY_REQUEST=True`
  - inactivity expiration behavior forces re-authentication (NFR13)
  - password handling uses Django auth hasher path (PBKDF2 baseline), no plaintext storage path

- Accessibility baseline checks (NFR26):
  - login form fields have associated labels
  - keyboard-only form submission path works (tab order + submit)

Recommended automated tests:
- `apps/accounts/tests/test_models.py`
- `apps/accounts/tests/test_views.py`
- `apps/accounts/tests/test_auth_flow.py` (or merged into `test_views.py`)
- optional settings smoke test to assert `AUTH_USER_MODEL` and session config invariants
### Previous Story Intelligence

Learnings carried from Story 1.1 (`1-1-project-scaffold-settings-configuration.md`):
- Settings split and environment contract already established; Story 1.2 should consume this foundation rather than redefining config structure.
- `django_htmx.middleware.HtmxMiddleware` and baseline stack pins are already part of project guardrails; authentication should integrate cleanly with that middleware chain.
- Story 1.1 explicitly warns about migration-order pitfalls; for Story 1.2 this translates to defining custom user model before any auth-dependent migrations.
- Project path conventions and app naming are fixed (`apps/accounts`, `apps/po`, `templates/accounts`); avoid creating parallel or temporary auth module paths.
- Validation expectations from Story 1.1 emphasize settings/migration integrity checks; reuse that pattern for auth model and session behavior verification in Story 1.2.

Risk prevention based on prior context:
- Do not delay `AUTH_USER_MODEL` wiring until after migrations are generated.
- Do not treat `Supplier` FK as optional from schema perspective by deferring the model definition; create minimal `Supplier` now.
- Do not broaden scope into RBAC policy logic (Story 1.4) while implementing login/session basics.
### Git Intelligence Summary

Recent commit analysis (last 4 commits):
- `9871a14` `before implementation`
- `f9f4159` `during UX design`
- `8306537` `validation done with codex`
- `b505442` `prd review codex`

Actionable interpretation for Story 1.2:
- Repository history is currently planning-document heavy; no production auth implementation patterns are present to reuse yet.
- Treat Story 1.2 as first concrete auth implementation baseline and establish clean conventions in canonical architecture paths.
- Avoid inferring existing runtime code behavior from commit history; verify directly in codebase during implementation.
- Keep commits for Story 1.2 scoped and atomic (model/settings, migrations, auth views/templates, tests) to simplify later Story 1.4 RBAC evolution.
### Latest Tech Information

Version/security checks validated on 2026-02-13 (UTC), distilled for Story 1.2 decisions:

- Django:
  - Current major line is 6.0.x; Django 5.2.11 LTS is available and includes recent fixes.
  - Story 1.2 should remain on Django 5.2.11 per project architecture and SQL Server backend compatibility.

- SQL Server backend (`mssql-django`):
  - Latest stable is 1.6 with support aligned to Django 5.2.
  - Do not move this story to Django 6.x while staying on `mssql-django==1.6`.

- `django-htmx` / HTMX:
  - `django-htmx` latest is 1.27.0; HTMX docs currently publish 2.0.8 install references.
  - Story 1.2 auth pages should remain compatible with HTMX middleware/request handling even if they are mostly non-HTMX flows.

- Session/runtime security notes:
  - Waitress 3.0.2 includes trusted-header/proxy hardening guidance; relevant for deployment behind IIS reverse proxy.
  - Keep auth/session logic framework-native (Django auth + DB sessions) and avoid custom session/token implementations in this story.

Primary sources used during research:
- Django releases/docs and project weblog
- PyPI + GitHub project pages for `mssql-django`, `django-htmx`, `waitress`, `django-environ`, `openpyxl`
- HTMX official docs
### Project Context Reference

Project context discovery result:
- `docs/project-context.md`: not found in this repository at story creation time.

Context sources used for Story 1.2:
- Epic/story source: `_bmad-output/planning-artifacts/epics.md` (Epic 1, Story 1.2 user story and acceptance criteria).
- Requirements baseline: `_bmad-output/planning-artifacts/prd.md` (FR37-FR40, NFR8, NFR9, NFR13, NFR26).
- Architecture constraints: `_bmad-output/planning-artifacts/architecture.md` (custom user pattern, session model, stack/version boundaries, path conventions).
- UX/accessibility baseline: `_bmad-output/planning-artifacts/ux-design-specification.md` (auth form accessibility and interaction expectations).
- Previous story context: `_bmad-output/implementation-artifacts/1-1-project-scaffold-settings-configuration.md`.

If `project-context.md` is added later, reconcile this story guidance with that source before implementation.
### Project Structure Notes

- Alignment with unified project structure (paths, modules, naming)
- Detected conflicts or variances (with rationale)

### References

- Cite all technical details with source paths and sections, e.g. [Source: docs/<file>.md#Section]

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Debug Log References

- `.venv\Scripts\python manage.py test apps.accounts.tests --settings=po_tracking.settings.development -v 2` (red run, then green run)
- `.venv\Scripts\python manage.py makemigrations po accounts --settings=po_tracking.settings.development`
- `.venv\Scripts\python manage.py migrate --settings=po_tracking.settings.development`
- `.venv\Scripts\python manage.py check --settings=po_tracking.settings.development`
- `.venv\Scripts\python manage.py test --settings=po_tracking.settings.development -v 2`
- `.venv\Scripts\python -m unittest discover -s tests -v`

### Completion Notes List

- Replaced placeholder task list with AC-mapped implementation tasks and executed them in order.
- Implemented `Supplier` and custom `accounts.User` models and wired `AUTH_USER_MODEL`.
- Added session policy settings: `SESSION_COOKIE_AGE=1800` and `SESSION_SAVE_EVERY_REQUEST=True`.
- Created initial migrations for `po` and `accounts` and verified migration chain applies successfully.
- Implemented login/logout views and routes under `/accounts/`, including POST logout semantics.
- Added `base_auth.html`, accessible login form template, and authenticated placeholder home route used as login redirect target.
- Added comprehensive automated tests for model wiring, auth flow, invalid credential handling, logout session invalidation, and session expiration re-authentication behavior.
- Validation complete: Django checks pass and full regression test suite passes.

### File List

- `apps/accounts/models.py`
- `apps/accounts/views.py`
- `apps/accounts/urls.py`
- `apps/accounts/migrations/__init__.py`
- `apps/accounts/migrations/0001_initial.py`
- `apps/accounts/tests/__init__.py`
- `apps/accounts/tests/test_models.py`
- `apps/accounts/tests/test_views.py`
- `apps/po/models.py`
- `apps/po/migrations/__init__.py`
- `apps/po/migrations/0001_initial.py`
- `po_tracking/settings/base.py`
- `po_tracking/urls.py`
- `templates/base_auth.html`
- `templates/accounts/login.html`
- `templates/accounts/home.html`
- `_bmad-output/implementation-artifacts/1-2-custom-user-model-authentication.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Senior Developer Review (AI)

**Reviewer:** Claude Opus 4.6 on 2026-02-13
**Outcome:** Approved with fixes applied

### Findings (7 fixed, 2 low deferred)

| # | Severity | Description | Resolution |
|---|----------|-------------|------------|
| H1 | HIGH | `home.html` was standalone HTML, not extending any base template | Fixed: now extends `base_auth.html`, shows username |
| H2 | HIGH | `Supplier.code` lacked `unique=True` constraint | Fixed: added `unique=True`, updated migration |
| H3 | HIGH | `LOGIN_REDIRECT_URL = "/"` hardcoded path instead of named URL | Fixed: changed to `"home"` |
| M1 | MEDIUM | `AccountLogoutView` returned 405 on GET with no friendly handling | Fixed: GET now redirects to login page |
| M2 | MEDIUM | `test_expired_session` used `time.sleep(2)` - slow and fragile | Fixed: replaced with direct session expiry date manipulation |
| M3 | MEDIUM | No tests for `Supplier` model fields or `__str__` | Fixed: added `SupplierModelTests` class |
| M4 | MEDIUM | `form.non_field_errors` rendered raw Django `<ul>` markup | Fixed: iterate errors as `<p>` tags |
| L1 | LOW | `Supplier.__str__` untested | Covered by new M3 fix |
| L2 | LOW | Home placeholder doesn't show logged-in user identity | Covered by H1 fix (added `{{ request.user.username }}`) |

### Post-fix validation
- 10/10 tests pass (including 2 new Supplier tests)
- Django system check: 0 issues
- All ACs verified as implemented

## Change Log

- 2026-02-13: Implemented Story 1.2 custom user model and authentication flow (models, settings, migrations, login/logout routes/views/templates, session policy checks, and automated tests). Story status set to `review`.
- 2026-02-13: Senior developer code review completed. 7 issues fixed (3 HIGH, 4 MEDIUM). Added `unique=True` to Supplier.code, fixed template hierarchy, corrected LOGIN_REDIRECT_URL, improved logout GET handling, replaced slow test, added Supplier tests, cleaned up error rendering. Status set to `done`.
