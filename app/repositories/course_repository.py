from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.course import Course
from app.schemas.course import CourseCreate


def create_course(db: Session, payload: CourseCreate) -> Course:
    course = Course(**payload.model_dump())
    db.add(course)
    return course


def get_course(db: Session, course_id: int) -> Course | None:
    return db.get(Course, course_id)


def list_courses(db: Session) -> list[Course]:
    return list(db.scalars(select(Course).order_by(Course.id)))
