import json
from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden


def _forbidden_response(is_htmx: bool) -> HttpResponseForbidden:
    response = HttpResponseForbidden()
    if is_htmx:
        response["HX-Trigger"] = json.dumps(
            {
                "showToast": {
                    "level": "error",
                    "message": "Access denied.",
                    "duration": 5000,
                }
            }
        )
    return response


def role_required(*allowed_roles):
    """Enforce role-based access on a view.

    Must be stacked below ``@login_required`` so that authentication runs first
    and unauthenticated users are redirected to the login page before the role
    check.  If ``@login_required`` is omitted, unauthenticated requests are
    still redirected to ``settings.LOGIN_URL`` by this decorator as a fallback,
    keeping authentication and authorization concerns properly separated.

    Example::

        @login_required
        @role_required("admin", "planner")
        def my_view(request): ...
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = getattr(request, "user", None)
            if user is None or not getattr(user, "is_authenticated", False):
                # Authentication concern: redirect to login (not 403)
                return redirect_to_login(request.get_full_path())

            user_role = getattr(user, "role", None)
            if user_role not in allowed_roles:
                return _forbidden_response(is_htmx=getattr(request, "htmx", False))

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator

