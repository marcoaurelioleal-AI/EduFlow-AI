from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import EnrollmentStatus, PaymentStatus


class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int
    status: EnrollmentStatus = "pending"
    payment_status: PaymentStatus = "pending"


class EnrollmentRead(EnrollmentCreate):
    id: int
    enrolled_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnrollmentStatusUpdate(BaseModel):
    status: EnrollmentStatus
    reason: str | None = Field(default=None, max_length=500)


class PaymentStatusUpdate(BaseModel):
    payment_status: PaymentStatus
    reason: str | None = Field(default=None, max_length=500)
