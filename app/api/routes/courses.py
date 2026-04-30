from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_session, require_operator_or_admin, require_viewer_or_above
from app.models.course import Course
from app.models.user import User
from app.repositories import course_repository
from app.schemas.course import CourseCreate, CourseRead, CourseStatusUpdate
from app.services.audit_service import create_audit_log

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_session),
    _: User = Depends(require_operator_or_admin),
) -> Course:
    course = course_repository.create_course(db, payload)
    db.commit()
    db.refresh(course)
    return course


@router.get("", response_model=list[CourseRead])
def list_courses(
    db: Session = Depends(get_session),
    _: User = Depends(require_viewer_or_above),
) -> list[Course]:
    return course_repository.list_courses(db)


@router.get("/{course_id}", response_model=CourseRead)
def get_course(
    course_id: int,
    db: Session = Depends(get_session),
    _: User = Depends(require_viewer_or_above),
) -> Course:
    course = course_repository.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    return course


@router.patch("/{course_id}/status", response_model=CourseRead)
def update_course_status(
    course_id: int,
    payload: CourseStatusUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(require_operator_or_admin),
) -> Course:
    course = course_repository.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found.")
    old_value = course.is_active
    course.is_active = payload.is_active
    create_audit_log(
        db,
        user_id=current_user.id,
        action="course_status_changed",
        entity_type="course",
        entity_id=course.id,
        old_value={"is_active": old_value},
        new_value={"is_active": payload.is_active},
        reason=payload.reason,
    )
    db.commit()
    db.refresh(course)
    return course
