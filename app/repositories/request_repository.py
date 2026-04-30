from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.administrative_request import AdministrativeRequest


def get_request(db: Session, request_id: int) -> AdministrativeRequest | None:
    return db.get(AdministrativeRequest, request_id)


def list_requests(
    db: Session,
    status: str | None = None,
    request_type: str | None = None,
    student_id: int | None = None,
    priority: str | None = None,
) -> list[AdministrativeRequest]:
    stmt = select(AdministrativeRequest)
    if status:
        stmt = stmt.where(AdministrativeRequest.status == status)
    if request_type:
        stmt = stmt.where(AdministrativeRequest.request_type == request_type)
    if student_id:
        stmt = stmt.where(AdministrativeRequest.student_id == student_id)
    if priority:
        stmt = stmt.where(AdministrativeRequest.priority == priority)
    return list(db.scalars(stmt.order_by(AdministrativeRequest.id.desc())))
