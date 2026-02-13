"""URL configuration for PO Tracking."""

from django.contrib import admin
from django.urls import include, path

from apps.accounts.views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("accounts/", include("apps.accounts.urls")),
    path("po/", include("apps.po.urls")),
    path("admin-portal/", include("apps.admin_portal.urls")),
    path("admin/", admin.site.urls),
]
