from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.database import Base, SessionLocal, engine
from app.models.course import Course
from app.models.user import User
from app.repositories.user_repository import get_user_by_email

DEFAULT_USERS = [
    ("Admin EduFlow", "admin@eduflow.ai", "admin123", "admin"),
    ("Operator EduFlow", "operator@eduflow.ai", "operator123", "operator"),
    ("Viewer EduFlow", "viewer@eduflow.ai", "viewer123", "viewer"),
]


def seed_users(db: Session) -> None:
    for name, email, password, role in DEFAULT_USERS:
        if not get_user_by_email(db, email):
            db.add(
                User(
                    name=name,
                    email=email,
                    hashed_password=get_password_hash(password),
                    role=role,
                    is_active=True,
                )
            )


def seed_courses(db: Session) -> None:
    if db.query(Course).count() == 0:
        db.add_all(
            [
                Course(name="Python Backend Professional", category="Technology", workload_hours=120),
                Course(name="Data Analytics for Business", category="Data", workload_hours=80),
            ]
        )


def run_seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_users(db)
        seed_courses(db)
        db.commit()


if __name__ == "__main__":
    run_seed()
