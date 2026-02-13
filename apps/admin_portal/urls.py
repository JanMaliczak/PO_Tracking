from django.urls import path

from .views import dashboard

app_name = "admin_portal"

urlpatterns = [
    path("", dashboard, name="dashboard"),
]

