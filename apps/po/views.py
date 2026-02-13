from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from apps.core.decorators import role_required


@login_required
@role_required("admin", "planner", "expeditor")
def po_list(request):
    return HttpResponse("PO list placeholder")


@login_required
@role_required("expeditor")
def milestone_update(request):
    return HttpResponse("Milestone update placeholder")

