from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from apps.core.decorators import role_required


@login_required
@role_required("admin")
def dashboard(request):
    return HttpResponse("Admin dashboard placeholder")

