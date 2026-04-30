import pytest
from fastapi import HTTPException

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.services.safe_change_service import validate_enrollment_status_change


def test_safe_change_service_rejects_completed_without_active_status() -> None:
    student = Student(id=1, name="Ana", email="ana@example.com", cpf="123", status="active")
    course = Course(id=1, name="Python", category="Tech", workload_hours=80, is_active=True)
    enrollment = Enrollment(
        id=1,
        student_id=student.id,
        course_id=course.id,
        status="pending",
        payment_status="paid",
    )
    enrollment.student = student
    enrollment.course = course

    with pytest.raises(HTTPException) as exc_info:
        validate_enrollment_status_change(enrollment, "completed")

    assert exc_info.value.status_code == 400
    assert "Only active enrollments can be completed" in exc_info.value.detail
