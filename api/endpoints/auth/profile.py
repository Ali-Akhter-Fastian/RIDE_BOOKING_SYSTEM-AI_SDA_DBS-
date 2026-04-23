from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from models.user import User
from schemas.auth import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)
