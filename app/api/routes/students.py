from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_operator_or_admin, require_viewer_or_above
from app.models.student import Student
from app.models.user import User
from app.repositories import student_repository
from app.schemas.student import StudentCreate, StudentRead, StudentStatusUpdate
from app.services.audit_service import create_audit_log
from app.services.safe_change_service import validate_student_status_change

router = APIRouter(prefix="/students", tags=["students"])


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_session),
    _: User = Depends(require_operator_or_admin),
) -> Student:
    if student_repository.get_student_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um aluno cadastrado com este e-mail.",
        )
    if student_repository.get_student_by_cpf(db, payload.cpf):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um aluno cadastrado com este CPF.",
        )
    student = student_repository.create_student(db, payload)
    db.commit()
    db.refresh(student)
    return student


@router.get("", response_model=list[StudentRead])
def list_students(
    status_filter: str | None = Query(default=None, alias="status"),
    name: str | None = None,
    email: str | None = None,
    db: Session = Depends(get_session),
    _: User = Depends(require_viewer_or_above),
) -> list[Student]:
    return student_repository.list_students(db, status=status_filter, name=name, email=email)


@router.get("/{student_id}", response_model=StudentRead)
def get_student(
    student_id: int,
    db: Session = Depends(get_session),
    _: User = Depends(require_viewer_or_above),
) -> Student:
    student = student_repository.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return student


@router.patch("/{student_id}/status", response_model=StudentRead)
def update_student_status(
    student_id: int,
    payload: StudentStatusUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_operator_or_admin),
) -> Student:
    student = student_repository.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    old_status = student.status
    validate_student_status_change(student, payload.status)
    student.status = payload.status
    blocked_enrollments: list[int] = []
    if payload.status == "blocked":
        for enrollment in student.enrollments:
            if enrollment.status == "active":
                enrollment.status = "blocked"
                blocked_enrollments.append(enrollment.id)
    create_audit_log(
        db,
        user_id=current_user.id,
        action="student_status_changed",
        entity_type="student",
        entity_id=student.id,
        old_value={"status": old_status},
        new_value={"status": payload.status, "blocked_enrollments": blocked_enrollments},
        reason=payload.reason,
    )
    db.commit()
    db.refresh(student)
    return student
