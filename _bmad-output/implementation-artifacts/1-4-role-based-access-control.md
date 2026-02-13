# Story 1.4: Role-Based Access Control

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an admin,
I want role-based access enforced across all application endpoints,
so that users can only access data and actions appropriate to their role and supplier scope.

## Acceptance Criteria

1. Given the custom User model with role field exists
   - When the `@role_required` decorator is implemented in `apps/core/decorators.py`
   - Then it accepts one or more role strings (e.g., `@role_required('admin', 'planner')`)
   - And it checks `request.user.role` against the allowed roles
   - And it returns HTTP 403 Forbidden if the user's role is not in the allowed list
   - And it works in combination with Django's `@login_required` (login check runs first)
2. Given the RBAC decorator exists
   - When the `.for_user()` queryset method is implemented
   - Then a custom manager on the `POLine` model (and other user-facing models) provides a `.for_user(user)` method
   - And for Expeditor users, the queryset is filtered to only PO lines belonging to the user's assigned supplier(s)
   - And for Planner and Admin users, the full unfiltered queryset is returned
   - And all views that access user-facing data use `.for_user(request.user)` to enforce scoping per FR39
3. Given RBAC is implemented at view and queryset level
   - When a request is made to any protected endpoint
   - Then authorization is enforced at the API boundary regardless of UI state per FR40
   - And an Expeditor cannot access PO data outside their supplier scope even by manipulating URLs or request parameters
   - And a Planner cannot perform Expeditor-only actions (e.g., milestone recording)
   - And only Admins can access admin portal endpoints
4. Given RBAC enforcement is in place
   - When an HTMX request is made by an unauthorized user
   - Then the response returns an appropriate error (403) with an `HX-Trigger` header to display an "Access denied" toast notification
   - And the response does not leak data from unauthorized scopes

## Tasks / Subtasks

- [x] Task 1: Implement role-based endpoint guardrails (AC: 1, 3, 4)
  - [x] Subtask 1.1: Create `apps/core/decorators.py` with `role_required(*allowed_roles)` enforcing authenticated role checks and HTTP 403 on mismatch
  - [x] Subtask 1.2: Ensure decorator composition pattern with `@login_required` is standardized and documented for all protected views
  - [x] Subtask 1.3: Add unauthorized HTMX response support (`HX-Trigger` access-denied toast contract) without leaking protected data
- [x] Task 2: Implement queryset-level scoping contract (AC: 2, 3)
  - [x] Subtask 2.1: Create reusable scoped queryset/manager utilities in `apps/core` for `.for_user(user)` behavior across user-facing models
  - [x] Subtask 2.2: Apply `.for_user(user)` contract to `POLine` manager when `POLine` model is present; if absent, implement reusable manager API now and wire immediately when `POLine` is introduced in Story 2.1
  - [x] Subtask 2.3: Enforce expeditor supplier-scoped filtering and planner/admin unrestricted query access in manager tests
- [x] Task 3: Enforce API-boundary authorization on routes (AC: 3, 4)
  - [x] Subtask 3.1: Protect admin-only endpoints with `@role_required('admin')`
  - [x] Subtask 3.2: Protect expeditor-only update endpoints and planner/admin read endpoints according to role policy
  - [x] Subtask 3.3: Ensure unauthorized direct URL access and manipulated requests return 403 consistently for standard and HTMX calls
- [x] Task 4: Add RBAC regression tests and validation (AC: 1-4)
  - [x] Subtask 4.1: Add decorator tests for allowed/denied role combinations and login-first behavior
  - [x] Subtask 4.2: Add `.for_user(user)` scoping tests for expeditor supplier constraints and planner/admin full access behavior
  - [x] Subtask 4.3: Add endpoint tests validating admin-only, expeditor-only, and unauthorized HTMX 403 behavior with access-denied trigger
  - [x] Subtask 4.4: Run full test suite and Django checks to confirm no regressions

## Dev Notes

### Developer Context Section

- Story 1.4 is the authorization boundary for the full product. All later epics assume this foundation is correct and enforced uniformly.
- Story 1.2 already delivered identity/session establishment; this story adds permission and data-scope enforcement.
- Enforce authorization at server/API boundary only. UI visibility is convenience, not security.
- Keep RBAC implementation explicit and readable: decorator-level endpoint checks plus queryset-level data scoping.
- HTMX unauthorized behavior must be first-class: return 403 and trigger standardized toast feedback without exposing protected content.

Dependency note on `POLine`:
- Acceptance criteria require `.for_user(user)` on `POLine`.
- If the full `POLine` model is not yet available in this repository stage, implement reusable scoped manager/queryset contract in `apps/core` now and apply it to `POLine` immediately once introduced (Story 2.1), without changing the public `.for_user(user)` API.

Implementation sequencing for lowest risk:
1. Implement and test `role_required` decorator.
2. Implement reusable scoping manager/queryset API.
3. Apply guardrails to protected endpoints.
4. Add HTMX unauthorized handling and full regression tests.

### Technical Requirements

- Implement `role_required(*roles)` in `apps/core/decorators.py`:
  - accepts one or more role names
  - validates authenticated user role against allowed set
  - returns HTTP 403 on unauthorized access
- Enforce decorator usage pattern with login check first (`@login_required` wrapping semantics preserved).
- Implement reusable queryset scoping API:
  - `.for_user(user)` method
  - expeditor data filtered by assigned supplier scope
  - planner/admin unrestricted data for user-facing querysets
- Apply `.for_user(request.user)` to all user-facing data access points introduced so far, and to `POLine` manager when model exists.
- Ensure unauthorized HTMX requests return:
  - status `403`
  - access-denied toast trigger contract via `HX-Trigger`
  - no protected payload leakage
- Enforce admin-only boundaries for admin portal endpoints and role-specific access for operational endpoints.

### Architecture Compliance

- Keep RBAC in backend decorators/querysets, never as template-only visibility checks.
- Align with architecture pattern:
  - `apps/core/decorators.py` for endpoint permission guardrails
  - model/queryset `.for_user(user)` for data-scope enforcement
- Do not bypass `.for_user(user)` in user-facing query code.
- Keep HTMX integration aligned with architecture error/trigger conventions (`HX-Trigger`, `request.htmx` pathways).
- Maintain Django monolith and synchronous request patterns; no alternate auth providers or token frameworks in this story.

### Library Framework Requirements

Required stack constraints for Story 1.4:
- `Django==5.2.11`
- `django-htmx==1.27.0`
- existing custom user model from Story 1.2 (`accounts.User` with `role` and `supplier`)

Authorization implementation requirements:
- Use Django decorators and queryset managers for enforcement.
- Use HTTP 403 semantics for authorization failures (authenticated but forbidden).
- Keep authentication and authorization concerns separated:
  - authentication: login/session flow (Story 1.2)
  - authorization: role/scope policy (Story 1.4)

Version guardrails:
- Remain within project baseline versions; no dependency additions required for RBAC foundation.

### File Structure Requirements

Create or update these paths in Story 1.4:
- `apps/core/decorators.py`
- `apps/core/mixins.py` and/or `apps/core/querysets.py` (for shared `.for_user(user)` scoping contract)
- `apps/po/models.py` (attach scoped manager when `POLine` exists)
- protected view modules under:
  - `apps/po/views.py`
  - `apps/admin_portal/views.py`
  - `apps/accounts/views.py` (where relevant)
- RBAC tests:
  - `apps/core/tests/test_decorators.py`
  - `apps/po/tests/test_scoped_querysets.py`
  - endpoint authorization tests in relevant app test modules

Path/naming constraints:
- Keep RBAC primitives centralized in `apps/core`.
- Use `.for_user(user)` as canonical scoping API name across models.
- Avoid duplicate permission utilities in multiple apps.

### Testing Requirements

Minimum validation targets for Story 1.4:

- Decorator behavior:
  - allowed roles receive access
  - disallowed roles receive HTTP 403
  - unauthenticated users follow login flow before role evaluation

- Query scoping behavior:
  - expeditor receives only assigned-supplier data
  - planner/admin receive full dataset
  - all user-facing views rely on `.for_user(request.user)` contract

- Endpoint protection:
  - admin-only endpoints reject non-admin users with 403
  - expeditor-only operations reject planners/admins where required
  - URL manipulation cannot bypass authorization

- HTMX unauthorized behavior:
  - HTMX forbidden requests return 403
  - response includes trigger for "Access denied" UI feedback
  - response contains no unauthorized data payload

- Regression checks:
  - existing authentication/session tests from Story 1.2 remain green
  - full test suite and Django checks pass

Recommended automated tests:
- unit tests for decorators and queryset scoping
- integration tests for protected endpoint access matrix
- HTMX forbidden-response behavior tests

### Previous Story Intelligence

Learnings carried from Story 1.3 (`1-3-base-ui-framework-htmx-setup.md`):
- Base UI shell, HTMX wiring, and toast infrastructure should already exist and be reused for unauthorized feedback behavior.
- Use shared base templates and JS primitives; do not duplicate access-denied messaging logic per feature.

Learnings carried from Story 1.2 (`1-2-custom-user-model-authentication.md`):
- Custom user role and supplier linkage are already available and must be used as RBAC input signals.
- Session/auth flow is stable and should remain unchanged while adding authorization logic.

Risk prevention based on prior context:
- Do not enforce RBAC only at template/UI layer.
- Do not introduce ad-hoc role checks across views; centralize via decorators and scoped querysets.
- Do not skip test matrix for role/supplier scope combinations.

### Git Intelligence Summary

Recent commit analysis (last 5 commits):
- `9ebd802` `story 1-1 implemented & reviewed`
- `e480bb8` `before development`
- `9871a14` `before implementation`
- `f9f4159` `during UX design`
- `8306537` `validation done with codex`

Actionable interpretation for Story 1.4:
- Existing runtime baseline is still early-stage; RBAC conventions introduced here will define long-term enforcement patterns.
- Keep RBAC changes cohesive and test-heavy to avoid future security regressions.
- Prefer explicit, centralized patterns over convenience shortcuts for authorization checks.

### Latest Tech Information

Version and compatibility guidance validated for this story context:

- Django authorization stack:
  - Django 5.2.11 baseline with built-in decorator/view auth patterns remains appropriate.
- HTMX integration:
  - `django-htmx` 1.27.0 supports request detection and error/redirect integration required for forbidden feedback flows.
- Project architecture:
  - RBAC remains role-field + scoped-queryset model, with API-boundary enforcement as the primary policy.

Implementation implication for Story 1.4:
- Keep RBAC implementation framework-native and explicit (decorators + scoped querysets + endpoint tests), avoiding additional auth frameworks.

### Project Context Reference

Project context discovery result:
- `docs/project-context.md`: not found in this repository at story creation time.

Context sources used for Story 1.4:
- Epic/story source: `_bmad-output/planning-artifacts/epics.md` (Epic 1, Story 1.4).
- Requirements baseline: `_bmad-output/planning-artifacts/prd.md` (FR38-FR40, NFR9, NFR26).
- Architecture constraints: `_bmad-output/planning-artifacts/architecture.md` (RBAC, decorator, queryset scoping, HTMX error handling conventions).
- UX baseline: `_bmad-output/planning-artifacts/ux-design-specification.md` (accessibility and feedback expectations).
- Previous story context:
  - `_bmad-output/implementation-artifacts/1-3-base-ui-framework-htmx-setup.md`
  - `_bmad-output/implementation-artifacts/1-2-custom-user-model-authentication.md`

If `project-context.md` is added later, reconcile this story guidance with that source before implementation.

### Project Structure Notes

- Alignment with unified project structure (paths, modules, naming)
- Detected conflicts or variances (with rationale)

### References

- `_bmad-output/planning-artifacts/epics.md` (Epic 1, Story 1.4)
- `_bmad-output/planning-artifacts/architecture.md` (RBAC and HTMX authorization patterns)
- `_bmad-output/planning-artifacts/prd.md` (FR38-FR40, NFR9)
- `_bmad-output/planning-artifacts/ux-design-specification.md` (accessibility and operational feedback patterns)
- `_bmad-output/implementation-artifacts/1-2-custom-user-model-authentication.md`
- `_bmad-output/implementation-artifacts/1-3-base-ui-framework-htmx-setup.md`

## Dev Agent Record

### Agent Model Used

Codex GPT-5

### Implementation Plan

- Implement reusable RBAC primitives (`role_required`, scoped queryset/manager contract) in `apps/core`.
- Apply RBAC at endpoint boundary via protected placeholder routes in `admin_portal` and `po`.
- Wire new URL namespaces into project URL configuration.
- Add focused RBAC tests (decorator behavior, endpoint access matrix, scoped query contract) and run full regression suite.

### Debug Log References

- `.venv\Scripts\python manage.py test apps.core.tests.test_decorators apps.po.tests.test_scoped_querysets apps.core.tests.test_rbac_endpoints --settings=po_tracking.settings.development -v 2` (red run, then green run)
- `.venv\Scripts\python manage.py check --settings=po_tracking.settings.development`
- `.venv\Scripts\python manage.py test --settings=po_tracking.settings.development -v 2`

### Completion Notes List

- Implemented `role_required(*allowed_roles)` in `apps/core/decorators.py` with HTTP 403 enforcement and HTMX `HX-Trigger` access-denied response support.
- Implemented reusable scope contract in `apps/core/querysets.py` (`scope_queryset_for_user`, `ScopedQuerySet`, `ScopedManager`) for `.for_user(user)` behavior.
- Added protected endpoint foundations:
  - admin-only dashboard placeholder in `apps/admin_portal/views.py`
  - expeditor-only milestone placeholder and authenticated PO list placeholders in `apps/po/views.py`
- Added URL namespaces for RBAC-protected routes in `apps/admin_portal/urls.py` and `apps/po/urls.py`, and wired them in `po_tracking/urls.py`.
- Added RBAC tests for decorator behavior, endpoint authorization matrix, HTMX forbidden trigger behavior, and scoped query contracts.
- Full project regression suite passed; story moved to `review`.

### File List

- `apps/core/decorators.py`
- `apps/core/querysets.py`
- `apps/admin_portal/views.py`
- `apps/admin_portal/urls.py`
- `apps/po/views.py`
- `apps/po/urls.py`
- `apps/core/tests/test_decorators.py`
- `apps/core/tests/test_rbac_endpoints.py`
- `apps/po/tests/__init__.py`
- `apps/po/tests/test_scoped_querysets.py`
- `po_tracking/urls.py`
- `_bmad-output/implementation-artifacts/1-4-role-based-access-control.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-02-13: Implemented Story 1.4 RBAC foundation (decorators, scoped query contract, protected endpoint placeholders, endpoint/HTMX authorization behavior tests) and validated via full regression suite. Story status set to `review`.
