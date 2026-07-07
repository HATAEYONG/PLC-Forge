"""Sensor Design Engine (PRD §14)."""

from django.db import transaction

from apps.design.models import RiskLevel
from apps.design.services import create_design_decision
from apps.knowledge.models import KnowledgeItem
from apps.requirements.models import ProjectFact
from apps.requirements.selectors import project_state
from apps.requirements.services import ACTIVE_STATUSES
from apps.sensors.design_rules import select_sensor_profile
from apps.sensors.models import SensorCandidate, SensorRequirement


def _measurement_facts(project):
    state = project_state(project_id=project.id)
    flat = {key: info["value"] for key, info in state.items()}
    measurements = flat.get("MEASUREMENT_REQUIREMENTS") or []
    if isinstance(measurements, str):
        measurements = [measurements]
    return flat, measurements


def _source_facts(project, keys):
    return list(
        ProjectFact.objects.filter(project=project, fact_key__in=keys, status__in=ACTIVE_STATUSES)
    )


@transaction.atomic
def generate_sensor_requirements(*, project, actor=None):
    """MEASUREMENT_REQUIREMENTS와 환경 Fact로 센서 요구사항을 생성한다 (idempotent)."""
    project.sensor_requirements.all().delete()

    flat, measurements = _measurement_facts(project)
    env_keys = [
        "MEASUREMENT_REQUIREMENTS",
        "STEAM_PRESENT_DURING_CIP",
        "STEAM_PRESENT",
        "CONTINUOUS_LEVEL_REQUIRED",
        "CORROSIVE_MATERIAL",
        "SANITARY_REQUIRED",
        "CIP_REQUIRED",
    ]
    source_facts = _source_facts(project, env_keys)

    created = []
    for measurement in measurements:
        profile = select_sensor_profile(measurement, flat)
        reason = (
            f"{measurement} 측정 요구 → {profile['principle'] or '원리 미정'}. "
            + "; ".join(profile.get("selection_reasons", []))
        ).strip("; ")

        knowledge_code = profile.get("knowledge_code")
        knowledge_items = (
            list(KnowledgeItem.objects.filter(code=knowledge_code, is_active=True))
            if knowledge_code
            else []
        )

        decision = create_design_decision(
            project=project,
            decision_type="SENSOR_REQUIREMENT",
            subject_type="SENSOR",
            subject_id=measurement,
            decision_value={
                "measurement_type": measurement,
                "principle": profile["principle"],
                "signal_type": profile["signal_type"],
            },
            reason=reason or f"{measurement} 측정 요구",
            input_facts=source_facts,
            knowledge_items=knowledge_items,
            risk_level=RiskLevel.LOW,
            actor=actor,
        )

        requirement = SensorRequirement.objects.create(
            project=project,
            decision=decision,
            measurement_type=measurement,
            measurement_principle=profile["principle"],
            sensor_technology=profile.get("technology", ""),
            signal_type=profile.get("signal_type", ""),
            accuracy=profile.get("accuracy", ""),
            response_time=profile.get("response_time", ""),
            material_compatibility=profile.get("material_compatibility", ""),
            environmental_rating=profile.get("environmental_rating", ""),
            communication_requirements=profile.get("communication_requirements", ""),
            is_continuous=profile.get("is_continuous", True),
        )
        # Vendor Independent 사양 후보(실제 벤더 모델은 MVP 범위 밖, §26)
        SensorCandidate.objects.create(
            requirement=requirement,
            vendor="(Vendor Independent)",
            model=profile.get("technology", ""),
            rationale="MVP는 벤더 카탈로그 미포함 — 측정 원리·신호 사양까지 확정",
        )
        created.append(requirement)
    return created
