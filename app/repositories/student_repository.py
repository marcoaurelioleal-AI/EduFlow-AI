from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student import Student
from app.schemas.student import StudentCreate


def create_student(db: Session, payload: StudentCreate) -> Student:
    student = Student(**payload.model_dump())
    db.add(student)
    return student


def get_student_by_email(db: Session, email: str) -> Student | None:
    return db.scalar(select(Student).where(Student.email == email))


def get_student_by_cpf(db: Session, cpf: str) -> Student | None:
    return db.scalar(select(Student).where(Student.cpf == cpf))


def get_student(db: Session, student_id: int) -> Student | None:
    return db.get(Student, student_id)


def list_students(
    db: Session,
    status: str | None = None,
    name: str | None = None,
    email: str | None = None,
) -> list[Student]:
    stmt = select(Student)
    if status:
        stmt = stmt.where(Student.status == status)
    if name:
        stmt = stmt.where(Student.name.ilike(f"%{name}%"))
    if email:
        stmt = stmt.where(Student.email.ilike(f"%{email}%"))
    return list(db.scalars(stmt.order_by(Student.id)))
