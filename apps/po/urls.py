from django.urls import path

from .views import milestone_update, po_list

app_name = "po"

urlpatterns = [
    path("", po_list, name="list"),
    path("milestone/update/", milestone_update, name="milestone_update"),
]

