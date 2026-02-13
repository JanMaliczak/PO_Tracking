from django.db import models


def scope_queryset_for_user(queryset, user, supplier_field: str = "supplier"):
    if user is None or not getattr(user, "is_authenticated", False):
        return queryset.none()

    role = getattr(user, "role", None)
    if role == "expeditor":
        supplier_id = getattr(user, "supplier_id", None)
        if supplier_id is None:
            return queryset.none()
        return queryset.filter(**{f"{supplier_field}_id": supplier_id})

    return queryset


class ScopedQuerySet(models.QuerySet):
    def for_user(self, user, supplier_field: str = "supplier"):
        return scope_queryset_for_user(self, user, supplier_field=supplier_field)


class ScopedManager(models.Manager):
    supplier_field = "supplier"

    def get_queryset(self):
        return ScopedQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user, supplier_field=self.supplier_field)

