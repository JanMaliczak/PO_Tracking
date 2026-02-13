from apps.audit.models import AuditEvent


def create_audit_event(
    *,
    event_type: str,
    source: str,
    po_line=None,
    user=None,
    previous_values=None,
    new_values=None,
    reason: str = "",
):
    return AuditEvent.objects.create(
        event_type=event_type,
        po_line=po_line,
        user=user,
        source=source,
        previous_values=previous_values or {},
        new_values=new_values or {},
        reason=reason,
    )
