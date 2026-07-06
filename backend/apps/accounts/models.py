import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    """PRD §4 핵심 사용자 역할."""

    ADMIN = "ADMIN", "관리자"
    CONSULTANT = "CONSULTANT", "자동화 컨설턴트"
    PLC_ENGINEER = "PLC_ENGINEER", "PLC 엔지니어"
    ELECTRICAL_ENGINEER = "ELECTRICAL_ENGINEER", "전기설계 엔지니어"
    HMI_ENGINEER = "HMI_ENGINEER", "HMI/SCADA 엔지니어"
    FAT_SAT = "FAT_SAT", "FAT/SAT 담당자"
    PROJECT_MANAGER = "PROJECT_MANAGER", "프로젝트 관리자"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.CONSULTANT)
