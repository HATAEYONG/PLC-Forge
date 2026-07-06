from apps.requirements.models import ProjectFact
from apps.requirements.services import ACTIVE_STATUSES


def facts_for_project(*, project_id, active_only=False):
    queryset = ProjectFact.objects.filter(project_id=project_id)
    if active_only:
        queryset = queryset.filter(status__in=ACTIVE_STATUSES)
    return queryset


def project_state(*, project_id):
    """ProjectState Projection — 활성 Fact의 최신 버전을 key-value로 요약 (PRD §10)."""
    state = {}
    for fact in facts_for_project(project_id=project_id, active_only=True).order_by(
        "fact_key", "version"
    ):
        state[fact.fact_key] = {
            "value": fact.value_json,
            "unit": fact.unit,
            "status": fact.status,
            "confidence": fact.confidence,
            "version": fact.version,
        }
    return state
