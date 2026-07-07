from django.db import models

from core.models import BaseModel


class NodeType(models.TextChoices):
    PLC = "PLC", "PLC"
    HMI = "HMI", "HMI"
    REMOTE_IO = "REMOTE_IO", "Remote I/O"
    INVERTER = "INVERTER", "인버터"
    SERVO = "SERVO", "서보"
    SCADA = "SCADA", "SCADA"
    GATEWAY = "GATEWAY", "게이트웨이"
    MES_ERP = "MES_ERP", "MES/ERP"
    METER = "METER", "계측기"


class NetworkSegment(models.TextChoices):
    CONTROL = "CONTROL", "제어 네트워크(PLC-HMI)"
    FIELD = "FIELD", "필드 네트워크(Remote I/O/구동)"
    SUPERVISORY = "SUPERVISORY", "감시 네트워크(SCADA)"
    ENTERPRISE = "ENTERPRISE", "상위 연동(MES/ERP)"


class FailureBehavior(models.TextChoices):
    HOLD = "HOLD", "마지막 값 유지"
    SAFE_STATE = "SAFE_STATE", "안전 상태로 전환"
    ALARM_ONLY = "ALARM_ONLY", "알람만"


class CommNode(BaseModel):
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="comm_nodes"
    )
    decision = models.ForeignKey(
        "design.DesignDecision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comm_nodes",
    )
    node_type = models.CharField(max_length=20, choices=NodeType.choices)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["node_type", "name"]

    def __str__(self):
        return f"{self.name} ({self.node_type})"


class CommLink(BaseModel):
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="comm_links"
    )
    decision = models.ForeignKey(
        "design.DesignDecision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comm_links",
    )
    source = models.ForeignKey(CommNode, on_delete=models.CASCADE, related_name="links_out")
    target = models.ForeignKey(CommNode, on_delete=models.CASCADE, related_name="links_in")
    protocol = models.CharField(max_length=50)
    segment = models.CharField(max_length=20, choices=NetworkSegment.choices)
    medium = models.CharField(max_length=50, blank=True)
    failure_behavior = models.CharField(
        max_length=20, choices=FailureBehavior.choices, default=FailureBehavior.ALARM_ONLY
    )
    comm_alarm = models.BooleanField(default=True)

    class Meta:
        ordering = ["segment"]

    def __str__(self):
        return f"{self.source.name} ↔ {self.target.name} [{self.protocol}]"


class ProtocolRequirement(BaseModel):
    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="protocol_requirements"
    )
    decision = models.ForeignKey(
        "design.DesignDecision",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="protocol_requirements",
    )
    requirement = models.CharField(max_length=50)  # OPC_UA, MQTT, GATEWAY, TIME_SYNC
    detail = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["requirement"]

    def __str__(self):
        return self.requirement
