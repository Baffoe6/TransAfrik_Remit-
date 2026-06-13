from sqlalchemy.orm import Session

from app.models.corridor import Corridor, CorridorProviderRoute
from app.models.enums import CorridorStatus, OperationsAuditCategory
from app.services.operations_audit import log_operations_action


def list_corridors(db: Session, *, active_only: bool = False) -> list[Corridor]:
    q = db.query(Corridor).order_by(Corridor.priority.desc(), Corridor.code)
    if active_only:
        q = q.filter(Corridor.status == CorridorStatus.ACTIVE)
    return q.all()


def get_corridor(db: Session, corridor_id: int) -> Corridor | None:
    return db.query(Corridor).filter(Corridor.id == corridor_id).first()


def create_corridor(db: Session, data: dict, user_id: int | None = None) -> Corridor:
    corridor = Corridor(**data)
    db.add(corridor)
    db.flush()
    log_operations_action(
        db,
        category=OperationsAuditCategory.CORRIDOR,
        action="corridor_created",
        entity_type="corridor",
        entity_id=corridor.id,
        user_id=user_id,
        details={"code": corridor.code},
    )
    return corridor


def update_corridor(db: Session, corridor: Corridor, updates: dict, user_id: int | None = None) -> Corridor:
    for key, value in updates.items():
        if value is not None and hasattr(corridor, key):
            setattr(corridor, key, value)
    log_operations_action(
        db,
        category=OperationsAuditCategory.CORRIDOR,
        action="corridor_updated",
        entity_type="corridor",
        entity_id=corridor.id,
        user_id=user_id,
        details=updates,
    )
    return corridor


def set_corridor_status(db: Session, corridor: Corridor, status: CorridorStatus, user_id: int | None = None) -> Corridor:
    corridor.status = status
    log_operations_action(
        db,
        category=OperationsAuditCategory.CORRIDOR,
        action="corridor_status_changed",
        entity_type="corridor",
        entity_id=corridor.id,
        user_id=user_id,
        details={"status": status.value},
    )
    return corridor


def list_corridor_routes(db: Session, corridor_id: int) -> list[CorridorProviderRoute]:
    return (
        db.query(CorridorProviderRoute)
        .filter(CorridorProviderRoute.corridor_id == corridor_id)
        .order_by(CorridorProviderRoute.priority.desc())
        .all()
    )
