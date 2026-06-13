from sqlalchemy.orm import Session

from app.models.enums import OperationsAuditCategory
from app.models.operations_audit import OperationsAuditLog


def log_operations_action(
    db: Session,
    *,
    category: OperationsAuditCategory,
    action: str,
    entity_type: str,
    user_id: int | None = None,
    entity_id: int | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
) -> OperationsAuditLog:
    entry = OperationsAuditLog(
        user_id=user_id,
        category=category,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(entry)
    db.flush()
    return entry
