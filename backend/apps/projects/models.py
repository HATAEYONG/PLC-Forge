from django.conf import settings
from django.db import models

from core.models import BaseModel


class ProjectStatus(models.TextChoices):
    DRAFT = "DRAFT", "작성 중"
    INTERVIEWING = "INTERVIEWING", "인터뷰 진행"
    DESIGNING = "DESIGNING", "설계 진행"
    IN_REVIEW = "IN_REVIEW", "검토 중"
    APPROVED = "APPROVED", "승인됨"
    DELIVERED = "DELIVERED", "납품 완료"
    ARCHIVED = "ARCHIVED", "보관"


class Project(BaseModel):
    company = models.ForeignKey(
        "companies.Company", on_delete=models.PROTECT, related_name="projects"
    )
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.DRAFT
    )
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.code}] {self.name}"
