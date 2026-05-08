from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from exception.payment_exceptions import raise_payment_http_exception
from schemas.payments.history import PaymentHistoryResponse
from services.payments.history import PaymentHistoryService

from .dependencies import get_current_user_id, get_payment_history_service

router = APIRouter()


@router.get(
    "/history",
    response_model=PaymentHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get paginated payment history for current user",
)
async def get_payment_history(
    user_id: UUID = Depends(get_current_user_id),
    service: PaymentHistoryService = Depends(get_payment_history_service),
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
) -> PaymentHistoryResponse:
    try:
        limit = page_size
        offset = (page - 1) * page_size
        
        result = await service.get_user_payment_history(user_id, limit=limit, offset=offset)
        return PaymentHistoryResponse(
            payments=result["payments"],
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
        )
    except Exception as exc:
        raise_payment_http_exception(exc)
