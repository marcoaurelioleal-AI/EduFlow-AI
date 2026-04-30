from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    category: str = Field(min_length=2, max_length=80)
    workload_hours: int = Field(gt=0, le=10000)
    is_active: bool = True


class CourseRead(CourseCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CourseStatusUpdate(BaseModel):
    is_active: bool
    reason: str | None = Field(default=None, max_length=500)
