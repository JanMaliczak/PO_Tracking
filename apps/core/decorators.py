import json
from functools import wraps

from django.http import HttpResponseForbidden


def _forbidden_response(is_htmx: bool) -> HttpResponseForbidden:
    response = HttpResponseForbidden("Forbidden")
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
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = getattr(request, "user", None)
            if user is None or not getattr(user, "is_authenticated", False):
                return _forbidden_response(is_htmx=getattr(request, "htmx", False))

            user_role = getattr(user, "role", None)
            if user_role not in allowed_roles:
                return _forbidden_response(is_htmx=getattr(request, "htmx", False))

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator

