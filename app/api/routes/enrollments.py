from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_operator_or_admin, require_viewer_or_above
from app.models.enrollment import Enrollment
from app.models.user import User
from app.repositories import enrollment_repository
from app.schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentRead,
    EnrollmentStatusUpdate,
    PaymentStatusUpdate,
)
from app.services import enrollment_service

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


def _get_enrollment_or_404(db: Session, enrollment_id: int) -> Enrollment:
    enrollment = enrollment_repository.get_enrollment(db, enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found.")
    return enrollment


@router.post("", response_model=EnrollmentRead, status_code=status.HTTP_201_CREATED)
def create_enrollment(
    payload: EnrollmentCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_operator_or_admin),
) -> Enrollment:
    return enrollment_service.create_enrollment(db, payload, current_user)


@router.get("", response_model=list[EnrollmentRead])
def list_enrollments(
    student_id: int | None = None,
    course_id: int | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    payment_status: str | None = None,
    db: Session = Depends(get_session),
    _: User = Depends(require_viewer_or_above),
) -> list[Enrollment]:
    return enrollment_repository.list_enrollments(
        db,
        student_id=student_id,
        course_id=course_id,
        status=status_filter,
        payment_status=payment_status,
    )


@router.get("/{enrollment_id}", response_model=EnrollmentRead)
def get_enrollment(
    enrollment_id: int,
    db: Session = Depends(get_session),
    _: User = Depends(require_viewer_or_above),
) -> Enrollment:
    return _get_enrollment_or_404(db, enrollment_id)


@router.patch("/{enrollment_id}/status", response_model=EnrollmentRead)
def update_enrollment_status(
    enrollment_id: int,
    payload: EnrollmentStatusUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_operator_or_admin),
) -> Enrollment:
    enrollment = _get_enrollment_or_404(db, enrollment_id)
    return enrollment_service.update_enrollment_status(
        db,
        enrollment,
        payload.status,
        current_user,
        reason=payload.reason,
    )


@router.patch("/{enrollment_id}/payment-status", response_model=EnrollmentRead)
def update_payment_status(
    enrollment_id: int,
    payload: PaymentStatusUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_operator_or_admin),
) -> Enrollment:
    enrollment = _get_enrollment_or_404(db, enrollment_id)
    return enrollment_service.update_payment_status(
        db,
        enrollment,
        payload.payment_status,
        current_user,
        reason=payload.reason,
    )
