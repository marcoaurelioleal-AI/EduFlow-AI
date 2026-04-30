from fastapi import HTTPException, status

from app.models.administrative_request import AdministrativeRequest
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student

STUDENT_STATUSES = {"active", "inactive", "blocked", "graduated"}
ENROLLMENT_STATUSES = {"pending", "active", "cancelled", "completed", "blocked"}
PAYMENT_STATUSES = {"pending", "paid", "overdue", "refunded"}
REQUEST_STATUSES = {"pending", "in_review", "approved", "rejected", "completed"}


def _bad_request(message: str) -> None:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def validate_student_status_change(student: Student, new_status: str) -> None:
    """Validate high-impact changes to the student lifecycle."""
    if new_status not in STUDENT_STATUSES:
        _bad_request(f"Invalid student status: {new_status}")
    if student.status == new_status:
        _bad_request("Student already has this status.")


def validate_enrollment_creation(student: Student, course: Course) -> None:
    if student.status == "blocked":
        _bad_request("Cannot create enrollment for a blocked student.")
    if not course.is_active:
        _bad_request("Cannot create enrollment for an inactive course.")


def validate_enrollment_status_change(enrollment: Enrollment, new_status: str) -> None:
    """Block unsafe enrollment transitions that manual SQL updates often miss."""
    if new_status not in ENROLLMENT_STATUSES:
        _bad_request(f"Invalid enrollment status: {new_status}")
    if enrollment.status == new_status:
        _bad_request("Enrollment already has this status.")
    if new_status == "active":
        if enrollment.student.status == "blocked":
            _bad_request("Cannot activate enrollment because the student is blocked.")
        if enrollment.payment_status == "overdue":
            _bad_request("Cannot activate enrollment with overdue payment status.")
        if not enrollment.course.is_active:
            _bad_request("Cannot activate enrollment in an inactive course.")
    if new_status == "completed" and enrollment.status != "active":
        _bad_request("Only active enrollments can be completed.")
    if new_status == "cancelled" and enrollment.status == "completed":
        _bad_request("Completed enrollments cannot be cancelled.")


def validate_payment_status_change(enrollment: Enrollment, new_payment_status: str) -> None:
    if new_payment_status not in PAYMENT_STATUSES:
        _bad_request(f"Invalid payment status: {new_payment_status}")
    if enrollment.payment_status == new_payment_status:
        _bad_request("Enrollment already has this payment status.")
    if enrollment.status == "completed" and new_payment_status in {"overdue", "pending"}:
        _bad_request("Cannot mark a completed enrollment as pending or overdue.")


def validate_request_status_transition(request: AdministrativeRequest, new_status: str) -> None:
    if new_status not in REQUEST_STATUSES:
        _bad_request(f"Invalid request status: {new_status}")
    allowed: dict[str, set[str]] = {
        "pending": {"in_review", "rejected"},
        "in_review": {"approved", "rejected"},
        "approved": {"completed"},
        "rejected": set(),
        "completed": set(),
    }
    if new_status not in allowed[request.status]:
        _bad_request(f"Cannot move request from {request.status} to {new_status}.")
