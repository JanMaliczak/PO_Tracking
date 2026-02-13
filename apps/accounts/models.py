from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = "admin"
    ROLE_PLANNER = "planner"
    ROLE_EXPEDITOR = "expeditor"

    ROLE_CHOICES = (
        (ROLE_ADMIN, "Admin"),
        (ROLE_PLANNER, "Planner"),
        (ROLE_EXPEDITOR, "Expeditor"),
    )

    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=ROLE_PLANNER)
    supplier = models.ForeignKey(
        "po.Supplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

