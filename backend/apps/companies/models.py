from django.db import models

from core.models import BaseModel


class Company(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    industry = models.CharField(max_length=100, blank=True)
    contact_name = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    memo = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
