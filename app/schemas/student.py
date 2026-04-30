from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.common import StudentStatus


def format_cpf_digits(value: str) -> str:
    digits = "".join(character for character in str(value) if character.isdigit())
    if len(digits) != 11:
        raise ValueError("CPF deve conter exatamente 11 dígitos.")
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


class StudentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    cpf: str = Field(min_length=14, max_length=14)
    status: StudentStatus = "active"

    @field_validator("cpf", mode="before")
    @classmethod
    def validate_and_format_cpf(cls, value: str) -> str:
        return format_cpf_digits(value)


class StudentRead(BaseModel):
    id: int
    name: str
    email: EmailStr
    cpf: str
    status: StudentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("cpf", mode="before")
    @classmethod
    def format_cpf_when_possible(cls, value: str) -> str:
        try:
            return format_cpf_digits(value)
        except ValueError:
            return str(value)


class StudentStatusUpdate(BaseModel):
    status: StudentStatus
    reason: str | None = Field(default=None, max_length=500)
