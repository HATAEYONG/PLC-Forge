from django.db import models

from core.models import BaseModel


class TestPhase(models.TextChoices):
    __test__ = False  # pytest 수집 대상 아님 (Django enum)
    FAT = "FAT", "FAT"
    SAT = "SAT", "SAT"


class TestStatus(models.TextChoices):
    __test__ = False
    NOT_RUN = "NOT_RUN", "미실행"
    PASS = "PASS", "합격"
    FAIL = "FAIL", "불합격"
    BLOCKED = "BLOCKED", "보류"


class TestCase(BaseModel):
    """FAT/SAT Test Case (PRD §24). phase로 FAT/SAT를 구분한다."""

    __test__ = False  # pytest 수집 대상 아님 (Django 모델)

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="test_cases"
    )
    phase = models.CharField(max_length=3, choices=TestPhase.choices)
    test_id = models.CharField(max_length=50)
    category = models.CharField(max_length=50, blank=True)
    precondition = models.TextField(blank=True)
    procedure = models.TextField(blank=True)
    expected_result = models.TextField(blank=True)
    actual_result = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=TestStatus.choices, default=TestStatus.NOT_RUN)
    evidence = models.CharField(max_length=255, blank=True)
    tester = models.CharField(max_length=100, blank=True)
    reviewer = models.CharField(max_length=100, blank=True)
    # 역추적: 어떤 산출물에서 생성되었는지
    source_type = models.CharField(max_length=30, blank=True)  # ALARM/INTERLOCK/SENSOR/SEQUENCE
    source_ref = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["phase", "test_id"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "phase", "test_id"], name="uniq_test_per_project_phase"
            )
        ]

    def __str__(self):
        return f"[{self.phase}] {self.test_id}"
