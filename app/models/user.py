from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="viewer")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    created_requests = relationship(
        "AdministrativeRequest",
        foreign_keys="AdministrativeRequest.created_by_user_id",
        back_populates="created_by",
    )
    reviewed_requests = relationship(
        "AdministrativeRequest",
        foreign_keys="AdministrativeRequest.reviewed_by_user_id",
        back_populates="reviewed_by",
    )
    audit_logs = relationship("AuditLog", back_populates="user")
