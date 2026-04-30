from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.administrative_request import AdministrativeRequest
from app.models.user import User
from app.repositories import request_repository, student_repository
from app.schemas.administrative_request import AdministrativeRequestCreate
from app.services.audit_service import create_audit_log
from app.services.safe_change_service import validate_request_status_transition


def create_request(
    db: Session,
    payload: AdministrativeRequestCreate,
    current_user: User,
) -> AdministrativeRequest:
    student = student_repository.get_student(db, payload.student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    request = AdministrativeRequest(
        **payload.model_dump(),
        status="pending",
        created_by_user_id=current_user.id,
    )
    db.add(request)
    db.flush()
    create_audit_log(
        db,
        user_id=current_user.id,
        action="request_created",
        entity_type="administrative_request",
        entity_id=request.id,
        new_value=payload.model_dump(),
    )
    db.commit()
    db.refresh(request)
    return request


def transition_request(
    db: Session,
    request: AdministrativeRequest,
    new_status: str,
    current_user: User,
    *,
    action: str,
    reason: str | None = None,
) -> AdministrativeRequest:
    old_status = request.status
    validate_request_status_transition(request, new_status)
    request.status = new_status
    request.reviewed_by_user_id = current_user.id
    request.reviewed_at = datetime.now(timezone.utc)
    create_audit_log(
        db,
        user_id=current_user.id,
        action=action,
        entity_type="administrative_request",
        entity_id=request.id,
        old_value={"status": old_status},
        new_value={"status": new_status},
        reason=reason,
    )
    db.commit()
    db.refresh(request)
    return request


def get_request_or_404(db: Session, request_id: int) -> AdministrativeRequest:
    request = request_repository.get_request(db, request_id)
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")
    return request
