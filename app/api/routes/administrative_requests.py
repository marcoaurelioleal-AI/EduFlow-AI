from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_operator_or_admin, require_viewer_or_above
from app.models.administrative_request import AdministrativeRequest
from app.models.user import User
from app.repositories import request_repository
from app.schemas.administrative_request import (
    AdministrativeRequestCreate,
    AdministrativeRequestRead,
    RequestReject,
)
from app.services import request_service

router = APIRouter(prefix="/requests", tags=["administrative requests"])


@router.post("", response_model=AdministrativeRequestRead, status_code=201)
def create_request(
    payload: AdministrativeRequestCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_operator_or_admin),
) -> AdministrativeRequest:
    return request_service.create_request(db, payload, current_user)


@router.get("", response_model=list[AdministrativeRequestRead])
def list_requests(
    status_filter: str | None = Query(default=None, alias="status"),
    request_type: str | None = None,
    student_id: int | None = None,
    priority: str | None = None,
    db: Session = Depends(get_session),
    _: User = Depends(require_viewer_or_above),
) -> list[AdministrativeRequest]:
    return request_repository.list_requests(
        db,
        status=status_filter,
        request_type=request_type,
        student_id=student_id,
        priority=priority,
    )


@router.get("/{request_id}", response_model=AdministrativeRequestRead)
def get_request(
    request_id: int,
    db: Session = Depends(get_session),
    _: User = Depends(require_viewer_or_above),
) -> AdministrativeRequest:
    return request_service.get_request_or_404(db, request_id)


@router.patch("/{request_id}/start-review", response_model=AdministrativeRequestRead)
def start_review(
    request_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_operator_or_admin),
) -> AdministrativeRequest:
    request = request_service.get_request_or_404(db, request_id)
    return request_service.transition_request(
        db,
        request,
        "in_review",
        current_user,
        action="request_started_review",
    )


@router.patch("/{request_id}/approve", response_model=AdministrativeRequestRead)
def approve_request(
    request_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_operator_or_admin),
) -> AdministrativeRequest:
    request = request_service.get_request_or_404(db, request_id)
    return request_service.transition_request(
        db,
        request,
        "approved",
        current_user,
        action="request_approved",
    )


@router.patch("/{request_id}/reject", response_model=AdministrativeRequestRead)
def reject_request(
    request_id: int,
    payload: RequestReject,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_operator_or_admin),
) -> AdministrativeRequest:
    request = request_service.get_request_or_404(db, request_id)
    return request_service.transition_request(
        db,
        request,
        "rejected",
        current_user,
        action="request_rejected",
        reason=payload.reason,
    )


@router.patch("/{request_id}/complete", response_model=AdministrativeRequestRead)
def complete_request(
    request_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_operator_or_admin),
) -> AdministrativeRequest:
    request = request_service.get_request_or_404(db, request_id)
    return request_service.transition_request(
        db,
        request,
        "completed",
        current_user,
        action="request_completed",
    )
