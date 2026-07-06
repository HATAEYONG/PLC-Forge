from django.conf import settings
from django.db import models

from core.models import BaseModel


class QuestionType(models.TextChoices):
    """PRD §8.3 질문 유형."""

    TEXT = "TEXT", "텍스트"
    YES_NO = "YES_NO", "예/아니오"
    SINGLE_CHOICE = "SINGLE_CHOICE", "단일 선택"
    MULTI_CHOICE = "MULTI_CHOICE", "복수 선택"
    INTEGER = "INTEGER", "정수"
    DECIMAL = "DECIMAL", "소수"
    RANGE = "RANGE", "범위"
    UNIT_VALUE = "UNIT_VALUE", "단위값"
    DEVICE_LIST = "DEVICE_LIST", "설비 목록"
    TABLE = "TABLE", "표"
    FILE_UPLOAD = "FILE_UPLOAD", "파일 업로드"
    CONFIRMATION = "CONFIRMATION", "확인"


class QuestionCategory(models.TextChoices):
    """PRD §8.4 질문 카테고리."""

    COMPANY = "COMPANY", "회사"
    INDUSTRY = "INDUSTRY", "업종"
    PROCESS = "PROCESS", "공정"
    PRODUCTION = "PRODUCTION", "생산"
    DEVICE = "DEVICE", "설비"
    MATERIAL = "MATERIAL", "물질"
    SENSOR = "SENSOR", "센서"
    QUALITY = "QUALITY", "품질"
    SAFETY = "SAFETY", "안전"
    ENVIRONMENT = "ENVIRONMENT", "환경"
    MAINTENANCE = "MAINTENANCE", "유지보수"
    NETWORK = "NETWORK", "네트워크"
    COMMUNICATION = "COMMUNICATION", "통신"
    PLC = "PLC", "PLC"
    HMI = "HMI", "HMI"
    SCADA = "SCADA", "SCADA"
    HISTORIAN = "HISTORIAN", "Historian"
    MES_ERP = "MES_ERP", "MES/ERP"
    ALARM = "ALARM", "알람"
    INTERLOCK = "INTERLOCK", "인터록"
    SEQUENCE = "SEQUENCE", "시퀀스"
    FAT = "FAT", "FAT"
    SAT = "SAT", "SAT"
    DELIVERY = "DELIVERY", "납품"


class Criticality(models.TextChoices):
    LOW = "LOW", "낮음"
    MEDIUM = "MEDIUM", "보통"
    HIGH = "HIGH", "높음"
    CRITICAL = "CRITICAL", "치명적"


class Question(BaseModel):
    """PRD §8.2 Question 데이터."""

    code = models.CharField(max_length=100)
    version = models.PositiveIntegerField(default=1)
    text = models.TextField()
    help_text = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=QuestionCategory.choices)
    question_type = models.CharField(max_length=20, choices=QuestionType.choices)
    answer_schema = models.JSONField(default=dict, blank=True)
    priority = models.IntegerField(default=0)
    criticality = models.CharField(
        max_length=10, choices=Criticality.choices, default=Criticality.MEDIUM
    )
    required_conditions = models.JSONField(default=dict, blank=True)
    exclusion_conditions = models.JSONField(default=dict, blank=True)
    applicable_industries = models.JSONField(default=list, blank=True)
    applicable_processes = models.JSONField(default=list, blank=True)
    unlocks_facts = models.JSONField(default=list, blank=True)
    unlocks_decisions = models.JSONField(default=list, blank=True)
    risk_detection_tags = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["code", "version"], name="uniq_question_code_version")
        ]
        ordering = ["code", "-version"]

    def __str__(self):
        return f"{self.code} v{self.version}"


class AnswerOption(BaseModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="options")
    value = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.question.code}: {self.value}"


class SessionStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "진행 중"
    COMPLETED = "COMPLETED", "완료"
    ABANDONED = "ABANDONED", "중단"


class InterviewSession(BaseModel):
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="interview_sessions"
    )
    status = models.CharField(
        max_length=20, choices=SessionStatus.choices, default=SessionStatus.IN_PROGRESS
    )
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class InterviewAnswer(BaseModel):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="answers")
    raw_answer = models.JSONField()
    answered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["created_at"]


class QuestionSelectionLog(BaseModel):
    """Question Engine의 질문 선택 이유 기록 (PRD §8.5 '선택 이유를 저장한다')."""

    session = models.ForeignKey(
        InterviewSession, on_delete=models.CASCADE, related_name="selection_logs"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="selection_logs")
    total_score = models.FloatField()
    score_breakdown = models.JSONField(default=dict)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
