from apps.audit.models import AuditEvent


def record_event(
    *, actor=None, action, object_type, object_id="", before=None, after=None, reason=""
):
    if actor is not None and not getattr(actor, "is_authenticated", False):
        actor = None
    return AuditEvent.objects.create(
        actor=actor,
        action=action,
        object_type=object_type,
        object_id=str(object_id),
        before_json=before,
        after_json=after,
        reason=reason,
    )
