from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment
from app.models.user import User
from app.repositories import course_repository, enrollment_repository, student_repository
from app.schemas.enrollment import EnrollmentCreate
from app.services.audit_service import create_audit_log
from app.services.safe_change_service import (
    validate_enrollment_creation,
    validate_enrollment_status_change,
    validate_payment_status_change,
)


def create_enrollment(db: Session, payload: EnrollmentCreate, current_user: User) -> Enrollment:
    student = student_repository.get_student(db, payload.student_id)
    course = course_repository.get_course(db, payload.course_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    validate_enrollment_creation(student, course)
    enrollment = enrollment_repository.create_enrollment(db, payload)
    db.flush()
    create_audit_log(
        db,
        user_id=current_user.id,
        action="enrollment_created",
        entity_type="enrollment",
        entity_id=enrollment.id,
        new_value=payload.model_dump(),
    )
    db.commit()
    db.refresh(enrollment)
    return enrollment


def update_enrollment_status(
    db: Session,
    enrollment: Enrollment,
    new_status: str,
    current_user: User,
    reason: str | None = None,
) -> Enrollment:
    old_status = enrollment.status
    validate_enrollment_status_change(enrollment, new_status)
    enrollment.status = new_status
    create_audit_log(
        db,
        user_id=current_user.id,
        action="enrollment_status_changed",
        entity_type="enrollment",
        entity_id=enrollment.id,
        old_value={"status": old_status},
        new_value={"status": new_status},
        reason=reason,
    )
    db.commit()
    db.refresh(enrollment)
    return enrollment


def update_payment_status(
    db: Session,
    enrollment: Enrollment,
    new_payment_status: str,
    current_user: User,
    reason: str | None = None,
) -> Enrollment:
    old_status = enrollment.payment_status
    validate_payment_status_change(enrollment, new_payment_status)
    enrollment.payment_status = new_payment_status
    create_audit_log(
        db,
        user_id=current_user.id,
        action="payment_status_changed",
        entity_type="enrollment",
        entity_id=enrollment.id,
        old_value={"payment_status": old_status},
        new_value={"payment_status": new_payment_status},
        reason=reason,
    )
    db.commit()
    db.refresh(enrollment)
    return enrollment
