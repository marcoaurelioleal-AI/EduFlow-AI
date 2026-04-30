import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def _serialize(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


def create_audit_log(
    db: Session,
    *,
    user_id: int | None,
    action: str,
    entity_type: str,
    entity_id: int,
    old_value: Any = None,
    new_value: Any = None,
    reason: str | None = None,
) -> AuditLog:
    """Register a critical business event in the same transaction as the change."""
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_value=_serialize(old_value),
        new_value=_serialize(new_value),
        reason=reason,
    )
    db.add(log)
    return log
