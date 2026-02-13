from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=64, unique=True)

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"

