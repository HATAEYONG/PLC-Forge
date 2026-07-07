"""Communication Design Engine (PRD §16)."""

from django.db import transaction

from apps.communications.models import (
    CommLink,
    CommNode,
    FailureBehavior,
    NetworkSegment,
    NodeType,
    ProtocolRequirement,
)
from apps.design.models import RiskLevel
from apps.design.services import create_design_decision
from apps.requirements.models import ProjectFact
from apps.requirements.selectors import project_state
from apps.requirements.services import ACTIVE_STATUSES

# 선호 프로토콜 Fact → 실제 프로토콜명
PROTOCOL_MAP = {
    "MODBUS": "Modbus TCP",
    "ETHERNET_IP": "EtherNet/IP",
    "PROFINET": "PROFINET",
    "CC_LINK": "CC-Link IE",
    "OPC_UA": "OPC UA",
    "NONE": "Modbus TCP",
    None: "Modbus TCP",
}


def _flat_state(project):
    state = project_state(project_id=project.id)
    return {key: info["value"] for key, info in state.items()}


def _source_facts(project, keys):
    return list(
        ProjectFact.objects.filter(project=project, fact_key__in=keys, status__in=ACTIVE_STATUSES)
    )


@transaction.atomic
def generate_communication(*, project, actor=None):
    """설계 상태로 통신 노드·링크·프로토콜 요구를 생성한다 (idempotent)."""
    project.comm_nodes.all().delete()
    project.comm_links.all().delete()
    project.protocol_requirements.all().delete()

    flat = _flat_state(project)
    facts = _source_facts(
        project,
        [
            "HMI_REQUIRED",
            "COMM_TARGETS",
            "INVERTER_USED",
            "SCADA_REQUIRED",
            "MES_INTEGRATION_REQUIRED",
            "REMOTE_MONITORING_REQUIRED",
            "PREFERRED_PROTOCOL",
        ],
    )
    # 통신 구성의 근거가 되는 Fact가 하나도 없으면 네트워크를 구성할 수 없다 → 건너뛴다.
    if not facts:
        return {"nodes": 0, "links": 0, "protocol_requirements": [], "skipped": True}

    decision = create_design_decision(
        project=project,
        decision_type="COMMUNICATION_DESIGN",
        subject_type="NETWORK",
        decision_value={"summary": "통신 아키텍처 초안"},
        reason="제어방식·연동장치·상위연동 요구로 네트워크를 구성",
        input_facts=facts,
        risk_level=RiskLevel.MEDIUM,
        actor=actor,
    )

    protocol = PROTOCOL_MAP.get(flat.get("PREFERRED_PROTOCOL"), "Modbus TCP")

    def node(node_type, name):
        return CommNode.objects.create(
            project=project, decision=decision, node_type=node_type, name=name
        )

    def link(src, tgt, proto, segment, medium="Ethernet", failure=FailureBehavior.ALARM_ONLY):
        return CommLink.objects.create(
            project=project,
            decision=decision,
            source=src,
            target=tgt,
            protocol=proto,
            segment=segment,
            medium=medium,
            failure_behavior=failure,
        )

    plc = node(NodeType.PLC, "PLC-01")

    # PLC-HMI 제어 네트워크
    if flat.get("HMI_REQUIRED"):
        hmi = node(NodeType.HMI, "HMI-01")
        link(plc, hmi, protocol, NetworkSegment.CONTROL)

    # 인버터/구동 필드 네트워크
    targets = flat.get("COMM_TARGETS") or []
    if isinstance(targets, str):
        targets = [targets]
    if flat.get("INVERTER_USED") or "INVERTER" in targets:
        inv = node(NodeType.INVERTER, "INV-Group")
        # 구동 장치 통신 두절 시 안전 상태로 (Safety 성격)
        link(plc, inv, protocol, NetworkSegment.FIELD, failure=FailureBehavior.SAFE_STATE)
    if "SERVO" in targets:
        servo = node(NodeType.SERVO, "SERVO-Group")
        link(plc, servo, protocol, NetworkSegment.FIELD, failure=FailureBehavior.SAFE_STATE)
    if "METER" in targets:
        meter = node(NodeType.METER, "METER-Group")
        link(plc, meter, "Modbus TCP", NetworkSegment.FIELD)

    # SCADA 감시 네트워크
    if flat.get("SCADA_REQUIRED"):
        scada = node(NodeType.SCADA, "SCADA")
        link(plc, scada, "OPC UA", NetworkSegment.SUPERVISORY)
        ProtocolRequirement.objects.create(
            project=project,
            decision=decision,
            requirement="OPC_UA",
            detail="SCADA 연동 표준 인터페이스",
        )

    # MES/ERP 상위 연동 (게이트웨이 경유)
    if flat.get("MES_INTEGRATION_REQUIRED"):
        gw = node(NodeType.GATEWAY, "GW-01")
        mes = node(NodeType.MES_ERP, "MES/ERP")
        link(plc, gw, "OPC UA", NetworkSegment.SUPERVISORY)
        link(gw, mes, "MQTT/REST", NetworkSegment.ENTERPRISE)
        for req, detail in [("MQTT", "MES 데이터 발행"), ("GATEWAY", "OT/IT 분리 게이트웨이")]:
            ProtocolRequirement.objects.create(
                project=project, decision=decision, requirement=req, detail=detail
            )

    # 원격 모니터링 → 게이트웨이 필요
    if flat.get("REMOTE_MONITORING_REQUIRED") and not flat.get("MES_INTEGRATION_REQUIRED"):
        ProtocolRequirement.objects.create(
            project=project,
            decision=decision,
            requirement="GATEWAY",
            detail="원격 모니터링용 보안 게이트웨이",
        )

    return {
        "nodes": project.comm_nodes.count(),
        "links": project.comm_links.count(),
        "protocol_requirements": list(
            project.protocol_requirements.values_list("requirement", flat=True)
        ),
    }
