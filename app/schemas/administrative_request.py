from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Priority, RequestStatus, RequestType


class AdministrativeRequestCreate(BaseModel):
    student_id: int
    request_type: RequestType
    description: str = Field(min_length=10)


class AdministrativeRequestRead(BaseModel):
    id: int
    student_id: int
    request_type: RequestType
    description: str
    status: RequestStatus
    priority: Priority | None
    created_by_user_id: int
    reviewed_by_user_id: int | None
    created_at: datetime
    reviewed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class RequestReject(BaseModel):
    reason: str = Field(min_length=5, max_length=1000)
