from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator

from core.enums import UserRole


class RegisterRequest(BaseModel):
    full_name: Annotated[str, Field(min_length=2, max_length=120)]
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=128)]
    confirm_password: Annotated[str, Field(min_length=8, max_length=128)]
    role: UserRole = UserRole.rider

    @model_validator(mode="after")
    def validate_password_confirmation(self) -> RegisterRequest:
        if self.password != self.confirm_password:
            raise ValueError("Password and confirm password must match")
        return self


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    role: UserRole
    created_at: datetime
    updated_at: datetime
