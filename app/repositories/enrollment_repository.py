from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentCreate


def create_enrollment(db: Session, payload: EnrollmentCreate) -> Enrollment:
    enrollment = Enrollment(**payload.model_dump())
    db.add(enrollment)
    return enrollment


def get_enrollment(db: Session, enrollment_id: int) -> Enrollment | None:
    return db.get(Enrollment, enrollment_id)


def list_enrollments(
    db: Session,
    student_id: int | None = None,
    course_id: int | None = None,
    status: str | None = None,
    payment_status: str | None = None,
) -> list[Enrollment]:
    stmt = select(Enrollment)
    if student_id:
        stmt = stmt.where(Enrollment.student_id == student_id)
    if course_id:
        stmt = stmt.where(Enrollment.course_id == course_id)
    if status:
        stmt = stmt.where(Enrollment.status == status)
    if payment_status:
        stmt = stmt.where(Enrollment.payment_status == payment_status)
    return list(db.scalars(stmt.order_by(Enrollment.id)))
