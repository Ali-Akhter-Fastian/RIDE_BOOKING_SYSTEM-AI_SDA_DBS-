from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, status

router = APIRouter(tags=["integrations"])


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
async def webhook_ride_requested(payload: dict):
    return {"accepted": True, "workflow": "ride-requested", "payload": payload}


@router.post("/webhooks/fare-estimate", status_code=status.HTTP_200_OK)
async def webhook_fare_estimate(payload: dict):
    return {"accepted": True, "workflow": "fare-estimate", "payload": payload}


@router.post("/webhooks/ride-completed", status_code=status.HTTP_200_OK)
async def webhook_ride_completed(payload: dict):
    return {"accepted": True, "workflow": "ride-completed", "payload": payload}


@router.post("/webhooks/payment-failed", status_code=status.HTTP_200_OK)
async def webhook_payment_failed(payload: dict):
    return {"accepted": True, "workflow": "payment-failed", "payload": payload}


@router.post("/webhooks/driver-signup", status_code=status.HTTP_200_OK)
async def webhook_driver_signup(payload: dict):
    return {"accepted": True, "workflow": "driver-signup", "payload": payload}
