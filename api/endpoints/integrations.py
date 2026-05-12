from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status

from app.dependencies import get_db
from repositories.n8n_workflow_log_repository import N8nWorkflowLogRepository

router = APIRouter(tags=["integrations"])


async def _log_webhook_event(
    connection,
    workflow_name: str,
    payload: dict,
) -> None:
    try:
        await N8nWorkflowLogRepository(connection).create_log(
            workflow_name=workflow_name,
            status="triggered",
            source="api_webhook",
            related_entity_type="integration",
            request_payload=payload,
        )
    except Exception:
        return


@router.get(
    "/integrations/status",
    status_code=status.HTTP_200_OK,
    summary="Integration health snapshot",
)
async def integrations_status():
    now = datetime.now(timezone.utc).isoformat()
    return {
        "timestamp": now,
        "workflows": {
            "driver_ranking": {"status": "configured"},
            "fare_estimate": {"status": "configured"},
            "ride_completed": {"status": "configured"},
        },
    }


@router.post("/webhooks/ride-requested", status_code=status.HTTP_200_OK)
async def webhook_ride_requested(payload: dict, connection=Depends(get_db)):
    await _log_webhook_event(connection, "ride_requested", payload)
    return {"accepted": True, "workflow": "ride-requested", "payload": payload}


@router.post("/webhooks/fare-estimate", status_code=status.HTTP_200_OK)
async def webhook_fare_estimate(payload: dict, connection=Depends(get_db)):
    await _log_webhook_event(connection, "fare_estimate", payload)
    return {"accepted": True, "workflow": "fare-estimate", "payload": payload}


@router.post("/webhooks/ride-completed", status_code=status.HTTP_200_OK)
async def webhook_ride_completed(payload: dict, connection=Depends(get_db)):
    await _log_webhook_event(connection, "ride_completed", payload)
    return {"accepted": True, "workflow": "ride-completed", "payload": payload}


@router.post("/webhooks/payment-failed", status_code=status.HTTP_200_OK)
async def webhook_payment_failed(payload: dict, connection=Depends(get_db)):
    await _log_webhook_event(connection, "payment_failed", payload)
    return {"accepted": True, "workflow": "payment-failed", "payload": payload}


@router.post("/webhooks/driver-signup", status_code=status.HTTP_200_OK)
async def webhook_driver_signup(payload: dict, connection=Depends(get_db)):
    await _log_webhook_event(connection, "driver_signup", payload)
    return {"accepted": True, "workflow": "driver-signup", "payload": payload}
