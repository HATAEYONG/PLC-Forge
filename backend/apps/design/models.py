from django.db import models

from core.models import BaseModel


class RuleType(models.TextChoices):
    HARD = "HARD", "Hard Rule (자동 무시 불가)"
    RECOMMENDATION = "RECOMMENDATION", "Recommendation Rule"


class Severity(models.TextChoices):
    INFO = "INFO", "정보"
    WARNING = "WARNING", "경고"
    ERROR = "ERROR", "오류"
    CRITICAL = "CRITICAL", "치명적"


class RiskLevel(models.TextChoices):
    LOW = "LOW", "낮음"
    MEDIUM = "MEDIUM", "보통"
    HIGH = "HIGH", "높음"
    CRITICAL = "CRITICAL", "치명적"


class ApprovalStatus(models.TextChoices):
    """PRD §23 Approval 상태."""

    DRAFT = "DRAFT", "작성 중"
    IN_REVIEW = "IN_REVIEW", "검토 중"
    APPROVED = "APPROVED", "승인됨"
    REJECTED = "REJECTED", "거절됨"
    SUPERSEDED = "SUPERSEDED", "대체됨"


class Rule(BaseModel):
    """PRD §12 JSON 기반 선언형 규칙."""

    code = models.CharField(max_length=100)
    version = models.PositiveIntegerField(default=1)
    rule_type = models.CharField(
        max_length=20, choices=RuleType.choices, default=RuleType.RECOMMENDATION
    )
    priority = models.IntegerField(default=0)
    conditions_json = models.JSONField(default=dict, blank=True)
    effects_json = models.JSONField(default=list, blank=True)
    explanation_template = models.TextField(blank=True)
    severity = models.CharField(max_length=10, choices=Severity.choices, default=Severity.INFO)
    confidence = models.FloatField(default=1.0)
    applicable_scope = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["code", "version"], name="uniq_rule_code_version")
        ]
        ordering = ["-priority", "code"]

    def __str__(self):
        return f"{self.code} v{self.version}"


class DesignDecision(BaseModel):
    """PRD §13 DesignDecision. Traceability(입력 Fact/규칙/지식) 없이는 생성할 수 없다."""

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="design_decisions"
    )
    decision_type = models.CharField(max_length=100)
    subject_type = models.CharField(max_length=100, blank=True)
    subject_id = models.CharField(max_length=100, blank=True)
    decision_value_json = models.JSONField()
    reason = models.TextField()
    # PRD §33-16: Traceability는 JSON ID 배열이 아닌 정규화된 조인 테이블(M2M)로 저장한다.
    input_facts = models.ManyToManyField(
        "requirements.ProjectFact", blank=True, related_name="design_decisions"
    )
    rules = models.ManyToManyField(Rule, blank=True, related_name="design_decisions")
    knowledge_items = models.ManyToManyField(
        "knowledge.KnowledgeItem", blank=True, related_name="design_decisions"
    )
    confidence = models.FloatField(default=1.0)
    risk_level = models.CharField(max_length=10, choices=RiskLevel.choices, default=RiskLevel.LOW)
    approval_required = models.BooleanField(default=False)
    approval_status = models.CharField(
        max_length=10, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT
    )
    version = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["project", "decision_type"])]

    def __str__(self):
        return f"{self.decision_type} ({self.project_id})"
